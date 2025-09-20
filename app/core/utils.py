from __future__ import annotations
from typing import Tuple

def estimate_speech_seconds(text: str, wpm: int = 160) -> float:
    words = max(1, len(text.split()))
    return words / (wpm/60.0)

def fit_narration_to_duration(text: str, duration_sec: int, min_wpm: int, max_wpm: int) -> Tuple[str, float, float]:
    est_min = estimate_speech_seconds(text, max_wpm)
    est_max = estimate_speech_seconds(text, min_wpm)
    est = (est_min + est_max) / 2
    ratio = est / duration_sec if duration_sec else 1.0
    return text, est, ratio
