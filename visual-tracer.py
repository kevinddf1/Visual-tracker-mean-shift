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

# You can format an entire file with Format Document (Ctrl+Shift+I)

from __future__ import division
import multiprocessing as mp
import numpy as np
import cv2
import sys
import time

# Mian steps
# 1. initiate a target region, (x,y,w,h)
# 2. press t to toggle tracking
# 3. mean-shift tracker, (target model, mean-shift vector using Bhattacharyya distance)
# 4. continue until user press q to quit

"""--------------------------------------------------------global data --------------------------------------"""
# bool flags
isTracking = False
showRectangle = False
roiSelect = False

# iamge frame info
image = []  # type: np.zeros((640, 480, 3), np.uint8)  # default size 640x480
imageWidth = imageHeight = 0

# region of interst info. roi is a rectangle repsentend by the left corner point(x,y) and width and hight
w, h = 40, 30  # roi width, roi hight
track_window = [0, 0, w, h]  # left corner point(x,y) and width and hight
trackedImage = []  # type: np.zeros((w, h, 3), np.uint8)
roi_hist = []

# other constants
max_loop = 10
sample_range = 5  # when click a intereted point, smaple to determine intested color
color_threshold = 40  # used to determine intested object

# parallelizing processing
pool = mp.Pool()

""" -------------------------------------------clickHandler (initiate a target region)---------------------------------------------"""

# initiate a target region, and build the target model using a histogram as feature
def clickHandler(event, x, y, flags, param):
    global showRectangle, isTracking, roiSelect, track_window, trackedImage, roi_hist
    if event == cv2.EVENT_LBUTTONUP:
        print("left button released at location ", x, y)
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
            print("building histogram")
            hsv_roi = cv2.cvtColor(trackedImage, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(
                hsv_roi, np.array((0.0, 60.0, 32.0)), np.array((180.0, 255.0, 255.0))
            )
            roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
            cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
            print("roi_hist size:", roi_hist.size)
            # print(roi_hist)
            print("finished  building histogram")


"""---------------------------------------------doTracking(mean-shift tracker)----------------------------------------------"""

# mean-shift tracker, (target histogram, Bhattacharyya distance)
def doTracking():
    global track_window
    # 1. intialize
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # print(hsv)
    # print("hsv size:", hsv.size)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
    # print(dst)
    # print("dst size:", dst.size)
    # apply meanshift to get the new location
    # ret, track_window = cv2.meanShift(dst, track_window, term_crit)

    # 2. define mean shift variables
    halfW= int(w / 2)  # half of tracker window w
    halfH = int(h / 2)  # half of tracker window h
    cx = cy = 0  # center x and center y
    cmx = track_window[0] + halfW # center mass x
    cmy = track_window[1] + halfH  #  center mass y
    loop_count = max_loop
    # 3. mean shift loops
    while (abs(cx - cmx) > 5 or abs(cy - cmy) > 5) and loop_count > 0:
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
        # print("totalmassX, totalmassY , totalmass:", totalmassX, totalmassY, totalmass)
        cmx = (int)(totalmassX / totalmass)
        cmy = (int)(totalmassY / totalmass)
        # print("cmx, cmy: ", cmx, cmy)
        # decrease loop_count
        loop_count -= 1

    # 4. update trackwindow
    track_window[0] = cmx - halfW
    track_window[1] = cmy - halfH

    # # parallel calculating
    # def tempFun(j):
    #     for i in range(imageHeight):
    #         TuneTracker(j, i)
    # tempList = range(imageWidth)
    # pool.map_async(tempFun, tempList)


"""--------------------------------------------captureVideo(set toggle tracking)--------------------------------"""
# read input video, and display output window
def captureVideo(src):
    global isTracking, showRectangle, roiSelect, image, imageHeight, imageWidth
    cap = cv2.VideoCapture(src)
    # 1. read input video
    # read web cam input CASE
    if cap.isOpened() and src == "0":
        ret = cap.set(3, 640) and cap.set(4, 480)
        imageWidth = 480
        imageHeight = 640
        # image = np.zeros((640, 480, 3), np.uint8)  # web cam window default size 640x480
        if ret == False:
            print("Cannot set frame properties, returning")
            return
    # read disk video CASE
    else:
        ret, image = cap.read()
        imageHeight, imageWidth, implanes = image.shape
        frate = cap.get(cv2.CAP_PROP_FPS)
        print(frate, " is the framerate")
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
            showRectangle = not showRectangle

    # 4. When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


"""----------------------------------------helper funcions--------------------------"""

# test user click position, it can't be at the edge, otherwise our red rectangle will be out of scope
def inBoundary(x, y):
    w = track_window[2]
    h = track_window[3]
    if (
        x < 0 + w / 2
        or x >= imageWidth - w / 2
        or y < 0 + h / 2
        or y >= imageHeight - h / 2
    ):
        return False
    else:
        return True


def determineWindowSize(x, y):
    # smaple around x, y to get the approximate color range
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    return 30, 40


def drawRectangle():
    global image
    p1 = (track_window[0], track_window[1])
    p2 = (track_window[0] + w, track_window[1] + h)
    cv2.rectangle(image, p1, p2, (0, 0, 255), thickness=2, lineType=cv2.LINE_8)


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
