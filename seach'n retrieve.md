### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Here is an example of how to include an image in your writeup.

Function Color_Thresh
using the RGB values, I created in essence a high pass filter for the color of the whitish sand/dirt (RGB > 160). Creating a binary array of where the traversable terrain existed

Function perspect_transform
using the the output of color_thresh, I translated the 2d image into pseudo 3d space using perspective lines

Function sample_detect
similar to color_thresh, I filtered for the sample rocks by looking for various shades of yellow, via 100+ for R and G and 60- for B

Function to obstacle_detect
similar to color_thresh, I filtered for obstacles by looking for RGB < 160


#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 
for some reason i am getting a 

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  