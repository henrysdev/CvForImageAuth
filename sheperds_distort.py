import numpy as np
import cv2
import random
import hashlib
from os import listdir
from os.path import isfile, join
import sys
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


def shift_row(img, factor, row_num, tile_size):
    row = img[row_num*tile_size:row_num*tile_size + tile_size, :]
    row = np.roll(row, factor)
    img[row_num*tile_size:row_num*tile_size + tile_size, :] = row
    row = np.roll(row, factor)
    return img


def shift_col(img, factor, col_num, tile_size):
    col = img[:, col_num*tile_size:col_num*tile_size + tile_size]
    col = np.roll(col, factor)
    img[:, col_num*tile_size:col_num*tile_size + tile_size] = col
    return img


def hash_to_iv(digest):
    l = len(digest[:KEY_SIZE])
    iv = np.ones((l))
    for i in range(l):
        iv[i] = ord(digest[i])

    print("iv: {}".format(iv))
    return iv


def shuffle(img):
    print("Enter Encryption Password (dont forget it!)")
    pword = input("> ")
    m = hashlib.sha256(bytearray(pword.encode('utf-8')))

    pword_hash = m.hexdigest()
    print(pword_hash)
    iv = hash_to_iv(pword_hash)

    random.seed(pword_hash)
    i = 0
    #sign = -1
    for t in range(TRANSFORMS):
        tile_size = random.choice(TILE_SIZES)
        shft_amt = int(iv[i] * t)
        if iv[i] % 2:
            img = shift_col(img, shft_amt, i, tile_size)
        else:
            img = shift_row(img, shft_amt, i, tile_size)
        print("tile_size: {}\nshft_amt: {}\n".format(tile_size, shft_amt))
        i+=1
        if i == iv.shape[0]:
            i = 0
        #show(img)
    return img


def mock_shuffle(img, pword):
    moves = []
    m = hashlib.sha256(bytearray(pword.encode('utf-8')))
    pword_hash = m.hexdigest()
    iv = hash_to_iv(pword_hash)

    random.seed(pword_hash)
    i = 0

    for t in range(TRANSFORMS):
        tile_size = random.choice(TILE_SIZES)
        shft_amt = int(iv[i] * t)# * sign**t)
        if iv[i] % 2:
            moves.append((i, 'col', tile_size, shft_amt))
        else:
            moves.append((i, 'row', tile_size, shft_amt))
        print("tile_size: {}\nshft_amt: {}\n".format(tile_size, shft_amt))
        i+=1
        if i == iv.shape[0]:
            i = 0
    return moves


def unshuffle(cimg):
    img = cimg.copy()
    print("Enter Decryption Password")
    pword = input("> ")
    m = hashlib.sha256(bytearray(pword.encode('utf-8')))

    pword_hash = m.hexdigest()
    print(pword_hash)
    iv = hash_to_iv(pword_hash)

    moves = mock_shuffle(img, pword)
    moves = moves[::-1]
    print(moves)

    for t in range(len(moves)):
        tile_size = moves[t][2]
        shft_amt = moves[t][3]
        i = moves[t][0]
        if moves[t][1] == 'col':
            img = shift_col(img, -shft_amt, i, tile_size)
        elif moves[t][1] == 'row':
            img = shift_row(img, -shft_amt, i , tile_size)
    return img


def decrypt_flow(img, filepath):  
    unshuff = unshuffle(img)
    show(unshuff)
    print("Save image? (y/n)")
    ifsave = input("> ")
    if ifsave.lower() == 'y':
        cv2.imwrite(filepath,unshuff)


def encrypt_flow(img, filepath):
    shuff = shuffle(img)
    show(shuff)
    print("Save image? (y/n)")
    ifsave = input("> ")
    if ifsave.lower() == 'y':
        cv2.imwrite(filepath,shuff)


def parse_args(args):
    argc = len(args)
    print(argc)
    print(args)
    if argc == 3:
        action = args[1]
        filepath = args[2]
        if action == "-E":
            if isfile(filepath):
                print("encrypting file")
                img = cv2.imread(filepath)
                encrypt_flow(img, filepath)
            else:
                print("not a file")
        if action == "-D":
            if isfile(filepath):
                print("decrypting file")
                img = cv2.imread(filepath)
                decrypt_flow(img, filepath)
            else:
                print("not a file")
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
