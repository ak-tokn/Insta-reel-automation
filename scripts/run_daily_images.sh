#!/bin/bash
# Daily AI Image Generator for StoicAlgo
# Run this via cron twice daily

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd /Users/ak/Documents/Projects/StoicAlgo

# Log file with date
LOG_FILE="logs/daily_generation_$(date +%Y%m%d).log"

echo "========================================" >> "$LOG_FILE"
echo "Run started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

python3 scripts/daily_image_generator.py --count 2 >> "$LOG_FILE" 2>&1

echo "Run completed: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
