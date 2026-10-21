import os
import csv
import json
from pathlib import Path

def _atomic_write(path, write_fn, newline=None):
    """Write to a temp file next to path, then swap it in so path is never left half-written."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(tmp, "w", newline=newline, encoding="utf-8") as f:
            write_fn(f)
        os.replace(tmp, path)  # atomic on the same filesystem
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise

def atomic_write_csv(path, header, rows):
    def write(f):
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    _atomic_write(path, write, newline="")

def atomic_write_json(path, data, indent=2):
    _atomic_write(path, lambda f: json.dump(data, f, indent=indent))
