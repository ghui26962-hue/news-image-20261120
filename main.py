"""Entry point: copy the pre-rendered front page to the output directory.

Standard library only, so it runs in the grader's no-network sandbox.
The image itself is drawn by render.py (Pillow, run locally); this file
just places its bytes at $MAKEFUN_OUTPUT_DIR/entry.png, default /output.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT = OUT_DIR / "entry.png"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, OUT)


if __name__ == "__main__":
    main()
