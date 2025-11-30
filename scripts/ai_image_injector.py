"""
AI Image Injector for StoicAlgo
Generates AI images using Stability AI for the ai_injected folder.
"""

import os
import requests
import base64
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from scripts.logger import get_logger
from scripts.utils import load_settings, get_env_var, ensure_dir, generate_id

logger = get_logger("AIImageInjector")


class AIImageInjector:
    """Generates AI images for the content pipeline."""
    
    def __init__(self):
        self.settings = load_settings()
        self.ai_config = self.settings.get('ai_image_generation', {})
        
        # Check if enabled
        self.enabled = self.ai_config.get('enabled', True)
        
        # API settings
        self.provider = self.ai_config.get('provider', 'stability')
        self.model = self.ai_config.get('model', 'stable-diffusion-xl-1024-v1-0')
        self.style_preset = self.ai_config.get('style_preset', 'cinematic')
        self.cfg_scale = self.ai_config.get('cfg_scale', 7)
        self.steps = self.ai_config.get('steps', 30)
        
        # Output settings
        self.weekly_count = self.ai_config.get('weekly_count', 2)
        
        # Paths
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / self.settings['paths']['images'] / "ai_injected"
        ensure_dir(self.output_dir)
        
        # Image dimensions (vertical for Reels)
        # SDXL allowed vertical dimensions: 640x1536, 768x1344, 832x1216, 896x1152
        self.width = 768
        self.height = 1344  # Best quality vertical option for SDXL
    
    def generate_weekly_images(self) -> List[Path]:
        """Generate the weekly batch of AI images."""
        
        if not self.enabled:
            logger.info("AI image generation is disabled")
            return []
        
        logger.info(f"Generating {self.weekly_count} AI images for this week")
        
        generated_paths = []
        
        for i in range(self.weekly_count):
            try:
                # Generate a prompt
                prompt = self._generate_stoic_prompt()
                
                # Generate image
                image_path = self.generate_image(prompt)
                
                if image_path:
                    generated_paths.append(image_path)
                    logger.info(f"Generated image {i+1}/{self.weekly_count}: {image_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to generate image {i+1}: {str(e)}")
        
        logger.info(f"Weekly generation complete: {len(generated_paths)} images created")
        return generated_paths
    
    def generate_image(self, prompt: str, negative_prompt: str = None) -> Optional[Path]:
        """
        Generate a single AI image.
        
        Args:
            prompt: The generation prompt
            negative_prompt: Things to avoid in the image
            
        Returns:
            Path to the generated image, or None if failed
        """
        
        if self.provider == 'stability':
            return self._generate_stability_image(prompt, negative_prompt)
        else:
            raise NotImplementedError(f"Provider {self.provider} not supported")
    
    def _generate_stability_image(self, prompt: str, negative_prompt: str = None) -> Optional[Path]:
        """Generate image using Stability AI API."""
        
        try:
            api_key = get_env_var('STABILITY_API_KEY')
        except ValueError:
            logger.error("STABILITY_API_KEY not set")
            return None
        
        # Default negative prompt
        if negative_prompt is None:
            negative_prompt = (
                "blurry, low quality, text, watermark, signature, "
                "bright colors, cheerful, cartoon, anime, oversaturated, "
                "people faces, hands, fingers"
            )
        
        # API endpoint
        url = f"https://api.stability.ai/v1/generation/{self.model}/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        body = {
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": negative_prompt, "weight": -1}
            ],
            "cfg_scale": self.cfg_scale,
            "height": self.height,
            "width": self.width,
            "samples": 1,
            "steps": self.steps,
            "style_preset": self.style_preset
        }
        
        logger.debug(f"Generating image with prompt: {prompt[:100]}...")
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code != 200:
                logger.error(f"Stability API error: {response.status_code} - {response.text}")
                return None
            
            # Parse response
            data = response.json()
            
            # Save image
            for i, artifact in enumerate(data.get("artifacts", [])):
                if artifact.get("finishReason") == "SUCCESS":
                    # Decode base64 image
                    image_data = base64.b64decode(artifact["base64"])
                    
                    # Generate filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"ai_{timestamp}_{generate_id()[:6]}.png"
                    output_path = self.output_dir / filename
                    
                    # Save
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    
                    return output_path
            
            logger.error("No successful artifacts in response")
            return None
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return None
    
    def _generate_stoic_prompt(self) -> str:
        """Generate a prompt matching the brand aesthetic."""
        
        # Base elements that define the aesthetic
        base_elements = [
            "dark cinematic lighting",
            "moody atmospheric",
            "dramatic shadows",
            "8k ultra detailed",
            "professional photography"
        ]
        
        # Subject options
        subjects = [
            "ancient Greek marble statue in dramatic pose",
            "Roman emperor bust in dark museum setting",
            "samurai warrior statue with katana",
            "stoic philosopher statue in contemplation",
            "ancient temple ruins in fog",
            "misty mountain peaks at dawn",
            "cosmic nebula with sacred geometry overlay",
            "dark forest path with ethereal light",
            "ancient library with glowing books",
            "desert landscape with single monolith"
        ]
        
        # Style modifiers
        style_modifiers = [
            "subtle green/emerald digital accents",
            "faint holographic elements",
            "geometric light patterns",
            "particle effects in the air",
            "volumetric fog and light rays",
            "cyberpunk undertones"
        ]
        
        # Technical requirements
        technical = [
            "vertical composition 9:16",
            "no text",
            "no logos",
            "no watermarks",
            "photorealistic"
        ]
        
        # Build prompt
        subject = random.choice(subjects)
        modifier = random.choice(style_modifiers)
        
        prompt = f"{subject}, {modifier}, {', '.join(base_elements)}, {', '.join(technical)}"
        
        return prompt
    
    def generate_custom_image(self, mood: str, suggestions: List[str]) -> Optional[Path]:
        """
        Generate an image based on content mood and suggestions.
        
        Args:
            mood: The mood of the content
            suggestions: Image suggestions from the LLM
            
        Returns:
            Path to generated image
        """
        
        # Build prompt from suggestions
        base_prompt = suggestions[0] if suggestions else "dark stoic aesthetic"
        
        # Mood modifiers
        mood_elements = {
            "contemplative": "serene, thoughtful, quiet, meditative",
            "powerful": "strong, imposing, dramatic, heroic",
            "serene": "peaceful, calm, zen, balanced",
            "determined": "focused, resolute, unwavering",
            "epic": "grand, vast, cosmic, awe-inspiring",
            "wise": "ancient, scholarly, reverent"
        }
        
        mood_modifier = mood_elements.get(mood.lower(), "atmospheric")
        
        # Build full prompt
        full_prompt = f"{base_prompt}, {mood_modifier}, dark cinematic lighting, 8k ultra detailed, vertical composition, subtle green digital accents, no text, no watermarks"
        
        return self.generate_image(full_prompt)
    
    def cleanup_old_images(self, keep_count: int = 10):
        """Remove old AI-generated images, keeping the most recent."""
        
        images = list(self.output_dir.glob("*.png")) + list(self.output_dir.glob("*.jpg"))
        
        if len(images) <= keep_count:
            return
        
        # Sort by modification time
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove older images
        for image in images[keep_count:]:
            try:
                os.remove(image)
                logger.info(f"Cleaned up old image: {image.name}")
            except Exception as e:
                logger.warning(f"Failed to remove {image.name}: {e}")


def generate_weekly_images() -> List[Path]:
    """Convenience function for weekly image generation."""
    injector = AIImageInjector()
    return injector.generate_weekly_images()


if __name__ == "__main__":
    # Test the AI image injector
    import os
    
    injector = AIImageInjector()
    
    print("=== AI Image Injector ===")
    print(f"Enabled: {injector.enabled}")
    print(f"Provider: {injector.provider}")
    print(f"Weekly count: {injector.weekly_count}")
    print(f"Output directory: {injector.output_dir}")
    
    # Check for API key
    if not os.environ.get('STABILITY_API_KEY'):
        print("\n⚠️  STABILITY_API_KEY not set. Set it to generate images.")
        print("\nExample prompt generation:")
        for i in range(3):
            prompt = injector._generate_stoic_prompt()
            print(f"\n{i+1}. {prompt[:200]}...")
    else:
        print("\n✓ API key found")
        
        # Test single image generation
        user_input = input("\nGenerate a test image? (y/n): ")
        if user_input.lower() == 'y':
            prompt = injector._generate_stoic_prompt()
            print(f"\nPrompt: {prompt}")
            print("Generating...")
            
            path = injector.generate_image(prompt)
            if path:
                print(f"✓ Image saved: {path}")
            else:
                print("✗ Generation failed")
