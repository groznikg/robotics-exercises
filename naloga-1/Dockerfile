# ROS2 Jazzy + turtlesim + C# WASD teleop (ros2cs)
# ros:jazzy is multi-arch (amd64 + arm64)
FROM ros:jazzy

# ── System packages ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    ros-jazzy-turtlesim \
    ros-jazzy-rosbridge-server \
    libgl1 \
    libglib2.0-0 \
    xterm \
    dotnet-sdk-8.0 \
    && rm -rf /var/lib/apt/lists/*

# ── Copy workspace ────────────────────────────────────────────────────────────
COPY ros2_ws /ros2_ws

# ── Build C# teleop with dotnet ───────────────────────────────────────────────
# ros2cs NuGet packages provide the C# ROS2 bindings.
# They P/Invoke into the native RCL libs already present in the ros:jazzy image.
WORKDIR /ros2_ws/src/turtle_teleop_wasd/TurtleTeleop
RUN dotnet restore
RUN dotnet build -c Release --no-restore

# ── Shell env ────────────────────────────────────────────────────────────────
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

COPY entrypoint.sh /entrypoint.sh
COPY start.sh      /start.sh
RUN chmod +x /entrypoint.sh /start.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
