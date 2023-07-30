#!/bin/bash

set -ex

find myimages/ -name "*.webp" -exec [ ! -f {}.jpg ] \; -exec  mv {} {}.jpg \;
find myimages/ -name "*.jp*g" -exec [ ! -f {}.png ] \; -exec mogrify -format png {} \;

python3 code/utils/align_images.py myimages/ myimages/aligned_images/ --output_size=1024
