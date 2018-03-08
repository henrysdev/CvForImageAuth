import numpy as np
import cv2
from matplotlib import pyplot as plt


def show(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def process(img):
    ratio = (img.shape[0]/512, img.shape[1]/512)
    orig = img.copy()
    img = cv2.resize(img, (512,512))

    img2 = cv2.blur(img,(2,2))
    show(img2)

    # Initiate FAST object with default values
    fast = cv2.FastFeatureDetector_create(threshold=50)

    # find and draw the keypoints
    kp = fast.detect(img2,None)

    img2 = cv2.drawKeypoints(img2, kp, None,color=(0,255,0))
    show(img2)
    kps = np.ones((len(kp),2))
    
    for x in range(len(kp)):
        kps[x,0] = kp[x].pt[0]
        kps[x,1] = kp[x].pt[1]

    s = kps.sum(axis=1)

    #top left
    tl = kps[np.argmin(s)]
    tl[0] *= ratio[0]
    tl[1] *= ratio[1]

    #bottom right
    br = kps[np.argmax(s)]
    br[0] *= ratio[0]
    br[1] *= ratio[1]

    diff = np.diff(kps, axis=1)
    #top right
    tr = kps[np.argmin(diff)]
    tr[0] *= ratio[0]
    tr[1] *= ratio[1]
    
    #bottom left
    bl = kps[np.argmax(diff)]
    bl[0] *= ratio[0]
    bl[1] *= ratio[1]

    rect = np.array([
        [tl,tr,br,bl]], dtype = "float32")

    # now that we have our rectangle of points, let's compute
    # the width of our new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    print("widthA: {}".format(widthA))
     
    # ...and now for the height of our new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
     
    # take the maximum of the width and height values to reach
    # our final dimensions
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
     
    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
     
    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))
    show(warp)
    resized_image = cv2.resize(warp, (512, 512)) 
    show(resized_image)
    return resized_image


def take_picture():
    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        cv2.imshow('frame', rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            out = cv2.imwrite('capture.jpg', frame)
            break

    cap.release()
    cv2.destroyAllWindows()

