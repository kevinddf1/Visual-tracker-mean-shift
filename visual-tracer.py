#!/usr/bin/python

# Author: Fan Ding
# Email: ding0322@umn.edu
# Date: 11/17/2021

"""
Visual tracer:
Read a video from either webcam or a disk movie file, and do visual trace on objects.
Press q to exit, 
Press t to toggle tracker rectangle
"""

# Reference:
# https://gist.github.com/jstadler/c47861f3d86c40b82d4c (find center mass)
# https://www.programcreek.com/python/example/89397/cv2.meanShift (openCV meanshift)
# capture.py from Prof.Junaed Sattar


from __future__ import division
import numpy as np
import cv2
import sys
import time
from scipy import spatial

# Mian steps
# 1. initiate a target region, (x,y,w,h)
# 2. press t to toggle tracking
# 3. mean-shift tracker, (target model using color histogram, mean-shift vector using Bhattacharyya distance)
# 4. continue until user press q to quit

"""--------------------------------------------------------global data --------------------------------------"""
# bool flags
isTracking = False
showRectangle = False
roiSelect = False

# iamge frame info
image = []  # np.zeros((640, 480, 3), np.uint8)
imageWidth = imageHeight = 0

# region of interst info. roi is a rectangle repsentend by the left corner point(x,y) and width and hight
w, h = 30, 20  # roi width, roi hight
track_window = [0, 0, w, h]  # left corner point(x,y) and width and hight
trackedImage = []  # np.zeros((w, h, 3), np.uint8)
roi_hist = []

# other constants
max_loop = 5


""" -------------------------------------------clickHandler (initiate a target region)---------------------------------------------"""

# initiate a target region, and build the target model using a histogram as feature
def clickHandler(event, x, y, flags, param):
    global showRectangle, isTracking, roiSelect, track_window, trackedImage, roi_hist
    if event == cv2.EVENT_LBUTTONUP:
        print(
            "ROI Selected, left button released at location ",
            x,
            y
        )
        # out of boundary
        if inBoundary(x, y) == False:
            print("invalid click position, try again")
        else:
            # change x,y to the rectangle left corner point
            x = int(x - w / 2)
            y = int(y - h / 2)
            # edit gobal variables
            showRectangle = True
            isTracking = True
            roiSelect = True
            track_window = [x, y, w, h]
            trackedImage = image[y : y + h, x : x + w]
            # build histogram
            roi_hist = buildHist(trackedImage)
            # print(roi_hist)


"""---------------------------------------------doTracking(mean-shift tracker)----------------------------------------------"""

# mean-shift tracker, (target histogram, Bhattacharyya distance)
def doTracking():
    global track_window
    # 1. dst stores each pixel probility base on roi histogram
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

    # 2. intialize mean shift variables
    halfW = int(w / 2)  # half of tracker window w
    halfH = int(h / 2)  # half of tracker window h
    cx = cy = 0  # center x and center y
    cmx = track_window[0] + halfW  # center mass x
    cmy = track_window[1] + halfH  #  center mass y
    loop_count = max_loop
    hist_curr = -1 * roi_hist
    similarity = bhatta(hist_curr, roi_hist)

    # 3. mean shift loops
    while similarity < 0.9 and loop_count > 0:
        # print("similarity: ", similarity)
        # assign center mass point to current center point
        cx = cmx
        cy = cmy
        totalmassX = 0
        totalmassY = 0
        totalmass = 0
        # calulate cmx and cmy base on the roi range
        for i in range(max(0, cx - halfW), min(cx + halfW, imageWidth)):
            for j in range(max(0, cy - halfH), min(cy + halfH, imageHeight)):
                # print('test')
                totalmassX += dst[j][i] * i
                totalmassY += dst[j][i] * j
                totalmass += dst[j][i]
        # update cmx and hist_curr
        if totalmass != 0:
            cmx = (int)(totalmassX / totalmass)
            cmy = (int)(totalmassY / totalmass)
        newWindow = image[
            max(0, cmy - halfH) : min(imageHeight - 1, cmy + halfH),
            max(0, cmx - halfW) : min(imageWidth - 1, cmx + halfW),
        ]
        hist_curr = buildHist(newWindow)
        similarity = bhatta(hist_curr, roi_hist)
        loop_count -= 1

    # 4. update trackwindow
    track_window[0] = cmx - halfW
    track_window[1] = cmy - halfH


"""--------------------------------------------captureVideo(set toggle tracking)--------------------------------"""
# read input video, and display output window
def captureVideo(src):
    global isTracking, showRectangle, roiSelect, image, imageHeight, imageWidth
    cap = cv2.VideoCapture(src)
    # 1. read input video
    if cap.isOpened() and src == "0":  # read web cam input CASE
        ret = cap.set(3, 640) and cap.set(4, 480)
        imageWidth = 480
        imageHeight = 640
        if ret == False:
            print("Cannot set frame properties, returning")
            return
    else:  # read disk video CASE
        ret, image = cap.read()
        imageHeight, imageWidth, implanes = image.shape
        frate = cap.get(cv2.CAP_PROP_FPS)
        print(frate, " is the frame rate")
        waitTime = int(1000 / frate)

    # 2. and setup the output window. (waitTime = time/frame. Adjust accordingly.)
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

    # 3. loop each frame, do visual tracing, display window
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        if ret == False:
            break

        # Display the resulting frame
        if isTracking:
            doTracking()
        if showRectangle:
            drawRectangle()
        cv2.imshow(windowName, image)
        inputKey = cv2.waitKey(waitTime) & 0xFF

        # user inferface handler
        if inputKey == ord("q"):
            break
        elif inputKey == ord("t"):
            print("please click a intested target and press t to start tracking")
            cv2.waitKey(-1)
            # showRectangle = not showRectangle

        # pause first frame for user to click the roi
        while roiSelect == False:
            print("please click a intested target and press t to start tracking")
            cv2.waitKey(-1)

    # 4. When everything done, release the capture
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


# Bhattacharyya distance used for determine similarity between 2 histograms. return range [0,1].  1 means exactly the same, 0 means totally different
def bhatta(hist1, hist2):
    if np.linalg.norm(hist1) == 0 or np.linalg.norm(hist2) == 0:
        return 0
    return 1 - spatial.distance.cosine(hist1, hist2)


# draw rectangle that indicate the target
def drawRectangle():
    global image
    p1 = (track_window[0], track_window[1])
    p2 = (track_window[0] + w, track_window[1] + h)
    cv2.rectangle(image, p1, p2, (0, 0, 255), thickness=2, lineType=cv2.LINE_8)


# take a 2D array as input window,and output its histgram
def buildHist(input_window):
    hsv_roi = cv2.cvtColor(input_window, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv_roi, np.array((0.0, 60.0, 32.0)), np.array((180.0, 255.0, 255.0))
    )
    ret_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv2.normalize(ret_hist, ret_hist, 0, 255, cv2.NORM_MINMAX)
    return ret_hist


"""----------------------------------------main--------------------------"""


print("Starting program")
if __name__ == "__main__":
    arglist = sys.argv
    src = 0
    # print("Argument count is ", len(arglist))
    if len(arglist) == 2:
        src = arglist[1]
    else:
        src = 0
    captureVideo(src)
else:
    print("Not in main")

print("Program end")
