from __future__ import annotations
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

class ExtractedContent(BaseModel):
    summary: str
    key_facts: List[str]
    detected_text: List[str]
    objects: List[str]
    suggested_sections: List[str]

class Beat(BaseModel):
    title: str
    text: str
    target_seconds: float
    visuals: List[str]

class ScriptPackage(BaseModel):
    script: List[Beat]
    narration: str
    beat_timestamps: List[float]

class PipelineStateEnum(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    error = "error"

class VideoStyleEnum(str, Enum):
    default = "default"
    whiteboard = "whiteboard"
    slides = "slides"

class UploadRequest(BaseModel):
    job_id: str
    image_path: str = ""
    video_duration_sec: int
    audience_preset: str
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None
    narration_language: Optional[str] = "ru"
    tone: Optional[str] = "дружелюбный, объяснительный"
    style: VideoStyleEnum = VideoStyleEnum.default
    source_type: Literal['image','pdf','pptx','text'] = 'image'
    text_payload: Optional[str] = None

    @validator("video_duration_sec")
    def validate_duration(cls, v):
        if v not in (15,30,60,90):
            raise ValueError("duration must be one of 15/30/60/90")
        return v

class PipelineStatus(BaseModel):
    job_id: str
    state: PipelineStateEnum
    progress: int = Field(ge=0, le=100)
    message: str = ""
    output_video_path: Optional[str] = None
    srt_path: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    progress_map: Dict[str,int] = Field(default_factory=dict)
