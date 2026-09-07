# Autonomous Drone Station - Project Summary

**Master-level Project** | **AI-Powered Autonomous Drone with Triple-Redundant Communication**

**Version**: 1.0  
**Date**: September 7, 2026  
**Repository**: https://github.com/toura8/autonomous-drone-station

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [System Architecture](#system-architecture)
4. [Hardware Components](#hardware-components)
5. [Communication Modes](#communication-modes)
6. [AI & Perception](#ai--perception)
7. [Ground Station](#ground-station)
8. [Software Stack](#software-stack)
9. [Project Structure](#project-structure)
10. [Getting Started](#getting-started)
11. [Learning Objectives](#learning-objectives)
12. [Safety & Redundancy](#safety--redundancy)
13. [References](#references)

---

## Executive Summary

**Autonomous Drone Station** is a comprehensive, production-grade system for autonomous drone operations designed for Master's-level students. The system features:

- **Triple-redundant communication** for mission-critical reliability
- **AI-powered path planning** with obstacle avoidance
- **Lightweight onboard perception** (OpenVINO + YOLOv8-Nano)
- **Heavy-duty ground processing** (NVIDIA Jetson AGX ORIN 64GB)
- **Long-distance autonomous missions** (10-50+ km)
- **Automated failover mechanisms** with human override priority

**Target Deployment**: Hexacopter (6 motors) with 6S LiPo power, capable of carrying sensors and payload for extended autonomous missions.

---

## Project Overview

### Vision
Create an **open-source, educational platform** for autonomous aerial robotics that combines:
- Real-world hardware constraints
- Academic rigor in algorithms
- Industry-standard tools (ROS 2, Nav2, OMPL)
- Multi-layer redundancy for reliability

### Scope
- **Onboard Intelligence** (LattePanda Sigma)
  - Real-time perception (RealSense D435i)
  - Lightweight AI inference (OpenVINO)
  - Local navigation (Nav2)
  - Multi-mode communication management

- **Ground Intelligence** (NVIDIA Jetson AGX ORIN)
  - Global path planning (OMPL RRT*)
  - Video stream processing (TensorRT GPU-accelerated)
  - Mission coordination
  - LoRa telemetry aggregation (ChirpStack)

- **Flight Controller** (Cube Orange+ with ArduPilot)
  - Motor control (6x ESC via PDB)
  - Sensor fusion (IMU, barometer, magnetometer, GPS)
  - Failsafe logic & return-to-home
  - Telemetry streaming

### Success Criteria
✅ Autonomous takeoff, waypoint navigation, and landing  
✅ Obstacle detection and avoidance in real-time  
✅ Communication failover within < 5 seconds  
✅ Extended range (10+ km) via LoRa  
✅ Human pilot can override any time (Herelink)  
✅ Full telemetry logging for post-flight analysis  

---

## System Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────┐
│  DRONE IN FLIGHT (Altitude 100m)    │
├─────────────────────────────────────┤
│                                     │
│  RealSense D435i ──→ LattePanda     │
│   (Perception)      Sigma (Brain)   │
│       ↓                  ↓          │
│   Depth USB-C       ┌───┼───┐      │
│       │             │   │   │      │
│       └─────────────┤   │   │      │
│                 OpenVINO Nav2 LoRa  │
│                     │   │   │      │
│                  ┌──┴───┴───┴──┐   │
│                  ↓             ↓   │
│            [5G Quectel]   [LoRa]   │
│                  │             │   │
│  ┌───────────────┼─────────────┤   │
│  │               │             │   │
│  ↓               ↓             ↓   │
│ Cube Orange+ ← ROS 2 + MAVLink    │
│ (Autopilot)                       │
│  │                                │
│  └──→ 6x T-Motor (FOC/DShot)      │
│                                    │
└─────────────────────────────────────┘

         ↓ (5G/LoRa/Herelink) ↓

┌─────────────────────────────────────┐
│  GROUND STATION (Campus/Bureau)     │
├─────────────────────────────────────┤
│                                     │
│  [5G Gateway] ──→ Jetson AGX ORIN   │
│  (VPN Husarnet)  (TensorRT + Nav2)  │
│                          │          │
│  [LoRa Gateways] → ChirpStack ─→ │  │
│  (RAK/Dragino)   (Local Server)  ���  │
│                                  ↓  │
│  [Herelink Ground] ← All telemetry  │
│  (Pilot Screen)                     │
│                                     │
└─────────────────────────────────────┘
```

### Communication Modes Hierarchy

| Priority | Mode | Range | Bandwidth | Latency | Purpose |
|----------|------|-------|-----------|---------|---------|
| 1 (Primary) | 5G Quectel | Unlimited | 50-100 Mbps | 20-50ms | HD video, ROS 2 topics |
| 2 (Secondary) | LoRa SX1262 | 10-30 km | 50 kbps | 100-500ms | Failsafe, GPS position |
| 3 (Tertiary) | Herelink | 20+ km | 2-4 Mbps | <200ms | FPV, human override |

**Automatic Failover Logic**:
```
Mode 1 Healthy? → YES → Use 5G (full autonomy + real-time video)
                   ↓ NO
Mode 2 Healthy? → YES → Use LoRa (reduced autonomy, critical telemetry)
                   ↓ NO
Mode 3 Active → Herelink (human pilot takes direct control)
```

---

## Hardware Components

### Onboard (Drone)

#### **LattePanda Sigma** (Primary Compute)
- **Role**: Onboard AI brain, mission control, communication arbitration
- **CPU**: Intel Atom x6000 series (x86-64)
- **RAM**: 8-16 GB LPDDR5
- **Storage**: 128-512 GB NVMe SSD
- **OS**: Ubuntu 22.04 LTS + ROS 2 Humble
- **Power**: 15W TDP
- **Weight**: ~150g
- **Key Features**:
  - OpenVINO runtime for lightweight inference
  - ROS 2 native support
  - Ethernet port (micro-ROS to Cube Orange+)
  - USB-C for RealSense camera

#### **Intel RealSense D435i** (Perception)
- **Sensor Type**: RGB-D (Depth + Color + IR)
- **Resolution**: 424×240 @ 30 FPS (depth), 424×240 @ 30 FPS (color)
- **IR Emitter**: Yes (stereo pair)
- **Connectivity**: USB-C
- **Range**: 0.1m - 10m
- **Weight**: ~90g
- **Use Case**: Real-time obstacle detection, 3D scene understanding

#### **Cube Orange+** (Flight Controller)
- **Firmware**: ArduPilot (primary) / PX4 (alternative)
- **Sensors**: IMU, Barometer, Magnetometer, GPS
- **Connectivity**:
  - Ethernet (micro-ROS bridge to LattePanda)
  - UART (Telemetry to LoRa module)
  - 8x PWM outputs (6 used for ESC, 2 spare)
- **Weight**: ~50g
- **Max Current**: 100A peak draw
- **Key Functions**:
  - Motor stabilization & control
  - Sensor fusion
  - Autonomous waypoint navigation
  - Return-to-Home logic

#### **Power Distribution Board (PDB)**
- **Model**: Matek Systems or iFlight (40A per output, 6S LiPo compatible)
- **Inputs**: 1x XT90-S connector (main battery)
- **Outputs**: 6x servo connectors (6 ESC + voltage rails)
- **Features**: BEC regulators, current sensing
- **Weight**: ~30g

#### **Battery**
- **Chemistry**: 6S LiPo (3.7V per cell, nominal 22.2V)
- **Capacity**: ~5000 mAh (typical)
- **Discharge Rate**: 100C continuous
- **Weight**: ~800-1000g
- **Flight Time**: 20-30 minutes

#### **Motor & ESC Setup**
- **Motors**: T-Motor U8 Pro or similar (hexacopter)
- **ESCs**: 6x brushless ESCs (40A+) with DShot protocol
- **Connectivity**: 3-phase + signal wire to PDB
- **Weight per motor**: ~100g each
- **Total thrust**: 24+ kg (4x gravity margin)

#### **Modem 5G Quectel**
- **Model**: Quectel RG500Q-EA or RG515Q-AE
- **Connectivity**: USB 3.0
- **Bands**: 5G NR (NSA/SA) + LTE multi-band
- **Antennas**: 2x external MIMO
- **Data Limit**: 1 TB per month
- **Latency**: 20-50ms typical
- **Throughput**: 50-100 Mbps (5G), 20-30 Mbps (LTE fallback)
- **Power**: ~5W active
- **Weight**: ~150g with antennas

#### **LoRa Module SX1262**
- **Frequency**: 868 MHz (EU ISM band)
- **Modulation**: LoRa (CSS)
- **Max Payload**: 255 bytes (12 bytes telemetry)
- **Range**: 10-30+ km line-of-sight
- **Interface**: SPI to Arduino Uno
- **Tx Power**: 14 dBm (max EU)
- **Current Draw**: 140 mA (Tx), 10 mA (Rx)
- **Weight**: ~50g

#### **Arduino Uno** (LoRa Bridge)
- **Role**: Interface between Cube Orange+ telemetry and LoRa module
- **Connectivity**: UART to Cube (JST-GH), SPI to LoRa
- **Power**: 5V from Cube telemetry rail
- **Weight**: ~25g

#### **Herelink Air Unit**
- **Role**: Receive HD video + emergency control link
- **Connectivity**: MAVLink + SBUS to Cube Orange+
- **Video Input**: HDMI from FPV camera
- **Radio**: 2.4 GHz (ISM)
- **Range**: 20+ km line-of-sight
- **Weight**: ~100g

#### **RunCam/DJI FPV Camera**
- **Resolution**: 1080p @ 60 FPS
- **Output**: HDMI (native)
- **Weight**: ~30g
- **Power**: 5V USB

### Ground Station (Station Au Sol)

#### **NVIDIA Jetson AGX ORIN 64GB** (Heavy Compute)
- **GPU**: 12-core NVIDIA GPU (384 CUDA cores, 275 TFLOPS FP32)
- **CPU**: 12-core ARM (Cortex-A78AE @ 3.0 GHz)
- **Memory**: 64 GB LPDDR5X
- **Storage**: 1 TB NVMe SSD
- **Connectivity**: Gigabit Ethernet + USB 3.1 Gen1
- **Power**: 250W TDP (cooling solution required)
- **OS**: Ubuntu 22.04 LTS (ARM64)
- **CUDA/cuDNN/TensorRT**: Fully enabled
- **ROS 2**: Humble (ARM64 native)
- **Use Case**:
  - TensorRT GPU-accelerated video processing
  - Global path planning (OMPL RRT*)
  - LoRa telemetry aggregation
  - Mission coordination

#### **Herelink Ground Unit (HD BLUE)**
- **Display**: HD touchscreen
- **Radio**: 2.4 GHz receiver
- **Video**: Live HD stream + HUD overlay
- **Control**: Joysticks + buttons
- **Telemetry**: Real-time flight data
- **Range**: 20+ km LOS

#### **LoRa Gateway Network**
- **Outdoor**: RAK Wireless Outdoor Gateway
  - IP67 enclosure
  - Dual LoRa card (EU863-870)
  - Ethernet backhaul
  - Antenna gain: 2-5 dBi
  
- **Indoor**: Dragino DLOS8 or similar
  - Desktop mounting
  - Single LoRa card
  - USB/Ethernet connectivity
  - Antenna gain: 0 dBi

#### **ChirpStack Server** (Local LoRa Backend)
- **Deployment**: Docker container on Jetson or separate Linux machine
- **Database**: PostgreSQL
- **UI**: Web dashboard (localhost:8080)
- **API**: REST + MQTT
- **Functions**:
  - Device registration & management
  - Frame decoding & storage
  - Alerting & downlink messages
  - API for application integration

---

## Communication Modes

### Mode 1: 5G Quectel (Primary Link)

**Characteristics**:
- **Bandwidth**: 50-100 Mbps (5G) / 20-30 Mbps (LTE)
- **Latency**: 20-50ms
- **Range**: Unlimited (global cellular coverage)
- **Data Quota**: 1 TB per month
- **Reliability**: 99.5% uptime (typical cellular)

**Network Stack**:
```
LattePanda (5G Modem USB) 
  ↓ (Linux network stack)
Husarnet VPN Tunnel
  ↓ (Encrypted, secure)
Public 5G/LTE Network
  ↓
Jetson AGX ORIN (VPN endpoint)
```

**VPN Configuration** (Husarnet or ZeroTier):
- Provides secure, zero-config networking
- Enables direct ROS 2 topic streaming
- Survives public IP changes
- Low-overhead encryption

**Data Flows**:
- ROS 2 topics (~100 kbps typical)
- HD video stream (~2-4 Mbps)
- Telemetry (position, battery, status)
- Mission updates & commands

**Failover Trigger**: Link quality < 10 Mbps or latency > 500ms

---

### Mode 2: LoRa SX1262 (Failsafe Link)

**Characteristics**:
- **Bandwidth**: ~50 kbps (extremely constrained)
- **Latency**: 100-500ms per message
- **Range**: 10-30+ km (line-of-sight)
- **Reliability**: ~95% (weather-dependent)
- **Cost**: Campus gateway infrastructure

**Telemetry Payload** (12 bytes):
```
Byte 0-1:   GPS Latitude (Int16, -90 to +90 degrees)
Byte 2-3:   GPS Longitude (Int16, -180 to +180 degrees)
Byte 4-5:   Altitude (Int16, 0-5000m)
Byte 6-7:   Battery Voltage (UInt16, millivolts)
Byte 8-9:   Flight Status (UInt16, bitmask flags)
Byte 10-11: CRC16 Checksum
```

**Transmission Schedule**:
- Normal: Every 60 seconds (minimal overhead)
- Emergency: Every 5 seconds (increased rate)
- Heartbeat: Every 30 seconds minimum

**Gateway Backend** (ChirpStack):
```
Physical Gateway (RAK/Dragino)
  ↓ (LoRa packet reception)
ChirpStack Server (Localhost)
  ↓ (Frame decoding + routing)
Jetson AGX ORIN (Application layer)
  ↓ (Mission controller)
LattePanda Sigma (Uplink commands)
```

**Use Cases**:
- Critical position updates when 5G fails
- Drone status monitoring (battery low, etc.)
- Manual failsafe commands (RTH, land)
- Long-distance mission support

---

### Mode 3: Herelink HD (Emergency Override)

**Characteristics**:
- **Bandwidth**: 2-4 Mbps (HD video + control)
- **Latency**: <200ms (low-latency video)
- **Range**: 20+ km (line-of-sight)
- **Reliability**: 99.8% (dedicated link)
- **Control Authority**: HUMAN OVERRIDE (absolute priority)

**Data Flows**:
- HD FPV video (1080p @ 30 FPS)
- Telemetry HUD (speed, altitude, heading)
- Manual joystick commands
- Flight mode switching

**Control Hierarchy**:
```
Herelink Ground Unit (Pilot)
  ↓ (MAVLink + SBUS protocol)
Herelink Air Unit (Drone)
  ↓ (Direct Cube Orange connection)
Cube Orange+ Flight Controller
  ↓ (Motor commands)
6x ESC + Motors (Physical control)
```

**Failover Trigger**: Autonomous mission running, human can press "Override" button anytime

**Safety Features**:
- Automatic mode switch to Manual when activated
- Geofence violations trigger RTH
- Battery critical triggers auto-land
- Loss of signal triggers RTH after 30 seconds

---

## AI & Perception

### Onboard AI Pipeline (LattePanda Sigma)

**Objective**: Real-time obstacle detection for autonomous avoidance

**Stack**:
- **Framework**: OpenVINO 2023.2+
- **Model**: YOLOv8-Nano (optimized for CPU)
- **Input**: RealSense D435i depth + RGB
- **Output**: Obstacle bounding boxes + distance estimates
- **Performance**: 15 FPS @ 424×240 resolution

**Model Optimization**:
```
YOLOv8-Nano (Original PyTorch)
  ↓ (Export to ONNX)
ONNX Model
  ↓ (OpenVINO Conversion Tool)
OpenVINO IR (Intermediate Representation)
  ↓ (Inference on LattePanda CPU)
Real-time detections @ 15 FPS
```

**Detection Classes**:
- Person
- Vehicle (car, motorcycle)
- Tree / Vegetation
- Building / Structure
- Terrain (water, cliff, etc.)
- Unknown obstacles

**Integration with Nav2**:
```python
# Perception layer publishes obstacle polygons
# Nav2 costmap ingests and inflates obstacles
# Local planner avoids detected regions
# Global planner re-routes if needed
```

**ROS 2 Nodes**:
- `perception_node`: Captures RealSense frames
- `obstacle_detector`: Runs YOLOv8 inference
- `costmap_updater`: Feeds Nav2 dynamic layers

---

### Ground AI Processing (Jetson AGX ORIN)

**Objective**: High-resolution video analysis for mission planning & monitoring

**Stack**:
- **Framework**: TensorRT 8.6+ (GPU-optimized)
- **Model**: YOLOv8-Medium (more accurate than Nano)
- **Input**: HD video stream from 5G
- **Output**: Real-time detections + tracking
- **Performance**: 60 FPS @ 1920×1080 (with batching)

**GPU Acceleration**:
- CUDA cores: 384 (FP32)
- Memory bandwidth: 1 TB/s
- Throughput: 275 TFLOPS
- **Result**: 30-50x faster than CPU inference

**Processing Pipeline**:
```
5G Video Stream (2-4 Mbps H.264)
  ↓ (Decode on GPU)
Raw frames (1920×1080)
  ↓ (Resize + normalize)
TensorRT inference engine
  ↓ (Batch processing, 4 frames at a time)
Detections (person, vehicle, etc.)
  ↓ (Post-processing + NMS)
Tracked objects + trajectories
  ↓ (ROS 2 publish)
Mission controller (update waypoints)
```

**Tracking**: 
- Kalman filter for object trajectory
- Hungarian algorithm for frame-to-frame association
- Prediction of future positions

---

## Ground Station

### NVIDIA Jetson AGX ORIN Role

**Primary Responsibilities**:

1. **Global Path Planner**
   - Receives goal waypoints from operator
   - Computes optimal trajectory (OMPL RRT*)
   - Avoids no-fly zones (geofence)
   - Sends waypoints to drone via 5G
   - Updates plan dynamically based on LoRa position updates

2. **Video Processor**
   - Receives HD video stream from drone
   - Runs TensorRT inference (YOLOv8-M)
   - Detects people, vehicles, obstacles
   - Publishes tracking data to ROS 2
   - Records annotated video for post-analysis

3. **LoRa Telemetry Aggregator**
   - Collects LoRa frames via ChirpStack API
   - Decodes 12-byte telemetry packets
   - Updates drone position & status
   - Triggers alerts (battery low, signal lost, etc.)
   - Stores data for mission replay

4. **Mission Coordinator**
   - Manages mission state machine
   - Handles communication failover
   - Coordinates between different subsystems
   - Publishes ROS 2 diagnostics
   - Web UI for monitoring

### ChirpStack LoRa Backend

**Deployment**:
```bash
# On Jetson or separate Linux machine
docker-compose up -d chirpstack

# Access at localhost:8080
```

**Key Components**:
- **NS** (Network Server): Manages devices & sessions
- **AS** (Application Server): Decodes payloads, stores data
- **UI**: Web dashboard for configuration
- **API**: REST + MQTT for external integration

**Device Registration**:
```yaml
Device EUI: 0123456789ABCDEF
App Key: (32-byte secret)
Profile: "autonomous_drone"
Payload codec: (custom 12-byte telemetry)
```

**Uplink Flow**:
```
Drone LoRa Tx (12 bytes)
  ↓
Gateway Reception (RAK/Dragino)
  ↓
ChirpStack NS Decoding
  ↓
Application Server Processing
  ↓
Database Storage + ROS 2 Publish
  ↓
Jetson Mission Controller
```

---

## Software Stack

### Onboard (LattePanda Sigma)

**OS & Runtime**:
- Ubuntu 22.04 LTS (x86-64)
- ROS 2 Humble (native x86-64 build)
- Python 3.10+

**Key Libraries**:
- `rclpy`: ROS 2 Python client
- `nav2`: Navigation stack (local planner)
- `openvino-toolkit`: Inference optimization
- `opencv-python`: Image processing
- `pyrealsense2`: RealSense camera driver
- `paho-mqtt`: MQTT for 5G telemetry
- `pyserial`: Arduino LoRa interface
- `husarnet`: VPN client

**ROS 2 Nodes**:
1. `perception_node.py` - Capture RealSense streams
2. `obstacle_detector.py` - Run YOLOv8-Nano inference
3. `nav2_client.py` - Interface to Nav2 stack
4. `communication_manager.py` - Arbitrate between 5G/LoRa/Herelink
5. `fc_bridge.py` - micro-ROS to Cube Orange+
6. `mission_manager.py` - Waypoint execution logic
7. `failsafe_handler.py` - Emergency procedures

**Topics Published**:
- `/autonomous_drone/camera/depth/image_raw` - Depth frames
- `/autonomous_drone/camera/color/image_raw` - RGB frames
- `/autonomous_drone/perception/obstacles` - Detected obstacles
- `/autonomous_drone/navigation/path` - Planned local path
- `/autonomous_drone/flight/status` - Battery, position, mode
- `/autonomous_drone/communication/mode` - Active link (5G/LoRa/Herelink)

### Flight Controller (Cube Orange+)

**Firmware**:
- ArduPilot Copter 4.4+ (primary)
- Alternative: PX4 Autopilot

**Configuration**:
- 6 motor outputs (PWM)
- micro-ROS Ethernet bridge
- UART telemetry to Arduino (LoRa)
- GPS + compass calibration
- Failsafe modes: RTH, Land, Loiter

**Parameters** (key safety settings):
- `BATTERY_FAILSAFE`: 10.5V (critical)
- `FS_THR_ENABLE`: Return-to-Home on signal loss
- `FS_TIMEOUT`: 30 seconds before failsafe
- `LAND_SPEED`: 1.0 m/s (gentle landing)

### Ground Station (Jetson AGX ORIN)

**OS & Runtime**:
- Ubuntu 22.04 LTS (ARM64)
- ROS 2 Humble (arm64 native)
- CUDA 12.2 + cuDNN 8.x + TensorRT 8.x
- Python 3.10+

**Key Libraries**:
- `tensorrt`: GPU-accelerated inference
- `torch + torchvision`: Deep learning
- `ultralytics`: YOLOv8 framework
- `chirpstack_api_client`: LoRa backend integration
- `ompl`: Motion planning library
- `nav2`: Global planner

**Services**:
- ChirpStack (Docker) - LoRa NMS
- PostgreSQL (Docker) - Database
- MQTT Broker (optional) - Message distribution

### Communication Middleware

**5G Link**:
- Husarnet or ZeroTier VPN
- Provides secure LAN overlay
- Zero-config networking
- Survives IP address changes

**LoRa Link**:
- UART serial interface (9600 baud)
- Binary protocol (12-byte frames)
- Checksum validation (CRC16)
- Automatic retry on loss

**Herelink Link**:
- MAVLink protocol (Cube Orange ↔ Herelink)
- SBUS for joystick input
- Native hardware integration

---

## Project Structure

```
autonomous-drone-station/
│
├── README.md                           # Main project documentation
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── docs/
│   ├── ARCHITECTURE.md                 # Detailed system design
│   ├── HARDWARE_SETUP.md               # Wiring guide & assembly
│   ├── SIMULATION_GUIDE.md             # Gazebo/AirSim setup
│   ├── DEPLOYMENT.md                   # Field deployment checklist
│   ├── PROJECT_SUMMARY.md              # This file
│   └── references/
│       ├── path_planning_libraries.md  # OMPL, Nav2, PX4 reference
│       ├── ardupilot_missions.md       # Mission planning guide
│       └── lora_protocol.md            # LoRa frame specification
│
├── config/
│   ├── ros2_launch.yaml                # ROS 2 launch configuration
│   ├── nav2_params.yaml                # Navigation stack tuning
│   ├── drone_params.yaml               # Drone-specific parameters
│   ├── lora_config.yaml                # LoRa radio settings
│   └── rviz_config.rviz                # RViz visualization setup
│
├── src/
│   ├── ground_station/
│   │   ├── ai_planner.py               # Global path planning (OMPL)
│   │   ├── mission_manager.py          # Mission control logic
│   │   ├── global_planner.py           # ROS 2 planner node
│   │   ├── video_processor.py          # TensorRT inference
│   │   ├── chirpstack_client.py        # LoRa backend integration
│   │   └── failsafe_handler.py         # Emergency procedures
│   │
│   ├── communication/
│   │   ├── ethernet_bridge.py          # Mode 1: 5G Quectel + Husarnet
│   │   ├── lora_handler.py             # Mode 2: LoRa SX1262 interface
│   │   ├── herelink_monitor.py         # Mode 3: Herelink FPV
│   │   └── communication_manager.py    # Failover logic
│   │
│   ├── perception/
│   │   ├── perception_node.py          # RealSense camera driver
│   │   ├── obstacle_detector.py        # YOLOv8 inference
│   │   └── costmap_updater.py          # Nav2 costmap integration
│   │
│   ├── flight_controller/
│   │   ├── fc_bridge.py                # micro-ROS bridge to Cube Orange+
│   │   ├── arducopter_config.param     # ArduPilot parameter file
│   │   ├── lora_sender.ino             # Arduino LoRa interface
│   │   └── failsafe_modes.txt          # RTH, land, loiter definitions
│   │
│   └── simulation/
│       ├── sitl_launcher.py            # Gazebo SITL environment
│       ├── test_missions.py            # Automated mission tests
│       └── sim_world.world             # Gazebo world file
│
├── tests/
│   ├── test_communication.py           # Failover mechanism tests
│   ├── test_path_planning.py           # Planner algorithm validation
│   ├── test_obstacle_detection.py      # AI model inference tests
│   └── test_failsafe.py                # Emergency procedure tests
│
└── examples/
    ├── basic_mission.py                # Simple takeoff-waypoint-land
    ├── ai_obstacle_avoidance.py        # Dynamic obstacle evasion
    ├── long_distance_flight.py         # Extended range mission
    └── video_stream_analysis.py        # Process video from drone

```

---

## Getting Started

### Prerequisites

**Hardware**:
- LattePanda Sigma with Ubuntu 22.04 LTS + ROS 2 Humble
- NVIDIA Jetson AGX ORIN with CUDA 12.2+
- Cube Orange+ with ArduPilot
- 6x T-Motor motors + ESCs + PDB
- 6S LiPo battery
- All communication modules (5G, LoRa, Herelink)

**Software**:
- ROS 2 Humble desktop installation
- Python 3.10+
- OpenVINO 2023.2+
- TensorRT 8.6+
- Docker (for ChirpStack)

### Installation

**1. Clone Repository**
```bash
git clone https://github.com/toura8/autonomous-drone-station.git
cd autonomous-drone-station
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
```

**3. Setup ROS 2**
```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

**4. Configure Hardware**

Edit `config/drone_params.yaml`:
- Set communication addresses (5G modem IP, LoRa gateway URL, Herelink port)
- Calibrate camera intrinsics
- Set geofence boundaries
- Configure motor directions & ESC calibration

**5. Start Ground Station (Jetson)**
```bash
docker-compose up -d  # Start ChirpStack
python3 src/ground_station/global_planner.py
```

**6. Start Onboard (LattePanda)**
```bash
ros2 launch config/ros2_launch.yaml
```

### Simulation (No Hardware Required)

```bash
# Terminal 1: SITL simulator
python3 src/simulation/sitl_launcher.py

# Terminal 2: ROS 2 stack
ros2 launch config/ros2_launch.yaml simulation:=true

# Terminal 3: Run test mission
python3 examples/basic_mission.py --simulation
```

---

## Learning Objectives

This project is designed for Master's-level students to achieve:

### Software Engineering
- ✅ Modular architecture design (separation of concerns)
- ✅ Real-time system development (hard deadlines)
- ✅ Distributed computing (drone ↔ ground station)
- ✅ Fault tolerance & failover mechanisms
- ✅ Version control & collaborative development (Git)

### Robotics & Autonomy
- ✅ Motion planning (RRT*, Dijkstra, A*)
- ✅ Path tracking control
- ✅ Sensor fusion (IMU, GPS, vision)
- ✅ Autonomous navigation in unknown environments
- ✅ Real-time obstacle avoidance

### AI & Computer Vision
- ✅ Deep learning inference (YOLOv8)
- ✅ Model optimization (OpenVINO, TensorRT)
- ✅ GPU acceleration (CUDA, TensorRT)
- ✅ Object detection & tracking
- ✅ 3D vision (depth map processing)

### Communication & Networking
- ✅ Multi-layer redundancy (5G, LoRa, Herelink)
- ✅ Protocol design (MAVLink, LoRa frames)
- ✅ Real-time data streaming
- ✅ VPN setup & security
- ✅ Wireless link budget calculations

### Systems Integration
- ✅ Hardware-software co-design
- ✅ Power management & thermal control
- ✅ End-to-end system testing
- ✅ Debugging complex distributed systems
- ✅ Field deployment & validation

### Research Topics

**Potential Master's Thesis Directions**:

1. **Advanced Path Planning**
   - Multi-agent UAV coordination
   - Adaptive RRT* for dynamic obstacles
   - Trajectory optimization with energy constraints

2. **Robust Communication**
   - Channel coding for LoRa
   - Predictive link quality assessment
   - Hybrid communication optimization

3. **Autonomous Perception**
   - Onboard semantic segmentation
   - Real-time SLAM on RealSense
   - Few-shot learning for new obstacle classes

4. **Energy Management**
   - Predictive battery model
   - Mission planning with energy constraints
   - Optimal waypoint timing

5. **Swarm Robotics**
   - Multi-drone coordination
   - Decentralized path planning
   - Formation flying

---

## Safety & Redundancy

### Design Principles

**Redundancy at Every Layer**:
1. **Communication**: 3 independent links (5G, LoRa, Herelink)
2. **Perception**: Onboard + ground AI + manual override
3. **Control**: Autopilot + failsafe modes
4. **Power**: Single battery + graceful degradation

**Failure Modes Handled**:
- ✅ 5G link loss → LoRa failover (< 5 seconds)
- ✅ LoRa link loss → Herelink activation
- ✅ All links lost → RTH (Return-to-Home)
- ✅ Battery critical → Auto-land
- ✅ GPS loss → Inertial hold
- ✅ Motor failure → Asymmetric thrust compensation
- ✅ Obstacle not detected → Manual override via Herelink

### Pre-Flight Checklist

**Before Every Flight**:
- ☐ Battery fully charged (22.2V for 6S)
- ☐ GPS lock acquired (10+ satellites)
- ☐ All 6 motors spinning correctly
- ☐ 5G modem connected to internet
- ☐ LoRa gateway receiving signals
- ☐ Herelink video stream active
- ☐ Geofence boundaries set
- ☐ Mission file validated
- ☐ Weather conditions suitable
- ☐ No-fly zones verified

### Safety Limits

| Parameter | Value | Reason |
|-----------|-------|--------|
| Max altitude | 500m | Legal/regulatory limit |
| Max speed | 20 m/s | Stability margin |
| Max distance | 50 km | LoRa range limit |
| Battery critical | 10.5V | 1.75V per 6S cell minimum |
| Signal timeout | 30 seconds | Quick RTH activation |
| Geofence margin | 100m | Emergency recovery buffer |

---

## References

### Open-Source Projects

- **[PX4 Autopilot](https://github.com/PX4/PX4-Autopilot)** - Open-source flight control
- **[ROS 2 Navigation](https://github.com/ros-planning/navigation2)** - Nav2 stack
- **[OMPL](https://ompl.kavrakilab.org/)** - Motion planning library
- **[AirSim](https://github.com/microsoft/AirSim)** - Drone simulation
- **[ArduPilot](https://ardupilot.org/)** - Alternative flight firmware
- **[ChirpStack](https://www.chirpstack.io/)** - LoRaWAN backend

### Academic References

- Reactive Navigation and Dead-Reckoning for Autonomous Mobile Robots (Borenstein & Koren)
- Optimal Randomized Path Planning (LaValle & Kuffner - RRT algorithms)
- Deep Learning for Vision-Based Mobile Robotics (recent papers on YOLO)
- UAV Communication Networks (multi-link redundancy)

### Learning Resources

- **ROS 2 Official**: https://docs.ros.org/en/humble/
- **ArduPilot Dev**: https://ardupilot.org/dev/
- **OpenVINO Docs**: https://docs.openvino.ai/
- **TensorRT Guide**: https://docs.nvidia.com/deeplearning/tensorrt/
- **LoRaWAN Spec**: https://lora-alliance.org/

### Community Forums

- [ROS Discourse](https://discourse.ros.org/)
- [ArduPilot Forums](https://discuss.ardupilot.org/)
- [NVIDIA Jetson Forums](https://forums.developer.nvidia.com/c/ai-data-science/jetson/)
- [The Drone Enthusiast](https://discuss.ardupilot.org/)

---

## Project Metadata

| Item | Value |
|------|-------|
| **Repository** | https://github.com/toura8/autonomous-drone-station |
| **License** | MIT |
| **Target Audience** | Master's students in Robotics/AI |
| **Complexity Level** | Advanced (600+ hours expected) |
| **Team Size** | 4-6 students recommended |
| **Version** | 1.0 (Initial Release) |
| **Last Updated** | September 7, 2026 |
| **Maintainer** | toura8 |

---

## Next Steps

**Phase 1: Simulation & Validation** (Weeks 1-4)
- [ ] Set up Gazebo SITL environment
- [ ] Test Nav2 path planning
- [ ] Validate failover logic
- [ ] Write unit tests

**Phase 2: Hardware Integration** (Weeks 5-8)
- [ ] Assemble drone platform
- [ ] Calibrate sensors (camera, IMU, compass)
- [ ] Test motor control via Cube Orange+
- [ ] Validate communication links

**Phase 3: AI & Perception** (Weeks 9-12)
- [ ] Deploy YOLOv8-Nano on LattePanda
- [ ] Test real-time obstacle detection
- [ ] Integrate with Nav2 costmap
- [ ] Optimize inference performance

**Phase 4: Field Testing** (Weeks 13-16)
- [ ] Short local flights (100m radius)
- [ ] Test failover mechanisms
- [ ] Extended range flights (5-10 km)
- [ ] Mission logging & analysis

---

**End of Project Summary**

---

*For detailed technical information, refer to `docs/ARCHITECTURE.md` and other documentation files.*

*Questions? Open an issue on GitHub or contact the maintainers.*
