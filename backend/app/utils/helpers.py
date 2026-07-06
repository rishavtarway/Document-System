from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_file_size(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"


def safe_filename(filename: str) -> str:
    import re
    return re.sub(r"[^\w\-_. ]", "_", filename)


def truncate_text(text: str, max_length: int = 2000) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
