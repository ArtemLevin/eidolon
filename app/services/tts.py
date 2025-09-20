from __future__ import annotations
from pathlib import Path

class ElevenLabsTTS:
    def synthesize(self, text: str, out_path: Path, voice_id: str | None, voice_name: str | None) -> str:
        # NOTE: Здесь должен быть вызов ElevenLabs TTS. Для офлайн-MVP создадим заглушку-«mp3».
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"FAKE_MP3")
        return str(out_path)
