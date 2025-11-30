"""
Orchestrator for StoicAlgo
Main pipeline that coordinates all services to generate and post content.
"""

import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from scripts.logger import get_logger, StoicLogger
from scripts.utils import load_settings, ensure_dir, Timer, generate_id
from scripts.quote_service import QuoteService
from scripts.caption_service import CaptionService
from scripts.image_selector import ImageSelector
from scripts.audio_selector import AudioSelector
from scripts.video_builder import VideoBuilder
from scripts.instagram_client import InstagramClient

logger = get_logger("Orchestrator")


class Orchestrator:
    """Main orchestrator for the StoicAlgo pipeline."""
    
    def __init__(self):
        self.settings = load_settings()
        self.run_id = generate_id("run")
        
        # Initialize services
        self.quote_service = QuoteService()
        self.caption_service = CaptionService()
        self.image_selector = ImageSelector()
        self.audio_selector = AudioSelector()
        self.video_builder = VideoBuilder()
        self.instagram_client = InstagramClient()
        
        # Run tracking
        self.run_data = {
            'run_id': self.run_id,
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'status': 'pending'
        }
    
    def run(self, post_to_instagram: bool = True, custom_theme: str = None) -> Dict:
        """
        Execute the complete content generation pipeline.
        
        Args:
            post_to_instagram: Whether to actually post (False for testing)
            custom_theme: Optional theme to focus the content on
            
        Returns:
            Dictionary with run results
        """
        
        logger.info(f"Starting pipeline run: {self.run_id}")
        
        try:
            # Step 1: Generate Content
            with Timer("Content Generation") as t:
                content = self._generate_content(custom_theme)
            self._log_step("content_generation", "success", {
                "quote": content.get('quote', '')[:50],
                "author": content.get('author', ''),
                "duration": t.elapsed
            })
            
            # Step 2: Build Caption
            with Timer("Caption Building") as t:
                caption = self._build_caption(content)
            self._log_step("caption_building", "success", {
                "length": len(caption),
                "duration": t.elapsed
            })
            
            # Step 3: Select Image
            with Timer("Image Selection") as t:
                image_path, image_source = self._select_image(content)
            self._log_step("image_selection", "success", {
                "image": image_path.name,
                "source": image_source,
                "duration": t.elapsed
            })
            
            # Store original image path for marking as used later
            original_image_path = image_path
            
            # Step 4: Prepare Image
            with Timer("Image Preparation") as t:
                prepared_image = self._prepare_image(image_path)
            self._log_step("image_preparation", "success", {
                "prepared_path": str(prepared_image),
                "duration": t.elapsed
            })
            
            # Step 5: Select Audio
            with Timer("Audio Selection") as t:
                audio_info = self._select_audio(content)
            self._log_step("audio_selection", "success", {
                "type": audio_info.get('type'),
                "duration": t.elapsed
            })
            
            # Step 6: Build Video
            with Timer("Video Building") as t:
                video_path, thumbnail_path = self._build_video(
                    prepared_image,
                    content,
                    audio_info
                )
            self._log_step("video_building", "success", {
                "video": video_path.name,
                "thumbnail": thumbnail_path.name,
                "duration": t.elapsed
            })
            
            # Step 7: Post to Instagram
            post_result = None
            if post_to_instagram:
                with Timer("Instagram Posting") as t:
                    post_result = self._post_to_instagram(
                        video_path,
                        caption,
                        audio_info,
                        thumbnail_path
                    )
                self._log_step("instagram_posting", "success", {
                    "post_id": post_result.get('post_id') if post_result else None,
                    "duration": t.elapsed
                })
            else:
                self._log_step("instagram_posting", "skipped", {
                    "reason": "post_to_instagram=False"
                })
            
            # Complete
            self.run_data['status'] = 'completed'
            self.run_data['end_time'] = datetime.now().isoformat()
            self.run_data['output'] = {
                'video_path': str(video_path),
                'thumbnail_path': str(thumbnail_path),
                'caption': caption[:200] + '...' if len(caption) > 200 else caption,
                'post_result': post_result
            }
            
            # Mark the original image as used (move to 'used' folder)
            self.image_selector.mark_as_used(original_image_path)
            
            logger.info(f"Pipeline completed successfully: {self.run_id}")
            
            # Log the complete run
            run_logger = StoicLogger()
            run_logger.log_run(self.run_data)
            
            return self.run_data
            
        except Exception as e:
            # Handle failure
            self.run_data['status'] = 'failed'
            self.run_data['error'] = str(e)
            self.run_data['traceback'] = traceback.format_exc()
            self.run_data['end_time'] = datetime.now().isoformat()
            
            logger.error(f"Pipeline failed: {str(e)}")
            
            # Log the failed run
            run_logger = StoicLogger()
            run_logger.log_run(self.run_data)
            
            raise
    
    def _generate_content(self, custom_theme: str = None) -> Dict:
        """Generate quote content using LLM."""
        logger.info("Generating content...")
        return self.quote_service.generate_content(custom_theme)
    
    def _build_caption(self, content: Dict) -> str:
        """Build Instagram caption from content."""
        logger.info("Building caption...")
        return self.caption_service.build_caption(content)
    
    def _select_image(self, content: Dict) -> tuple:
        """Select image based on content mood."""
        logger.info("Selecting image...")
        mood = content.get('mood', 'contemplative')
        return self.image_selector.select_image(mood=mood)
    
    def _prepare_image(self, image_path: Path) -> Path:
        """Prepare image for video (resize/crop)."""
        logger.info("Preparing image...")
        
        # Create prepared image in output directory
        output_dir = Path(self.settings['paths']['output']) / "prepared"
        ensure_dir(output_dir)
        
        prepared_path = output_dir / f"prepared_{image_path.name}"
        return self.image_selector.prepare_image(image_path, prepared_path)
    
    def _select_audio(self, content: Dict) -> Dict:
        """Select audio based on content mood."""
        logger.info("Selecting audio...")
        mood = content.get('mood', 'dark')
        return self.audio_selector.select_audio(mood=mood)
    
    def _build_video(self, image_path: Path, content: Dict, audio_info: Dict) -> tuple:
        """Build the video with text overlay and audio."""
        logger.info("Building video...")
        
        return self.video_builder.build_video(
            image_path,
            content,
            audio_info
        )
    
    def _post_to_instagram(self, video_path: Path, caption: str, audio_info: Dict, thumbnail_path: Path = None) -> Dict:
        """Post the video to Instagram."""
        logger.info("Posting to Instagram...")
        
        # Get Instagram audio asset ID if using IG audio
        audio_asset_id = None
        if audio_info.get('type') == 'instagram':
            audio_asset_id = audio_info.get('asset_id')
        
        return self.instagram_client.post_reel(
            video_path,
            caption,
            thumbnail_path=thumbnail_path,
            audio_asset_id=audio_asset_id
        )
    
    def _log_step(self, step_name: str, status: str, details: Dict = None):
        """Log a pipeline step."""
        step_data = {
            'step': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.run_data['steps'].append(step_data)
        logger.log_step(step_name, status, details)


def run_pipeline(post_to_instagram: bool = True, custom_theme: str = None) -> Dict:
    """
    Convenience function to run the complete pipeline.
    
    Args:
        post_to_instagram: Whether to post to Instagram
        custom_theme: Optional theme focus
        
    Returns:
        Run result dictionary
    """
    orchestrator = Orchestrator()
    return orchestrator.run(post_to_instagram, custom_theme)


def run_test():
    """Run the pipeline in test mode (no Instagram posting)."""
    return run_pipeline(post_to_instagram=False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='StoicAlgo Content Pipeline')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (no Instagram posting)'
    )
    parser.add_argument(
        '--theme',
        type=str,
        default=None,
        help='Custom theme to focus content on'
    )
    parser.add_argument(
        '--post',
        action='store_true',
        help='Actually post to Instagram'
    )
    
    args = parser.parse_args()
    
    # Determine posting mode
    post_to_ig = args.post and not args.test
    
    print("=" * 50)
    print("StoicAlgo Content Pipeline")
    print("=" * 50)
    print(f"Mode: {'TEST (no posting)' if not post_to_ig else 'PRODUCTION (will post)'}")
    if args.theme:
        print(f"Theme: {args.theme}")
    print("=" * 50)
    
    try:
        result = run_pipeline(
            post_to_instagram=post_to_ig,
            custom_theme=args.theme
        )
        
        print("\n" + "=" * 50)
        print("PIPELINE COMPLETED")
        print("=" * 50)
        print(f"Run ID: {result['run_id']}")
        print(f"Status: {result['status']}")
        
        if result.get('output'):
            print(f"\nOutput:")
            print(f"  Video: {result['output'].get('video_path')}")
            print(f"  Thumbnail: {result['output'].get('thumbnail_path')}")
            
            if result['output'].get('post_result'):
                print(f"  Post ID: {result['output']['post_result'].get('post_id')}")
        
        print("\nSteps completed:")
        for step in result.get('steps', []):
            status_icon = "✓" if step['status'] == 'success' else "○"
            print(f"  {status_icon} {step['step']}")
        
    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        sys.exit(1)
