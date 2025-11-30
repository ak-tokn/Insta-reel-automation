# StoicAlgo - Automated Instagram Reels Pipeline

## Overview
StoicAlgo is an automated content creation and posting system for Instagram Reels, focused on stoic/philosophical quotes. The system generates video content with text overlays, background music, and posts on a configurable schedule.

## Recent Changes
- **Nov 30, 2025**: Added Flash Reel format - dramatic voiceover with synchronized word reveals and flashing images
- **Nov 30, 2025**: Added voiceover service using fal.ai Chatterbox HD TTS with dramatic/sinister voice modes
- **Nov 30, 2025**: Added reference person video generation using fal.ai Vidu API (every 10th post features the reference person)
- **Nov 30, 2025**: Added animated video backgrounds using fal.ai Kling API (every 5th post uses animation)
- **Nov 30, 2025**: Fixed post counter logic to only increment after successful completion
- **Nov 30, 2025**: Added proper video validation for animated backgrounds (scaling, cropping, looping)

## Project Architecture

### Core Components
- `scheduler.py` - Main entry point, schedules 5 daily posts (7am, 12pm, 5pm, 8pm, 10pm)
- `scripts/orchestrator.py` - Pipeline coordinator, manages the content creation workflow
- `scripts/video_builder.py` - FFmpeg-based video generation with Ken Burns, vignette, and glitch effects
- `scripts/flash_reel_builder.py` - Flash reel format with rapid image transitions and voiceover
- `scripts/voiceover_service.py` - fal.ai Chatterbox HD TTS for dramatic voiceovers
- `scripts/animated_background.py` - fal.ai Kling API integration for animated video backgrounds
- `scripts/reference_person_video.py` - fal.ai Vidu API integration for reference person videos
- `scripts/quote_service.py` - LLM-powered quote generation
- `scripts/instagram_client.py` - Instagram posting via Graph API

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
  "image_flash_duration_ms": 300, // How long each image shows
  "images_per_reel": 15,         // Number of images per reel
  "words_per_flash": 2,          // Words shown at a time
  "dramatic_pause_ms": 800,      // Pause between quote and motivation
  "ending_phrase": "read the caption for real world applications",
  "voice": {
    "model": "resemble-ai/chatterboxhd/text-to-speech",
    "exaggeration": 0.7,         // Normal dramatic level
    "sinister_exaggeration": 1.2 // More intense for motivation
  }
}
```
The flash reel format features:
- Rapid image flashing from a single category
- Masculine, stoic voiceover reading the quote
- Words appearing 1-2 at a time synchronized with speech
- Dramatic pause before motivation section
- Darker/sinister tone for the motivational part
- Ends with call-to-action for caption

### Required Secrets
- `FAL_API_KEY` - fal.ai API key for Kling and Vidu video generation
- Instagram API credentials (configured in settings)

## Key Features
- Automated quote generation with LLM
- **Two reel formats**: Standard (Ken Burns) and Flash Reel (voiceover + word reveals)
- Ken Burns zoom effect on static backgrounds
- AI-animated video backgrounds (every 5th post)
- Reference person videos (every 10th post features your persona)
- Flash reels with dramatic voiceover and synchronized text
- Text overlays with custom fonts and glow effects
- Background music selection based on mood
- Watermark positioning below motivation text
- Scheduled posting (5 times daily)

## User Preferences
- Animation frequency: every 5th post
- Video duration: 10 seconds
- Aspect ratio: 9:16 (vertical/portrait)
- Resolution: 1080x1920
