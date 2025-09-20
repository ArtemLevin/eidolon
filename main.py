from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router

app = FastAPI(title="Explainer MVP")
app.include_router(api_router)
app.mount("/", StaticFiles(directory="app/web", html=True), name="web")
