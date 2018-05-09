import numpy as np
import cv2
import random
import hashlib
import math

KEY_SIZE = 16
TRANSFORMS = 500
BORDER_WIDTH = 30


def show(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def power_two(n):
    try:
        return int(math.log(n, 2))
    except:
        return 0


def shift_row(img, factor, row_num, tile_size):
    row = img[row_num:row_num + tile_size, :]
    row = np.roll(row, factor)
    img[row_num:row_num + tile_size, :] = row
    return img


def shift_col(img, factor, col_num, tile_size):
    col = img[:, col_num:col_num + tile_size]
    col = np.roll(col, factor)
    img[:, col_num:col_num + tile_size] = col
    return img


def hash_to_iv(digest):
    l = len(digest[:KEY_SIZE])
    iv = np.ones((l))
    for i in range(l):
        iv[i] = ord(digest[i])
    return iv


def shuffle(img, keypass):
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    keypass_hash = m.hexdigest()
    iv = hash_to_iv(keypass_hash)
    random.seed(keypass_hash)

    width, height = img.shape[0], img.shape[1]
    axis = width
    
    i = 0
    for t in range(TRANSFORMS):
        shft_amt = random.randint(-8989898,8989898)
        if iv[i] % 2 == 0:
            axis = width
        else:
            axis = height
        targ_row = random.randint(0, axis)
        avail_tiles = [2 ** power_two(abs(axis - targ_row))]
        if len(avail_tiles) > 0:
            tile_size = random.choice(avail_tiles)
            if axis == width:
                print("width, targ_row: ", targ_row, "tile_size: ", tile_size, "shft_amt: ", shft_amt)
                tile_size = random.choice(avail_tiles)
                img = shift_col(img, shft_amt, targ_row, tile_size)
            elif axis == height:
                print("height, targ_row: ", targ_row, "tile_size: ", tile_size, "shft_amt: ", shft_amt)
                tile_size = random.choice(avail_tiles)
                img = shift_row(img, shft_amt, targ_row, tile_size)
        i += 1
        if i == iv.shape[0]:
            i = 0
        #show(img)
    return img


def mock_shuffle(img, keypass):
    moves = []
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    keypass_hash = m.hexdigest()
    iv = hash_to_iv(keypass_hash)
    random.seed(keypass_hash)

    width, height = img.shape[0], img.shape[1]
    axis = width

    i = 0
    for t in range(TRANSFORMS):
        shft_amt = random.randint(-8989898,8989898)
        if iv[i] % 2 == 0:
            axis = width
        else:
            axis = height
        targ_row = random.randint(0, axis)
        avail_tiles = [2 ** power_two(abs(axis - targ_row))]
        if len(avail_tiles) > 0:
            tile_size = random.choice(avail_tiles)
            if axis == width:
                tile_size = random.choice(avail_tiles)
                moves.append((targ_row, 'col', tile_size, shft_amt))
            elif axis == height:
                tile_size = random.choice(avail_tiles)
                moves.append((targ_row, 'row', tile_size, shft_amt))
        i += 1
        if i == iv.shape[0]:
            i = 0
    return moves


def unshuffle(cimg, keypass):
    img = cimg.copy()
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    keypass_hash = m.hexdigest()
    iv = hash_to_iv(keypass_hash)

    moves = mock_shuffle(img, keypass)
    moves = moves[::-1]

    for t in range(len(moves)):
        tile_size = moves[t][2]
        shft_amt = moves[t][3]
        i = moves[t][0]
        if moves[t][1] == 'col':
            img = shift_col(img, -shft_amt, i, tile_size)
        elif moves[t][1] == 'row':
            img = shift_row(img, -shft_amt, i , tile_size)
    return img
