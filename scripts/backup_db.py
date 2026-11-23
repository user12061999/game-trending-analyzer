"""Back up the SQLite database to data/backups/ and keep the newest N copies.

Uses SQLite's online backup API, so it is safe to run while the app is crawling.
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import config  # noqa: E402


def backup(keep: int = 8, backup_dir: Path = None) -> Path:
    src_path = Path(config.DB_PATH)
    if not src_path.exists():
        raise FileNotFoundError(f"Database not found: {src_path}")
    backup_dir = Path(backup_dir or (Path(config.DATA_DIR) / "backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest_path = backup_dir / f"{src_path.stem}_{datetime.now():%Y-%m-%d_%H%M%S}.db"

    src = sqlite3.connect(src_path)
    dest = sqlite3.connect(dest_path)
    try:
        src.backup(dest)
        ok = dest.execute("PRAGMA integrity_check").fetchone()[0]
        if ok != "ok":
            raise RuntimeError(f"Backup integrity check failed: {ok}")
    finally:
        dest.close()
        src.close()

    copies = sorted(backup_dir.glob(f"{src_path.stem}_*.db"))
    for old in copies[:-keep] if keep > 0 else []:
        old.unlink()
    return dest_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Back up the market database.")
    parser.add_argument("--keep", type=int, default=8, help="Number of backups to keep (default 8)")
    args = parser.parse_args(argv)
    try:
        path = backup(keep=args.keep)
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr if sys.stderr else None)
        return 1
    if sys.stdout is not None:
        print(f"Backup written: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
