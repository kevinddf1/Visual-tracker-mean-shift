#!/usr/bin/python
""" Constructs a videocapture device on either webcam or a disk movie file.
Press q to exit

Junaed Sattar
October 2021
"""
from __future__ import division
import numpy as np
import cv2
import sys


    
    
    
"""global data common to all vision algorithms"""
isTracking = False
showRectangle = False
targetX = targetY = 0 # for target region
targetRegionSize = 20  # the target region size
r = g = b = 0.0
image = np.zeros((640, 480, 3), np.uint8)
trackedImage = np.zeros((640, 480, 3), np.uint8)
imageWidth = imageHeight = 0












"""Defines a color model for the target of interest.
   Now, just reading pixel color at location
"""


def TuneTracker(x, y):
    global r, g, b, image
    b, g, r = image[y, x]
    sumpixels = float(b) + float(g) + float(r)
    if sumpixels != 0:
        b = (b / sumpixels,)
        r = r / sumpixels
        g = g / sumpixels
    print(r, g, b, "at location ", x, y)


""" Have to update this to perform Sequential Monte Carlo
    tracking, i.e. the particle filter steps.

    Currently this is doing naive color thresholding.
"""


def doTracking():
    global isTracking, image, r, g, b
    if isTracking==False:
        return
    print("is tracking")
    # print(image.shape)
    imheight, imwidth, implanes = image.shape
    
   
    for j in range(imwidth):
        for i in range(imheight):
            bb, gg, rr = image[i, j]
            sumpixels = float(bb) + float(gg) + float(rr)
            if sumpixels == 0:
                sumpixels = 1
            if rr / sumpixels >= r and gg / sumpixels >= g and bb / sumpixels >= b:
                image[i, j] = [255, 255, 255]
            else:
                image[i, j] = [0, 0, 0]


def clickHandler(event, x, y, flags, param):
    global targetX, targetY, showRectangle
    if event == cv2.EVENT_LBUTTONUP:
        print("left button released")
        TuneTracker(x, y)
        targetX=x
        targetY=y
        showRectangle=True
        
        


def mapClicks(x, y, curWidth, curHeight):
    global imageHeight, imageWidth
    imageX = x * imageWidth / curWidth
    imageY = y * imageHeight / curHeight
    return imageX, imageY


"""-----------------------------------------------------new functions----------------------------"""

"""Defines a color model for the target of interest.
   Now, just reading pixel color at location
"""
def drawRectangle():
    global image
    p1 = (int(targetX-targetRegionSize/2), int(targetY-targetRegionSize/2))
    p2 = (int(targetX+targetRegionSize/2), int(targetY+targetRegionSize/2))
    cv2.rectangle(image, p1, p2, (0, 0, 255), thickness= 1, lineType=cv2.LINE_8) 
    print("rectangle draw!")





def captureVideo(src):
    global image, isTracking, showRectangle, trackedImage
    cap = cv2.VideoCapture(src)
    if cap.isOpened() and src == "0":
        ret = cap.set(3, 640) and cap.set(4, 480)
        if ret == False:
            print("Cannot set frame properties, returning")
            return
    else:
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
    
    
    #beging visual tracing
    # 1. initiate a target region, (targetX, targetY, targetRegionSize)
    # 2. press t to toggle tracking
    # 3. mean-shift tracker, (target model, mean-shift vector, KL divergence/Bhattacharyya distance)
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        if ret == False:
            break

        # Display the resulting frame
        if isTracking:
            doTracking()
        if(showRectangle==True):
            drawRectangle()
        cv2.imshow(windowName, image)
        inputKey = cv2.waitKey(waitTime) & 0xFF
        if inputKey == ord("q"):
            break
        elif inputKey == ord("t"):
            showRectangle = not showRectangle

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


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
