#!/bin/bash

set -ex

img=$1
ref_img=$2
out=$3

python3 code/utils/match_histograms.py -i $img -r $ref_img -o $out