#!/usr/bin/python

from __future__ import division
import numpy as np
import cv2
import sys

cap = cv2.VideoCapture("/David/img/%04d.jpg", cv2.CAP_IMAGES)

while(1):
   ret, frame = cap.read()
   cv2.imshow('image', frame)
   cv2.waitKey()
   print(frame.shape)
