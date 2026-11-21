#!/usr/bin/env python3
"""Entrypoint for the 21 November 2026 news-image bounty.

Copies the pre-rendered entry.png into the grader's output
directory and prints its sha256. Standard library only, no
network, fully deterministic.
"""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        out_dir = "."
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    digest = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    print("entry.png sha256: " + digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
