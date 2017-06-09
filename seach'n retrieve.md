### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  


### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

Function Color_Thresh
using the RGB values, I created in essence a high pass filter for the color of the whitish sand/dirt (RGB > 160). Creating a binary array of where the traversable terrain existed

Function perspect_transform
using the the output of color_thresh, I translated the 2d image into pseudo 3d space using perspective lines

Function sample_detect
similar to color_thresh, I filtered for the sample rocks by looking for various shades of yellow, via 100+ for R and G and 60- for B.

Function to obstacle_detect
similar to color_thresh, I filtered for obstacles by looking for RGB < 160


#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

Having index errors trying to process the user video. Attempted to cease video process before bad index, unsuccessful in getting it to work.

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

using the color_thesh  and obstacle detection functions, navigable and obstacle azimuths are stored in the Rover.nav_angles and Rover.obs_angles.  This allows for the rover to detemine possible steer angles and potential obstacles.

To ensure fidelity of the map, map addition is ceased if pitch and roll exceeds 0.5 degrees off waterline.

When a sample is detected via sample_detect, a flag is triggered placing the rover into sample retrieval mode, and rover steering is based off of angles to the sample with an slight offset.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

The rover is set to wall crawl the terrain on the left side. This is accomplished by setting the rover to max left turn anytime the max navigable azimuth exceeds 50 degrees. This is damped by resetting the steer angle to zero on every other decision step. This is done to prevent the rover from getting into an infinite turns in the open areas.

A stuck mode is initiated when the rover has a velocity of 0 with a non zero throttle for more than 1 decision cycle. When initaited the rover will try to make a max azimuth turn towards the side with the most navigable area.

Improvements if I had more time:

Better crawl logic; have the rover maintain a set distance from any wall, should reduce fidelity loss due to constant yaw changes.

Location store and waypoint system; determine already mapped areas and auto route rover to missing areas. Could increase rover speed and maintain map fidelity.

Improved sample approach routing; Allows for rover to temporarly break LOS of sample to reposition to allow for better approach vector.
