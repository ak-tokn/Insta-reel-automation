#!/usr/bin/env python3
"""Manual post script - run a single post to Instagram."""

import sys
from scripts.orchestrator import Orchestrator

def main():
    print("=" * 50)
    print("MANUAL POST - StoicAlgo")
    print("=" * 50)
    
    try:
        orch = Orchestrator()
        result = orch.run(post_to_instagram=True)
        
        if result.get('status') == 'completed':
            post_id = result.get('output', {}).get('post_result', {}).get('post_id', 'N/A')
            author = "Unknown"
            for step in result.get('steps', []):
                if step.get('step') == 'content_generation':
                    author = step.get('details', {}).get('author', 'Unknown')
                    break
            
            print("\n" + "=" * 50)
            print("SUCCESS!")
            print(f"  Post ID: {post_id}")
            print(f"  Author: {author}")
            print("=" * 50)
            return 0
        else:
            print(f"\nFailed with status: {result.get('status', 'unknown')}")
            return 1
            
    except Exception as e:
        print(f"\nError: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
