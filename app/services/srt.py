from __future__ import annotations
from pathlib import Path
from typing import List

def make_srt(narration: str, timestamps: List[float], out_path: Path) -> str:
    # простая нарезка по предложениям и beat-таймкодам
    sents = [s.strip() for s in narration.split('.') if s.strip()]
    if not sents:
        sents = [narration.strip()]
    out = []
    start = 0.0
    for i, s in enumerate(sents, start=1):
        end = timestamps[min(i-1, len(timestamps)-1)] if timestamps else start + 2.0
        def fmt(t):
            ms = int((t - int(t)) * 1000)
            h = int(t // 3600); m = int(t%3600 // 60); sec = int(t%60)
            return f"{h:02}:{m:02}:{sec:02},{ms:03}"
        out.append(f"{i}\n{fmt(start)} --> {fmt(end)}\n{s}.\n")
        start = end
    out_path.write_text("\n".join(out), encoding="utf-8")
    return str(out_path)
