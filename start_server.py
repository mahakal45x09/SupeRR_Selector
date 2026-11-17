"""
SupeRR Selector — Full-Stack Server Launcher
Runs the FastAPI Backend & Serves the Interactive Frontend.

Usage:
    python start_server.py

Access:
    Web App:  http://127.0.0.1:8000
    API Docs: http://127.0.0.1:8000/docs
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("  Starting SupeRR Selector Full-Stack Application")
    print("  Backend API:  http://127.0.0.1:8000/api")
    print("  Swagger Docs: http://127.0.0.1:8000/docs")
    print("  Frontend UI:  http://127.0.0.1:8000/")
    print("=" * 70)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
