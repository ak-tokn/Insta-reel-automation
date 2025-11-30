# StoicAlgo - Master Handoff Document

## Project Overview
**Fully Automated Instagram Reels System** for posting Stoic/philosophical quotes with technical insights.

### Core Functionality
- Generate philosophical quotes with modern tech interpretations
- Create cinematic vertical videos with Ken Burns effect
- Post automatically to Instagram Reels
- Run on Replit with local storage (no AWS/S3)

### Brand Aesthetic
- Dark, Stoic, Cinematic, Futuristic, Technical
- Green/emerald digital accents
- Premium, minimal, elegant

---

## Implementation Progress

### Phase 1: Project Structure ⏳ IN PROGRESS
- [ ] Create folder structure
- [ ] Set up configuration files
- [ ] Create settings templates

### Phase 2: Core Services ⏳ PENDING
- [ ] quote_service.py - LLM quote generation
- [ ] caption_service.py - Caption building
- [ ] image_selector.py - Image selection logic
- [ ] audio_selector.py - Audio handling
- [ ] video_builder.py - FFmpeg video creation
- [ ] instagram_client.py - Graph API integration

### Phase 3: Support Services ⏳ PENDING
- [ ] ai_image_injector.py - Weekly AI image generation
- [ ] logger.py - Local logging system
- [ ] utils.py - Helper functions

### Phase 4: Orchestration ⏳ PENDING
- [ ] orchestrator.py - Main pipeline
- [ ] Manual run testing
- [ ] Error handling

### Phase 5: Deployment Setup ⏳ PENDING
- [ ] Replit configuration
- [ ] Environment variables
- [ ] Scheduled tasks setup
- [ ] Final testing

---

## Current Status

**Last Updated:** Starting implementation
**Current Phase:** Phase 1 - Project Structure
**Next Action:** Create folder structure and configuration files

---

## File Structure (Target)

```
/StoicAlgo
├── MasterHandoffs/
│   └── Master_Handoff.md
├── assets/
│   ├── images/
│   │   ├── statues/
│   │   ├── warriors/
│   │   ├── nature/
│   │   ├── temples/
│   │   ├── cosmic/
│   │   ├── geometry/
│   │   └── ai_injected/
│   ├── audio/
│   │   ├── original_tracks/
│   │   └── instagram_audio_ids.json
│   └── fonts/
├── config/
│   ├── settings.json
│   └── instagram_credentials.json
├── logs/
├── output/
│   ├── videos/
│   └── thumbnails/
├── scripts/
│   ├── __init__.py
│   ├── quote_service.py
│   ├── caption_service.py
│   ├── image_selector.py
│   ├── ai_image_injector.py
│   ├── video_builder.py
│   ├── audio_selector.py
│   ├── instagram_client.py
│   ├── logger.py
│   ├── utils.py
│   └── orchestrator.py
├── main.py
├── requirements.txt
├── .replit
└── README.md
```

---

## API Requirements

### Required APIs
1. **LLM API** (OpenAI/Claude) - Quote & caption generation
2. **Instagram Graph API** - Posting reels
3. **Stability AI** (optional) - AI image generation

### Environment Variables Needed
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`
- `STABILITY_API_KEY` (optional)

---

## Quick Resume Guide

### To Continue Development
1. Check "Current Status" section above
2. Look at the current phase's unchecked items
3. Implement next pending item
4. Update this document when complete

### To Run the System
```bash
cd /Users/ak/Documents/Projects/StoicAlgo
python main.py
```

### To Test Individual Components
```bash
python -m scripts.quote_service
python -m scripts.video_builder
```

---

## Completion Checklist

- [ ] All folders created
- [ ] All configuration files in place
- [ ] All Python modules implemented
- [ ] Requirements.txt complete
- [ ] Manual test successful
- [ ] Instagram posting verified
- [ ] Documentation complete
- [ ] Replit deployment configured

---

## Notes & Decisions

### Technical Decisions
- Using FFmpeg for video generation (most reliable)
- Pillow for text overlays
- Local JSON for configuration
- Structured logging to /logs

### Content Strategy
- 85-90% curated images, 10-15% AI-generated
- Multiple audio modes supported
- LLM generates quote → interpretation → tech insight → applications

---

*This document auto-updates as implementation progresses*
