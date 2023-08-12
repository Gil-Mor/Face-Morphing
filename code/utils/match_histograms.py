import argparse
import cv2
from PIL import Image
import numpy as np
from skimage import exposure

def match_histograms(img, ref_img):
    return exposure.match_histograms(img, ref_img, channel_axis=-1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--img", required=True, help="The source image")
    parser.add_argument("-r", "--reference-img", required=True, help="The reference image")
    parser.add_argument("-o", "--output", required=True, help="Output image path (.jpeg)")
    args = parser.parse_args()

    img = cv2.imread(args.img)
    ref_img = cv2.imread(args.reference_img)
    histo = match_histograms(img, ref_img)
    res = Image.fromarray(cv2.cvtColor(np.uint8(histo), cv2.COLOR_BGR2RGB))
    res.save(args.output)