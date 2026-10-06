from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Only the live UI (and local dev) may call the engine from a browser. CORS
# does not stop scripts; the limits in app/api/routes.py protect the credits.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://orbit-3d-pipeline.vercel.app", "http://localhost:3000"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("temp", exist_ok=True)
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
app.include_router(router)

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Orbit-Engine API is running."}