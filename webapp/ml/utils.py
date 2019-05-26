import os, mimetypes

import cv2
import numpy as np
from werkzeug.utils import secure_filename


class Utils:
    @staticmethod
    def remove_file_ext(filename):
        """
        Get the filename without extension
        """
        pp_filename = secure_filename(filename)
        splitted_pp_filename = os.path.splitext(pp_filename)
        return splitted_pp_filename[0]

    @staticmethod
    def mimetype2ext(mimetype):
        ext = mimetypes.guess_extension(mimetype)
        # Switch to .jpg since it is more common
        if ext == ".jpe":
            ext = ".jpg"
        return ext

    @staticmethod
    def photo2tactile(binary_data, file_ext):
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

        Based on fine-grained saliency detection from Sebastian Montabone and Alvaro Soto. Human detection using a mobile platform and novel features derived from a visual saliency mechanism. In Image and Vision Computing, Vol. 28 Issue 3, pages 391–402. Elsevier, 2010.
        Source: https://docs.opencv.org/3.4.3/da/dd0/classcv_1_1saliency_1_1StaticSaliencyFineGrained.html
        """
        # Convert binary to numpy array
        nparr_data = np.fromstring(binary_data, np.uint8)
        # Convert numpy array to image
        image = cv2.imdecode(nparr_data, cv2.IMREAD_COLOR)

        # Read image, grayscale, equalize
        # Source: https://docs.opencv.org/3.4.3/d4/d1b/tutorial_histogram_equalization.html
        image_grayscaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_equalized = cv2.equalizeHist(image_grayscaled)

        fine_saliency = cv2.saliency.StaticSaliencyFineGrained_create()
        _, fine_saliency_map = fine_saliency.computeSaliency(image_equalized)

        # Scale the values to [0, 255]
        fine_saliency_map = (fine_saliency_map * 255).astype('uint8')

        # Compute binary threshold map
        threshold_map = cv2.threshold(
            fine_saliency_map.astype('uint8'), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Invert the binary threshold map so it is Swell Paper Tactile Printer friendly
        inverse_threshold_map = cv2.bitwise_not(threshold_map)

        # Convert numpy array to binary
        # https://stackoverflow.com/questions/50630045/how-to-turn-numpy-array-image-to-bytes
        _, encoded_image = cv2.imencode(file_ext, inverse_threshold_map)
        inverse_threshold_map_binary = encoded_image.tobytes()
        return inverse_threshold_map_binary
