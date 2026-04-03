from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request
from typing import Optional
import os
import uuid
import subprocess
import asyncio

from app.services.tripo import generate_raw_mesh, upload_image_to_tripo
from app.services.utils import download_model
from app.services.groq_ai import generate_educational_context

router = APIRouter()

@router.post("/generate")
async def generate_3d_asset(
    request: Request,
    prompt: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    try:
        print(f"[*] API: Received multimodal generation request.")
        
        # 1. Handle the physical file upload securely
        file_token = None
        if file and file.filename:
            print(f"[*] API: Processing uploaded file: {file.filename}")
            file_bytes = await file.read()
            file_token = await upload_image_to_tripo(file_bytes, file.filename, file.content_type)
        
        if not prompt and not image_url and not file_token:
            raise Exception("You must provide a text prompt or upload an image.")

        # 2. Process concurrently
        context_subject = prompt if prompt else "an uploaded image object"
        # Pass the file_bytes directly to Groq if the user uploaded a file
        groq_task = generate_educational_context(
            prompt=prompt, 
            file_bytes=file_bytes if file else None, 
            mime_type=file.content_type if file else "image/jpeg"
        )
        tripo_task = generate_raw_mesh(prompt, image_url, file_token)
        
        educational_context, raw_mesh_url = await asyncio.gather(groq_task, tripo_task)
        
        # 3. Downloader
        job_id = str(uuid.uuid4())
        raw_filepath = await download_model(raw_mesh_url, f"{job_id}_raw.glb")

        # 4. Blender Optimization
        optimized_filepath = os.path.join("temp", f"{job_id}_optimized.glb")
        abs_raw, abs_opt = os.path.abspath(raw_filepath), os.path.abspath(optimized_filepath)

        print(f"[*] API: Initiating Headless Blender Optimization...")
        result = subprocess.run(["blender", "-b", "-P", "blender/optimize.py", "--", abs_raw, abs_opt],
            capture_output=True, text=True
        )

        if result.returncode != 0 or not os.path.exists(abs_opt):
            print(f"--- BLENDER LOG ---\n{result.stderr}")
            raise Exception("Mesh optimization process failed.")

        return {
            "status": "success",
            "message": "3D asset generated and optimized successfully.",
            "educational_context": educational_context,
            "original_mesh_url": raw_mesh_url,
            "optimized_local_file": optimized_filepath,
            "optimized_web_url": f"{request.base_url}temp/{job_id}_optimized.glb"
        }
    except Exception as e:
        print(f"\n[!!!] PIPELINE CRASHED: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))