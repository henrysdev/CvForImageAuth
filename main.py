import numpy as np
import cv2
import random
import hashlib
from os import listdir
from os.path import isfile, join
import sys
import shuffle as shuff_algo
import find_and_warp as detecter
import format_for_publish as publish

KEY_SIZE = 16
TRANSFORMS = 500 #45
TILE_SIZES = [16, 32, 64, 128]
FILE_EXTENSIONS = [".png",".jpg", ".JPG", ".PNG"]
BORDER_WIDTH = 30
# DEBUG
TEST_DIR = 'test_files'


def show(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def decrypt_flow(img, filepath, keypass):  
    unshuff = shuff_algo.unshuffle(img, keypass)
    show(unshuff)
    print("Save image? (y/n)")
    ifsave = input("> ")
    if ifsave.lower() == 'y':
        cv2.imwrite(filepath,unshuff)


def encrypt_flow(img, filepath, keypass):
    shuff = shuff_algo.shuffle(img, keypass)
    show(shuff)
    print("Save image? (y/n)")
    ifsave = input("> ")
    if ifsave.lower() == 'y':
        cv2.imwrite(filepath,shuff)


def parse_args(args):
    argc = len(args)
    # in-place transforms (no edge detection)
    if argc == 4:
        action = args[1]
        filepath = args[2]
        keypass = args[3]
        # encryption
        if action.lower() in ["e", "enc", "encrypt"]:
            if isfile(filepath):
                print("encrypting file")
                img = cv2.imread(filepath)
                encrypt_flow(img, filepath, keypass)
            else:
                print("not a file")
        # decryption
        elif action.lower() in ["d", "dec", "decrypt"]:
                if isfile(filepath):
                    print("decrypting file")
                    img = cv2.imread(filepath)
                    decrypt_flow(img, filepath, keypass)
                else:
                    print("not a file")
    # edge detection followed by decryption
    elif argc == 2:
        filepath = args[1]
        if isfile(filepath):
            print("finding and decrypting img")
            img = cv2.imread(filepath)
            show(img)
            img = detecter.process(img)
            show(img)
            decrypt_flow(img, filepath)
        else:
            print("not a file")
    else:
        print("Exiting")


if __name__ == "__main__":
    parse_args(sys.argv)