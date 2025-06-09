""" COLOUR CORRECTION
This script should:
    - Take in video streams or files...
    - Automatically perform colour correction by converting the colour space of the image from BGR to LAB 
"""


import cv2
import numpy as np

def colour_convert(image):

    # creates numpy array to display LAB values
    mean_sum = np.array([0.,0.,0.])


    # only used when testing
    # image = cv2.imread(image)

    # converts from BGR colour space to LAB colour space
    imagelab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # calculates mean LAB value of image
    # the first one (Lightness) is most important, other 2 unnecessary
    mean, std = cv2.meanStdDev(imagelab)
    mean_sum += np.squeeze(mean)
    print(mean_sum)

    # if lightness is below a certain threshold, performs the colour correction
    if mean_sum[0] < 85: 
        # splits image into 3
        l, a, b = cv2.split(imagelab)

        # performs histogram equalisation on the L channel image referring to light
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2,2))
        l = clahe.apply(l)

        
        # merges images back together
        imagelab = cv2.merge((l,a,b))

        mean_sum = np.array([0.,0.,0.])
        mean, std = cv2.meanStdDev(imagelab)
        mean_sum += np.squeeze(mean)
        print(mean_sum)
    

    
    # converts LAB image back to BGR image
    output = cv2.cvtColor(imagelab, cv2.COLOR_Lab2BGR)

    return output