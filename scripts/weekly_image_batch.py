"""
Weekly Batch Image Generator for StoicAlgo
Generates 10 new images per category and saves them to their respective folders.
Runs once per week automatically via scheduler.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from scripts.batch_image_generator import BatchImageGenerator, CATEGORY_ESSENCES
from scripts.logger import get_logger

logger = get_logger("WeeklyImageBatch")

BATCH_LOG_FILE = project_root / "logs" / "weekly_batch_log.json"
IMAGES_PER_CATEGORY = 10
DELAY_BETWEEN_IMAGES = 3.0


def load_batch_log() -> dict:
    """Load the batch generation log."""
    if BATCH_LOG_FILE.exists():
        with open(BATCH_LOG_FILE, 'r') as f:
            return json.load(f)
    return {"last_run": None, "runs": []}


def save_batch_log(log: dict):
    """Save the batch generation log."""
    BATCH_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BATCH_LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


def is_batch_due() -> bool:
    """Check if a week has passed since the last batch run."""
    log = load_batch_log()
    
    if not log.get("last_run"):
        return True
    
    last_run = datetime.fromisoformat(log["last_run"])
    days_since = (datetime.now() - last_run).days
    
    logger.info(f"Days since last batch: {days_since}")
    return days_since >= 7


def run_weekly_batch(force: bool = False) -> dict:
    """
    Run the weekly batch image generation.
    
    Args:
        force: If True, run even if a week hasn't passed
        
    Returns:
        Result dictionary with success status and details
    """
    logger.info("=" * 60)
    logger.info("WEEKLY IMAGE BATCH GENERATOR")
    logger.info("=" * 60)
    
    if not force and not is_batch_due():
        log = load_batch_log()
        last_run = log.get("last_run", "never")
        logger.info(f"Batch not due yet. Last run: {last_run}")
        return {
            "success": True,
            "skipped": True,
            "message": f"Not due yet. Last run: {last_run}"
        }
    
    categories = list(CATEGORY_ESSENCES.keys())
    total_images = len(categories) * IMAGES_PER_CATEGORY
    
    logger.info(f"Categories: {', '.join(categories)}")
    logger.info(f"Images per category: {IMAGES_PER_CATEGORY}")
    logger.info(f"Total images to generate: {total_images}")
    logger.info(f"Estimated time: ~{total_images * (DELAY_BETWEEN_IMAGES + 15) / 60:.1f} minutes")
    
    generator = BatchImageGenerator(save_to_category_folders=True)
    
    start_time = datetime.now()
    results = {}
    
    for idx, category in enumerate(categories):
        logger.info(f"\n[{idx+1}/{len(categories)}] Generating {category.upper()}...")
        
        try:
            generated = generator.generate_category_batch(
                category=category,
                count=IMAGES_PER_CATEGORY,
                delay=DELAY_BETWEEN_IMAGES
            )
            results[category] = {
                "success": len(generated),
                "paths": [str(p) for p in generated]
            }
            logger.info(f"[{category}] Generated {len(generated)} images")
            
        except Exception as e:
            logger.error(f"[{category}] Failed: {str(e)}")
            results[category] = {
                "success": 0,
                "error": str(e)
            }
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    total_generated = sum(r.get("success", 0) for r in results.values())
    
    log = load_batch_log()
    log["last_run"] = datetime.now().isoformat()
    log["runs"].append({
        "timestamp": datetime.now().isoformat(),
        "total_generated": total_generated,
        "duration_minutes": round(duration / 60, 1),
        "by_category": {cat: r.get("success", 0) for cat, r in results.items()}
    })
    
    if len(log["runs"]) > 10:
        log["runs"] = log["runs"][-10:]
    
    save_batch_log(log)
    
    logger.info("=" * 60)
    logger.info("BATCH COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total generated: {total_generated}/{total_images}")
    logger.info(f"Duration: {duration/60:.1f} minutes")
    logger.info(f"Next batch due: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
    
    return {
        "success": True,
        "skipped": False,
        "total_generated": total_generated,
        "duration_minutes": round(duration / 60, 1),
        "results": results
    }


def get_image_counts() -> dict:
    """Get current image counts per category."""
    images_path = project_root / "assets" / "images"
    counts = {}
    
    for category in CATEGORY_ESSENCES.keys():
        cat_path = images_path / category
        if cat_path.exists():
            images = [f for f in cat_path.iterdir() 
                     if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp']
                     and 'used' not in str(f)]
            counts[category] = len(images)
        else:
            counts[category] = 0
    
    return counts


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Batch Image Generator')
    parser.add_argument('--force', action='store_true', help='Force run even if not due')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--counts', action='store_true', help='Show image counts per category')
    
    args = parser.parse_args()
    
    if args.status:
        log = load_batch_log()
        print("\n=== WEEKLY BATCH STATUS ===")
        print(f"Last run: {log.get('last_run', 'Never')}")
        print(f"Is due: {is_batch_due()}")
        if log.get("runs"):
            last = log["runs"][-1]
            print(f"Last batch generated: {last.get('total_generated', 0)} images")
        print()
        
    elif args.counts:
        counts = get_image_counts()
        print("\n=== IMAGE COUNTS BY CATEGORY ===")
        for cat, count in counts.items():
            print(f"  {cat}: {count} images")
        print(f"\nTotal: {sum(counts.values())} images")
        print()
        
    else:
        result = run_weekly_batch(force=args.force)
        if result.get("skipped"):
            print(f"\nSkipped: {result['message']}")
        else:
            print(f"\nGenerated {result['total_generated']} images in {result['duration_minutes']} minutes")
