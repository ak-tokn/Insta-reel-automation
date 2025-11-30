# StoicAlgo Replit Deployment Guide

## Overview
This guide will help you deploy StoicAlgo to Replit for automated daily Instagram posting (5 posts/day).

---

## Step 1: Create Replit Account & Project

1. Go to [replit.com](https://replit.com) and sign up/login
2. Click **"Create Repl"**
3. Select **"Python"** template
4. Name it `StoicAlgo`
5. Click **"Create Repl"**

---

## Step 2: Upload Project Files

### Option A: Git Import (Recommended)
If your project is on GitHub:
1. In Replit, click **"Create Repl"** → **"Import from GitHub"**
2. Paste your repo URL
3. Replit will auto-import everything

### Option B: Manual Upload
1. In Replit, click the three dots next to "Files" → **"Upload folder"**
2. Upload these folders/files from your local project:
   ```
   StoicAlgo/
   ├── scripts/           # All Python scripts
   ├── config/            # settings.json
   ├── assets/
   │   ├── audio/         # meandthedevil.mp3
   │   ├── fonts/         # Panchang-Regular.ttf, Comico-Regular.ttf
   │   └── images/        # All image categories
   ├── main.py
   ├── requirements.txt
   └── .replit            # We'll create this
   ```

---

## Step 3: Configure Environment Variables (Secrets)

In Replit, go to **"Secrets"** (lock icon in left sidebar) and add:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `INSTAGRAM_ACCESS_TOKEN` | Your long-lived Instagram token |
| `INSTAGRAM_USER_ID` | `17841477859351381` |
| `META_APP_ID` | `2220573955098627` |
| `META_APP_SECRET` | Your Meta app secret |

---

## Step 4: Create Replit Configuration Files

### Create `.replit` file:
```toml
run = "python main.py"
language = "python3"
entrypoint = "main.py"

[nix]
channel = "stable-22_11"

[env]
PYTHONPATH = "${PYTHONPATH}:${HOME}/${REPL_SLUG}"

[packager]
language = "python3"

[packager.features]
enabledForHosting = false
packageSearch = true
guessImports = true

[deployment]
run = "python scheduler.py"
```

### Create `replit.nix` file:
```nix
{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.ffmpeg
    pkgs.imagemagick
  ];
}
```

### Update `requirements.txt`:
```
openai>=1.0.0
requests>=2.28.0
Pillow>=9.0.0
python-dotenv>=1.0.0
schedule>=1.2.0
flask>=2.0.0
```

---

## Step 5: Create the Scheduler

Create `scheduler.py` in the root directory:

```python
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
            logger.info(f"✅ Post successful!")
        else:
            logger.error(f"❌ Post failed: {result}")
            
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

def add_jitter(base_time: str, jitter_minutes: int = 15) -> str:
    """Add random jitter to posting time to appear more human."""
    hour, minute = map(int, base_time.split(':'))
    jitter = random.randint(-jitter_minutes, jitter_minutes)
    new_minute = (minute + jitter) % 60
    if minute + jitter >= 60:
        hour = (hour + 1) % 24
    elif minute + jitter < 0:
        hour = (hour - 1) % 24
    return f"{hour:02d}:{new_minute:02d}"

def setup_schedule():
    """
    Set up 5 daily posts at optimal engagement times.
    
    Optimal posting times (US-centric, adjust for your audience):
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
    logger.info("🚀 StoicAlgo Scheduler Starting...")
    logger.info(f"Current time: {datetime.now()}")
    
    setup_schedule()
    
    logger.info("=" * 50)
    logger.info("Scheduler running. Posts scheduled for:")
    for job in schedule.get_jobs():
        logger.info(f"  → {job}")
    logger.info("=" * 50)
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    run_scheduler()
```

---

## Step 6: Create Keep-Alive Server (Required for Replit)

Replit will stop your repl if there's no web activity. Create `keep_alive.py`:

```python
"""
Keep-alive server for Replit.
Prevents the repl from sleeping.
"""

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "StoicAlgo is running! 🚀"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "StoicAlgo"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
```

### Update `scheduler.py` to include keep-alive:

Add at the top:
```python
from keep_alive import keep_alive
```

Add before the while loop:
```python
# Start keep-alive server
keep_alive()
logger.info("🌐 Keep-alive server started on port 8080")
```

---

## Step 7: Set Up External Uptime Monitor

Replit needs external pings to stay awake. Use one of these free services:

### Option A: UptimeRobot (Recommended)
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account
3. Add new monitor:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `StoicAlgo`
   - URL: `https://your-repl-name.your-username.repl.co`
   - Monitoring Interval: **5 minutes**

### Option B: Cron-job.org
1. Go to [cron-job.org](https://cron-job.org)
2. Create account
3. Add new cron job to ping your Replit URL every 5 minutes

---

## Step 8: Deploy and Run

1. In Replit, click **"Run"** button
2. Wait for dependencies to install
3. You should see:
   ```
   🚀 StoicAlgo Scheduler Starting...
   📅 Scheduled post at 07:05
   📅 Scheduled post at 12:08
   📅 Scheduled post at 17:02
   📅 Scheduled post at 20:11
   📅 Scheduled post at 22:03
   🌐 Keep-alive server started on port 8080
   ```

4. Copy your Replit URL (shown in webview) and add to UptimeRobot

---

## Step 9: Enable Always-On (Optional but Recommended)

For guaranteed uptime, consider Replit's paid plans:

| Plan | Price | Benefit |
|------|-------|---------|
| Hacker | $7/month | Always-on repls |
| Pro | $20/month | More resources + always-on |

Without paid plan, the free tier + UptimeRobot combo works ~95% of the time.

---

## Folder Structure on Replit

```
StoicAlgo/
├── .replit
├── replit.nix
├── main.py
├── scheduler.py
├── keep_alive.py
├── requirements.txt
├── config/
│   └── settings.json
├── scripts/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── quote_service.py
│   ├── caption_service.py
│   ├── video_builder.py
│   ├── image_selector.py
│   ├── audio_selector.py
│   ├── instagram_client.py
│   ├── token_manager.py
│   ├── logger.py
│   └── utils.py
├── assets/
│   ├── audio/
│   │   └── meandthedevil.mp3
│   ├── fonts/
│   │   ├── Panchang-Regular.ttf
│   │   └── Comico-Regular.ttf
│   └── images/
│       ├── statues/
│       ├── warriors/
│       ├── nature/
│       ├── temples/
│       └── sonder/
├── output/
│   ├── videos/
│   ├── thumbnails/
│   └── prepared/
└── logs/
```

---

## Monitoring & Maintenance

### Check Logs
In Replit console, you'll see real-time logs of:
- Scheduled post times
- Content generation
- Video building
- Instagram posting results

### Token Refresh
The token auto-refreshes, but check monthly that it's still valid:
```python
python -c "from scripts.token_manager import TokenManager; TokenManager().check_token_validity()"
```

### Image Replenishment
When images run low, the system will warn you. Upload new batches to:
- `assets/images/statues/`
- `assets/images/warriors/`
- etc.

---

## Troubleshooting

### "Module not found" errors
Run in Replit shell:
```bash
pip install -r requirements.txt
```

### FFmpeg not working
Ensure `replit.nix` includes `pkgs.ffmpeg`

### Repl keeps sleeping
1. Verify UptimeRobot is pinging correctly
2. Check keep_alive.py is running
3. Consider Replit Hacker plan ($7/mo)

### Instagram token expired
1. Go to Meta Graph API Explorer
2. Generate new token
3. Update in Replit Secrets

---

## Cost Summary

| Service | Cost |
|---------|------|
| Replit (free tier) | $0 |
| UptimeRobot (free) | $0 |
| OpenAI API | ~$0.50-2/day (depending on usage) |
| **Total** | **~$15-60/month** |

For guaranteed uptime, add Replit Hacker ($7/mo) = ~$22-67/month total.

---

## Quick Start Commands

After setup, run these in Replit shell to test:

```bash
# Test single post (no Instagram)
python main.py --test

# Test single post (with Instagram)
python main.py

# Start scheduler
python scheduler.py
```

---

## Need Help?

- Replit Docs: https://docs.replit.com
- Meta Graph API: https://developers.facebook.com/tools/explorer
- OpenAI API: https://platform.openai.com

Good luck! 🚀
