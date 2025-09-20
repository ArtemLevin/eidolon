from __future__ import annotations
from pathlib import Path
from app.core.config import settings
from app.core.models import ExtractedContent
from app.services.preprocess import preprocess_image_to

VISION_PROMPT = """Ты — ассистент по компьютерному зрению. Получишь одно изображение.
1) Кратко опиши, что на нём (2–3 предложения).
2) Извлеки список ключевых фактов (до 8).
3) Извлеки распознанный текст (если есть).
4) Выдели логические секции/темы для объяснения.
Ответ строго в JSON под схему:
{
  "summary": "...",
  "key_facts": ["...", "..."],
  "detected_text": ["...", "..."],
  "objects": ["...", "..."],
  "suggested_sections": ["...", "..."]
}
Без комментариев вовне JSON.
"""

class VisionExtractor:
    def extract(self, image_path: str) -> ExtractedContent:
        prep = image_path
        if settings.preprocess_image:
            prep = preprocess_image_to(image_path, str(Path(image_path).with_suffix('.prep.jpg')))
        # NOTE: Здесь должен быть вызов OpenAI Vision. Для офлайн-MVP вернём заглушку.
        # Реальная интеграция: отправить bytes + VISION_PROMPT, распарсить JSON в ExtractedContent.
        return ExtractedContent(
            summary="Демо-описание изображения.",
            key_facts=["Факт 1","Факт 2"],
            detected_text=[],
            objects=["diagram","text"],
            suggested_sections=["Введение","Главная идея","Итоги"],
        )
