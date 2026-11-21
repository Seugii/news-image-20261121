# main.py — entrypoint for make.fun news-image-20261121 (round 3).
# Standard library only. Copies the pre-rendered entry.png into the
# grader's output directory and prints its sha256. Deterministic: the
# same bytes are written on every run.
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(outdir):
        outdir = os.getcwd()
    dest = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dest)
    digest = hashlib.sha256(open(dest, "rb").read()).hexdigest()
    print("entry.png sha256 %s" % digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
