import numpy as np
import cv2
import argparse
import shutil
import base64
from datetime import datetime
import os
import cv2
import numpy as np
import socketio
import eventlet
import eventlet.wsgi
from PIL import Image
from flask import Flask
from io import BytesIO, StringIO
import json
import pickle
import matplotlib.image as mpimg
import time

# constants
# defining worldspace
worldmap = np.zeros((200, 200))
scale = 10	
		
# functions 

def perspect_transform(img):
    img_size = (img.shape[1], img.shape[0])
    # Define calibration box in source (actual) and destination (desired) coordinates
    # These source and destination points are defined to warp the image
    # to a grid where each 10x10 pixel square represents 1 square meter
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    bottom_offset = 6
    src = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    dst = np.float32([[img_size[0]/2 - dst_size, img_size[1] - bottom_offset],
                      [img_size[0]/2 + dst_size, img_size[1] - bottom_offset],
                      [img_size[0]/2 + dst_size, img_size[1] - 2*dst_size - bottom_offset], 
                      [img_size[0]/2 - dst_size, img_size[1] - 2*dst_size - bottom_offset],
                      ])
       
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, img_size)# keep same size as input image
    return warped

def color_thresh(img, rgb_thresh=(170, 170, 170)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all thre threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

def sample_detect(img):
    #Detects the sample rocks by isolating yellow and creating a binary image array
    #initialize sampleDetect array
    sampleDetect = np.zeros_like(img[:,:,0])
    sampleDetectYellow = (img[:,:,0] > 100) \
                & (img[:,:,1] > 100) \
                & (img[:,:,2] < 60)
    sampleDetect[sampleDetectYellow] = 1
    return sampleDetect
    
def obstacle_detect(img):
    #Detects the obstacles by isolating filtering out sand color and creating a binary image array
    #initialize sampleDetect array
    obstacleDetect = np.zeros_like(img[:,:,0])
    obstacleDetectArray = (img[:,:,0] < 160) \
                & (img[:,:,1] < 160) \
                & (img[:,:,2] < 160)
    obstacleDetect[obstacleDetectArray] = 1
    return obstacleDetect
    
def distAtAz(aZ,distArray,azArray): 
    # deteremines max travel distance at given azimuth
    index, = np.where(azArray == find_nearest(azArray,aZ))
    print(azArray[index])
    dist = distArray[index]
    return dist

def find_nearest(array,value): # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    #determines closest number in an array, in this case approximating the avg angle to on definied in the az array
    idx = (np.abs(array-value)).argmin()
    print(array[idx])
    return array[idx]

def to_polar_coords(xpix, ypix):
    # Calculate distance to each pixel
    dist = np.sqrt(xpix**2 + ypix**2)
    # Calculate angle using arctangent function
    angles = np.arctan2(ypix, xpix)
    return dist, angles

def sampleAzRange(img):
    return


def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel

def rotate_pix(xpix, ypix, yaw):
    # TODO:
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # TODO:
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot/scale) + xpos
    ypix_translated = (ypix_rot/scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated

def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world
    
		
# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    # 2) Apply perspective transform
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    # 5) Convert map image pixel values to rover-centric coords
    # 6) Convert rover-centric pixel values to world coordinates
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
	#################code start###################

     #load image from Rover

     image = Rover.img

     #apply perspective translation

     warped = perspect_transform(image)

     #convert to binary

     colorsel = color_thresh(warped, rgb_thresh=(160, 160, 160))

     #check for Sample

     sample = sample_detect(image)
     sampleWarped = perspect_transform(sample)

     #check for obstacle
     
     obstacle =  obstacle_detect(image)
     obstacleWarped = perspect_transform(obstacle)
  

     #update Rover vision 
     Rover.vision_image[:,:,0] = obstacleWarped * 255
     Rover.vision_image[:,:,1] = sampleWarped * 255
     Rover.vision_image[:,:,2] = colorsel * 255

     #get Rover Position and Orientation

     rover_xpos = Rover.pos[0]
     rover_ypos = Rover.pos[1]
     rover_yaw = Rover.yaw

   # translate current detected environment to Rover Coodinates
     nxpix, nypix = rover_coords(colorsel)
     sxpix, sypix = rover_coords(sampleWarped)
     oxpix,oypix = rover_coords(obstacleWarped)

     # Get navigable and sample pixel positions in world coords
     o_x_world, o_y_world = pix_to_world(oxpix, oypix, rover_xpos, rover_ypos, rover_yaw, worldmap.shape[0], scale)
     n_x_world, n_y_world = pix_to_world(nxpix, nypix, rover_xpos, rover_ypos, rover_yaw, worldmap.shape[0], scale)						
     s_x_world, s_y_world = pix_to_world(sxpix, sypix, rover_xpos, rover_ypos, rover_yaw, worldmap.shape[0], scale)
               # Add pixel positions to worldmap
     if (Rover.pitch <= 0.5 or Rover.pitch >= 359.5): 
          if (Rover.roll <= 0.5 or Rover.roll >= 359.5 ): #damping
          # update map 
               Rover.worldmap[o_y_world, o_x_world, 0] += 1
               Rover.worldmap[s_y_world, s_x_world, 1] += 1
               Rover.worldmap[n_y_world, n_x_world, 2] += 1

     # convert to polar

     n_distances, n_angles = to_polar_coords(nxpix, nypix)
     Rover.nav_dists = n_distances
     Rover.nav_angles = n_angles
      #n_avg_angle = np.mean(n_angles)
     s_distances, s_angles = to_polar_coords(sxpix, sypix)
     o_distances, o_angles = to_polar_coords(oxpix, oypix)
     Rover.obs_dists = o_distances
     Rover.obs_angles = o_angles
     if np.count_nonzero(sample)>0:
          Rover.seeSample = True
          Rover.samp_angles = s_angles
          Rover.samp_dists = s_distances
     #else: 
      #Rover.seeSample = False
      #Rover.near_sample = False
      #Rover.pick_up = False
      #Rover.samp_angles = None
          # #s_avg_angle = np.mean(s_angles)
        
     return Rover
