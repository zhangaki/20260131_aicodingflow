import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Import the refactored Gemini generator
try:
    from generate_images_gemini import GeminiImageGenerator, QuotaExceededError
except ImportError:
    # If standard import fails, try relative or direct path insertion
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from generate_images_gemini import GeminiImageGenerator, QuotaExceededError

class MultiProviderImageGenerator:
    def __init__(self):
        load_dotenv()
        env_path = Path("/Users/mac/code/super-individual/.env")
        if env_path.exists():
            load_dotenv(env_path)
        
        self.gemini = GeminiImageGenerator()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
             raise ValueError("OPENAI_API_KEY not found in environment.")
        
        self.openai_client = OpenAI(api_key=openai_key)
        self.use_openai_fallback = False
        self.enable_openai_fallback = False # Explicitly disabled to save cost

    def generate_with_openai(self, prompt, output_path):
        """Generates an image using DALL-E 3."""
        try:
            print(f"OpenAI: Generating {os.path.basename(output_path)}...")
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024", # Target roughly same aspect or square
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            if image_url:
                img_data = requests.get(image_url).content
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                return True
            return False
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return False

    def run(self, plan_file="image_generation_tasks.json"):
        if not os.path.exists(plan_file):
            print(f"Plan file {plan_file} not found.")
            return

        with open(plan_file, 'r') as f:
            tasks = json.load(f)

        project_root = Path(__file__).resolve().parent.parent
        print(f"Working in Project Root: {project_root}")

        # Filter for existing images
        tasks_to_run = []
        for task in tasks:
            rel_path = task.get('output_image_path').lstrip('/')
            final_path = project_root / "public" / rel_path
            if final_path.exists():
                continue
            task['final_output_path'] = str(final_path)
            tasks_to_run.append(task)

        print(f"Remaining images to generate: {len(tasks_to_run)}")
        
        success_count = 0
        for i, task in enumerate(tasks_to_run):
            print(f"\n[{i+1}/{len(tasks_to_run)}] {task['title']}")
            
            output_path = Path(task['final_output_path'])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            md_path = project_root / task['file_path']
            rel_image_path = task['output_image_path']
            
            success = False
            
            # 1. Try Gemini first unless fallback is already active
            if not self.use_openai_fallback:
                try:
                    if self.gemini.generate(task['prompt'], output_path, md_path, rel_image_path):
                        success = True
                        success_count += 1
                        time.sleep(2) # Normal rate limit
                except QuotaExceededError:
                    if self.enable_openai_fallback:
                        print("!!! Switching to OpenAI Fallback for this session !!!")
                        self.use_openai_fallback = True
                    else:
                        print("!!! Gemini Quota Exceeded. OpenAI Fallback is DISABLED. Stoping Batch. !!!")
                        break
            
            # 2. Try OpenAI Fallback
            if not success and self.use_openai_fallback:
                if self.generate_with_openai(task['prompt'], output_path):
                    # Update Markdown (OpenAI doesn't have the ref to MD update yet in helper)
                    self.gemini.update_blog_post(md_path, rel_image_path)
                    success = True
                    success_count += 1
                    time.sleep(5) # DALL-E 3 rate limit is usually tighter
            
            if not success:
                print(f"Critical Failure: Could not generate image for {task['title']}")

        print(f"\nBatch Finished. Generated {success_count}/{len(tasks_to_run)} images.")

if __name__ == "__main__":
    generator = MultiProviderImageGenerator()
    generator.run()
