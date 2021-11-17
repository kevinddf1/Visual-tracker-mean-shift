#!/usr/bin/python
""" Constructs a videocapture device on either webcam or a disk movie file.
Press q to exit

Junaed Sattar
October 2021
"""
from __future__ import division
import multiprocessing as mp
import numpy as np
import cv2
import sys

# Mian steps
# 1. initiate a target region, (targetX, targetY, targetRegionSize)
# 2. press t to toggle tracking
# 3. mean-shift tracker, (target model, mean-shift vector, KL divergence/Bhattacharyya distance)
# 4. continue until user press q to quit

"""--------------------------------------global data common to all vision algorithms---------------------------"""
# bool flags
isTracking = False
showRectangle = False
roiSlecet = False

# iamge info
r = g = b = 0.0
image = np.zeros((640, 480, 3), np.uint8)
imageWidth = imageHeight = 0

# roi info # region of interst
w, h = (
    60,
    40,
)  # roi is a rectangle repsentend by the left corner point(x,y) and width and hight
track_window = (0, 0, w, h)
trackedImage = np.zeros((h, w, 3), np.uint8)

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt
term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)


# parallelizing processing
pool = mp.Pool()

""" -------------------------------------------clickHandler---------------------------------------------"""

# initiate a target region, and build the target model using a histogram as feature
def clickHandler(event, x, y, flags, param):
    global showRectangle, isTracking, roiSlecet, image, track_window, trackedImage
    if event == cv2.EVENT_LBUTTONUP:
        print("left button released at location ", x, y)
        # out of boundary
        if inBoundary(x, y) == False:
            print("invalid click position, try again")
        else:
            # change it to the rectangle left corner point
            x = int(x - w / 2)
            y = int(y - h / 2)
            # edit gobal variables
            showRectangle = True
            isTracking = True
            roiSlecet = True
            track_window = (x, y, w, h)
            trackedImage = image[y : y + h, x : x + w]
            # build histogram
            print("building histogram")
            hsv_roi = cv2.cvtColor(trackedImage, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(
                hsv_roi, np.array((0.0, 60.0, 32.0)), np.array((180.0, 255.0, 255.0))
            )
            roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
            cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
            print(roi_hist)
            print("finished  building histogram")


"""---------------------------------------------doTracking----------------------------------------------"""


def doTracking():
    global isTracking, image, r, g, b
    
    

    # parallel calculating
    def tempFun(j):
        for i in range(imageHeight):
            TuneTracker(j, i)
    tempList = range(imageWidth)
    pool.map_async(tempFun, tempList)


"""--------------------------------------------captureVideo--------------------------------"""
# read input video and setup output window
def captureVideo(src):
    # read input video and setup the output window
    global  isTracking, showRectangle,image, imageHeight, imageWidth
    cap = cv2.VideoCapture(src)
    if cap.isOpened() and src == "0":
        ret = cap.set(3, 640) and cap.set(4, 480)
        if ret == False:
            print("Cannot set frame properties, returning")
            return
    else:
        ret, image = cap.read()
        imageHeight, imageWidth, implanes = image.shape
        frate = cap.get(cv2.CAP_PROP_FPS)
        print(frate, " is the framerate")
        waitTime = int(1000 / frate)

    # waitTime = time/frame. Adjust accordingly.
    if src == 0:
        waitTime = 1
    if cap:
        print("Succesfully set up capture device")
    else:
        print("Failed to setup capture device")

    windowName = "Input View, press q to quit"
    cv2.namedWindow(windowName)
    cv2.setMouseCallback(windowName, clickHandler)

    print("image size is ", image.shape)

    # visual tracer loop
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        if ret == False:
            break

        # make a copy just for later ouput
        imageCopy = image.copy()

        # Display the resulting frame
        if isTracking:
            doTracking()
        if showRectangle:
            drawRectangle(imageCopy)
        cv2.imshow(windowName, imageCopy)
        inputKey = cv2.waitKey(waitTime) & 0xFF

        # user inferface handler
        if inputKey == ord("q"):
            break
        elif inputKey == ord("t"):
            showRectangle = not showRectangle

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


"""----------------------------------------helper funcions--------------------------"""

# test user click position, it can't be at the edge, otherwise our red rectangle will be out of scope
def inBoundary(x, y):
    if (
        x < 0 + w / 2
        or x >= imageWidth - w / 2
        or y < 0 + h / 2
        or y >= imageHeight - h / 2
    ):
        return False
    else:
        return True

# tune the brightness of the image
def TuneTracker(x, y):
    global r, g, b, image
    b, g, r = image[y, x]
    sumpixels = float(b) + float(g) + float(r)
    if sumpixels != 0:
        b = int(b / sumpixels)
        r = int(r / sumpixels)
        g = int(g / sumpixels)
        # print(r, g, b, "at location ", x, y)
        image[y, x] = [b, g, r]


# def mapClicks(x, y, curWidth, curHeight):
#     global imageHeight, imageWidth
#     imageX = x * imageWidth / curWidth
#     imageY = y * imageHeight / curHeight
#     return imageX, imageY


def drawRectangle(imageCopy):
    p1 = (track_window[0], track_window[1]) 
    p2 = (track_window[0] + w, track_window[1] + h) 
    cv2.rectangle(imageCopy, p1, p2, (0, 0, 255), thickness=2, lineType=cv2.LINE_8)


"""----------------------------------------main--------------------------"""


print("Starting program")
if __name__ == "__main__":
    arglist = sys.argv
    src = 0
    print("Argument count is ", len(arglist))
    if len(arglist) == 2:
        src = arglist[1]
    else:
        src = 0
    captureVideo(src)
else:
    print("Not in main")

# close parallel programming
pool.close()
print("Program end")
