from pydantic import BaseModel, model_validator
from typing import Optional, Any

class GenerationRequest(BaseModel):
    prompt: Optional[str] = None
    image_url: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_inputs(cls, data: Any) -> Any:
        prompt = data.get('prompt')
        image_url = data.get('image_url')
        
        if not prompt and not image_url:
            raise ValueError('You must provide either a "prompt" (text) or an "image_url".')
        
        return data