"""
StoicAlgo Scheduler for Replit
Runs daily content: 2 Reel posts + 1 Daily Ai'ds carousel post.
"""

import schedule
import time
import random
import logging
from datetime import datetime
from scripts.orchestrator import run_pipeline
from scripts.daily_aids_orchestrator import run_daily_aids
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Scheduler")


def post_reel():
    """Execute a single Reel (quote) post."""
    try:
        logger.info("=" * 50)
        logger.info(f"Starting scheduled REEL post at {datetime.now()}")
        
        result = run_pipeline(post_to_instagram=True)
        
        if result.get('status') == 'completed':
            post_id = result.get('output', {}).get('post_result', {}).get('post_id', 'N/A')
            logger.info(f"✅ Reel post successful! Post ID: {post_id}")
        else:
            logger.error(f"❌ Reel post failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Reel scheduler error: {e}", exc_info=True)


def post_daily_aids():
    """Execute the Daily Ai'ds carousel post."""
    try:
        logger.info("=" * 50)
        logger.info(f"Starting scheduled DAILY AI'DS post at {datetime.now()}")
        
        result = run_daily_aids(dry_run=False)
        
        if result.get('success'):
            post_id = result.get('post_id', 'N/A')
            logger.info(f"✅ Daily Ai'ds post successful! Post ID: {post_id}")
        else:
            logger.error(f"❌ Daily Ai'ds post failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Daily Ai'ds scheduler error: {e}", exc_info=True)


def add_jitter(base_time: str, jitter_minutes: int = 15) -> str:
    """Add random jitter to posting time to appear more human."""
    hour, minute = map(int, base_time.split(':'))
    jitter = random.randint(-jitter_minutes, jitter_minutes)
    new_minute = minute + jitter
    
    if new_minute >= 60:
        hour = (hour + 1) % 24
        new_minute = new_minute - 60
    elif new_minute < 0:
        hour = (hour - 1) % 24
        new_minute = 60 + new_minute
        
    return f"{hour:02d}:{new_minute:02d}"


def setup_schedule():
    """
    Set up daily content schedule (PST):
    - 2 Reel posts (stoic quotes)
    - 1 Daily Ai'ds carousel post
    
    Schedule:
    - 8:00 AM  - Reel (morning motivation)
    - 12:00 PM - Daily Ai'ds (lunch break learning)
    - 6:00 PM  - Reel (evening scroll)
    """
    
    reel_times = [
        "08:00",  # Morning motivation
        "18:00",  # Evening scroll
    ]
    
    daily_aids_times = [
        "12:00",  # Lunch break - perfect for learning content
    ]
    
    for base_time in reel_times:
        scheduled_time = add_jitter(base_time, jitter_minutes=10)
        schedule.every().day.at(scheduled_time).do(post_reel)
        logger.info(f"📅 Scheduled REEL at {scheduled_time}")
    
    for base_time in daily_aids_times:
        scheduled_time = add_jitter(base_time, jitter_minutes=10)
        schedule.every().day.at(scheduled_time).do(post_daily_aids)
        logger.info(f"📅 Scheduled DAILY AI'DS at {scheduled_time}")


def run_scheduler():
    """Main scheduler loop."""
    logger.info("=" * 60)
    logger.info("🚀 StoicAlgo Scheduler Starting...")
    logger.info(f"📍 Current time: {datetime.now()}")
    logger.info("=" * 60)
    
    # Start keep-alive server for Replit
    keep_alive()
    logger.info("🌐 Keep-alive server started on port 8080")
    
    # Setup the posting schedule
    setup_schedule()
    
    logger.info("=" * 60)
    logger.info("✅ Scheduler running! Daily content schedule:")
    logger.info("  📹 2x Reels (stoic quotes)")
    logger.info("  🎠 1x Daily Ai'ds (carousel)")
    logger.info("")
    logger.info("Scheduled times:")
    for job in schedule.get_jobs():
        logger.info(f"  → {job.next_run.strftime('%H:%M')}")
    logger.info("=" * 60)
    logger.info("Waiting for scheduled times...")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scheduler()
