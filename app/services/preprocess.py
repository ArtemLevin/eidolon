from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np

def preprocess_image_to(path_in: str, path_out: str, long_edge: int = 1600) -> str:
    img = cv2.imread(path_in, cv2.IMREAD_COLOR)
    if img is None:
        return path_in
    h, w = img.shape[:2]
    scale = long_edge / max(h, w)
    if scale < 1.0:
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    res = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    out = Path(path_out); out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), res)
    return str(out)
