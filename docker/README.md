# Zuko Robot – ROS2 in Docker

ROS2 Humble runs inside an **Ubuntu 22.04 container** on a **Raspberry Pi OS** host. The container has access to the Pi’s I2C (PCA9685) and USB (gamepad) so the robot works the same as a native install, with minimal host setup.

## Quick start (from repo root)

```bash
# Build the Docker image
docker compose -f docker/docker-compose.yml build

# Build the ROS2 workspace (first time only)
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && colcon build"

# Run the robot
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 ./docker/run.sh
```

Or in one shot (builds workspace if needed, then launches):

```bash
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && ( [ -f install/setup.bash ] || colcon build ) && source install/setup.bash && ros2 launch quad_main quad_live.launch.py"
```

## Requirements

- **Host:** Raspberry Pi OS (64-bit) on Raspberry Pi 4
- **Docker:** Docker and Docker Compose installed on the Pi
- **I2C:** Enabled (e.g. `raspi-config` → Interfacing Options → I2C)
- **Hardware:** PCA9685 and gamepad connected as in the main setup guide

## Why Docker?

- **Replication:** Same Ubuntu + ROS2 image on any Pi; no manual ROS2 install.
- **Isolation:** No conflict with Pi OS packages; easy to rebuild or roll back.
- **Host access:** `network_mode: host` and `privileged: true` give the container I2C and USB so ROS2 talks to the hardware like a native install.

## Files

- `Dockerfile` – Ubuntu 22.04 + ROS2 Humble + Python deps (smbus2, numpy, pyyaml).
- `docker-compose.yml` – Builds image, mounts repo, passes through devices, runs from `quad_ws`.
- `run.sh` – Builds workspace if needed and launches `quad_live.launch.py`.

## Rebuilding after code changes

```bash
# Rebuild ROS2 workspace only
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && colcon build"

# Rebuild Docker image (e.g. after Dockerfile change)
docker compose -f docker/docker-compose.yml build --no-cache
```

## Shell for debugging

```bash
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash
# Inside container:
source /opt/ros/humble/setup.bash && source install/setup.bash
ros2 launch quad_main quad_live.launch.py
# or: ros2 run quad_gamepad quad_gamepad ...
```

## Servo calibration

Calibration runs inside the container with access to I2C:

```bash
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws/src/quad_motors/quad_motors && ./servo_calibration.py"
```

See **INSTALL_RPI.md** and **ROBOT_SETUP_GUIDE.md** for full setup (Pi OS, Docker install, clone, build, run).
