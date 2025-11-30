# StoicAlgo

**Fully Automated Instagram Reels System** for posting Stoic/philosophical quotes with modern technical insights.

## Overview

StoicAlgo automatically generates and posts Instagram Reels daily, combining:
- Ancient Stoic wisdom
- Modern AI/tech interpretations
- Cinematic vertical videos
- Automated scheduling

## Features

- 🤖 **LLM-Powered Content**: Generates quotes, interpretations, and tech insights
- 🎬 **Ken Burns Video Effect**: Smooth zoom/pan animations
- 🎨 **Hybrid Image Strategy**: Mix of curated and AI-generated images
- 🎵 **Flexible Audio**: Original tracks, IG audio, or minimal
- 📱 **Instagram Graph API**: Direct posting to Reels
- 📊 **Full Logging**: Track every run and step

## Quick Start

### 1. Clone to Replit

Import this project into Replit or clone locally.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (if not on Replit)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Replit: Already configured in .replit
```

### 4. Set Environment Variables

In Replit Secrets (or your `.env` file):

```
OPENAI_API_KEY=sk-your-openai-key
INSTAGRAM_ACCESS_TOKEN=your-ig-access-token
INSTAGRAM_USER_ID=your-ig-user-id
STABILITY_API_KEY=your-stability-key  # Optional
```

### 5. Add Images

Add ~30 curated images to the folders:
```
assets/images/statues/
assets/images/warriors/
assets/images/nature/
assets/images/temples/
assets/images/cosmic/
assets/images/geometry/
```

Images should be high-quality, matching the dark/stoic/cinematic aesthetic.

### 6. Run Test

```bash
python main.py --test
```

### 7. Run Production

```bash
python main.py --post
```

## Project Structure

```
StoicAlgo/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── .replit                 # Replit configuration
│
├── assets/
│   ├── images/            # Curated image bank
│   │   ├── statues/
│   │   ├── warriors/
│   │   ├── nature/
│   │   ├── temples/
│   │   ├── cosmic/
│   │   ├── geometry/
│   │   └── ai_injected/   # AI-generated images
│   ├── audio/
│   │   ├── original_tracks/
│   │   └── instagram_audio_ids.json
│   └── fonts/
│
├── config/
│   ├── settings.json      # Main configuration
│   └── instagram_credentials.json
│
├── scripts/
│   ├── orchestrator.py    # Main pipeline
│   ├── quote_service.py   # LLM content generation
│   ├── caption_service.py # Caption building
│   ├── image_selector.py  # Image selection
│   ├── audio_selector.py  # Audio handling
│   ├── video_builder.py   # FFmpeg video creation
│   ├── ai_image_injector.py # Weekly AI image generation
│   ├── instagram_client.py # Instagram API
│   ├── logger.py          # Logging system
│   └── utils.py           # Utilities
│
├── output/
│   ├── videos/            # Generated videos
│   └── thumbnails/        # Generated thumbnails
│
└── logs/                  # Run logs
```

## Configuration

Edit `config/settings.json` to customize:

```json
{
  "video": {
    "duration_seconds": 10,
    "zoom_factor": 1.15
  },
  "audio": {
    "mode": "MIXED"  // ORIGINAL_ONLY, IG_AUDIO_ONLY, MIXED, MINIMAL_FOR_MANUAL_REPLACE
  },
  "image": {
    "curated_weight": 0.85,
    "ai_injected_weight": 0.15
  }
}
```

## Usage

### Manual Run

```bash
# Test mode (no posting)
python main.py --test

# Production (posts to Instagram)
python main.py --post

# With custom theme
python main.py --post --theme "resilience and adversity"
```

### Scheduled Run (Replit)

1. Go to Replit Deployments
2. Select "Scheduled"
3. Set cron schedule (e.g., `0 9 * * *` for daily at 9 AM)
4. Deploy

### Individual Components

```python
# Generate content only
from scripts.quote_service import QuoteService
service = QuoteService()
content = service.generate_content()

# Build video only
from scripts.video_builder import VideoBuilder
builder = VideoBuilder()
video, thumb = builder.build_video(image_path, quote, author)
```

## Instagram Setup

### Requirements
- Instagram Business or Creator account
- Meta Developer App
- Instagram Graph API permissions

### Getting Credentials

1. Create app at [developers.facebook.com](https://developers.facebook.com)
2. Add Instagram Graph API product
3. Generate User Token with permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
4. Get your Instagram User ID from the Graph API Explorer

### Video Hosting

Instagram requires videos at public URLs. Options:
- Replit static hosting
- Cloudflare R2
- AWS S3
- Custom CDN

Set `REPLIT_URL` or `VIDEO_PUBLIC_URL` environment variable.

## Content Pipeline

1. **Quote Generation** - LLM creates quote + interpretation + tech insight
2. **Caption Building** - Formats with hashtags
3. **Image Selection** - 85% curated, 15% AI-generated
4. **Video Building** - Ken Burns effect + text overlay
5. **Audio Addition** - Original or IG royalty-free
6. **Instagram Posting** - Via Graph API

## Weekly AI Images

Generate new AI images weekly:

```bash
python -c "from scripts.ai_image_injector import generate_weekly_images; generate_weekly_images()"
```

Or schedule in Replit separately.

## Troubleshooting

### FFmpeg not found
```bash
# Check installation
ffmpeg -version

# Install on Replit (already in .replit)
# Install locally: brew install ffmpeg
```

### Instagram posting fails
- Check access token is valid
- Verify video URL is publicly accessible
- Ensure video meets Instagram requirements (< 60s, 9:16 ratio)

### No images found
- Add images to `assets/images/` subfolders
- Check supported formats: .jpg, .jpeg, .png, .webp

### API rate limits
- OpenAI: Implement retry logic (included)
- Instagram: Max 25 posts per 24 hours

## Logs

Check `logs/` for:
- `stoicalgo.log` - General logs
- `run_YYYY-MM-DD.json` - Daily run details

## Brand Guidelines

### Aesthetic
- Dark, moody, cinematic
- Stoic, philosophical
- Futuristic, technical
- Green/emerald accents

### Content
- Ancient wisdom + modern tech
- Practical applications
- Premium, minimal presentation

### Hashtags
Mix of: #stoicism, #philosophy, #ai, #technology, #mindset, #wisdom

## Zero to Live Checklist

- [ ] Project imported to Replit
- [ ] Dependencies installed
- [ ] FFmpeg working
- [ ] Environment variables set
- [ ] 30+ curated images added
- [ ] Fonts added (optional)
- [ ] Test run successful
- [ ] Instagram credentials verified
- [ ] Production run successful
- [ ] Scheduled deployment configured

## License

MIT License

## Contributing

Contributions welcome! Please read the contribution guidelines first.

---

Built with 🏛️ ancient wisdom and 🤖 modern technology.
