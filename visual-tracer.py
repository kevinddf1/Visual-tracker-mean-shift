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
isTracking = False
showRectangle = False
targetX = targetY = 0  # for target region
targetRegionSize = 20  # the target region size
r = g = b = 0.0
image = np.zeros((640, 480, 3), np.uint8)
imageWidth = imageHeight = 0
trackedImage = np.zeros((640, 480, 3), np.uint8)

pool = mp.Pool() # for parallellizing processing

""" -------------------------------------------clickHandler---------------------------------------------"""

# initiate a target region, and build the target model using a histogram as feature
def clickHandler(event, x, y, flags, param):
    global targetX, targetY, showRectangle, isTracking
    if event == cv2.EVENT_LBUTTONUP:
        print("left button released at location ", x, y)
        if(inBoundary(x,y)==False):
            print("invalid click position, try again")
        else:
            # store gobal variables
            targetX = x
            targetY = y
            showRectangle = True
            isTracking = True
            # build histogram
            print("building histogram")
        


"""---------------------------------------------doTracking----------------------------------------------"""


def doTracking():
    global isTracking, image, r, g, b
    if isTracking == False:
        return
    print("is tracking")
    # print(image.shape)
    imheight, imwidth, implanes = image.shape

    def tempFun(j):
        for i in range(imheight):
            TuneTracker(j, i)
    
    tempList = range(imwidth)
    pool.map_async(tempFun, tempList)


"""--------------------------------------------captureVideo--------------------------------"""
# read input video and setup output window
def captureVideo(src):
    # read input video and setup the output window
    global image, imageHeight, imageWidth, isTracking, showRectangle, trackedImage
    cap = cv2.VideoCapture(src)
    if cap.isOpened() and src == "0":
        ret = cap.set(3, 640) and cap.set(4, 480)
        if ret == False:
            print("Cannot set frame properties, returning")
            return
    else:
        ret, image = cap.read()
        imageHeight,imageWidth, implanes = image.shape
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
    

    print("image size is ",image.shape)
    
    # visual tracer loop
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        #print("image size is ",image.shape )
        if ret == False:
            break
        imageCopy = image.copy()
        #print("copyimage size is ",image.shape )

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


def inBoundary(x, y):
    if (
        x < 0 + targetRegionSize / 2
        or x >= imageWidth - targetRegionSize / 2
        or y < 0 + targetRegionSize / 2
        or y >= imageHeight - targetRegionSize / 2
    ):
        return False
    else:
        return True


def TuneTracker(x, y):
    global r, g, b, image
    b, g, r = image[y, x]
    sumpixels = float(b) + float(g) + float(r)
    if sumpixels != 0:
        b = int(b / sumpixels)
        r = int(r / sumpixels)
        g = int(g / sumpixels)
        #print(r, g, b, "at location ", x, y)
        image[y, x] = [b, g, r]


def mapClicks(x, y, curWidth, curHeight):
    global imageHeight, imageWidth
    imageX = x * imageWidth / curWidth
    imageY = y * imageHeight / curHeight
    return imageX, imageY


def drawRectangle(imageCopy):
    p1 = (int(targetX - targetRegionSize / 2), int(targetY - targetRegionSize / 2))
    p2 = (int(targetX + targetRegionSize / 2), int(targetY + targetRegionSize / 2))
    cv2.rectangle(imageCopy, p1, p2, (0, 0, 255), thickness=1, lineType=cv2.LINE_8)


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

pool.close()
print("Program end")