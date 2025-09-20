from app.services.ingest.text import ingest_text

def test_ingest_text():
    t, imgs = ingest_text("Hello world")
    assert "Hello" in t
    assert imgs == []
