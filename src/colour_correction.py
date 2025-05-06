""" COLOUR CORRECTION """
""" 
This script should:
    - Take in video streams or files...
    - Automatically perform colour correction by converting the colour space of the image from BGR to LAB 
"""


import cv2

def colour_convert(image):

    image = cv2.imread(image)
    # converts from BGR colour space to LAB colour space
    imagelab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # splits image into 3
    l, a, b = cv2.split(imagelab)

    # performs histogram equalisation on the L channel image referring to light
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2,2))
    l = clahe.apply(l)

    # merges images back together
    imagelab = cv2.merge((l,a,b))

    # converts LAB image back to BGR image
    output = cv2.cvtColor(imagelab, cv2.COLOR_Lab2BGR)

    return output

# image = "data/test4.jpg"
# cv2.imshow('test',colour_convert(image))
# cv2.waitKey(0)
