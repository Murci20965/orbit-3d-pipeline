import asyncio
import httpx
from app.core.config import settings

TRIPO_URL = "https://api.tripo3d.ai/v2/openapi/task"
UPLOAD_URL = "https://api.tripo3d.ai/v2/openapi/upload"

async def upload_image_to_tripo(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Uploads the raw image to Tripo3D's secure servers and gets a file token."""
    print(f"[*] Tripo Service: Uploading physical file '{filename}' to Tripo3D...")
    headers = {"Authorization": f"Bearer {settings.TRIPO_API_KEY}"}
    files = {"file": (filename, file_bytes, content_type)}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(UPLOAD_URL, headers=headers, files=files)
        data = response.json()
        if response.status_code != 200 or data.get("code") != 0:
            raise Exception(f"Tripo Upload Error: {data}")
        return data["data"]["image_token"]

async def generate_raw_mesh(prompt: str = None, image_url: str = None, file_token: str = None) -> str:
    """Generates a 3D model from text, an image URL, or an uploaded file token."""
    headers = {
        "Authorization": f"Bearer {settings.TRIPO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if file_token:
        print("[*] Tripo Service: Initializing Image-to-3D with secure file_token...")
        payload = {
            "type": "image_to_model",
            "model_version": "v3.1-20260211",
            "file": {"type": "jpg", "file_token": file_token}
        }
    elif image_url:
        print("[*] Tripo Service: Initializing Image-to-3D with URL...")
        payload = {
            "type": "image_to_model",
            "model_version": "v3.1-20260211",
            "file": {"type": "jpg", "url": image_url}
        }
    else:
        print(f"[*] Tripo Service: Initializing Text-to-3D for prompt: '{prompt}'...")
        payload = {
            "type": "text_to_model",
            "model_version": "v3.1-20260211",
            "prompt": prompt
        }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(TRIPO_URL, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code != 200 or response_data.get("code") != 0:
            raise Exception(f"Tripo API Error: {response_data}")
            
        task_id = response_data['data']['task_id']
        print(f"[*] Tripo Task ID: {task_id}. Awaiting completion...", flush=True)

        attempts = 0
        while attempts < 100:
            await asyncio.sleep(3)
            attempts += 1
            
            poll_response = await client.get(f"{TRIPO_URL}/{task_id}", headers=headers)
            poll_data = poll_response.json()
            status = poll_data['data']['status']
            
            print(f"[*] Tripo Polling[{attempts}/100] - Status: {status}", flush=True)
            
            if status == "success":
                output_data = poll_data['data'].get('output', {})
                return output_data.get('pbr_model') or output_data.get('model')
            elif status in["failed", "cancelled", "unknown"]:
                raise Exception(f"Tripo generation failed. Status: {status}")
                
        raise Exception("Tripo3D API Timeout.")