#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered entry.png to the output directory.

Standard library only. No network. Deterministic: the output is a
byte-for-byte copy of entry.png, so two runs produce identical output.
"""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out):
        out = "."
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    h = hashlib.sha256()
    with open(dst, "rb") as f:
        h.update(f.read())
    print(h.hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
