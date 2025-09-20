from __future__ import annotations
from pathlib import Path
import shutil

def combine(video_path: str, audio_path: str, final_path: Path, target_duration: int) -> str:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    # NOTE: В реальности используем ffmpeg. Для офлайн-MVP просто копируем «видео».
    shutil.copyfile(video_path, final_path)
    return str(final_path)
