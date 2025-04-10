""" TRAIN/TEST """
""" This script should:
    - Be used for training and finetuning models during development.
    - Be used for evaluating AI models alone.
    - Be used testing new techniques in regards to the AI models.
    - Be used for testing various things that need testing."""

import store
from PIL import Image

# ===================== SETUP =====================

def test_gps_tag():
    test_image = Image.open("data/test.jpg")

    saved = store.tag_and_store(test_image)

    check_image = Image.open(saved)
    print(check_image.getexif())

# ===================== TRAIN =====================





# ===================== EVALUATION =====================


#test_gps_tag()

