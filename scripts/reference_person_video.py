"""
Reference Person Video Generator for StoicAlgo
Uses fal.ai Vidu Reference-to-Video API to generate videos with a specific person.
"""

import os
import asyncio
import requests
from pathlib import Path
from typing import Optional, List
import fal_client
from scripts.logger import get_logger
from scripts.utils import load_settings, get_timestamp_filename

logger = get_logger("ReferencePersonVideo")


class ReferencePersonVideoGenerator:
    """Generates videos featuring a reference person using Vidu API."""
    
    def __init__(self):
        self.settings = load_settings()
        self.api_key = os.environ.get('FAL_API_KEY')
        self.model = "fal-ai/vidu/reference-to-video"
        
        if self.api_key:
            os.environ['FAL_KEY'] = self.api_key
        
        project_root = Path(__file__).parent.parent
        self.reference_dir = project_root / "assets" / "reference_person"
        self.output_dir = project_root / "output" / "reference_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ref_config = self.settings.get('reference_person', {})
        self.enabled = self.ref_config.get('enabled', False)
        self.frequency = self.ref_config.get('frequency', 10)
    
    def is_available(self) -> bool:
        """Check if reference person video generation is available."""
        if not self.api_key:
            logger.warning("FAL_API_KEY not found in environment")
            return False
        if not self.enabled:
            return False
        if not self.reference_dir.exists():
            logger.warning("Reference person directory not found")
            return False
        return len(self.get_reference_images()) > 0
    
    def should_use_reference_person(self, post_count: int) -> bool:
        """Determine if this post should feature the reference person."""
        if not self.is_available():
            return False
        return post_count % self.frequency == 0
    
    def get_reference_images(self) -> List[Path]:
        """Get all reference person images."""
        if not self.reference_dir.exists():
            return []
        
        supported = ['.jpg', '.jpeg', '.png', '.webp']
        images = [f for f in self.reference_dir.iterdir() 
                  if f.suffix.lower() in supported and f.is_file()]
        return sorted(images)
    
    def _upload_image(self, image_path: Path) -> Optional[str]:
        """Upload image to temporary hosting for fal.ai to access."""
        try:
            with open(image_path, 'rb') as f:
                files = {
                    'reqtype': (None, 'fileupload'),
                    'time': (None, '1h'),
                    'fileToUpload': (image_path.name, f)
                }
                response = requests.post(
                    'https://litterbox.catbox.moe/resources/internals/api.php',
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200 and response.text.startswith('http'):
                    return response.text.strip()
                else:
                    logger.error(f"Image upload failed: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return None
    
    def generate_reference_video(
        self,
        background_image: Path = None,
        prompt: str = None,
        output_name: str = None
    ) -> Optional[Path]:
        """
        Generate a video featuring the reference person.
        
        Args:
            background_image: Optional background/environment image (not used in reference-to-video)
            prompt: Motion/action prompt for the person
            output_name: Optional output filename
            
        Returns:
            Path to the generated video, or None if failed
        """
        if not self.is_available():
            logger.error("Reference person video generation not available")
            return None
        
        logger.info("Generating reference person video...")
        
        reference_images = self.get_reference_images()
        if not reference_images:
            logger.error("No reference images found")
            return None
        
        reference_urls = []
        for img in reference_images[:7]:
            url = self._upload_image(img)
            if url:
                reference_urls.append(url)
                logger.info(f"Uploaded reference: {img.name}")
        
        if not reference_urls:
            logger.error("Failed to upload reference images")
            return None
        
        if prompt is None:
            prompt = self.ref_config.get(
                'default_prompt',
                "Person walking slowly and contemplatively, serene expression, cinematic lighting, atmospheric, slow motion"
            )
        
        try:
            logger.info(f"Submitting to {self.model} with {len(reference_urls)} reference images")
            logger.info(f"Prompt: {prompt}")
            
            def on_queue_update(update):
                if isinstance(update, fal_client.Queued):
                    logger.info(f"Queued. Position: {update.position}")
                elif isinstance(update, fal_client.InProgress):
                    logger.info("In progress...")
                    if hasattr(update, 'logs') and update.logs:
                        for log in update.logs[-3:]:
                            if isinstance(log, dict):
                                logger.info(f"API: {log.get('message', '')}")
                            else:
                                logger.info(f"API: {log}")
            
            movement = self.ref_config.get('movement_amplitude', 'medium')
            
            result = fal_client.subscribe(
                self.model,
                arguments={
                    "prompt": prompt,
                    "reference_image_urls": reference_urls,
                    "movement_amplitude": movement
                },
                with_logs=True,
                on_queue_update=on_queue_update
            )
            
            logger.info(f"Result received: {type(result)}")
            
            if result and 'video' in result:
                video_url = result['video'].get('url')
                if video_url:
                    logger.info(f"Video URL: {video_url}")
                    return self._download_video(video_url, output_name)
            
            logger.error(f"No video in result: {result}")
            return None
            
        except Exception as e:
            logger.error(f"Reference person video generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _download_video(self, video_url: str, output_name: str = None) -> Optional[Path]:
        """Download the generated video."""
        try:
            if output_name is None:
                output_name = get_timestamp_filename("reference_person", "mp4")
            
            output_path = self.output_dir / output_name
            
            response = requests.get(video_url, timeout=120)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Reference person video saved: {output_path}")
                return output_path
            else:
                logger.error(f"Video download failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Video download error: {e}")
            return None


def get_reference_post_count() -> int:
    """Get the current reference person post count."""
    try:
        import json
        project_root = Path(__file__).parent.parent
        log_file = project_root / "logs" / "reference_post_count.json"
        
        if log_file.exists():
            with open(log_file) as f:
                data = json.load(f)
                return data.get('count', 0)
        return 0
    except:
        return 0


def increment_reference_post_count() -> int:
    """Increment and return the reference person post count."""
    try:
        import json
        project_root = Path(__file__).parent.parent
        log_file = project_root / "logs" / "reference_post_count.json"
        
        count = get_reference_post_count() + 1
        
        with open(log_file, 'w') as f:
            json.dump({'count': count}, f)
        
        return count
    except:
        return 1
