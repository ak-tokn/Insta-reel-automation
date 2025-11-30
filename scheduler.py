"""
StoicAlgo Scheduler for Replit
Runs 5 posts per day at strategic times for maximum engagement.
"""

import schedule
import time
import random
import logging
from datetime import datetime
from scripts.orchestrator import run_pipeline
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Scheduler")


def post_to_instagram():
    """Execute a single Instagram post."""
    try:
        logger.info("=" * 50)
        logger.info(f"Starting scheduled post at {datetime.now()}")
        
        result = run_pipeline(post_to_instagram=True)
        
        if result.get('status') == 'completed':
            post_id = result.get('output', {}).get('post_result', {}).get('post_id', 'N/A')
            logger.info(f"✅ Post successful! Post ID: {post_id}")
        else:
            logger.error(f"❌ Post failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}", exc_info=True)


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
    Set up 5 daily posts at optimal engagement times (PST).
    
    Optimal posting times:
    - 7:00 AM  - Morning commute
    - 12:00 PM - Lunch break  
    - 5:00 PM  - End of work day
    - 8:00 PM  - Evening scroll
    - 10:00 PM - Late night
    """
    
    post_times = [
        "07:00",  # Morning
        "12:00",  # Lunch
        "17:00",  # After work
        "20:00",  # Evening
        "22:00",  # Night
    ]
    
    for base_time in post_times:
        # Add slight randomization to appear more natural
        scheduled_time = add_jitter(base_time, jitter_minutes=10)
        schedule.every().day.at(scheduled_time).do(post_to_instagram)
        logger.info(f"📅 Scheduled post at {scheduled_time}")


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
    logger.info("✅ Scheduler running! Posts scheduled for today:")
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
