#!/usr/bin/env python3
"""
Simple script to start only the Streamlit app.
Use this if you want to start the FastAPI server manually.
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Start the Streamlit app."""
    print("🎨 Starting PedaRAGy Streamlit App")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found. Please run from project root.")
        sys.exit(1)
    
    print("📝 Make sure your FastAPI server is running on http://localhost:8000")
    print("   You can start it with: uvicorn app.main:app --reload")
    print()
    
    # Ask user if they want to open browser
    try:
        response = input("🌐 Open browser automatically? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🚀 Starting Streamlit and opening browser...")
            # Start Streamlit without headless mode so it opens browser
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "streamlit_app.py",
                "--server.port", "8501"
            ])
        else:
            print("🚀 Starting Streamlit in headless mode...")
            print("💡 You can manually open http://localhost:8501 in your browser")
            # Start Streamlit in headless mode
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "streamlit_app.py",
                "--server.port", "8501",
                "--server.headless", "true"
            ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
