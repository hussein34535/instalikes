import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.python.run_likes import run_auto_liker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Insta Auto Liker CLI')
    parser.add_argument('url', type=str, help='Target Post URL')
    
    args = parser.parse_args()
    
    print(f"Starting job for: {args.url}")
    
    # Run synchronously (blocking)
    try:
        run_auto_liker(args.url)
        print("Job finished successfully.")
    except Exception as e:
        print(f"Job failed: {e}")
        sys.exit(1)
