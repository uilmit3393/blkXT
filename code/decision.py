import numpy as np

def distAtAz(aZ,distArray,azArray): # matches values in dist array to values in azArray
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
	
# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):
     # Implement conditionals to decide what to do given perception data
     # Here you're all set up with some basic functionality but you'll need to
     # improve on this decision tree to do a good job of navigating autonomously!
     print("Current mode = ", Rover.mode, "See Sample = ", Rover.seeSample)
     if Rover.throttle > 0 and Rover.lastVel == 0 and Rover.vel < 0.09 and Rover.mode != 'stop':
        Rover.mode = 'stuck'	


    # Check if we have vision data to make decisions with
     if Rover.nav_angles is not None:
        # Check for Rover.mode status

          Rover.lastVel = Rover.vel
          lastHeading = Rover.steer
          currentHeading = lastHeading
          if np.size(Rover.nav_angles) > 0:
               maxNavAz = np.max(Rover.nav_angles * 180/np.pi)
               minNavAz = np.min(Rover.nav_angles * 180/np.pi)
               distToWallMaxAz = np.min(distAtAz(maxNavAz,Rover.nav_dists,Rover.nav_angles)) 
               distInFront = np.max(distAtAz(0*np.pi/180,Rover.nav_dists,Rover.nav_angles)) - np.min(distAtAz(0*np.pi/180,Rover.nav_dists,Rover.nav_angles))
               distToClosestObs = np.min(Rover.obs_dists)
               azToClosestObs = np.min(distAtAz(distToClosestObs,Rover.obs_angles,Rover.obs_dists)) * 180/np.pi
               print("Dist in front of rover ", distInFront ," dist to closest obs ",distToClosestObs, "az to closest obs", azToClosestObs)
               if (Rover.nav_angles > 0).sum() < (Rover.nav_angles < 0).sum():
                    mod = -1
               else:
                    mod = 1
          else:
               maxNavAz = 0
               minNavAz = 0
               distToWallMaxAz = 0
               distInFront = 0
               distToClosestObs = 0
               azToClosestObs = 0
               mod = 1
               
          if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
               if distInFront > 10 and distToClosestObs > 6:  
                    currentHeading = lastHeading
                    obs = False
                    print("Obstacle detected turning to ", currentHeading , "closest wall az" ,azToClosestObs, " dist " , distToClosestObs)
               else:
                    if Rover.vel > .5:
                         Rover.throttle = 0
                    currentHeading = azToClosestObs - 10* mod
                    obs = True
                    print("Obstacle detected turning to ", currentHeading , "closest wall az" ,azToClosestObs, " dist " , distToClosestObs)
               if Rover.seeSample == False:
                    if len(Rover.nav_angles) >= Rover.stop_forward:  
                     # If mode is forward, navigable terrain looks good 
                     # and velocity is below max, then throttle 
                         if Rover.vel < Rover.max_vel:
                         # Set throttle value to throttle setting
                            Rover.throttle = Rover.throttle_set
                         else: # Else coast
                              Rover.throttle = 0
                              Rover.brake = 0
                         # Set steering to average angle clipped to the range +/- 15
                         print("Max detected azimuth = ", maxNavAz, " Min detected azimuth = ", minNavAz," Obs =  ",obs)

                         if maxNavAz > 50 and obs == False: # check if there is a left turn and clear path in that direction
                              if lastHeading > 10 :
                                   currentHeading = 0
                              else:
                                   currentHeading =np.clip( maxNavAz - np.abs(np.median(Rover.nav_angles * 180/np.pi)), -15*mod, 15)
                              # if np.max(distAtAz(currentHeading*np.pi/180,Rover.nav_dists,Rover.nav_angles)) < 10:
                                   # currentHeading = lastHeading
                              print("Left Heading = ", currentHeading)
                         else:
                              currentHeading = np.clip(maxNavAz - np.abs(minNavAz), 15*mod,15)
                         print("Selected Heading = ", currentHeading)
                         if np.abs(azToClosestObs) < 15 and distToClosestObs < 10:
                              currentHeading = mod * 15
                              print("avoiding obstacle", currentHeading)
                         Rover.steer = currentHeading
                    # If there's a lack of navigable terrain pixels then go to 'stop' mode
                    elif len(Rover.nav_angles) < Rover.stop_forward:
                         # Set mode to "stop" and hit the brakes!
                         Rover.throttle = 0
                         # Set brake to stored brake value
                         Rover.brake = Rover.brake_set
                         Rover.steer = 0
                         Rover.mode = 'stop'
                     #elif distAtAz(0,Rover.nav_dists,Rover.nav_angles) < 10 && Rover.vel == 0:

               elif Rover.seeSample == True:
                # if Rover.vel == 0 and Rover.throttle != 0:
                          # #Rover.lastPos = Rover.pos
                    # Rover.throttle = 0
                    # Rover.steer = 0
                    # Rover.mode = 'stuck'
                    print("Max detected azimuth = ",  np.mean((Rover.samp_angles * 180/np.pi)), " mod val ", mod," Obs =  ",obs)
                    if np.size(Rover.samp_dists) > 0:
                         if np.min(Rover.samp_dists) >= 10:
                              if np.min(np.abs(Rover.samp_angles) * 180/np.pi) > 15 and obs == False:
                                   Rover.throttle = 0
                                   Rover.steer = np.clip(np.mean((Rover.samp_angles * 180/np.pi)+5*mod), -10, 10)
                                   #Rover.mode = 'stop'
                              elif obs == False:
                                   Rover.brake = 0
                                   Rover.throttle = 0.2
                                   Rover.steer = np.clip(np.mean((Rover.samp_angles * 180/np.pi)+5*mod), -10, 10)
                              else:
                                   Rover.brake = Rover.brake_set
                                   Rover.steer = 0
                                   Rover.mode = 'stop'
                         elif Rover.near_sample == 0:
                              Rover.steer = np.clip(np.mean((Rover.samp_angles * 180/np.pi)+5*mod), -10, 10)
                              Rover.throttle = 0.2
                              # Set brake to stored brake value
                         elif Rover.near_sample == 1: 
                              Rover.brake = Rover.brake_set
                              Rover.mode = 'stop'
                    else:
                         Rover.seeSample = False
                         Rover.send_pickup = False
                         Rover.pick_up = 0
					
          # If we're already in "stop" mode then make different decisions
          elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
               if Rover.seeSample == False:
                    if np.abs(Rover.vel) > 0.2:
                         Rover.throttle = 0
                         Rover.brake = Rover.brake_set
                         Rover.steer = 0
                #If we're not moving (vel < 0.2) then do something else
                    elif np.abs(Rover.vel) <= 0.2:
                    # Now we're stopped and we have vision data to see if there's a path forward				
                         if len(Rover.nav_angles) < Rover.go_forward:
                            Rover.throttle = 0
                            # Release the brake to allow turning
                            Rover.brake = 0
                            # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                            Rover.steer = -15 # Could be more clever here about which way to turn
                            # If we're stopped but see sufficient navigable terrain in front then go!
                         elif len(Rover.nav_angles) >= Rover.go_forward:
                            # Set throttle back to stored value
                            Rover.throttle = Rover.throttle_set
                            # Release the brake
                            Rover.brake = 0
                            Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -10, 10)
                            # Set steer to mean angle
                            # lastHeading =  Rover.steer
                            # maxNavAz = np.max(Rover.nav_angles * 180/np.pi) 
                            # if maxNavAz > 15:
                                 # if np.min(distAtAz(maxNavAz,Rover.nav_dists,Rover.nav_angles)) > 30: 
                                      # currentHeading = np.clip(np.mean(Rover.nav_angles * 180/np.pi), 0, 10)
                                 # else:
                                      # currentHeading = 0
                            # elif maxNavAz < 5:
                                 # currentHeading = -5   
                              # #currentHeading = lastHeading
                            # else:
                                 # currentHeading = lastHeading					   
                            # Rover.steer = currentHeading
                            Rover.mode = 'forward'
               elif Rover.seeSample == True:
                    if np.size(Rover.samp_dists) > 0:
                         if np.min(Rover.samp_dists) >= 10:
                              Rover.throttle = Rover.throttle_set
                              # Release the brake
                              Rover.brake = 0
                              # Set steer to mean angle
                              Rover.steer = np.clip(np.mean(Rover.samp_angles * 180/np.pi), -10, 10)
                              if np.abs(np.mean(Rover.samp_angles * 180/np.pi)) <= 15:
                                   Rover.mode = 'forward'
                         elif Rover.near_sample == 1:
                              #Rover.near_sample = True
                              Rover.send_pickup = True
                              #Rover.pick_up = 0
                              #Rover.samples_found += 1
                              Rover.seeSample = False
                              Rover.brake = 0
                              Rover.throttle = Rover.throttle_set
                              Rover.mode = 'forward'
                         else:
                              Rover.steer = np.clip(np.mean(Rover.samp_angles * 180/np.pi), -10, 10)
                              Rover.brake = 0
                              Rover.mode = 'forward'
                    else:
                         Rover.seeSample = False
                         Rover.send_pickup = False
                         Rover.pick_up = 0					
          elif Rover.mode == "stuck":
               print("Rover is stuck")
               #Rover.throttle = -1
               #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
               Rover.throttle = 0
               if maxNavAz > np.max(Rover.obs_angles):
                    Rover. steer = -15
               elif minNavAz > np.min(Rover.obs_angles):
                    Rover.steer = 15
               else:
                    Rover.steer = 15*mod
               #Rover.throttle = -1
               Rover.mode = 'stop'
          # Just to make the rover do something 
          # even if no modifications have been made to the code
          else:
               Rover.throttle = Rover.throttle_set
               Rover.steer = 0
               Rover.brake = 0

     return Rover

