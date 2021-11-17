# Visual-tracker-mean-shift
Author: Fan Ding \
Date: 11/17/2021 \
Description: This repository captures a video from either webcam or a disk movie file, and do visual trace on selected objects. A red rectangle will indicate where is the region of interest. 


## Develop steps
1. Initiate a target region, repesented as (x,y,w,h). (x,y) is the left up corner of the region, and w is width, h is highth.
2. Mean-shift tracker (target model using histogram, mean-shift vector using Bhattacharyya distance)
3. Implement clickHandler: Press t to toggle tracking, Pess q to quit 


## To run the code
1. Format:
`python3` `visual-tracer.py` `input_file_name` 
2. Example:
`python3 visual-tracer.py Girl/img/%04d.jpg` 


## Notes
1. This program comes with many test input folders
2. Makefile is included, simply type `make` in the terminal can run an example

