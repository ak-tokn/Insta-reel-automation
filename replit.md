# StoicAlgo - Automated Instagram Content Pipeline

## Overview
StoicAlgo is an automated content creation and posting system for Instagram, focused on stoic/philosophical quotes (Reels) and AI-powered money-making ideas (Carousel posts). The system generates video and image content with text overlays, background music, and posts on a configurable schedule.

## Recent Changes
- **Dec 02, 2025**: Updated schedule: 2 Reels (8am, 6pm) + 1 Daily Ai'ds (12pm) per day
- **Dec 02, 2025**: Enhanced idea generation with 30+ creative themes and modern tech requirements (GPT-4o, Claude 3.5)
- **Dec 02, 2025**: Added "(ai can do it)" indicator for steps AI can fully automate
- **Dec 02, 2025**: Scaling steps now show revenue math (price × clients = target)
- **Dec 02, 2025**: Added "Daily Ai'ds" carousel post feature - AI-generated money-making ideas with step-by-step breakdowns
- **Dec 02, 2025**: Added carousel posting capability to Instagram client
- **Dec 02, 2025**: Created DailyAidService for OpenAI-powered idea generation
- **Dec 02, 2025**: Created DailyAidSlideBuilder for rendering carousel images (title, steps, CTA slides)
- **Nov 30, 2025**: Added Flash Reel format - dramatic voiceover with synchronized word reveals and flashing images
- **Nov 30, 2025**: Added voiceover service using fal.ai Chatterbox HD TTS with dramatic/sinister voice modes
- **Nov 30, 2025**: Added reference person video generation using fal.ai Vidu API (every 10th post features the reference person)
- **Nov 30, 2025**: Added animated video backgrounds using fal.ai Kling API (every 5th post uses animation)
- **Nov 30, 2025**: Fixed post counter logic to only increment after successful completion
- **Nov 30, 2025**: Added proper video validation for animated backgrounds (scaling, cropping, looping)

## Project Architecture

### Core Components
- `scheduler.py` - Main entry point, schedules 3 daily posts (2 Reels + 1 Daily Ai'ds carousel)
- `scripts/orchestrator.py` - Pipeline coordinator, manages the content creation workflow
- `scripts/video_builder.py` - FFmpeg-based video generation with Ken Burns, vignette, and glitch effects
- `scripts/flash_reel_builder.py` - Flash reel format with rapid image transitions and voiceover
- `scripts/voiceover_service.py` - fal.ai Chatterbox HD TTS for dramatic voiceovers
- `scripts/animated_background.py` - fal.ai Kling API integration for animated video backgrounds
- `scripts/reference_person_video.py` - fal.ai Vidu API integration for reference person videos
- `scripts/quote_service.py` - LLM-powered quote generation
- `scripts/instagram_client.py` - Instagram posting via Graph API (Reels + Carousels)

### Daily Ai'ds Components (NEW)
- `scripts/daily_aid_service.py` - OpenAI-powered business idea generation
- `scripts/daily_aid_slide_builder.py` - Pillow-based carousel image rendering
- `scripts/daily_aids_orchestrator.py` - Coordinates idea generation, slide building, and posting
- `logs/daily_aids_count.json` - Tracks the current Daily Ai'ds number

### Reference Person
- `assets/reference_person/` - Contains reference images for Vidu API (up to 7 images)
- Every 10th post generates a video featuring the reference person in the scene

### Configuration
- `config/settings.json` - All settings including video, audio, animation, and scheduling

### Animation Settings
```json
"animation": {
  "enabled": true,
  "frequency": 5,        // Every 5th post uses animated background
  "duration": "10",      // 10-second clips (matches full reel, no looping)
  "provider": "fal-ai",
  "model": "kling-video/v2.1/standard/image-to-video",
  "preferred_categories": ["nature", "sonder", "warriors"],
  "avoid_categories": ["temples", "statues"]
}
```

### Reference Person Settings
```json
"reference_person": {
  "enabled": false,       // Toggle on/off (off by default)
  "frequency": 10,        // Every 10th post features the reference person
  "model": "fal-ai/vidu/q1/reference-to-video",  // Q1 = higher quality, ~5 sec videos
  "movement_amplitude": "medium",  // small, medium, or large
  "preferred_backgrounds": ["temples", "nature", "warriors"]
}
```
Note: Vidu reference-to-video produces ~5-second clips (fixed by API). For 10-second reels, the video is looped/extended.

### Flash Reel Settings (NEW)
```json
"flash_reel": {
  "enabled": false,              // Toggle on/off (off by default)
  "image_flash_duration_ms": 300, // How long each image shows (independent of words)
  "images_per_reel": 20,         // Number of images per reel
  "words_per_flash": 2,          // Words shown at a time
  "dramatic_pause_ms": 800,      // Pause between quote and motivation
  "ending_phrase": "read the caption for real world applications",
  "voice": {
    "model": "resemble-ai/chatterboxhd/text-to-speech",
    "voice": "Cliff",            // Deep masculine voice (options: Cliff, Blade, Carl, Richard)
    "exaggeration": 0.5,         // Normal dramatic level
    "sinister_exaggeration": 0.7 // More intense for motivation
  }
}
```
The flash reel format features:
- "As [author name] once said..." intro before the quote
- Deep masculine voiceover (Cliff voice via ChatterboxHD)
- Rapid image flashing at fixed intervals (independent of word timing)
- Words appearing 1-2 at a time synchronized with speech
- Dramatic pause before motivation section
- Darker/sinister tone for the motivational part
- Ending phrase is voice-only (not displayed on screen)
- Images are NOT moved to 'used' folder for flash reels

### Required Secrets
- `FAL_API_KEY` - fal.ai API key for Kling and Vidu video generation
- Instagram API credentials (configured in settings)

### Daily Ai'ds Settings
```json
"daily_aids": {
  "enabled": true,
  "llm": {
    "model": "gpt-4o",
    "temperature": 0.85
  },
  "carousel": {
    "width": 1080,
    "height": 1350,
    "background_color": "#0A0A0A",
    "accent_color": "#FF3B3B",
    "min_steps": 5,
    "max_steps": 10
  },
  "branding": {
    "header_text": "DAILY AI'DS",
    "watermark": "@techiavellian",
    "cta_text": "Copy the caption into Claude/ChatGPT to get started"
  },
  "fonts": {
    "header": "Comico-Regular.ttf",
    "title": "Nippo-Bold.ttf",
    "numbers": "Orbitron-Bold.ttf",
    "body": "Chillax-Variable.ttf",
    "light": "Montserrat-Light.ttf"
  },
  "title_slide": {
    "background": "dimmed random image from assets",
    "header_format": "Daily Ai'Ds #N (Comico font, red)",
    "title_format": "Build a [IDEA NAME] to make money by [income method]",
    "earnings": "Set up once and make [amount/mo] easily!",
    "tagline": "The hardest part is getting started..I just solved that - so give this a shot?"
  }
}
```
The Daily Ai'ds feature generates:
- AI-powered money-making ideas using OpenAI GPT-4o
- Carousel posts with 5-10 step breakdowns
- Title slide with idea summary and earning potential
- Individual step slides with actionable instructions
- CTA slide directing users to copy the caption
- Full kickoff prompt in the caption for users to paste into ChatGPT/Claude

## Key Features
- Automated quote generation with LLM
- **Daily Ai'ds**: AI-generated business idea carousels with step-by-step guides
- **Two reel formats**: Standard (Ken Burns) and Flash Reel (voiceover + word reveals)
- Ken Burns zoom effect on static backgrounds
- AI-animated video backgrounds (every 5th post)
- Reference person videos (every 10th post features your persona)
- Flash reels with dramatic voiceover and synchronized text
- Text overlays with custom fonts and glow effects
- Background music selection based on mood
- Watermark positioning below motivation text
- Scheduled posting (5 times daily)
- Instagram carousel posting via Graph API

## User Preferences
- Animation frequency: every 5th post
- Video duration: 10 seconds
- Aspect ratio: 9:16 (vertical/portrait) for Reels
- Carousel ratio: 4:5 (1080x1350) for Daily Ai'ds
- Resolution: 1080x1920 for Reels
