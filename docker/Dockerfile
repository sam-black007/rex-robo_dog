# Zuko Robot - ROS2 Humble in Docker (Ubuntu 22.04)
# Use on Raspberry Pi OS host: ROS2 runs inside container with access to I2C and USB.
# Supports arm64 (Raspberry Pi 4) and amd64 (development).

ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}-ros-base-jammy

# Install build and runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-argcomplete \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Python deps for I2C (PCA9685) and config
RUN pip3 install --no-cache-dir smbus2 numpy pyyaml

# Workspace is mounted at /workspace/quad_ws; build on first run or via compose.
WORKDIR /workspace/quad_ws

# Default: source and run (overridden by docker-compose/run)
RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc
RUN echo "if [ -f /workspace/quad_ws/install/setup.bash ]; then source /workspace/quad_ws/install/setup.bash; fi" >> /etc/bash.bashrc

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch quad_main quad_live.launch.py"]
