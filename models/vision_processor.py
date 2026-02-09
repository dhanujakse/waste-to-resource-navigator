import io
import base64
from PIL import Image
from dotenv import load_dotenv
import os
import json
import re
from utils.openrouter_config import (
    get_openrouter_client,
    get_openrouter_headers,
    get_openrouter_model_vision,
    is_strict_genai
)

load_dotenv()

class WasteVisionAnalyzer:
    """
    Analyzes waste images using Google Gemini to identify material type, 
    characteristics, and generates behavioral nudges.
    """
    
    def __init__(self):
        # Initialize OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.client = get_openrouter_client()
        self.model_name = get_openrouter_model_vision()
        self.headers = get_openrouter_headers()
        self.strict = is_strict_genai()

    def analyze_waste_image(self, image_data, image_format='bytes', filename=None):
        """
        Analyze waste image using GenAI only (no fallback).
        """
        # 1. Try Real AI (OpenRouter Vision)
        try:
            # Convert bytes to PIL Image
            if image_format == 'bytes':
                image = Image.open(io.BytesIO(image_data))
                raw_bytes = image_data
            elif image_format == 'path':
                image = Image.open(image_data)
                with open(image_data, "rb") as f:
                    raw_bytes = f.read()
            else:
                raise ValueError("Unsupported image format")
            
            # Sanity Check for OpenRouter Key
            if os.getenv("OPENROUTER_API_KEY"):
                # Create the prompt 
                prompt = """
                Analyze this waste image. Return JSON:
                {
                    "material_type": "string",
                    "confidence_score": integer,
                    "hazardous_indicators": ["list"],
                    "recyclability_status": "Recyclable|Non-recyclable|Hazardous",
                    "description": "Technical description",
                    "material_category": "Plastic|Glass|Metal|Paper|Electronic|Chemical|Mixed",
                    "sustainability_nudge": "Impact statement"
                }
                """
                mime_type = "image/jpeg"
                if image.format:
                    fmt = image.format.lower()
                    if fmt == "png":
                        mime_type = "image/png"
                    elif fmt == "webp":
                        mime_type = "image/webp"

                b64 = base64.b64encode(raw_bytes).decode("utf-8")
                data_url = f"data:{mime_type};base64,{b64}"
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    extra_headers=self.headers,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": data_url}}
                            ]
                        }
                    ]
                )
                content = response.choices[0].message.content or ""
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    data["analysis_source"] = "openrouter"
                    return data

        except Exception as e:
            raise RuntimeError(f"OpenRouter vision failed: {e}")

    def validate_material_type(self, material_type):
        """
        Validate and normalize material types to standard categories
        """
        material_mapping = {
            'pet': 'PET',
            # ... (mappings)
        }
        normalized = material_type.lower().strip()
        return material_mapping.get(normalized, material_type.upper())
