import os
import httpx

async def download_model(url: str, filename: str) -> str:
    """Download the raw mesh from the internet to the temp folder."""
    os.makedirs("temp", exist_ok=True)
    filepath = os.path.join("temp", filename)
    
    print(f"[*] Downloading mesh to {filepath}...")
    
    # Use a long timeout because 3D files can be large
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url)
        if response.status_code == 200:
            # Write the raw bytes to a physical file
            with open(filepath, "wb") as f:
                f.write(response.content)
            print("[*] Download complete!")
            return filepath
        else:
            raise Exception(f"Failed to download mesh. Status: {response.status_code}")