#!/usr/bin/env python3
"""
Daily AI Image Generator for StoicAlgo
Generates 2 images per category, designed to run twice daily via cron.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from scripts.batch_image_generator import BatchImageGenerator
from scripts.logger import get_logger
from datetime import datetime

logger = get_logger("DailyImageGenerator")


def run_daily_generation(images_per_category: int = 2):
    """
    Generate a small batch of images for each category.
    Designed to be run twice daily via cron.
    
    Args:
        images_per_category: Number of images to generate per category (default: 2)
    """
    
    logger.info(f"Starting daily image generation: {images_per_category} per category")
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily Image Generation")
    print("=" * 50)
    
    generator = BatchImageGenerator()
    
    categories = ["statues", "warriors", "nature", "temples", "cosmic", "geometry"]
    total_generated = 0
    total_failed = 0
    
    for category in categories:
        try:
            paths = generator.generate_category_batch(
                category, 
                count=images_per_category, 
                delay=2.0
            )
            total_generated += len(paths)
            total_failed += images_per_category - len(paths)
            print(f"  ✓ {category}: {len(paths)}/{images_per_category} images")
        except Exception as e:
            logger.error(f"Failed to generate {category}: {e}")
            print(f"  ✗ {category}: Error - {e}")
            total_failed += images_per_category
    
    print("=" * 50)
    print(f"Complete: {total_generated} generated, {total_failed} failed")
    logger.info(f"Daily generation complete: {total_generated} generated, {total_failed} failed")
    
    return total_generated, total_failed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily AI Image Generator')
    parser.add_argument('--count', type=int, default=2, help='Images per category (default: 2)')
    
    args = parser.parse_args()
    run_daily_generation(args.count)
