from app.core.utils import estimate_speech_seconds

def test_estimate_speech_seconds():
    s = estimate_speech_seconds("one two three four five", wpm=150)
    assert s > 0
