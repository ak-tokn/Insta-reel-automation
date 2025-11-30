"""
Animated Background Generator for StoicAlgo
Uses fal.ai Kling API to create animated video backgrounds from static images.
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict
from scripts.logger import get_logger
from scripts.utils import load_settings

logger = get_logger("AnimatedBackground")

class AnimatedBackgroundGenerator:
    """Generates animated video backgrounds using fal.ai Kling AI."""
    
    def __init__(self):
        self.settings = load_settings()
        self.api_key = os.environ.get('FAL_API_KEY')
        self.base_url = "https://queue.fal.run"
        self.model = "fal-ai/kling-video/v2.1/standard/image-to-video"
        
        project_root = Path(__file__).parent.parent
        self.output_dir = project_root / "output" / "animated"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.animation_config = self.settings.get('animation', {})
        self.enabled = self.animation_config.get('enabled', True)
        self.frequency = self.animation_config.get('frequency', 5)
        self.duration = self.animation_config.get('duration', '5')
    
    def is_available(self) -> bool:
        """Check if animated background generation is available."""
        if not self.api_key:
            logger.warning("FAL_API_KEY not found in environment")
            return False
        return self.enabled
    
    def should_generate_animated(self, post_count: int) -> bool:
        """Determine if this post should use an animated background."""
        if not self.is_available():
            return False
        return post_count % self.frequency == 0
    
    def _upload_image(self, image_path: Path) -> Optional[str]:
        """Upload image to a temporary hosting service for fal.ai to access."""
        try:
            with open(image_path, 'rb') as f:
                files = {'reqtype': (None, 'fileupload'), 'time': (None, '1h'), 'fileToUpload': (image_path.name, f)}
                response = requests.post('https://litterbox.catbox.moe/resources/internals/api.php', files=files, timeout=60)
                
                if response.status_code == 200 and response.text.startswith('http'):
                    logger.info(f"Image uploaded: {response.text}")
                    return response.text
                else:
                    logger.error(f"Image upload failed: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return None
    
    def generate_animated_background(
        self,
        image_path: Path,
        prompt: str = None,
        output_name: str = None
    ) -> Optional[Path]:
        """
        Generate an animated video background from a static image.
        
        Args:
            image_path: Path to the source image
            prompt: Optional motion prompt (defaults to subtle ambient motion)
            output_name: Optional output filename
            
        Returns:
            Path to the generated video, or None if failed
        """
        if not self.is_available():
            logger.error("Animated background generation not available")
            return None
        
        logger.info(f"Generating animated background from: {image_path.name}")
        
        image_url = self._upload_image(image_path)
        if not image_url:
            return None
        
        if prompt is None:
            prompt = "Subtle ambient motion, gentle movement, cinematic atmosphere, slow drift, atmospheric particles floating"
        
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": self.duration,
            "aspect_ratio": "9:16",
            "negative_prompt": "fast motion, jerky movement, distortion, blur, low quality, text, watermark",
            "cfg_scale": 0.5
        }
        
        try:
            submit_response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if submit_response.status_code != 200:
                logger.error(f"Failed to submit request: {submit_response.text}")
                return None
            
            result = submit_response.json()
            request_id = result.get('request_id')
            
            if not request_id:
                logger.error(f"No request_id in response: {result}")
                return None
            
            logger.info(f"Request submitted, ID: {request_id}")
            
            status_url = f"{self.base_url}/{self.model}/requests/{request_id}/status"
            max_wait = 600
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(status_url, headers=headers, timeout=30)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    logger.info(f"Generation status: {status}")
                    
                    if status == 'COMPLETED':
                        result_url = f"{self.base_url}/{self.model}/requests/{request_id}"
                        result_response = requests.get(result_url, headers=headers, timeout=30)
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            video_url = result_data.get('video', {}).get('url')
                            
                            if video_url:
                                return self._download_video(video_url, output_name)
                        
                        logger.error(f"Failed to get result: {result_response.text}")
                        return None
                    
                    elif status == 'FAILED':
                        logger.error(f"Generation failed: {status_data}")
                        return None
                    
                    elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                        time.sleep(10)
                    else:
                        time.sleep(5)
                else:
                    logger.warning(f"Status check failed: {status_response.text}")
                    time.sleep(10)
            
            logger.error("Generation timed out")
            return None
            
        except Exception as e:
            logger.error(f"Animation generation failed: {e}")
            return None
    
    def _download_video(self, video_url: str, output_name: str = None) -> Optional[Path]:
        """Download the generated video."""
        try:
            if output_name is None:
                from scripts.utils import get_timestamp_filename
                output_name = get_timestamp_filename("animated", "mp4")
            
            output_path = self.output_dir / output_name
            
            response = requests.get(video_url, timeout=120)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Animated background saved: {output_path}")
                return output_path
            else:
                logger.error(f"Video download failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Video download error: {e}")
            return None


def get_post_count() -> int:
    """Get the current post count from logs."""
    try:
        import json
        project_root = Path(__file__).parent.parent
        log_file = project_root / "logs" / "post_count.json"
        
        if log_file.exists():
            with open(log_file) as f:
                data = json.load(f)
                return data.get('count', 0)
        return 0
    except:
        return 0


def increment_post_count() -> int:
    """Increment and return the post count."""
    try:
        import json
        project_root = Path(__file__).parent.parent
        log_file = project_root / "logs" / "post_count.json"
        
        count = get_post_count() + 1
        
        with open(log_file, 'w') as f:
            json.dump({'count': count}, f)
        
        return count
    except:
        return 1
