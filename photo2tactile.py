"""
Convert scenery image to tactile image.

# Algorithm
1. Read scenery image.
2. Grayscale.
3. Histogram equalize.
4. Compute fine-grained saliency map.
5. Scale to [0, 255]
6. Compute binary threshold map.
7. Invert binary threshold map.
8. Write tactile image.

References at the corresponding source code below.
"""
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument('-s', '--show', required=False, action='store_true', help='Show output')
ap.add_argument('-f', '--fine', required=False, action='store_true', help='Fine-grained salient only mode')
ap.add_argument('-i', '--image', required=True, help='Input: image file path')
ap.add_argument('-o', '--output', required=False, help='Output: tactile image file path')
args = ap.parse_args()

# Read image, grayscale, equalize
# Source: https://docs.opencv.org/3.4.3/d4/d1b/tutorial_histogram_equalization.html
image = cv2.imread(args.image)
image_grayscaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image_equalized = cv2.equalizeHist(image_grayscaled)

"""
Fine-grained saliency detection from
Sebastian Montabone and Alvaro Soto.
Human detection using a mobile platform and novel features derived from a visual saliency mechanism.
In Image and Vision Computing, Vol. 28 Issue 3, pages 391–402. Elsevier, 2010.
Source: https://docs.opencv.org/3.4.3/da/dd0/classcv_1_1saliency_1_1StaticSaliencyFineGrained.html
"""
fine_saliency = cv2.saliency.StaticSaliencyFineGrained_create()
_, fine_saliency_map = fine_saliency.computeSaliency(image_equalized)

# Scale the values to [0, 255]
fine_saliency_map = (fine_saliency_map * 255).astype('uint8')

# Compute binary threshold map
threshold_map = cv2.threshold(
    fine_saliency_map.astype('uint8'), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Invert the binary threshold map so it is Swell Paper Tactile Printer friendly
inverse_threshold_map = cv2.bitwise_not(threshold_map)

if args.fine:
    selected_map = fine_saliency_map
else:
    selected_map = inverse_threshold_map

# Save output
cv2.imwrite(args.output, selected_map)

if args.show:
    # Show output
    cv2.imshow('Inverse Threshold Map', selected_map)

    # Press any key to exit
    cv2.waitKey(0)