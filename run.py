"""Launcher script for Game Market Trending Analyzer Dashboard."""

import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    print("Opening browser at http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 65)
    print("🎮 GAME MARKET TRENDING ANALYZER (PC & MOBILE)")
    print("=" * 65)
    print("• Khởi động máy chủ Web Dashboard tại: http://127.0.0.1:8000")
    print("• Cơ sở dữ liệu SQLite: data/game_trends.db")
    print("• Nhấn Ctrl+C để dừng máy chủ")
    print("=" * 65)

    # Automatically launch browser in a thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI server
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
