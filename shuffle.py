import numpy as np
import cv2
import random
import hashlib
import math

KEY_SIZE = 16
TRANSFORMS = 500
BORDER_WIDTH = 30


"""
def show(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""


def power_two(n):
    """ determine the greatest power of 2 less than n """

    try:
        return int(math.log(n, 2))
    except:
        return 0


def shift_row(img, factor, row_num, tile_size):
    """ shift a row of image pixels of width tile_size horizontally """

    row = img[row_num:row_num + tile_size, :]
    row = np.roll(row, factor)
    img[row_num:row_num + tile_size, :] = row
    return img


def shift_col(img, factor, col_num, tile_size):
    """ shift a column of image pixels of width tile_size vertically """

    col = img[:, col_num:col_num + tile_size]
    col = np.roll(col, factor)
    img[:, col_num:col_num + tile_size] = col
    return img


def shuffle(img, keypass):
    """ core shuffle algorithm that relies on largest power of 2 to shift """

    # take the sha256 hash of the image password passed to the function
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    # cast the sha256 to alphanumeric characters
    keypass_hash = m.hexdigest()
    # random seed derived from value of hash
    random.seed(keypass_hash)
    # map alphanumeric chars to numpy array of integers corresponding to
    # their respective ASCII values
    iv = np.asarray(list(map(lambda x: ord(x), digest)))
    width, height = img.shape[0], img.shape[1]
    axis = width
    # i represents the current position in the iv array
    i = 0
    # loop through transform operations
    for t in range(TRANSFORMS):
        # determine an amount to shift a row/column by
        shft_amt = random.randint(-8989898,8989898)
        # determine whether to shift a row or column by the parity
        # of the value of the current value in the iv array
        if iv[i] % 2 == 0:
            axis = width
        else:
            axis = height
        # determine a target row/column to shift within bounds """
        targ_row = random.randint(0, axis)
        # determine the largest power of two less than the pos of the 
        # target row. This will be the width of the row/column to be
        # shifted
        tile_size = 2 ** power_two(abs(axis - targ_row))
        if tile_size:
            # shift a row/column of specified width at a specified position
            # a specified amount and update the matrix
            if axis == width:
                img = shift_col(img, shft_amt, targ_row, tile_size)
            elif axis == height:
                img = shift_row(img, shft_amt, targ_row, tile_size)
        # increment the current pos of iv being inspected. If i reaches
        # the end of the iv, start it back at zero.
        i += 1
        if i == iv.shape[0]:
            i = 0
        #show(img)
    return img


def mock_shuffle(img, keypass):
    """ dummy shuffle that keeps track of moves for backtracking """

    moves = []
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    keypass_hash = m.hexdigest()
    random.seed(keypass_hash)
    iv = np.asarray(list(map(lambda x: ord(x), digest)))
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
        tile_size = 2 ** power_two(abs(axis - targ_row))
        if tile_size:
            if axis == width:
                moves.append((targ_row, 'col', tile_size, shft_amt))
            elif axis == height:
                moves.append((targ_row, 'row', tile_size, shft_amt))
        i += 1
        if i == iv.shape[0]:
            i = 0
    return moves


def unshuffle(cimg, keypass):
    """ unshuffle by repeating the shuffle moves backwards """

    img = cimg.copy()
    m = hashlib.sha256(bytearray(keypass.encode('utf-8')))
    keypass_hash = m.hexdigest()
    moves = mock_shuffle(img, keypass)
    # reverse moves list
    moves = moves[::-1]
    # apply inverse operations of shuffle algo to effectively
    # unshuffle the image
    for t in range(len(moves)):
        tile_size = moves[t][2]
        shft_amt = moves[t][3]
        i = moves[t][0]
        if moves[t][1] == 'col':
            img = shift_col(img, -shft_amt, i, tile_size)
        elif moves[t][1] == 'row':
            img = shift_row(img, -shft_amt, i , tile_size)
    return img
