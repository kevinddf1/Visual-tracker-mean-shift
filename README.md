# Visual-tracker-mean-shift
Author: Fan Ding \
Date: 11/17/2021 \
Description: This repository captures a video from either webcam or a disk movie file, and do visual trace on selected objects. A red rectangle will indicate where the region of interest is. 

## Screenshots
![Alt text](/Screenshot_Surfer?raw=true "Optional Title")
![Alt text](/Screenshot_Girl?raw=true "Optional Title")




## Develop steps
1. Initiate a target region, repesented as (x,y,w,h). (x,y) is the left up corner point of the region, and w is width, h is highth.
2. Mean-shift tracker (used Histogram, and Bhattacharyya distance).
3. Implement clickHandler: Press t to toggle tracking. Pess q to quit.


## To run the code
1. Format:
`python3` `visual-tracer.py` `input_file_name` 
2. Example:
`python3 visual-tracer.py Girl/img/%04d.jpg` 


## Notes
1. This program comes with many test input folders.
2. Makefile is included, simply type `make` in the terminal can run an example.

## Brift report on test folders
1. Surfer: The visual tracker works well in tracking the target throughout the video.
2. Girl: The visual tracker tracks a girl's face very well until a man's face blocks it.
3. Biker: When the object moves suddenly, the tracker misses the target.
4. Panda: the color of the panda is similar to the ground, the tracker loses the target.

## Performance feedback
1. Speed: This program uses mean-shift algorithm. Runtime speed is much faster than brute force apporach.
2. Accuracy: Since this program uses a color histogram as the target model, it works well when the target color distinguishes with the background. But when the target color is similar to the background, the tracker sometimes loses track.
3. Occlusion: If a similar object occludes with our proven target, it could "steal" the tracker's attention.

## Limitation and possible solution
1. Grayscale video does not work because the program uses color histograms to build the target model. Potential fix: adding new edges or shape target models.
2. If the target moves too fast, the tracker may lose the target. Possible solution: larger mean-shift area (increases circle radius)

