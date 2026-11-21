#!/usr/bin/env python3
"""Copy the pre-rendered entry.png into the output directory.

Standard library only. No network, no image work: the image is drawn
by render_image.py at build time and shipped as entry.png.
"""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(outdir):
        outdir = os.path.join(os.getcwd())
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
