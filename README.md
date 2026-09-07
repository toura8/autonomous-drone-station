# Autonomous Drone Station 🚁

**Master-level project:** AI-powered ground station for autonomous drone operations with triple-redundant communication and long-distance autonomous missions.

## 🎯 Project Overview

A comprehensive system designed for student researchers to deploy autonomous drones with:

- **🤖 AI Ground Station** (LattePanda Sigma): Real-time mission planning and decision-making
- **🚁 Hexacopter with Cube Orange+**: Powerful autopilot with 6-motor control
- **📡 Triple-Redundant Communication**:
  - **Mode 1**: Ethernet (micro-ROS) - High-bandwidth, short-range
  - **Mode 2**: LoRa - Long-distance, low-bandwidth failsafe
  - **Mode 3**: Herelink - FPV video + emergency control
- **🗺️ AI-Driven Path Planning**: Autonomous trajectory generation with obstacle avoidance
- **🔋 6S LiPo Power Distribution**: Centralized PDB for 6 ESC motors

---

## 📋 Hardware Architecture

```
┌─────────────────────────────────────────────────────────┐
│         GROUND STATION (LattePanda Sigma)               │
│  • ROS 2 + Python                                       │
│  • AI/ML for path planning & mission logic              │
│  • Failsafe & telemetry aggregation                     │
└──────────────┬──────────────────────────────────────────┘
               │ Mode 1: Ethernet (JST-GH → RJ45)
               │ Mode 2: LoRa (UART via Arduino)
               │ Mode 3: Herelink (WiFi/4G)
               ▼
┌─────────────────────────────────────────────────────────┐
│          FLIGHT CONTROLLER (Cube Orange+)               │
│  • ArduPilot autopilot firmware                         │
│  • Stabilization & autonomous navigation               │
│  • 6 ESC motor control via PDB                          │
│  • Failsafe modes & RTH (Return-to-Home)               │
└──────────────┬──────────────────────────────────────────┘
               │
      ┌────────┼────────┐
      │        │        │
      ▼        ▼        ▼
   Motor1  Motor2    Motor3
   Motor4  Motor5    Motor6
```

**Key Components:**
- **Flight Controller**: Cube Orange+ (CubePilot)
- **Power Distribution**: Matek PDB (40A per output)
- **Battery**: 6S LiPo with XT90-S connectors
- **Telemetry**: CubePilot JST-GH cables → Arduino/LoRa module
- **Vision**: RunCam/DJI HDMI camera → Herelink Air Unit
- **Ground Unit**: LattePanda Sigma running ROS 2

---

## 🗺️ AI Path Planning Integration

This project integrates industry-standard autonomous path planning libraries:

### **Primary: ROS 2 Navigation Stack (Nav2)**
- **Repository**: [ros-planning/navigation2](https://github.com/ros-planning/navigation2)
- **3D Planning**: [nav2_costmap_3d](https://github.com/SteveMacenski/nav2_costmap_3d)
- **Features**: Global/local planners, costmaps, obstacle avoidance
- **Use Case**: Medium-range autonomous missions (5-20 km)

### **Secondary: Open Motion Planning Library (OMPL)**
- **Repository**: [OMPL](https://ompl.kavrakilab.org/)
- **Algorithms**: RRT*, PRM, RRT-Connect
- **Features**: Sampling-based motion planning for high-dimensional spaces
- **Use Case**: Complex trajectory optimization, swarm coordination

### **Tertiary: PX4 Autopilot Integration**
- **Repository**: [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
- **Alternative**: ArduPilot with waypoint missions
- **Features**: Built-in collision avoidance, intelligent flight modes

### **Simulation: AirSim + Gazebo**
- **AirSim** ([microsoft/AirSim](https://github.com/microsoft/AirSim)): Fast physics-based simulation
- **Gazebo**: ArduPilot SITL (Software-in-the-Loop) testing
- **Use Case**: Algorithm validation before real-world deployment

---

## 📁 Project Structure

```
autonomous-drone-station/
│
├── README.md                          # This file
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
│
├── docs/
│   ├── ARCHITECTURE.md                # System design & communication flows
│   ├── HARDWARE_SETUP.md              # Wiring guide & component specs
│   ├── SIMULATION_GUIDE.md            # Gazebo/AirSim setup
│   ├── DEPLOYMENT.md                  # Real-world deployment checklist
│   └── references/
│       ├── path_planning_libraries.md # OMPL, Nav2, PX4 guides
│       └── ardupilot_missions.md      # Mission planning reference
│
├── src/
│   ├── ground_station/
│   │   ├── ai_planner.py              # ROS 2 node for path planning
│   │   ├── mission_manager.py         # Mission control logic
│   │   └── failsafe_handler.py        # Triple-redundancy logic
│   │
│   ├── communication/
│   │   ├── ethernet_bridge.py         # Mode 1: Direct micro-ROS
│   │   ├── lora_handler.py            # Mode 2: LoRa failsafe
│   │   └── herelink_monitor.py        # Mode 3: Herelink FPV
│   │
│   ├── flight_controller/
│   │   ├── arducopter_config.param    # Cube Orange+ ArduPilot config
│   │   └── failsafe_modes.txt         # Failsafe behavior definitions
│   │
│   └── simulation/
│       ├── sitl_launcher.py           # Gazebo SITL environment
│       └── test_missions.py           # Automated mission testing
│
├── config/
│   ├── ros2_launch.yaml               # ROS 2 launch configuration
│   ├── nav2_params.yaml               # Navigation stack parameters
│   └── drone_params.yaml              # Drone-specific parameters
│
├── tests/
│   ├── test_communication.py          # Communication redundancy tests
│   ├── test_path_planning.py          # Planner algorithm tests
│   └── test_failsafe.py               # Failsafe scenario tests
│
└── examples/
    ├── basic_mission.py               # Simple waypoint mission
    ├── ai_obstacle_avoidance.py       # AI-driven obstacle detection
    └── long_distance_flight.py        # Extended range mission example
```

---

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone https://github.com/toura8/autonomous-drone-station.git
cd autonomous-drone-station
pip install -r requirements.txt
```

### 2. **Simulation (No Hardware Required)**
```bash
# Launch Gazebo SITL environment
python src/simulation/sitl_launcher.py

# In another terminal, run a test mission
python examples/basic_mission.py --simulation
```

### 3. **Real Drone Deployment**
See `docs/DEPLOYMENT.md` for hardware assembly and field testing procedures.

---

## 🔧 Communication Modes

### **Mode 1: Ethernet (Primary - Direct)**
- **Range**: < 100m (WiFi) or direct cable
- **Bandwidth**: High (~1 Gbps)
- **Latency**: Ultra-low (< 10ms)
- **Use Case**: Test flights, local operations
- **Implementation**: `src/communication/ethernet_bridge.py`

### **Mode 2: LoRa (Secondary - Long-Distance)**
- **Range**: 10-30+ km (line-of-sight)
- **Bandwidth**: Low (~50 kbps)
- **Latency**: ~100-500ms
- **Use Case**: Extended range missions, failsafe
- **Implementation**: `src/communication/lora_handler.py`
- **Hardware**: Arduino Uno + LoRa module via UART

### **Mode 3: Herelink (Tertiary - Emergency)**
- **Range**: 20+ km (4G/cellular backup)
- **Bandwidth**: Medium (~2 Mbps video stream)
- **Latency**: Variable
- **Use Case**: FPV monitoring, emergency override
- **Implementation**: `src/communication/herelink_monitor.py`

**Automatic Failover**: If Mode 1 fails → Mode 2 activates → Mode 3 activates

---

## 🤖 AI Path Planner Features

### Integrated Algorithms:
1. **ROS 2 Nav2** - Global costmap navigation
2. **OMPL RRT*** - Optimal rapid-exploring random trees
3. **ArduPilot Missions** - GPS waypoint execution
4. **Custom ML Models** - Neural networks for obstacle classification

### Example: Autonomous Obstacle Avoidance
```python
from src.ground_station.ai_planner import AutonomousPlanner
from src.communication.ethernet_bridge import EthernetBridge

planner = AutonomousPlanner(algorithm='rrt_star')
comm = EthernetBridge()

# Define goal
goal_waypoints = [(lat1, lon1, alt1), (lat2, lon2, alt2)]

# Plan path with obstacle avoidance
trajectory = planner.plan_trajectory(
    start=drone.current_position(),
    goal=goal_waypoints,
    obstacle_map=drone.get_lidar_data()
)

# Send to drone
comm.send_trajectory(trajectory)
```

---

## 📚 Learning Resources

### For Students:
- **ROS 2 Basics**: [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- **ArduPilot Developer**: [ArduPilot Docs](https://ardupilot.org/dev/)
- **Path Planning Theory**: [OMPL Documentation](https://ompl.kavrakilab.org/)
- **Drone Autonomy**: [PX4 Guide](https://docs.px4.io/main/en/)

### Papers & Research:
- Motion planning for UAVs: [IEEE Xplore](https://ieeexplore.ieee.org/)
- Obstacle avoidance algorithms: [Robotics and Autonomous Systems](https://www.sciencedirect.com/journal/robotics-and-autonomous-systems)

---

## 🛡️ Safety & Testing

⚠️ **Before any real flight:**
1. ✅ Complete `docs/DEPLOYMENT.md` checklist
2. ✅ Test all three communication modes in simulation
3. ✅ Validate failsafe modes
4. ✅ Perform local outdoor tests (short flights)
5. ✅ Gradually extend range under supervision

---

## 👥 Contributors

This is a **master's curriculum project** designed for collaborative learning.

**Your role**: Implement one or more subsystems:
- **IA Planification**: Develop advanced path planning algorithms
- **Communication**: Implement reliable multi-mode failover
- **Simulation**: Create realistic drone models in Gazebo
- **Integration**: Orchestrate all subsystems together

---

## 📜 License

MIT License - See LICENSE file for details.

---

## 🔗 Related Projects & References

- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) - Open-source flight controller
- [ROS 2 Navigation](https://github.com/ros-planning/navigation2) - Navigation stack
- [OMPL](https://ompl.kavrakilab.org/) - Motion planning library
- [ArduPilot](https://ardupilot.org/) - Alternative flight firmware
- [AirSim](https://github.com/microsoft/AirSim) - Drone simulation platform

---

**Created**: 2026 | **Master's Program** | **Hexacopter + AI Ground Station**

For questions, see the `docs/` folder or open an Issue on GitHub.
