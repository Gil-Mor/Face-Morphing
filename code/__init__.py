from face_landmark_detection import generate_face_correspondences
from delaunay_triangulation import make_delaunay
from face_morph import generate_morph_sequence

import subprocess
import argparse
import shutil
import os
import cv2

def doMorphing(img1, img2, duration, frame_rate, draw_triangles, alpha_blend_method, match_histograms, intermediate_output, video_output):

	[size, img1, img2, points1, points2, list3] = generate_face_correspondences(img1, img2)

	tri = make_delaunay(size[1], size[0], list3, img1, img2)

	generate_morph_sequence(duration, frame_rate, img1, img2, points1, points2, tri, size, draw_triangles, alpha_blend_method, match_histograms, intermediate_output, video_output)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("--img1", required=True, help="The First Image")
	parser.add_argument("--img2", required=True, help="The Second Image")
	parser.add_argument("--duration", type=int, default=5, help="The duration")
	parser.add_argument("--frame", type=int, default=20, help="The frameame Rate")
	parser.add_argument("-triangles", "--draw-triangles", action="store_true", help="Whether to draw the triangulation in the output images.")
	parser.add_argument("-ab", "--alpha-blend-method", choices=['transition', 'average'], help="Method to alpha blend the 2 images. How to swap colors.", default="transition")
	parser.add_argument("-histo", "--match-histograms", action='store_true', help="If True Each frame histogram will be matched to that of the 'target' image (img2). That can make face swapping easier color-wise.")
	parser.add_argument("-imout", "--intermediate-output", type=str, help="A path to save intermediate images as jpeg images. Each frame will be saved as <intermediate-output>_<frame number>. If this argument isn't given then intermediate images won't be saved.")
	parser.add_argument("--video-output", type=str, help="Output Video Path. If not given a video won't be saved.")
	args = parser.parse_args()

	image1 = cv2.imread(args.img1)
	image2 = cv2.imread(args.img2)

	doMorphing(image1, image2, args.duration, args.frame, args.draw_triangles, args.alpha_blend_method, args.match_histograms, args.intermediate_output, args.video_output)
	