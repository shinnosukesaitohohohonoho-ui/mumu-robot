#!/bin/bash

ros2 topic pub --once /model/vehicle_blue/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.1}, angular: {z: 0.0}}'
sleep 2
ros2 topic pub --once /model/vehicle_blue/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0}, angular: {z: 0.0}}'
