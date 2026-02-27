# Zuko Robot – Raspberry Pi Installation (Pi OS + Docker)

This guide sets up the Zuko quadruped on **Raspberry Pi OS** with **ROS2 Humble running in Docker** (Ubuntu 22.04 container). The container has access to the Pi’s I2C and USB so the robot works the same as a native install, with minimal and repeatable setup on any Raspberry Pi.

## Overview

- **Host OS:** Raspberry Pi OS (64-bit) – primary OS on the Pi
- **ROS2:** Runs inside a Docker container (Ubuntu 22.04 + ROS2 Humble)
- **Hardware access:** I2C (PCA9685) and USB (gamepad) are passed into the container so ROS2 controls the robot seamlessly

## Prerequisites

- Raspberry Pi 4 (4GB or 8GB recommended)
- MicroSD card (32GB or larger, Class 10)
- USB-C power supply (5V, 3A minimum)
- Network connection (Ethernet or Wi-Fi)
- PCA9685 and servos (see ROBOT_SETUP_GUIDE.md for wiring)

---

## Step 1: Install Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.org/software/).
2. Choose **Raspberry Pi OS (64-bit)** (recommended) or 32-bit.
3. Write the image to the microSD card, then boot the Pi.
4. Complete the initial setup (language, Wi‑Fi, user, password).
5. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Step 2: Enable I2C (for PCA9685)

1. Run:
   ```bash
   sudo raspi-config
   ```
2. Go to **Interfacing Options → I2C → Enable**.
3. Reboot if prompted:
   ```bash
   sudo reboot
   ```
4. After reboot, check I2C (PCA9685 should appear at `0x40`):
   ```bash
   sudo i2cdetect -y 1
   ```

---

## Step 3: Install Docker

1. Install Docker and Docker Compose:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   ```
2. Log out and back in (or reboot) so the `docker` group applies.
3. Test:
   ```bash
   docker run hello-world
   ```

---

## Step 4: Clone the Repository

From your home directory:

**Option A – Sparse clone (recommended):**
```bash
cd ~
git clone --filter=blob:none --sparse https://github.com/MrTheMech/rex-zuko-try.git
cd rex-zuko-try
git sparse-checkout set quad_ws docs scripts docker
```

**Option B – Full clone:**
```bash
cd ~
git clone https://github.com/MrTheMech/rex-zuko-try.git
cd rex-zuko-try
```

---

## Step 5: Build the Docker Image and ROS2 Workspace

From the **repo root** (`rex-zuko-try`):

1. Build the ROS2 Docker image:
   ```bash
   docker compose -f docker/docker-compose.yml build
   ```

2. Build the ROS2 workspace inside the container (first time only):
   ```bash
   docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && colcon build"
   ```

---

## Step 6: Run the Robot

1. Connect hardware: PCA9685, servos, power, and PS4/PS5 controller (USB or Bluetooth).
2. From the repo root:
   ```bash
   docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash docker/run.sh
   ```

   Or use the default command:
   ```bash
   docker compose -f docker/docker-compose.yml run --rm zuko-ros2
   ```

The `run.sh` script sources ROS2, builds the workspace if needed, and runs `ros2 launch quad_main quad_live.launch.py`.

---

## Step 7: Bluetooth for Wireless Controller (Optional)

On the **host** (Raspberry Pi OS):

1. Install and enable Bluetooth:
   ```bash
   sudo apt install -y pi-bluetooth
   sudo reboot
   ```
2. Pair the controller:
   ```bash
   sudo bluetoothctl
   ```
   Then: `scan on` → put controller in pairing mode (e.g. Share + PS) → `connect <MAC>` → `trust <MAC>` → `exit`.
3. Confirm the gamepad is visible:
   ```bash
   ls /dev/input/js*
   ```

The Docker container uses the host’s network and devices, so the gamepad is available inside the container.

---

## Step 8: Servo Calibration

Run calibration **inside the container** (it has I2C access):

```bash
cd ~/rex-zuko-try
docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws/src/quad_motors/quad_motors && chmod +x servo_calibration.py && ./servo_calibration.py"
```

Calibration writes to `quad_ws/src/quad_motors/config/servo_parameters.yaml` (in the mounted repo), so it persists on the host.

---

## Step 9: Rebuild After Code Changes

From repo root:

- Rebuild only the ROS2 workspace:
  ```bash
  docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws && colcon build"
  ```

- Rebuild the Docker image (e.g. after editing `docker/Dockerfile`):
  ```bash
  docker compose -f docker/docker-compose.yml build --no-cache
  ```

---

## Troubleshooting

### I2C not visible in container

- On the host, enable I2C and check: `sudo i2cdetect -y 1`.
- Ensure you run the container with the compose file (it uses `privileged: true` and `network_mode: host` so devices are available).

### Controller not detected

- On the host: `ls /dev/input/js*`. If no device, pair the controller (Step 7).
- Use wired USB first to confirm the stack works, then try Bluetooth.

### Docker permission denied

- Ensure your user is in the `docker` group: `sudo usermod -aG docker $USER`, then log out and back in.

### “install/setup.bash not found”

- Build the workspace once (Step 5, second command). After that, `run.sh` will find it.

---

## Quick Reference

| Task              | Command (from repo root) |
|-------------------|---------------------------|
| Build image       | `docker compose -f docker/docker-compose.yml build` |
| Build workspace   | `docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws && colcon build"` |
| Run robot         | `docker compose -f docker/docker-compose.yml run --rm zuko-ros2` |
| Shell in container| `docker compose -f docker/docker-compose.yml run --rm zuko-ros2 bash` |
| Servo calibration| See Step 8 above |

---

## Additional Resources

- **Docker details:** `docker/README.md`
- **Full setup (hardware + software):** `ROBOT_SETUP_GUIDE.md`
- **Project overview:** `PROJECT_OVERVIEW.md`
- **PS5 controller:** `PS5_CONTROLLER_GUIDE.md`

---

**Note:** This guide uses Raspberry Pi OS as the primary OS and ROS2 Humble in Docker. For a native Ubuntu + ROS2 install on the Pi, see `quad_ws/dev-notes/ros2-setup.txt` (legacy).
