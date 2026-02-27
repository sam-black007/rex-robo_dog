#!/bin/bash
# Build workspace inside container if needed, then launch the robot.
# Run from repo root: ./docker/run.sh
# Or: docker compose -f docker/docker-compose.yml run --rm zuko-ros2 ./docker/run.sh

set -e
cd /workspace/quad_ws
source /opt/ros/humble/setup.bash

if [ ! -f install/setup.bash ]; then
  echo "First run: building workspace..."
  colcon build
fi

source install/setup.bash
exec ros2 launch quad_main quad_live.launch.py
