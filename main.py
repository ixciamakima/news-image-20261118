#!/usr/bin/env python3
"""Entry for news-image-20261118: 'The World in One Day'.

Copies the pre-rendered front page (entry.png, produced by render.py
with Pillow at build time) into the output directory as entry.png.
Stdlib only, no network, deterministic: the output is byte-identical
to the bundled PNG on every run.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        raise SystemExit("entry.png missing next to main.py")
    if len(sys.argv) > 1:
        out_dir = sys.argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        out_dir = os.environ["MAKEFUN_OUTPUT_DIR"]
    else:
        out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)


if __name__ == "__main__":
    main()
