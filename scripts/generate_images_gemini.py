import os
import re
from pathlib import Path
from google import genai
from dotenv import load_dotenv

class GeminiImageGenerator:
    def __init__(self, api_key=None):
        if not api_key:
            load_dotenv()
            # Try multiple locations for .env if needed
            api_key = os.getenv("Gemini_api_key")
            if not api_key:
                env_path = Path("/Users/mac/code/super-individual/.env")
                if env_path.exists():
                    load_dotenv(env_path)
                    api_key = os.getenv("Gemini_api_key")

        if not api_key:
            raise ValueError("Gemini API key not found. Please set Gemini_api_key in .env")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "imagen-4.0-fast-generate-001"

    def update_blog_post(self, md_path, rel_image_path):
        if not os.path.exists(md_path):
            return False
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'heroImage:' in content:
            updated = re.sub(
                r'heroImage:\s*["\'][^"\']*["\']',
                f'heroImage: "{rel_image_path}"',
                content
            )
            if updated != content:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(updated)
                return True
        return False

    def generate(self, prompt, output_path, md_path=None, rel_image_path=None):
        """
        Generates an image using Gemini Imagen.
        Returns True if successful, False otherwise.
        """
        try:
            print(f"Gemini: Generating {os.path.basename(output_path)}...")
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=genai.types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9", 
                )
            )
            
            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                
                # Update Markdown if provided
                if md_path and rel_image_path:
                    self.update_blog_post(md_path, rel_image_path)
                
                return True
            else:
                print(f"Gemini Failed: No images returned for prompt.")
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"Gemini Quota Exceeded: {error_msg}")
                raise QuotaExceededError(error_msg)
            print(f"Gemini Error: {e}")
            return False

class QuotaExceededError(Exception):
    """Raised when the API quota is hit."""
    pass

if __name__ == "__main__":
    # Test (Stand-alone mode)
    try:
        gen = GeminiImageGenerator()
        # gen.generate("A futuristic city in Swiss Design style", "test_gemini.jpg")
    except Exception as e:
        print(f"Error: {e}")
