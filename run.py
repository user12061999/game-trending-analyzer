"""Launcher script for Game Market Trending Analyzer Dashboard."""

import sys
import os

# Ensure console handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["PYTHONIOENCODING"] = "utf-8"

import webbrowser
import threading
import time
import uvicorn
from app.config import PORT, HOST

def open_browser():
    time.sleep(1.5)
    print(f"Opening browser at http://127.0.0.1:{PORT} ...")
    webbrowser.open(f"http://127.0.0.1:{PORT}")

if __name__ == "__main__":
    print("=" * 65)
    print("[*] GAME MARKET TRENDING ANALYZER (PC & MOBILE)")
    print("=" * 65)
    print(f"• Khoi dong may chu Web Dashboard tai: http://127.0.0.1:{PORT}")
    print("• Co so du lieu SQLite: data/games.db")
    print("• Nhan Ctrl+C de dung may chu")
    print("=" * 65)

    # Automatically launch browser in a thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI server
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False, log_level="info")
