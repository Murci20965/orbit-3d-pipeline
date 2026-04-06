import base64
from groq import AsyncGroq
from app.core.config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

async def generate_educational_context(prompt: str = None, file_bytes: bytes = None, mime_type: str = "image/jpeg") -> str:
    """Generates an educational summary using either text or vision models."""
    try:
        # PATH 1: The user uploaded an image (Use the Vision Model)
        if file_bytes:
            print("[*] Groq Service: Analyzing uploaded image with Llama-3.2 Vision Model...")
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content":[
                            {
                                "type": "text", 
                                "text": "You are a professional educational AI. Look at this image. Identify the main object and provide 2 short sentences explaining its physical structure, anatomy, how it functions, or its scientific properties."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct", 
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
            
        # PATH 2: The user typed a text prompt (Use the standard Text Model)
        else:
            print(f"[*] Groq Service: Requesting context for text prompt: '{prompt}'...")
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional educational AI. Explain what the user's generated 3D object is in 2 short sentences, focusing entirely on its physical structure, anatomy, or scientific function."},
                    {"role": "user", "content": f"The user generated a 3D model of: {prompt}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"[!] Groq Error: {str(e)}")
        return "Educational context could not be loaded at this time."