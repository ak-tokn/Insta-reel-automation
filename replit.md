# StoicAlgo - Automated Instagram Reels Pipeline

## Overview
StoicAlgo is an automated content creation and posting system for Instagram Reels, focused on stoic/philosophical quotes. The system generates video content with text overlays, background music, and posts on a configurable schedule.

## Recent Changes
- **Nov 30, 2025**: Added animated video backgrounds using fal.ai Kling API (every 5th post uses animation)
- **Nov 30, 2025**: Fixed post counter logic to only increment after successful completion
- **Nov 30, 2025**: Added proper video validation for animated backgrounds (scaling, cropping, looping)

## Project Architecture

### Core Components
- `scheduler.py` - Main entry point, schedules 5 daily posts (7am, 12pm, 5pm, 8pm, 10pm)
- `scripts/orchestrator.py` - Pipeline coordinator, manages the content creation workflow
- `scripts/video_builder.py` - FFmpeg-based video generation with Ken Burns, vignette, and glitch effects
- `scripts/animated_background.py` - fal.ai Kling API integration for animated video backgrounds
- `scripts/quote_service.py` - LLM-powered quote generation
- `scripts/instagram_client.py` - Instagram posting via Graph API

### Configuration
- `config/settings.json` - All settings including video, audio, animation, and scheduling

### Animation Settings
```json
"animation": {
  "enabled": true,
  "frequency": 5,        // Every 5th post uses animated background
  "duration": "5",       // 5-second generated clips
  "provider": "fal-ai",
  "model": "kling-video/v2.1/standard/image-to-video"
}
```

### Required Secrets
- `FAL_API_KEY` - fal.ai API key for Kling video generation
- Instagram API credentials (configured in settings)

## Key Features
- Automated quote generation with LLM
- Ken Burns zoom effect on static backgrounds
- AI-animated video backgrounds (every Nth post)
- Text overlays with custom fonts and glow effects
- Background music selection based on mood
- Watermark positioning below motivation text
- Scheduled posting (5 times daily)

## User Preferences
- Animation frequency: every 5th post
- Video duration: 10 seconds
- Aspect ratio: 9:16 (vertical/portrait)
- Resolution: 1080x1920
