import numpy as np, cv2
from pathlib import Path
from app.services.preprocess import preprocess_image_to

def test_preprocess_basic(tmp_path):
    img = np.zeros((200,300,3), dtype=np.uint8)
    img[:] = (10,10,10)
    p = tmp_path / "in.jpg"
    cv2.imwrite(str(p), img)
    out = preprocess_image_to(str(p), str(tmp_path / "out.jpg"), long_edge=100)
    assert Path(out).exists()
