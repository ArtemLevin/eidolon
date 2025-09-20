from __future__ import annotations
from typing import List
from app.core.models import ExtractedContent, ScriptPackage, Beat

SCRIPT_PLANNER_PROMPT = """Ты — сценарист объясняющих видео. На входе: ExtractedContent и параметры:
- total_seconds = {VIDEO_DURATION_SEC}
- audience = {TARGET_AUDIENCE_PRESET}
- language = {NARRATION_LANGUAGE}
- tone = {TONE}

Сформируй 3–7 биитов (beats) так, чтобы суммарная длительность ≈ total_seconds.
Каждый биит: title, text (1–3 предложения), target_seconds (float), visuals (подсказки).
Сгенерируй связный текст озвучки (narration), один блок, естественная речь.
Ответ строго в JSON по схеме ScriptPackage.
"""

class ScriptWriter:
    def compose(self, extracted: ExtractedContent, audience_preset: str, duration_sec: int, language: str, tone: str) -> ScriptPackage:
        # NOTE: Здесь должен быть вызов LLM. Для офлайн-MVP сделаем детерминированную заготовку.
        beats: List[Beat] = [
            Beat(title="Введение", text="Короткое вступление.", target_seconds=max(3, duration_sec*0.2), visuals=["title","bullet"]),
            Beat(title="Идея", text="Главная мысль и пример.", target_seconds=max(4, duration_sec*0.5), visuals=["diagram","arrow"]),
            Beat(title="Итоги", text="Вывод и призыв к действию.", target_seconds=max(3, duration_sec*0.3), visuals=["summary"]),
        ]
        # Нормируем под duration_sec
        total = sum(b.target_seconds for b in beats)
        k = duration_sec / total if total else 1.0
        for b in beats:
            b.target_seconds = round(b.target_seconds * k, 2)
        narration = " ".join(b.text for b in beats)
        timestamps = []
        acc = 0.0
        for b in beats:
            acc += b.target_seconds
            timestamps.append(round(acc,2))
        return ScriptPackage(script=beats, narration=narration, beat_timestamps=timestamps)
