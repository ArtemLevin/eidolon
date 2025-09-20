from __future__ import annotations
import subprocess, tempfile
from pathlib import Path
from typing import List
from app.core.models import Beat, VideoStyleEnum
from app.core.config import settings

MANIM_TEMPLATE = '''from manim import *

class ExplainerScene(Scene):
    def construct(self):
        pass

def render_beat(scene: Scene, beat_title: str, visuals: list[str], seconds: float):
    title = Text(beat_title).to_edge(UP)
    scene.play(Write(title))
    # TODO: визуальные подсказки -> простая геометрия/буллеты/стрелки
    scene.wait(seconds * 0.7)
    scene.play(FadeOut(title))
'''

class ManimBuilder:
    def __init__(self, workdir: str, style: VideoStyleEnum):
        self.workdir = Path(workdir)
        self.style = style

    def generate_code(self, beats: List[Beat]) -> str:
        code_path = self.workdir / "manim_scene.py"
        lines = [MANIM_TEMPLATE, "", "class GeneratedExplainer(ExplainerScene):", "    def construct(self):"]
        for b in beats:
            lines.append(f"        render_beat(self, {b.title!r}, {b.visuals!r}, {b.target_seconds})")
        code_path.write_text("\n".join(lines), encoding="utf-8")
        return str(code_path)

    def render(self, code_path: str) -> str:
        out_dir = self.workdir / "videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        # Для MVP можно сымитировать вывод, чтобы не требовать Manim локально.
        # Реальный вариант: вызвать manim CLI.
        fake = out_dir / "video.mp4"
        fake.write_bytes(b"FAKE_MP4")
        return str(fake)
