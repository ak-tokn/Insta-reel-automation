#!/usr/bin/env python3
"""
StoicAlgo - Automated Instagram Reels System
Main entry point for running the content pipeline.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from scripts.orchestrator import run_pipeline, run_test


def main():
    """Main entry point."""
    
    # Check if running in test mode
    test_mode = '--test' in sys.argv or os.environ.get('STOIC_TEST_MODE', '').lower() == 'true'
    
    # Get custom theme if provided
    theme = None
    for i, arg in enumerate(sys.argv):
        if arg == '--theme' and i + 1 < len(sys.argv):
            theme = sys.argv[i + 1]
    
    # Run pipeline
    if test_mode:
        print("Running in TEST MODE (no Instagram posting)")
        result = run_test()
    else:
        # Check for required environment variables
        required = ['OPENAI_API_KEY', 'INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_USER_ID']
        missing = [v for v in required if not os.environ.get(v)]
        
        if missing:
            print("ERROR: Missing required environment variables:")
            for var in missing:
                print(f"  - {var}")
            print("\nPlease set these in Replit Secrets or your environment.")
            sys.exit(1)
        
        result = run_pipeline(post_to_instagram=True, custom_theme=theme)
    
    return result


if __name__ == "__main__":
    main()
