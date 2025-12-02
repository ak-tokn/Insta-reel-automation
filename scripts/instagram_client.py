"""
Instagram Client for StoicAlgo
Handles posting Reels to Instagram via the Graph API.
"""

import os
import time
import requests
from pathlib import Path
from typing import Dict, Optional
from scripts.logger import get_logger
from scripts.utils import load_settings, get_env_var

logger = get_logger("InstagramClient")


class InstagramClient:
    """Client for Instagram Graph API interactions."""
    
    # API endpoints
    BASE_URL = "https://graph.facebook.com/v19.0"
    
    def __init__(self):
        self.settings = load_settings()
        self.ig_config = self.settings['instagram']
        
        # Load credentials from environment
        self.access_token = get_env_var('INSTAGRAM_ACCESS_TOKEN')
        self.user_id = get_env_var('INSTAGRAM_USER_ID')
        
        # Optional
        self.app_id = os.environ.get('INSTAGRAM_APP_ID')
    
    def _ensure_valid_token(self):
        """Check and refresh token if needed before making API calls."""
        try:
            from scripts.token_manager import TokenManager
            manager = TokenManager()
            if manager.ensure_valid_token():
                # Reload the token in case it was refreshed
                from dotenv import load_dotenv
                load_dotenv(override=True)
                self.access_token = get_env_var('INSTAGRAM_ACCESS_TOKEN')
                return True
            return False
        except Exception as e:
            logger.warning(f"Token check failed: {e}")
            return True  # Continue anyway, might still work
    
    def post_reel(
        self,
        video_path: Path,
        caption: str,
        thumbnail_path: Path = None,
        audio_asset_id: str = None
    ) -> Dict:
        """
        Post a Reel to Instagram.
        
        This is a two-step process:
        1. Create media container
        2. Publish the container
        
        Args:
            video_path: Path to the video file
            caption: Caption for the post
            thumbnail_path: Optional custom thumbnail
            audio_asset_id: Optional Instagram audio asset ID
            
        Returns:
            Dictionary with post result info
        """
        
        logger.info(f"Posting Reel to Instagram: {video_path.name}")
        
        # Ensure we have a valid token before posting
        self._ensure_valid_token()
        
        # Step 1: Upload video to a publicly accessible URL
        video_url = self._get_video_url(video_path)
        
        if not video_url:
            raise ValueError("Could not get video URL for upload")
        
        # Step 1b: Upload thumbnail if provided
        thumbnail_url = None
        if thumbnail_path and thumbnail_path.exists():
            logger.info(f"Uploading thumbnail: {thumbnail_path.name}")
            thumbnail_url = self._upload_image_to_hosting(thumbnail_path)
            if thumbnail_url:
                logger.info(f"Thumbnail uploaded: {thumbnail_url}")
        
        # Step 2: Create media container
        container_id = self._create_media_container(
            video_url=video_url,
            caption=caption,
            thumbnail_url=thumbnail_url,
            audio_asset_id=audio_asset_id
        )
        
        if not container_id:
            raise RuntimeError("Failed to create media container")
        
        # Step 3: Wait for media to be ready
        self._wait_for_media_ready(container_id)
        
        # Step 4: Publish
        post_id = self._publish_media(container_id)
        
        logger.info(f"Reel published successfully! Post ID: {post_id}")
        
        return {
            'success': True,
            'post_id': post_id,
            'container_id': container_id,
            'video_path': str(video_path)
        }
    
    def _get_video_url(self, video_path: Path) -> str:
        """
        Get a publicly accessible URL for the video.
        
        NOTE: Instagram requires the video to be at a publicly accessible URL.
        Options:
        1. Upload to a CDN/cloud storage
        2. Use a temporary file hosting service
        3. Host via Replit's static files
        
        For production, implement proper cloud storage.
        """
        
        # Option 1: Check for existing public URL
        public_url = os.environ.get('VIDEO_PUBLIC_URL')
        if public_url:
            return public_url
        
        # Option 2: For Replit, you can use the public URL if configured
        replit_url = os.environ.get('REPLIT_URL')
        if replit_url:
            # Assuming video is in output/videos and served statically
            return f"{replit_url}/output/videos/{video_path.name}"
        
        # Option 3: Upload to temporary file hosting (0x0.st)
        logger.info("Uploading video to temporary hosting...")
        try:
            upload_url = self._upload_to_temp_hosting(video_path)
            if upload_url:
                logger.info(f"Video uploaded: {upload_url}")
                return upload_url
        except Exception as e:
            logger.error(f"Failed to upload to temp hosting: {e}")
        
        logger.warning(
            "No public video URL available. "
            "Instagram requires videos to be publicly accessible. "
            "Configure VIDEO_PUBLIC_URL or REPLIT_URL environment variable."
        )
        
        return None
    
    def _upload_to_temp_hosting(self, video_path: Path) -> Optional[str]:
        """Upload video to file hosting service."""
        
        # Use catbox.moe permanent hosting (Instagram accepts this)
        try:
            logger.info("Uploading to catbox.moe...")
            with open(video_path, 'rb') as f:
                response = requests.post(
                    'https://catbox.moe/user/api.php',
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': (video_path.name, f, 'video/mp4')},
                    timeout=180
                )
                if response.status_code == 200 and response.text.startswith('http'):
                    url = response.text.strip()
                    logger.info(f"Upload successful: {url}")
                    return url
                else:
                    logger.warning(f"Catbox response: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            logger.warning(f"Catbox upload failed: {e}")
        
        # Fallback to 0x0.st 
        try:
            logger.info("Trying 0x0.st...")
            with open(video_path, 'rb') as f:
                response = requests.post(
                    'https://0x0.st',
                    files={'file': (video_path.name, f, 'video/mp4')},
                    timeout=180
                )
                if response.status_code == 200:
                    return response.text.strip()
                else:
                    logger.warning(f"0x0.st response: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            logger.warning(f"0x0.st upload failed: {e}")
        
        return None
    
    def _upload_image_to_hosting(self, image_path: Path) -> Optional[str]:
        """Upload image to file hosting service for cover image."""
        
        # Use catbox.moe permanent hosting
        try:
            with open(image_path, 'rb') as f:
                response = requests.post(
                    'https://catbox.moe/user/api.php',
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': (image_path.name, f, 'image/jpeg')},
                    timeout=60
                )
                if response.status_code == 200 and response.text.startswith('http'):
                    return response.text.strip()
        except Exception as e:
            logger.warning(f"Image upload failed: {e}")
        
        return None
    
    def _create_media_container(
        self,
        video_url: str,
        caption: str,
        thumbnail_url: str = None,
        audio_asset_id: str = None
    ) -> Optional[str]:
        """Create an Instagram media container for the video."""
        
        endpoint = f"{self.BASE_URL}/{self.user_id}/media"
        
        params = {
            'access_token': self.access_token,
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'share_to_feed': str(self.ig_config.get('share_to_feed', True)).lower()
        }
        
        # Add cover/thumbnail image URL
        if thumbnail_url:
            params['cover_url'] = thumbnail_url
            logger.info(f"Using cover image: {thumbnail_url}")
        
        # Add audio asset ID if using Instagram's royalty-free audio
        if audio_asset_id:
            params['audio_asset_id'] = audio_asset_id
        
        logger.debug(f"Creating media container: {endpoint}")
        
        try:
            response = requests.post(endpoint, params=params)
            data = response.json()
            
            if 'id' in data:
                container_id = data['id']
                logger.info(f"Media container created: {container_id}")
                return container_id
            else:
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                logger.error(f"Container creation failed: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Container creation error: {str(e)}")
            return None
    
    def _wait_for_media_ready(self, container_id: str, max_attempts: int = 30):
        """Wait for the media container to be ready for publishing."""
        
        endpoint = f"{self.BASE_URL}/{container_id}"
        
        params = {
            'access_token': self.access_token,
            'fields': 'status_code,status'
        }
        
        logger.info("Waiting for media to be processed...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(endpoint, params=params)
                data = response.json()
                
                # Check for API error response
                if 'error' in data:
                    error = data['error']
                    error_msg = error.get('message', 'Unknown API error')
                    error_code = error.get('code', 'N/A')
                    logger.error(f"API Error (code {error_code}): {error_msg}")
                    raise RuntimeError(f"API Error: {error_msg}")
                
                status = data.get('status_code')
                status_detail = data.get('status', '')
                
                logger.info(f"Status check {attempt + 1}/{max_attempts}: {status} - {status_detail}")
                
                if status == 'FINISHED':
                    logger.info("Media processing complete")
                    return True
                elif status == 'ERROR':
                    error = status_detail or 'Unknown error'
                    raise RuntimeError(f"Media processing failed: {error}")
                elif status == 'IN_PROGRESS':
                    time.sleep(10)  # Wait 10 seconds between checks
                elif status == 'EXPIRED':
                    raise RuntimeError("Media container expired - please retry")
                else:
                    logger.debug(f"Unknown status: {status}, waiting...")
                    time.sleep(5)
                    
            except RuntimeError:
                raise
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                logger.warning(f"Status check error: {e}")
                time.sleep(5)
        
        raise TimeoutError("Media processing timed out")
    
    def _publish_media(self, container_id: str) -> str:
        """Publish the media container to Instagram."""
        
        endpoint = f"{self.BASE_URL}/{self.user_id}/media_publish"
        
        params = {
            'access_token': self.access_token,
            'creation_id': container_id
        }
        
        logger.debug(f"Publishing media: {endpoint}")
        
        try:
            response = requests.post(endpoint, params=params)
            data = response.json()
            
            if 'id' in data:
                return data['id']
            else:
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                raise RuntimeError(f"Publishing failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Publishing error: {str(e)}")
            raise
    
    def get_insights(self, media_id: str) -> Dict:
        """Get insights for a published post."""
        
        endpoint = f"{self.BASE_URL}/{media_id}/insights"
        
        params = {
            'access_token': self.access_token,
            'metric': 'plays,reach,saved,comments,likes,shares'
        }
        
        try:
            response = requests.get(endpoint, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Insights error: {str(e)}")
            return {}
    
    def verify_credentials(self) -> bool:
        """Verify that credentials are valid."""
        
        endpoint = f"{self.BASE_URL}/{self.user_id}"
        
        params = {
            'access_token': self.access_token,
            'fields': 'id,username'
        }
        
        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if 'username' in data:
                logger.info(f"Credentials verified for @{data['username']}")
                return True
            else:
                error = data.get('error', {}).get('message', 'Unknown')
                logger.error(f"Credential verification failed: {error}")
                return False
                
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False


def post_reel(video_path: Path, caption: str, audio_asset_id: str = None) -> Dict:
    """Convenience function to post a Reel."""
    client = InstagramClient()
    return client.post_reel(video_path, caption, audio_asset_id=audio_asset_id)


if __name__ == "__main__":
    # Test the Instagram client
    import os
    
    print("=== Instagram Client Test ===")
    
    # Check for credentials
    required_vars = ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_USER_ID']
    missing = [v for v in required_vars if not os.environ.get(v)]
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("\nSet these in Replit Secrets or your environment:")
        print("  INSTAGRAM_ACCESS_TOKEN - Your Instagram Graph API token")
        print("  INSTAGRAM_USER_ID - Your Instagram Business/Creator account ID")
        print("\nTo get these:")
        print("  1. Create a Meta Developer App")
        print("  2. Add Instagram Graph API")
        print("  3. Generate access token with publish permissions")
    else:
        print("✓ Credentials found")
        
        # Verify credentials
        client = InstagramClient()
        
        user_input = input("\nVerify credentials? (y/n): ")
        if user_input.lower() == 'y':
            if client.verify_credentials():
                print("✓ Credentials are valid")
            else:
                print("✗ Credential verification failed")
        
        print("\nTo post a Reel:")
        print("  from scripts.instagram_client import post_reel")
        print("  from pathlib import Path")
        print("  result = post_reel(")
        print("      Path('output/videos/reel.mp4'),")
        print("      'Your caption here #stoicism #wisdom'")
        print("  )")
