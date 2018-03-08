import cv2
import numpy as np

BORDER_WIDTH = 30

def add_border(img):
    new_img = np.array(img.shape[0] + BORDER_WIDTH, 
                       img.shape[0] + BORDER_WIDTH)
    print(new_img.shape)
    print(img.shape)
    tl = img[0,0]
    tr = img[0,511]
    br = img[511,511]
    bl = img[511,0]


if __name__ == "__main__":
    img = cv2.imread('test_files/words/words.png')
    add_border(img)