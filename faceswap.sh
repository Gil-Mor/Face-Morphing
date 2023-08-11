#!/bin/bash

set -ex

# Name of image file from myresults/ Run code/utils/__init__.py (can be done via run.sh) first to create morph frames. Try to use the --match-histograms to match colors of frames.
src=$1
dst=$2

python3 code/utils/faceswap.py $src $dst