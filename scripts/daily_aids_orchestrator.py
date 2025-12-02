"""
Daily Ai'ds Orchestrator for StoicAlgo
Coordinates the generation, slide building, and posting of Daily Ai'ds carousels.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from scripts.logger import get_logger
from scripts.utils import load_settings
from scripts.daily_aid_service import DailyAidService
from scripts.daily_aid_slide_builder import DailyAidSlideBuilder
from scripts.instagram_client import InstagramClient

logger = get_logger("DailyAidsOrchestrator")


class DailyAidsOrchestrator:
    """Orchestrates the Daily Ai'ds carousel pipeline."""
    
    COUNTER_FILE = Path('logs/daily_aids_count.json')
    
    def __init__(self):
        self.settings = load_settings()
        self.config = self.settings.get('daily_aids', {})
        
        self.idea_service = DailyAidService()
        self.slide_builder = DailyAidSlideBuilder()
        self.instagram_client = InstagramClient()
        
        self.COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def get_current_count(self) -> int:
        """Get the current Daily Ai'ds count."""
        if self.COUNTER_FILE.exists():
            try:
                with open(self.COUNTER_FILE) as f:
                    data = json.load(f)
                    return data.get('count', 0)
            except Exception as e:
                logger.warning(f"Error reading counter file: {e}")
        return 0
    
    def _increment_count(self) -> int:
        """Increment and save the count. Returns the new count."""
        current = self.get_current_count()
        new_count = current + 1
        
        try:
            with open(self.COUNTER_FILE, 'w') as f:
                json.dump({'count': new_count}, f)
            logger.info(f"Daily Ai'ds count incremented to {new_count}")
        except Exception as e:
            logger.error(f"Error saving counter: {e}")
        
        return new_count
    
    def _build_caption(self, idea: Dict) -> str:
        """Build the Instagram caption for the carousel post."""
        
        caption_config = self.config.get('caption', {})
        max_length = caption_config.get('max_length', 2200)
        hashtags = caption_config.get('hashtags', [])
        
        idea_number = idea.get('idea_number', 1)
        title = idea.get('title', '')
        hook = idea.get('hook', '')
        summary = idea.get('summary', '')
        kickoff_prompt = idea.get('kickoff_prompt', '')
        
        caption_parts = []
        
        caption_parts.append(f"DAILY AI'DS #{idea_number}: {title}")
        caption_parts.append("")
        
        if hook:
            caption_parts.append(f"{hook}")
            caption_parts.append("")
        
        if summary:
            caption_parts.append(summary)
            caption_parts.append("")
        
        caption_parts.append("---")
        caption_parts.append("")
        caption_parts.append("YOUR KICKOFF PROMPT:")
        caption_parts.append("")
        caption_parts.append(f'"{kickoff_prompt}"')
        caption_parts.append("")
        
        caption_parts.append("---")
        caption_parts.append("")
        caption_parts.append("Copy the prompt above into ChatGPT or Claude to get started.")
        caption_parts.append("")
        
        if hashtags:
            caption_parts.append(" ".join(hashtags[:10]))
        
        caption = "\n".join(caption_parts)
        
        if len(caption) > max_length:
            logger.warning(f"Caption exceeds {max_length} chars ({len(caption)}), may need external hosting")
            
            truncate_at = max_length - 100
            truncated_prompt = kickoff_prompt[:truncate_at - len(kickoff_prompt)] + "... (See link in bio for full prompt)"
            
            caption_parts_truncated = []
            caption_parts_truncated.append(f"DAILY AI'DS #{idea_number}: {title}")
            caption_parts_truncated.append("")
            if hook:
                caption_parts_truncated.append(f"{hook}")
                caption_parts_truncated.append("")
            caption_parts_truncated.append("---")
            caption_parts_truncated.append("")
            caption_parts_truncated.append("YOUR KICKOFF PROMPT:")
            caption_parts_truncated.append("")
            caption_parts_truncated.append(f'"{truncated_prompt}"')
            caption_parts_truncated.append("")
            caption_parts_truncated.append("Full prompt in link in bio!")
            caption_parts_truncated.append("")
            if hashtags:
                caption_parts_truncated.append(" ".join(hashtags[:10]))
            
            caption = "\n".join(caption_parts_truncated)
        
        return caption
    
    def run_pipeline(self, dry_run: bool = False) -> Dict:
        """
        Run the complete Daily Ai'ds pipeline.
        
        Args:
            dry_run: If True, generates content and slides but doesn't post
            
        Returns:
            Dictionary with pipeline results
        """
        
        logger.info("=" * 50)
        logger.info("Starting Daily Ai'ds Pipeline")
        logger.info("=" * 50)
        
        next_number = self.get_current_count() + 1
        logger.info(f"Generating Daily Ai'ds #{next_number}")
        
        try:
            idea = self.idea_service.generate_idea(next_number)
            logger.info(f"Generated idea: {idea.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to generate idea: {e}")
            return {'success': False, 'error': f"Idea generation failed: {e}"}
        
        if dry_run:
            try:
                slides = self.slide_builder.build_all_slides(idea, is_preview=True)
                logger.info(f"Built {len(slides)} preview slides")
            except Exception as e:
                logger.error(f"Failed to build slides: {e}")
                return {'success': False, 'error': f"Slide building failed: {e}"}
            
            caption = self._build_caption(idea)
            logger.info(f"Caption length: {len(caption)} chars")
            
            logger.info("DRY RUN - Skipping Instagram post")
            logger.info("Preview slides saved to: output/daily_aids/preview/")
            return {
                'success': True,
                'dry_run': True,
                'idea_number': next_number,
                'idea': idea,
                'slides': [str(s) for s in slides],
                'caption': caption,
                'preview_folder': 'output/daily_aids/preview/'
            }
        
        try:
            slides = self.slide_builder.build_all_slides(idea, is_preview=False)
            logger.info(f"Built {len(slides)} slides")
        except Exception as e:
            logger.error(f"Failed to build slides: {e}")
            return {'success': False, 'error': f"Slide building failed: {e}"}
        
        caption = self._build_caption(idea)
        logger.info(f"Caption length: {len(caption)} chars")
        
        try:
            result = self.instagram_client.post_carousel(slides, caption)
            logger.info(f"Posted carousel! Post ID: {result.get('post_id')}")
        except Exception as e:
            logger.error(f"Failed to post carousel: {e}")
            return {'success': False, 'error': f"Instagram posting failed: {e}"}
        
        self._increment_count()
        
        logger.info("=" * 50)
        logger.info(f"Daily Ai'ds #{next_number} completed successfully!")
        logger.info(f"Slides saved to: output/daily_aids/post_{next_number}/")
        logger.info("=" * 50)
        
        return {
            'success': True,
            'idea_number': next_number,
            'idea': idea,
            'slides': [str(s) for s in slides],
            'caption': caption,
            'post_id': result.get('post_id'),
            'instagram_result': result,
            'slides_folder': f'output/daily_aids/post_{next_number}/'
        }


def run_daily_aids(dry_run: bool = False) -> Dict:
    """Convenience function to run the Daily Ai'ds pipeline."""
    orchestrator = DailyAidsOrchestrator()
    return orchestrator.run_pipeline(dry_run=dry_run)


if __name__ == "__main__":
    import sys
    
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    if dry_run:
        print("Running Daily Ai'ds pipeline in DRY RUN mode...")
    else:
        print("Running Daily Ai'ds pipeline...")
    
    result = run_daily_aids(dry_run=dry_run)
    
    if result.get('success'):
        print(f"\nSuccess! Daily Ai'ds #{result.get('idea_number')}")
        print(f"Title: {result.get('idea', {}).get('title', 'Unknown')}")
        print(f"Slides: {len(result.get('slides', []))}")
        if not dry_run:
            print(f"Post ID: {result.get('post_id')}")
    else:
        print(f"\nFailed: {result.get('error')}")
