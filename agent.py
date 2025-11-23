"""
Resilience Coach Agent - Unified Launcher
Starts both backend and frontend servers and opens the UI
"""

import subprocess
import time
import webbrowser
import sys
import os
from threading import Thread

def start_backend():
    """Start the Flask backend server"""
    print("🔧 Starting Flask backend server on port 5000...")
    try:
        subprocess.run([sys.executable, "-m", "backend.app"], check=True)
    except KeyboardInterrupt:
        print("\n✅ Backend server stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the frontend HTTP server"""
    print("🌐 Starting frontend server on port 8000...")
    try:
        os.chdir("frontend")
        subprocess.run([sys.executable, "-m", "http.server", "8000"], check=True)
    except KeyboardInterrupt:
        print("\n✅ Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def open_browser():
    """Open the web interface in default browser"""
    time.sleep(3)  # Wait for servers to start
    print("🚀 Opening Resilience Coach Agent in browser...")
    webbrowser.open("http://localhost:8000")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import google.generativeai
        import langgraph
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Please install dependencies: pip install -r requirements.txt")
        return False

def main():
    """Main launcher function"""
    print("="*60)
    print("     Resilience Coach Agent - AI Mental Wellness Support")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found")
        print("📝 Please create .env file with your GEMINI_API_KEY")
        print("   Copy .env.example to .env and add your API key")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🎯 Starting Resilience Coach Agent...")
    print("   - Backend API: http://localhost:5000")
    print("   - Frontend UI: http://localhost:8000")
    print("\n⚠️  Press Ctrl+C to stop all servers\n")
    
    # Start backend in separate thread
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(2)
    
    # Start frontend in separate thread
    frontend_thread = Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Open browser
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("     Shutting down Resilience Coach Agent...")
        print("="*60)
        print("\n✅ All servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
