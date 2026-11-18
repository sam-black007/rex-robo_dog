# rex-robo_dog - A Quadruped Robot Dog

**rex-robo_dog** is a 12-DOF quadruped robot dog built on **ROS2 Humble** and running on a **Raspberry Pi 4/5** with Raspberry Pi OS as the host. ROS2 runs inside a **Docker container** (Ubuntu 22.04) for a minimal, repeatable setup. Control is via a **PS4/PS5 controller**.

> Status: **Development** — Frame v2.2 is being tested and is nearly ready for replication.

## Watch rex-robo_dog Walk

See rex-robo_dog in action below:

<video src="assets/walking.mp4" autoplay loop muted playsinline width="100%">
  Your browser does not support the video tag.
</video>

> Add your own walking video: place an MP4 (or GIF) file at `assets/walking.mp4` and it will appear here automatically.

## Upgrades

This repository is an upgraded version of the original Rex/Zuko quadruped project:

- **Hardware:** Upgraded from **Raspberry Pi 3** to **Raspberry Pi 4/5**.
- **Software:** Migrated from **ROS1 to ROS2**, and upgraded **ROS2 Foxy to ROS2 Humble**.

## Features

- 12 RC servos (3 per leg: hip, upper leg, lower leg) driven by a **PCA9685** I2C PWM driver
- **Linked-leg inverse kinematics** for a Spot-Mini-Mini-style quadruped
- **Bezier curve gait generation** for smooth walking
- PS4/PS5 controller teleoperation (wired or Bluetooth)
- Per-servo calibration tool with YAML configuration
- PyBullet-based simulation environment
- Custom expansion board and battery boards (see hardware docs)
- Runs fully containerized: Raspberry Pi OS host + ROS2 Humble in Docker

## Repository Structure

```
rex-robo_dog/
├── assets/                 # Media (walking video, photos, etc.)
│   └── walking.mp4         # Walking demo video (add your own)
├── quad_ws/                # ROS2 workspace (main codebase)
│   └── src/
│       ├── quad_main/        # Main control: kinematics, gaits, commander
│       ├── quad_motors/      # Servo control via PCA9685 + calibration
│       ├── quad_gamepad/     # PS4/PS5 controller input
│       ├── quad_interfaces/  # Custom ROS2 messages
│       ├── quad_simulation/  # PyBullet simulation
│       ├── quad_urdf/        # URDF robot description
│       ├── quad_sensors/     # Sensor handling (IMU, foot sensors, etc.)
│       └── quad_output/      # Peripheral output (LEDs, NeoPixels, etc.)
├── docker/                 # Docker image, compose file, run script
├── scripts/                # Standalone scripts
│   └── kinematics-simulation/# Forward/inverse kinematics tests
├── LICENSE                 # MIT License
└── README.md
```

## Quick Start (Raspberry Pi)

### 1. Install Raspberry Pi OS

Install **Raspberry Pi OS (Bookworm, 64-bit)** and enable I2C:

```bash
sudo raspi-config   # Interfacing Options -> I2C -> Enable
```

Verify the PCA9685 is detected at `0x40`:

```bash
sudo i2cdetect -y 1
```

### 2. Install Docker

```bash
sudo apt update
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # log out and back in
sudo apt install -y docker-compose-plugin
```

### 3. Clone and Build

```bash
git clone --filter=blob:none --sparse https://github.com/sam-black007/rex-robo_dog.git
cd rex-robo_dog && git sparse-checkout set quad_ws scripts docker
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm rex-robo_dog-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws && colcon build"
```

### 4. Run

Connect the PCA9685, servos, power, and a PS4/PS5 controller (USB or Bluetooth), then:

```bash
docker compose -f docker/docker-compose.yml run --rm rex-robo_dog-ros2
```

The `docker/run.sh` script sources ROS2, builds the workspace if needed, and launches `quad_main quad_live.launch.py`.

### 5. Servo Calibration

```bash
docker compose -f docker/docker-compose.yml run --rm rex-robo_dog-ros2 bash -c "source /opt/ros/humble/setup.bash && cd /workspace/quad_ws/src/quad_motors/quad_motors && ./servo_calibration.py"
```

Calibration results are written to `quad_ws/src/quad_motors/config/servo_parameters.yaml` (persisted on the host).

## Running Locally (without Docker)

See `quad_ws/dev-notes/ros2-setup.txt` and `ros2-commands.txt` for native ROS2 Humble setup on desktop or the Pi.

## ROS2 Workspace Overview

| Package          | Purpose                                              |
|------------------|------------------------------------------------------|
| `quad_main`      | ROS2 wrapper, commander, inverse kinematics, Bezier/dingo gaits, joystick interpretation |
| `quad_motors`    | Servo control node, PCA9685 driver, calibration tool |
| `quad_gamepad`   | Gamepad node publishing `sensor_msgs/Joy`            |
| `quad_interfaces`| `JointAngles` and `Outputs` custom messages          |
| `quad_simulation`| PyBullet physics simulation and Gym environment      |
| `quad_urdf`      | URDF/Xacro robot description and RViz config         |
| `quad_sensors`   | IMU and foot-sensor handling                         |
| `quad_output`    | LED / NeoPixel output control                        |

### Key Topics

- `/joy` — gamepad input (`sensor_msgs/Joy`)
- `/joint_angles` — joint angle commands (`quad_interfaces/JointAngles`)

## Hardware

- **Computer:** Raspberry Pi 4 (4 GB/8 GB) or Raspberry Pi 5
- **Actuators:** 12x RC servos, controlled via PCA9685 I2C PWM driver (`0x40`)
- **Controller:** PS4/PS5 (USB or Bluetooth)
- **Boards:** Custom expansion board and 8x 18650 battery board with onboard BMS

## License

This project is released under the **MIT License** — see [LICENSE](LICENSE).

The simulation, kinematics, Bezier curves, and machine learning are largely based on **[spot_mini_mini](https://github.com/OpenQuadruped/spot_mini_mini)** (MIT, © 2020 Maurice Rahme), which is in turn based on [SpotMicroAI](https://spotmicroai.readthedocs.io/en/latest/). The frame and leg-linkage design was inspired by [Baris Alp's Kangel robot dog](https://grabcad.com/library/diy-quadruped-robot-1).

## Communities

- SpotMicroAI Discord: https://discord.gg/m5fsENhT
- Quadrupedalism: https://quadrupedalism.com/

## About

rex-robo_dog - a 12-DOF quadruped robot dog. ROS2 Humble in Docker on a Raspberry Pi 4/5 (upgraded from Pi 3, migrated from ROS1). Joint hardware & software project.

### Topics

[docker](/topics/docker)[hardware](/topics/hardware)[kinematics](/topics/kinematics)[pca9685](/topics/pca9685)[quadruped](/topics/quadruped)[raspberry-pi](/topics/raspberry-pi)[robot-dog](/topics/robot-dog)[robotics](/topics/robotics)[ros2](/topics/ros2)[ros2-humble](/topics/ros2-humble)[software](/topics/software)
