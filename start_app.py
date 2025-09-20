#!/usr/bin/env python3
"""
Startup script for PedaRAGy application.
This script helps you start both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import importlib.util
        
        # Check uvicorn
        if importlib.util.find_spec("uvicorn") is None:
            raise ImportError("uvicorn not found")
        
        # Check streamlit
        if importlib.util.find_spec("streamlit") is None:
            raise ImportError("streamlit not found")
        
        # Check requests
        if importlib.util.find_spec("requests") is None:
            raise ImportError("requests not found")
        
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with:")
        print("pip install -r requirements.txt")
        print("pip install -r requirements_streamlit.txt")
        return False

def start_fastapi():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    try:
        # Start FastAPI server
        fastapi_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment and check if it started successfully
        time.sleep(2)
        if fastapi_process.poll() is None:
            print("✅ FastAPI server started on http://localhost:8000")
            return fastapi_process
        else:
            print("❌ FastAPI server failed to start")
            return None
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None

def start_streamlit():
    """Start the Streamlit app."""
    print("🎨 Starting Streamlit app...")
    try:
        # Start Streamlit app without auto-opening browser
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"  # Prevent auto browser opening
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment and check if it started successfully
        time.sleep(3)
        if streamlit_process.poll() is None:
            print("✅ Streamlit app started on http://localhost:8501")
            return streamlit_process
        else:
            print("❌ Streamlit app failed to start")
            return None
    except Exception as e:
        print(f"❌ Failed to start Streamlit app: {e}")
        return None

def main():
    """Main function to start the application."""
    print("🎯 PedaRAGy Application Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app/main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start FastAPI server
    fastapi_process = start_fastapi()
    if not fastapi_process:
        sys.exit(1)
    
    # Start Streamlit app
    streamlit_process = start_streamlit()
    if not streamlit_process:
        print("❌ Failed to start Streamlit app")
        fastapi_process.terminate()
        sys.exit(1)
    
    # Both services are running
    print("\n" + "=" * 50)
    print("🎉 Both services are running successfully!")
    print("=" * 50)
    print("📱 Streamlit UI: http://localhost:8501")
    print("🔧 FastAPI Docs: http://localhost:8000/docs")
    print("🌐 API Base: http://localhost:8000")
    print("=" * 50)
    
    # Ask user if they want to open the browser
    try:
        response = input("\n🌐 Would you like to open the Streamlit app in your browser? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🚀 Opening browser...")
            webbrowser.open("http://localhost:8501")
        else:
            print("💡 You can manually open http://localhost:8501 in your browser")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n📝 To stop the services, press Ctrl+C")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("❌ FastAPI server stopped unexpectedly")
                break
            if streamlit_process.poll() is not None:
                print("❌ Streamlit app stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
