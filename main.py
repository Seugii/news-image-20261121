#!/usr/bin/env python3
"""Copy the pre-rendered entry.png to the output directory (stdlib only)."""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "."
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    digest = hashlib.sha256()
    with open(dst, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    print(digest.hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
