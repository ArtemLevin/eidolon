from __future__ import annotations
import uuid, shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.models import UploadRequest, VideoStyleEnum, PipelineStateEnum
from app.workers.pipeline import run_pipeline

router = APIRouter(prefix="/api")

def allowed_duration(v: int) -> bool:
    return v in (15,30,60,90)

def allowed_audience(s: str) -> bool:
    return s in ("школьники","начинающие","продвинутые","руководители")

def secure_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (".","_","-")).strip("._")

@router.post("/upload")
async def upload(
    image: UploadFile = File(None),
    video_duration_sec: int = Form(...),
    audience_preset: str = Form(...),
    voice_id: Optional[str] = Form(None),
    voice_name: Optional[str] = Form(None),
    narration_language: Optional[str] = Form("ru"),
    tone: Optional[str] = Form("дружелюбный, объяснительный"),
    style: Optional[str] = Form("default"),
    source_type: Optional[str] = Form("image"),
    text: Optional[str] = Form(None),
):
    if source_type not in ("image","pdf","pptx","text"):
        raise HTTPException(422, detail="invalid source_type")
    if not allowed_duration(video_duration_sec):
        raise HTTPException(400, detail="duration must be one of 15/30/60/90")
    if not allowed_audience(audience_preset):
        raise HTTPException(400, detail="invalid audience preset")
    if style not in ("default","whiteboard","slides"):
        raise HTTPException(400, detail="invalid style")

    job_id = str(uuid.uuid4())
    workdir = Path(settings.work_dir) / job_id
    workdir.mkdir(parents=True, exist_ok=True)

    file_path = None
    if source_type == "image":
        if image is None or image.content_type not in ("image/jpeg","image/png"):
            raise HTTPException(400, detail="image must be jpeg or png")
        filename = secure_filename(image.filename or f"upload.{image.content_type.split('/')[-1]}")
        file_path = workdir / filename
        with file_path.open("wb") as f:
            shutil.copyfileobj(image.file, f)
    elif source_type in ("pdf","pptx"):
        if image is None:
            raise HTTPException(400, detail="file is required")
        if source_type=="pdf" and image.content_type not in ("application/pdf",):
            raise HTTPException(400, detail="pdf required")
        if source_type=="pptx" and image.content_type not in ("application/vnd.openxmlformats-officedocument.presentationml.presentation","application/octet-stream"):
            raise HTTPException(400, detail="pptx required")
        filename = secure_filename(image.filename or ("upload.pdf" if source_type=="pdf" else "upload.pptx"))
        file_path = workdir / filename
        with file_path.open("wb") as f:
            shutil.copyfileobj(image.file, f)
    else:
        if not text or not text.strip():
            raise HTTPException(400, detail="text is empty")

    req = UploadRequest(
        job_id=job_id,
        image_path=str(file_path) if file_path else "",
        video_duration_sec=video_duration_sec,
        audience_preset=audience_preset,
        voice_id=voice_id,
        voice_name=voice_name,
        narration_language=narration_language,
        tone=tone,
        style=VideoStyleEnum(style),
        source_type=source_type,
        text_payload=text,
    )

    # Synchronous pipeline for MVP
    from app.workers.pipeline import run_pipeline
    status = run_pipeline(req)
    (workdir / "status.json").write_text(status.json(indent=2), encoding="utf-8")
    return {"job_id": job_id}

@router.get("/status/{job_id}")
async def status(job_id: str):
    p = Path(settings.work_dir) / job_id / "status.json"
    if not p.exists():
        return {"state": "queued", "progress": 0, "message": "queued"}
    return json.loads(p.read_text(encoding="utf-8"))

@router.get("/download/{job_id}")
async def download(job_id: str, kind: Optional[str] = None):
    workdir = Path(settings.work_dir) / job_id
    if kind == "srt":
        srt = workdir / "subtitles.srt"
        if not srt.exists():
            raise HTTPException(404, "SRT not found")
        return FileResponse(str(srt), media_type="text/plain", filename="subtitles.srt")
    f = workdir / "final.mp4"
    if not f.exists():
        raise HTTPException(404, "final video not found")
    return FileResponse(str(f), media_type="video/mp4", filename="final.mp4")
