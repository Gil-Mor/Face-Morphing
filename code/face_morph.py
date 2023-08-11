import numpy as np
import cv2
import sys
import os
import math
from subprocess import Popen, PIPE
from PIL import Image
# from skimage import exposure
# from skimage.transform import match_histograms
from skimage import exposure
from skimage.exposure import match_histograms

# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def apply_affine_transform(src, srcTri, dstTri, size) :
    
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform(np.float32(srcTri), np.float32(dstTri))
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

    return dst


# Warps and alpha blends triangular regions from img1 and img2 to img
def morph_triangle(img1, img2, img, t1, t2, t, alpha) :

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))
    r = cv2.boundingRect(np.float32([t]))

    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    tRect = []

    for i in range(0, 3):
        tRect.append(((t[i][0] - r[0]),(t[i][1] - r[1])))
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))

    # Get mask by filling triangle
    mask = np.zeros((r[3], r[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(tRect), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    img2Rect = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]]

    size = (r[2], r[3])
    warpImage1 = apply_affine_transform(img1Rect, t1Rect, tRect, size)
    warpImage2 = apply_affine_transform(img2Rect, t2Rect, tRect, size)

    # Alpha blend rectangular patches
    imgRect = (1.0 - alpha) * warpImage1 + alpha * warpImage2

    # Copy triangular region of the rectangular patch to the output image
    img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] = img[r[1]:r[1]+r[3], r[0]:r[0]+r[2]] * ( 1 - mask ) + imgRect * mask


def generate_morph_sequence(duration,frame_rate,img1,img2,points1,points2,tri_list,size,draw_triangles, alpha_blend_method, match_histogram, intermediate_output, video_output):

    num_images = int(duration*frame_rate)
    if video_output:
        os.makedirs(os.path.dirname(video_output), exist_ok=True)
        p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-r', str(frame_rate),'-s',str(size[1])+'x'+str(size[0]), '-i', '-', '-c:v', 'libx264', '-crf', '25','-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2','-pix_fmt','yuv420p', video_output], stdin=PIPE)

    for j in range(0, num_images):

        # Convert Mat to float data type
        img1 = np.float32(img1)
        img2 = np.float32(img2)

        # Read array of corresponding points
        points = []
        if alpha_blend_method == 'transition':
            # This will gradually transition ito the colors of the 2nd image.
            alpha = j/(num_images-1)
        elif alpha_blend_method == 'average':
            # This will equalize colors in the same amount for all frames.
            alpha = 0.5

        # Compute weighted average point coordinates
        for i in range(0, len(points1)):
            # alpha needs to be weights otherwise all images are the same.
            weighted_alpha = j/(num_images-1)
            x = (1 - weighted_alpha) * points1[i][0] + weighted_alpha * points2[i][0]
            y = (1 - weighted_alpha) * points1[i][1] + weighted_alpha * points2[i][1]
            points.append((x,y))
        
        # Allocate space for final output
        morphed_frame = np.zeros(img1.shape, dtype = img1.dtype)

        for i in range(len(tri_list)):    
            x = int(tri_list[i][0])
            y = int(tri_list[i][1])
            z = int(tri_list[i][2])
            
            t1 = [points1[x], points1[y], points1[z]]
            t2 = [points2[x], points2[y], points2[z]]
            t = [points[x], points[y], points[z]]

            # Morph one triangle at a time.
            morph_triangle(img1, img2, morphed_frame, t1, t2, t, alpha)

            if draw_triangles:
                pt1 = (int(t[0][0]), int(t[0][1]))
                pt2 = (int(t[1][0]), int(t[1][1]))
                pt3 = (int(t[2][0]), int(t[2][1]))

                cv2.line(morphed_frame, pt1, pt2, (255, 255, 255), 1, 8, 0)
                cv2.line(morphed_frame, pt2, pt3, (255, 255, 255), 1, 8, 0)
                cv2.line(morphed_frame, pt3, pt1, (255, 255, 255), 1, 8, 0)

        if match_histogram:
            morphed_frame = match_histograms(morphed_frame, img2, channel_axis=-1)

        res = Image.fromarray(cv2.cvtColor(np.uint8(morphed_frame), cv2.COLOR_BGR2RGB))

        if video_output:
            res.save(p.stdin,'JPEG')

        if intermediate_output:
            os.makedirs(intermediate_output, exist_ok=True)
            res.save(f"{intermediate_output}/{j}.jpeg")

    if intermediate_output and match_histogram:
        # save histogram matched version for face swapping with more matching colors
        histo = match_histograms(img1, img2, channel_axis=-1)
        res = Image.fromarray(cv2.cvtColor(np.uint8(histo), cv2.COLOR_BGR2RGB))
        res.save(f"{intermediate_output}/matched_histograms_1_by_2.jpeg")
        histo = match_histograms(img2, img1, channel_axis=-1)
        res = Image.fromarray(cv2.cvtColor(np.uint8(histo), cv2.COLOR_BGR2RGB))
        res.save(f"{intermediate_output}/matched_histograms_2_by_1.jpeg")

    if video_output:
        p.stdin.close()
        p.wait()