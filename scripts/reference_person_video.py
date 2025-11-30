"""
Reference Person Video Generator for StoicAlgo
Uses fal.ai Vidu Reference-to-Video API to generate videos with a specific person.
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, List
from scripts.logger import get_logger
from scripts.utils import load_settings, get_timestamp_filename

logger = get_logger("ReferencePersonVideo")


class ReferencePersonVideoGenerator:
    """Generates videos featuring a reference person using Vidu API."""
    
    def __init__(self):
        self.settings = load_settings()
        self.api_key = os.environ.get('FAL_API_KEY')
        self.base_url = "https://queue.fal.run"
        self.model = "fal-ai/vidu/reference-to-video"
        
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
                    return response.text
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
            background_image: Optional background/environment image
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
        
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "reference_image_urls": reference_urls,
            "aspect_ratio": "9:16",
            "resolution": "720p",
            "duration": self.ref_config.get('duration', 4)
        }
        
        if background_image and background_image.exists():
            bg_url = self._upload_image(background_image)
            if bg_url:
                payload["first_frame_image"] = bg_url
                logger.info(f"Using background: {background_image.name}")
        
        try:
            submit_response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if submit_response.status_code not in [200, 202]:
                logger.error(f"Failed to submit request: {submit_response.text}")
                return None
            
            result = submit_response.json()
            request_id = result.get('request_id')
            status_url = result.get('status_url')
            response_url = result.get('response_url')
            
            if not request_id:
                logger.error(f"No request_id in response: {result}")
                return None
            
            logger.info(f"Request submitted, ID: {request_id}")
            
            if not status_url:
                status_url = f"{self.base_url}/{self.model}/requests/{request_id}/status"
            if not response_url:
                response_url = f"{self.base_url}/{self.model}/requests/{request_id}"
            
            max_wait = 600
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(status_url, headers=headers, timeout=30)
                
                if status_response.status_code in [200, 202]:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    logger.info(f"Generation status: {status}")
                    
                    if status == 'COMPLETED':
                        if 'response' in status_data:
                            video_url = status_data.get('response', {}).get('video', {}).get('url')
                            if video_url:
                                return self._download_video(video_url, output_name)
                        
                        result_response = requests.get(response_url, headers=headers, timeout=30)
                        
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            video_url = result_data.get('video', {}).get('url')
                            
                            if video_url:
                                return self._download_video(video_url, output_name)
                        
                        logger.error(f"Failed to get result: {result_response.text}")
                        return None
                    
                    elif status == 'FAILED':
                        error_msg = status_data.get('error', 'Unknown error')
                        logger.error(f"Generation failed: {error_msg}")
                        return None
                    
                    elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                        time.sleep(10)
                    else:
                        time.sleep(5)
                else:
                    logger.warning(f"Status check failed: {status_response.status_code}")
                    time.sleep(10)
            
            logger.error("Generation timed out")
            return None
            
        except Exception as e:
            logger.error(f"Reference person video generation failed: {e}")
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
