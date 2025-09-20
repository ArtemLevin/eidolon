from __future__ import annotations
from pathlib import Path
from app.core.models import UploadRequest, PipelineStatus, PipelineStateEnum, ExtractedContent
from app.core.config import settings
from app.services.vision_extractor import VisionExtractor
from app.services.script_writer import ScriptWriter
from app.services.manim_builder import ManimBuilder
from app.services.tts import ElevenLabsTTS
from app.services.mux import combine
from app.services.srt import make_srt
from app.services.ingest import ingest_pdf, ingest_pptx, ingest_text
from app.core.utils import fit_narration_to_duration

def _from_text(text: str) -> ExtractedContent:
    text = (text or '').strip()
    return ExtractedContent(
        summary=text[:200] + ('...' if len(text) > 200 else ''),
        key_facts=[],
        detected_text=[text] if text else [],
        objects=[],
        suggested_sections=["Введение","Основная идея","Итоги"]
    )

def run_pipeline(req: UploadRequest) -> PipelineStatus:
    job_id = req.job_id
    workdir = Path(settings.work_dir) / job_id
    workdir.mkdir(parents=True, exist_ok=True)

    logs = []
    def log(m): logs.append(m)

    state = PipelineStateEnum.processing
    progress = 5
    message = "Step A: ingest/vision"
    srt_path = None
    output_video_path = None

    try:
        if req.source_type == "image":
            extractor = VisionExtractor()
            extracted = extractor.extract(req.image_path)
        elif req.source_type == "pdf":
            txt, imgs = ingest_pdf(req.image_path, settings.max_pages)
            if imgs:
                tmp_img = workdir / "first_page.png"
                tmp_img.write_bytes(imgs[0])
                ex = VisionExtractor().extract(str(tmp_img))
                ex.detected_text = (ex.detected_text or []) + ([txt] if txt else [])
                extracted = ex
            else:
                extracted = _from_text(txt)
        elif req.source_type == "pptx":
            txt, imgs = ingest_pptx(req.image_path, settings.max_pages)
            if imgs:
                tmp_img = workdir / "first_slide.png"
                tmp_img.write_bytes(imgs[0])
                ex = VisionExtractor().extract(str(tmp_img))
                ex.detected_text = (ex.detected_text or []) + ([txt] if txt else [])
                extracted = ex
            else:
                extracted = _from_text(txt)
        else:
            extracted = _from_text(req.text_payload or "")

        progress = 25; message = "Step B: compose script & narration"; log(message)
        writer = ScriptWriter()
        pkg = writer.compose(extracted, req.audience_preset, req.video_duration_sec, req.narration_language, req.tone)

        narration, est, ratio = fit_narration_to_duration(pkg.narration, req.video_duration_sec, settings.speech_min_wpm, settings.speech_max_wpm)

        progress = 45; message = "Step C: generate Manim code"; log(message)
        manim = ManimBuilder(workdir=str(workdir), style=req.style)
        py_code = manim.generate_code(pkg.script)

        progress = 60; message = "Step C: render video with Manim"; log(message)
        video_path = manim.render(py_code)

        progress = 75; message = "Step D: synthesize voice"; log(message)
        tts = ElevenLabsTTS()
        audio_path = workdir / "narration.mp3"
        tts.synthesize(narration, audio_path, req.voice_id, req.voice_name)

        progress = 82; message = "Step D+: generate SRT"; log(message)
        srt_path = str(make_srt(narration, pkg.beat_timestamps, workdir / "subtitles.srt"))

        progress = 90; message = "Step E: mux A/V"; log(message)
        final_path = workdir / "final.mp4"
        combine(video_path, audio_path, final_path, req.video_duration_sec)
        output_video_path = str(final_path)

        progress = 100; message = "Done"
        state = PipelineStateEnum.done
    except Exception as e:
        state = PipelineStateEnum.error
        message = f"Error: {e}"
    return PipelineStatus(
        job_id=job_id, state=state, progress=progress, message=message,
        output_video_path=output_video_path, srt_path=srt_path, logs=logs
    )
