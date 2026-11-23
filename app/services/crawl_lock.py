"""Cross-process crawl lock (lock file), so the web server and the scheduled
Windows task never crawl at the same time."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from app import config

# A lock older than this is assumed to belong to a crashed process
STALE_AFTER_SECONDS = 2 * 60 * 60


def lock_path() -> Path:
    return Path(config.DATA_DIR) / "crawl.lock"


def _read() -> Optional[dict]:
    try:
        return json.loads(lock_path().read_text(encoding="utf-8"))
    except Exception:
        return None


def is_locked() -> bool:
    p = lock_path()
    if not p.exists():
        return False
    try:
        age = time.time() - p.stat().st_mtime
    except OSError:
        return False
    return age < STALE_AFTER_SECONDS


def acquire(owner: str) -> bool:
    """Creates the lock file atomically. Returns False if another live process holds it."""
    p = lock_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not is_locked():
        try:
            p.unlink()  # stale lock from a crashed run
        except OSError:
            return False
    try:
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"owner": owner, "pid": os.getpid(), "since": datetime.now().isoformat(timespec="seconds")}, f)
    return True


def release() -> None:
    info = _read()
    if info and info.get("pid") not in (None, os.getpid()):
        return  # not ours
    try:
        lock_path().unlink()
    except FileNotFoundError:
        pass


def holder() -> Optional[dict]:
    return _read() if is_locked() else None
