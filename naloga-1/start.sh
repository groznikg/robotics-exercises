#!/bin/bash
source /opt/ros/jazzy/setup.bash

# turtlesim GUI
ros2 run turtlesim turtlesim_node </dev/null &

# rosbridge WebSocket server (default port 9090)
# The C# teleop publishes via JSON over WebSocket – no native RCL needed
ros2 launch rosbridge_server rosbridge_websocket_launch.xml </dev/null &

sleep 3

# C# teleop (foreground – keyboard input)
dotnet /ros2_ws/src/turtle_teleop_wasd/TurtleTeleop/bin/Release/net8.0/TurtleTeleop.dll

kill %1 %2 2>/dev/null
