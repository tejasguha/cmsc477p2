import numpy as np
from robomaster import robot
from robomaster import camera
import time
import math
import detection
import gripping

# Defines functionality that is specific
# to the robot handing off the lego tower (the giver)

# have receiver strafe to the giver
def strafe_to_giver(translational_speed = 0.075, k = 0.05, ep_camera=None):
    
    distance = 1000000
    print('RECEIVER: Strafing to Giver robot')

    lastTime = time.time() # get time started search
    
    # want bounding box as close to center of img in horizontal dir
    while np.abs(distance) > 10: # bounding box x-center must be 10 away from center of img

        results = detection.detect_object_in_image(c='robot', ep_camera=ep_camera)

        if results[0]: # if lego in FOV
            bb = results[1] # bounding box -  array of format [x,y,w,h]
            horizontal_center = bb[0] + bb[2]/2
            distance = horizontal_center - 360 # finding error in horizontal

            control = translational_speed * distance * k
            
            print("control: ", translational_speed * distance * k)

            if np.abs(control) < 0.06: # around when actuator starts acting weird
                break
            
            ep_chassis.drive_speed(x=0, y=translational_speed * distance * k, z=0, timeout=5)

        else:

            currTime = time.time()
            if currTime-lastTime > 2: # switch directions if haven't seen robot in 2s
                translational_speed = translational_speed*-1
            
            ep_chassis.drive_speed(x=0, y=translational_speed, z=0, timeout=5)

        time.sleep(0.1)

    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5) # stop moving
    time.sleep(0.1)
    print('RECEIVER: Facing Giver')

# have receiver move to giver



# make reeciver face endpoint
def search_endpoint(rotational_speed = 10, k = 0.01, ep_camera=None): 
    
    distance = 1000000
    print('RECEIVER: Seaching for Endpoint')

    # want bounding box as close to center of img in horizontal dir
    while np.abs(distance) > 20: # bounding box x-center must be 15 away from center of img

        results = detection.detect_endpoint(ep_camera=ep_camera, show=False)

        if results[0]: # if lego in FOV
            bb = results[1] # bounding box -  array of format [x,y,w,h]
            horizontal_center = bb[0] + bb[2]/2
            distance = horizontal_center - 1280/2 # finding error in horizontal
            ep_chassis.drive_speed(x=0, y=0, z=k * distance * rotational_speed, timeout=5)

        else:
            ep_chassis.drive_speed(x=0, y=0, z=rotational_speed, timeout=5)

        time.sleep(0.1)

    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5) # stop rotating
    print('RECEIVER: Facing Endpoint')

# make reeciver go to endpoint
def move_to_endpoint(translation_speed = 0.04, rotational_speed = 10, 
                 k_t = 0.01, k_r = 0.05, ep_camera=None): 
    
    height = 0
    print('RECEIVER: Moving to Endpoint')

    goal_height = 460

    prev_height = 0
    count = 0

    # want bounding box as close to center of img in horizontal dir
    while height < goal_height:
        
        results = detection.detect_endpoint(ep_camera=ep_camera, show=False)

        if results[0]: # if lego in FOV
            
            bb = results[1] # bounding box -  array of format [x,y,w,h] scaled to image size of (384, 640)
            height = bb[1]
            height_error = (goal_height+20) - height # finding height in error

            horizontal_center = bb[0] + bb[2]/2
            horizontal_distance = horizontal_center - 1280/2 # finding error in horizontal


            if (horizontal_distance > 100):
                ep_chassis.drive_speed(x=translation_speed * k_t * height_error, y=0,
                                z= rotational_speed * k_r * horizontal_distance, timeout=5)

            if (horizontal_distance <= 100):
                ep_chassis.drive_speed(x=translation_speed * k_t * height_error, y=0,
                                z=0, timeout=5)

            if prev_height == height:
                count = count + 1
            if prev_height != height:
                count = 0
            prev_height = height

            if count == 3:
                break

        else:
            ep_chassis.drive_speed(x=0, y=0, z=rotational_speed, timeout=5)

        time.sleep(0.1)

    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5) # stop moving
    time.sleep(0.1)
    print('RECEIVER: At Endpoint')



if __name__ == '__main__':
    
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_gripper = ep_robot.gripper
    ep_arm = ep_robot.robotic_arm
    
    ep_camera.start_video_stream(display=False)

    # for strafing to giver
    strafe_to_giver(ep_camera=ep_camera)

    # moving to giver

    # for going to endpoint
    #gripping.LookDown(ep_gripper=ep_gripper, ep_arm=ep_arm, x=0, y=50) # have arm down before looking for endpoint
    #search_endpoint(ep_camera=ep_camera)
    #move_to_endpoint(ep_camera=ep_camera)
    
