# Visual-tracker-mean-shift
Author: Fan Ding \
Date: 11/17/2021 \
Description: This repository Read a video from either webcam or a disk movie file, and do visual trace on objects.

## Mian steps
1. initiate a target region, (x,y,w,h)
2. press t to toggle tracking
3. mean-shift tracker, (target model using histogram, mean-shift vector using Bhattacharyya distance)
4. continue until user press q to quit


## To run the code
1. Format:
`python3` `visual-tracer.py` `input_file_name` 
2. Example:
`python3 visual-tracer.py Girl/img/%04d.jpg` 

## Notes
1. This program comes with many test input folders
2. Makefile is included, simply type `make` in the terminal can run an example

