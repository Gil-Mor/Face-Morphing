#!/bin/bash

set -ex

# Name of image file from myimages/aligned_images. Run ./align-images.sh first if needed.
img1=$1
img2=$2

# python3 code/__init__.py --img1 myimages/aligned_images/me-run-snow_01.png --img2 myimages/aligned_images/Paul_Rudd_LF_01.png -imout myresults/alpha-average --frame 10 --duration 1 -ab "average"

# python3 code/__init__.py --img1 myimages/aligned_images/me-run-snow_01.png --img2 myimages/aligned_images/Paul_Rudd_LF_01.png -imout myresults/alpha-transition-me-to-rudd --frame 10 --duration 1 -ab "transition" --match-histograms

# python3 code/__init__.py --img2 myimages/aligned_images/me-run-snow_01.png --img1 myimages/aligned_images/Paul_Rudd_LF_01.png -imout myresults/alpha-transition-rudd-to-me --frame 10 --duration 1 -ab "transition" --match-histograms

python3 code/__init__.py --img2 myimages/aligned_images/me-run-snow-crop-trans_01.png --img1 myimages/aligned_images/Paul_Rudd_LF_01-crop-trans_01.png -imout myresults/alpha-transition-rudd-to-me-crop-trans --frame 10 --duration 1 -ab "transition" --match-histograms
