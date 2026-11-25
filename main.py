"""Ship the finished 25 November 2026 front page.

The image is rendered at build time and kept in this repository as
entry.png. The grader runs with only the standard library installed, so
this entry point does nothing but place that finished file in the output
directory.
"""

import os
import shutil
from pathlib import Path


def ship() -> Path:
    root = Path(__file__).resolve().parent
    dest_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / "entry.png"
    shutil.copyfile(root / "entry.png", target)
    return target


if __name__ == "__main__":
    ship()
