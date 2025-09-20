import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY","")
    openai_model_vision: str = os.getenv("OPENAI_MODEL_VISION","gpt-4o-mini")
    openai_model_text: str = os.getenv("OPENAI_MODEL_TEXT","gpt-4o-mini")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY","")
    elevenlabs_voice_default: str = os.getenv("ELEVENLABS_VOICE","Rachel")

    retries: int = 3

    # Ingest/limits
    preprocess_image: int = int(os.getenv('PREPROCESS_IMAGE', '0'))
    max_upload_mb: int = int(os.getenv('MAX_UPLOAD_MB', '25'))
    max_pages: int = int(os.getenv('MAX_PAGES', '20'))

    # Speech pace (wpm)
    speech_min_wpm: int = 150
    speech_max_wpm: int = 170

    work_dir: str = os.getenv("WORK_DIR","./_jobs")
    redis_url: str = os.getenv("REDIS_URL","redis://localhost:6379/0")
    rq_queue_name: str = os.getenv("RQ_QUEUE_NAME","explainer")

settings = Settings()
