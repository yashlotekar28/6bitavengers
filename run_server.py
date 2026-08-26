import os
import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    print("\n🚀 Opening ProcureShield AI Dashboard in your browser: http://localhost:8000")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    # Add backend directory to sys.path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)

    print("=" * 65)
    print("  ProcureShield AI — GeM Vendor Verification & Compliance Engine")
    print("=" * 65)
    print("Starting FastAPI Engine + Interactive Dashboard at http://localhost:8000")
    print("Swagger API Docs: http://localhost:8000/docs\n")

    threading.Thread(target=open_browser, daemon=True).start()
    
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000)
