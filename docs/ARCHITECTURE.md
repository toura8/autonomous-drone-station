# Architecture Système - Autonomous Drone Station

## Vue d'ensemble complète

```mermaid
graph TD
    classDef real fill:#DCE6F2,stroke:#1F4E79,stroke-width:2px,color:#000000;
    classDef panda fill:#C6E0B4,stroke:#568723,stroke-width:2px,color:#000000;
    classDef trans fill:#DDEBF7,stroke:#2E75B6,stroke-width:2px,color:#000000;
    classDef lora fill:#FFF2CC,stroke:#D68B38,stroke-width:2px,color:#000000;
    classDef cube fill:#FCE4D6,stroke:#C65911,stroke-width:2px,color:#000000;
    classDef jetson fill:#F2F2F2,stroke:#000000,stroke-width:2px,color:#000000;

    subgraph EQUIPEMENT_EMBARQUE_DRONE [EQUIPEMENT EMBARQUE SUR LE DRONE]
        A[Intel RealSense D435i<br>Perception IA 3D]:::real -->|Flux 3D USB-C| B[LATTEPANDA SIGMA 32GB<br>Ubuntu Linux / ROS 2 Humble<br>+ LoRa Intégré<br>+ Modem 5G Quectel Intégré]:::panda
        B -->|OpenVINO / YOLOv8-Nano| B_AI[IA Légère<br>Évitement Obstacles]:::panda
        B -->|Lien Nominal 5G| C[Modem 5G Quectel<br>(Intégré à LattePanda)]:::trans
        B -->|Lien Secours LoRa 868 MHz| D[Module LoRa SX1262<br>(Intégré à LattePanda)<br>Trame binaire 12 octets]:::lora
        B -->|micro-ROS Ethernet| E[CUBE ORANGE+<br>Autopilote ArduPilot/PX4]:::cube
        E2[Récepteur Radio Herelink Air Unit<br>Attaché au Cube Orange+]:::cube -->|MAVLink & SBUS| E
        E --> F[6x Moteurs T-Motor<br>FOC / DShot]:::jetson
    end

    subgraph RESEAUX_DE_COMMUNICATION [RESEAUX DE COMMUNICATION]
        C -->|Tunnel VPN Husarnet/ZeroTier| G[Réseau Cellulaire 5G Public]:::trans
        D -->|RF 868 MHz| H[Passerelles LoRaWAN Campus<br>Dragino Indoor + RAK WisGate Edge Pro]:::lora
    end

    subgraph INFRASTRUCTURE_SOL [STATION AU SOL]
        G -->|Flux Vidéo HD + ROS 2| I[NVIDIA JETSON AGX ORIN 64GB<br>TensorRT + Planification Globale A-B]:::jetson
        H -->|Serveur local ChirpStack| I
        I2[RADIOMANDE HERELINK GROUND UNIT HD BLUE<br>Ecran Pilote au sol]:::cube <===>|((( Liaison Radio 2.4 GHz )))<br>Priorité Humaine Absolue| E2
    end
```

---

## 🛰️ Détail des trois modes de communication

### **Mode 1 : 5G Quectel (Lien nominal - Haute bande passante)**

**Caractéristiques:**
- **Débit**: 50-100 Mbps (5G) / 20-30 Mbps (LTE fallback)
- **Latence**: 20-50ms
- **Portée**: Illimitée (couverture réseau)
- **Enveloppe**: 1 To par mois
- **Use case**: Streaming vidéo HD, ROS 2 topics en temps réel, téléopération

**Composants:**
- Modem Quectel 5G **intégré à LattePanda Sigma 32GB**
- Tunnel VPN Sécurisé (Husarnet / ZeroTier)
- Forfait 1 To illimité

**Configuration:**
```bash
# Sur LattePanda Sigma 32GB
# Voir: src/communication/5g_handler.py
$ systemctl status quectel-modem
$ ip route show  # Vérifier la route par défaut
```

**VPN Husarnet (recommandé pour drones):**
```bash
# Installation
curl https://install.husarnet.com/install.sh | sudo bash

# Configuration
sudo husarctl status
sudo husarctl announce "autonomous-drone-station"

# Python client
import husarnet
client = husarnet.HusarnetClient()
```

---

### **Mode 2 : LoRa SX1262 (Lien de secours - Longue distance)**

**Caractéristiques:**
- **Débit**: ~50 kbps (très faible)
- **Latence**: 100-500ms
- **Portée**: 10-30+ km (line-of-sight)
- **Bande**: 868 MHz (ISM EU)
- **Use case**: Failsafe critique, position GPS, telemetry simple

**Composants:**
- Module LoRa **SX1262 intégré à LattePanda Sigma 32GB**
- Trame binaire standardisée: **12 octets max**
- Passerelles LoRaWAN Campus :
  - **Dragino Indoor** (réception bâtiments)
  - **RAK WisGate Edge Pro (RAK7289)** (couverture outdoor longue distance)
- Serveur ChirpStack (décodage & stockage)

**Trame LoRa (12 bytes):**
```
Byte 0-1:   GPS Latitude (Int16, -90 to +90)
Byte 2-3:   GPS Longitude (Int16, -180 to +180)
Byte 4-5:   Altitude (Int16, 0-5000m)
Byte 6-7:   Battery Voltage (UInt16, mV)
Byte 8-9:   Flight Status (UInt16, flags)
Byte 10-11: Checksum CRC16
```

**Configuration LoRa:**
```yaml
# config/lora_config.yaml
frequency: 868000000  # Hz (EU ISM band)
bandwidth: 125000     # Hz
spreading_factor: 10  # SF7-SF12
coding_rate: 1        # 4/5 to 4/8
tx_power: 14          # dBm (max EU allowed)
```

**Code d'envoi (LattePanda - Python/ROS 2):**
```python
# src/communication/lora_handler.py
import serial
import struct

class LoRaManager:
    def __init__(self):
        # Le module LoRa est intégré à LattePanda Sigma
        self.serial_port = serial.Serial('/dev/ttyUSB0', 9600)
    
    def send_telemetry(self, lat, lon, alt, battery_mv):
        """Envoie trame LoRa 12 bytes"""
        frame = struct.pack('<hhHHHH', 
                           int(lat*1000), 
                           int(lon*1000), 
                           alt, 
                           battery_mv,
                           0,  # Flight status
                           0)  # CRC placeholder
        
        self.serial_port.write(frame)
```

**Intégration ChirpStack (sol):**
```python
# src/ground_station/chirpstack_client.py
import requests

class ChirpStackClient:
    def __init__(self, api_url="http://localhost:8080/api"):
        self.api_url = api_url
        self.token = self.authenticate()
    
    def get_device_telemetry(self, device_id):
        """Récupère dernière trame LoRa du drone"""
        response = requests.get(
            f"{self.api_url}/devices/{device_id}/frames",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()
```

---

### **Mode 3 : Herelink HD Blue (Secours radio + FPV)**

**Caractéristiques:**
- **Débit**: 2-4 Mbps (vidéo + données)
- **Latence**: < 200ms (vidéo HD)
- **Portée**: 20+ km (LoS)
- **Use case**: FPV pilote, override humain d'urgence

**Composants:**
- **Récepteur Herelink Air Unit** (attaché au Cube Orange+)
- **Station sol: Herelink Ground Unit HD BLUE** (écran pilote)
- Liaison radio 2.4 GHz
- **Priorité absolue** : Le pilote peut reprendre le contrôle à tout moment

**MAVLink & SBUS:**
```
Herelink Air Unit ←→ CUBE ORANGE+ (via MAVLink + SBUS)
                   ↓
             Autopilote ArduPilot/PX4
```

---

## 🤖 IA Embarquée : OpenVINO + YOLOv8-Nano

### **Pipeline de perception (LattePanda Sigma 32GB)**

```python
# src/perception/perception_pipeline.py
import cv2
from openvino.runtime import Core
import numpy as np

class ObstacleDetector:
    def __init__(self):
        # OpenVINO Runtime
        self.ie = Core()
        
        # Charger modèle YOLOv8-Nano optimisé
        self.model = self.ie.read_model(
            model="/path/to/yolov8n.onnx"
        )
        self.compiled_model = self.ie.compile_model(
            self.model, 
            device_name="CPU"  # LattePanda CPU x86-64
        )
        
        # RealSense camera
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 424, 240, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 424, 240, rs.format.bgr8, 30)
        self.pipeline.start(self.config)
    
    def detect_obstacles(self):
        """Détecte obstacles en temps réel"""
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        
        # Inférence YOLO
        img = np.asarray(color_frame.get_data())
        results = self.compiled_model([img])
        
        # Post-processing
        detections = self._parse_yolo_output(results)
        
        return detections, depth_frame
    
    def _parse_yolo_output(self, results):
        """Parse YOLO output et filtre obstacles"""
        # Retourner uniquement obstacles (person, car, tree, etc.)
        return filtered_detections
```

### **Intégration Nav2 (ROS 2)**

```python
# src/perception/nav2_obstacle_layer.py
from nav2_costmap_2d.costmap_2d_ros import Costmap2DROS
from geometry_msgs.msg import Polygon, Point32
import rclpy

class PerceptionLayer:
    def __init__(self):
        self.declare_parameter('topic_name', 'perception/obstacles')
        self.obstacle_sub = self.create_subscription(
            PolygonStamped,
            self.get_parameter('topic_name').value,
            self.obstacle_callback,
            10
        )
    
    def obstacle_callback(self, msg):
        """Ajoute obstacles détectés à la costmap Nav2"""
        # Publish vers Nav2 costmap
        self.costmap_pub.publish(msg)
```

---

## 📊 Station Sol : NVIDIA Jetson AGX Orin 64GB

### **Rôle: Planification Globale + Traitement Vidéo + Gestion LoRa**

**Spécifications:**
- **GPU**: 12-core NVIDIA GPU (384 CUDA cores)
- **CPU**: 12-core ARM CPU
- **RAM**: 64 GB LPDDR5
- **Stockage**: 1 TB NVMe SSD
- **Performance**: 275 TFLOPS (FP32)

**Stack Software:**
```yaml
# Jetson AGX Orin 64GB Configuration
OS: Ubuntu 22.04 LTS (ARM64)
CUDA: 12.2
cuDNN: 8.x
TensorRT: 8.x
ROS 2: Humble (arm64 build)
ChirpStack: Docker container (LoRa backend)
```

### **Pipeline Traitement Vidéo (TensorRT)**

```python
# src/ground_station/video_processing.py
import tensorrt as trt
import numpy as np
import cv2

class VideoProcessor:
    def __init__(self):
        # Charger moteur TensorRT optimisé
        self.engine = self._load_engine("/path/to/yolov8m-tensorrt.engine")
        self.context = self.engine.create_execution_context()
        
        # Streaming vidéo 5G via Husarnet VPN
        self.video_stream = self._connect_5g_stream()
    
    def process_frame(self, frame):
        """Traitement GPU-accéléré (TensorRT)"""
        # Préprocessing
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640))
        
        # Inférence TensorRT
        output = self.context.execute_v2([blob])
        
        # Post-processing
        detections = self._parse_output(output)
        
        return detections
    
    def _connect_5g_stream(self):
        """Connexion 5G VPN Husarnet"""
        # Récupérer flux vidéo HD du drone
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("drone-hostname.local", 5000))
        return sock
```

### **Planification Globale A-B (ROS 2 Nav2)**

```python
# src/ground_station/global_planner.py
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped

class GlobalPlanner:
    def __init__(self):
        self.navigator = BasicNavigator()
    
    def plan_mission(self, start_pose, goal_waypoints):
        """
        Planification A-B complète
        - A: Position initiale
        - B: Waypoints finaux
        """
        self.navigator.waitUntilNav2Active()
        
        for waypoint in goal_waypoints:
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            goal_pose.pose.position.x = waypoint[0]
            goal_pose.pose.position.y = waypoint[1]
            goal_pose.pose.orientation.w = 1.0
            
            self.navigator.goToPose(goal_pose)
            
            # Attendre arrivée
            while not self.navigator.isTaskComplete():
                time.sleep(0.1)
```

### **ChirpStack Server (LoRa Management)**

```bash
# Installation ChirpStack sur Jetson
wget https://artifacts.chirpstack.io/downloads/chirpstack-docker-compose.yml
docker-compose up -d

# API ChirpStack
curl -X GET "http://localhost:8080/api/devices" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Passerelles LoRaWAN**

```yaml
# Dragino Indoor Gateway
- Modèle: Dragino DLOS8 ou DLWS74
- Placement: Bureau/Campus indoor
- Bande: 868 MHz (EU)
- Backhaul: Ethernet ou WiFi

# RAK WisGate Edge Pro (RAK7289)
- Modèle: RAK7289
- Placement: Outdoor (toit/mât)
- Bande: 868 MHz (EU)
- Couverture: 10-30+ km longue distance
- Backhaul: Ethernet + 4G optional
```

---

## 🎯 Modes de fonctionnement

### **Nominal (5G actif)**
```
LattePanda Sigma 32GB ←[5G Quectel + ROS 2 Husarnet VPN]→ JETSON AGX ORIN 64GB (sol)
    ↓
OpenVINO/YOLO (perception embarquée)
    ↓
Nav2 local (planification locale)
    ↓
Envoi waypoints → Cube Orange+
```

### **Dégradé (5G down → LoRa)**
```
LattePanda Sigma 32GB ←[LoRa 868 MHz]→ Dragino Indoor + RAK7289 (sol)
                                            ↓
                                 ChirpStack (décodage)
                                            ↓
                             JETSON AGX ORIN 64GB (fallback mode)
                                            ↓
                        Mode autonome Nav2 + évitement obstacles
```

### **Secours (Herelink)**
```
Pilote (Herelink Ground Unit HD BLUE) ←[Herelink Radio 2.4 GHz]→ Herelink Air Unit
                                                                        ↓
                                                              Cube Orange+ Flight Controller
                                                                        ↓
                                                          Contrôle direct du drone (mode MANUAL)
```

---

## 📡 Flux de données complet

```
┌────────────────────────────────────────────────────────┐
│          DRONE EN VOL (Altitude 100m)                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  RealSense D435i ──→ LattePanda Sigma 32GB            │
│   (Perception 3D)    (Décision IA légère)             │
│       ↓              (LoRa + 5G intégrés)             │
│   Profondeur USB-C      │                              │
│       │            ┌────┼──────┐                       │
│       │            │    │      │                       │
│       │       OpenVINO Nav2  LoRa                      │
│       │            │    │      │                       │
│       └────────────┘    │      │                       │
│                         │      │                       │
│           ┌─────────────┴──────┴──────┐                │
│           │                          │                │
│           ↓                          ↓                │
│      [5G Quectel]              [LoRa SX1262]          │
│      (Intégré)                  (Intégré)             │
│           │                          │                │
│  ┌────────┼──────────────────────────┤                │
│  │        │                          │                │
│  │        ↓                          ↓                │
│  │  Herelink Air Unit ← ROS 2 Topics + MAVLink        │
│  │  (Sur Cube Orange+)                                │
│  │        │                                           │
│  ↓        ↓                                           │
│ Cube Orange+ (Autopilote ArduPilot/PX4)              │
│  │                                                   │
│  └──→ 6x T-Motor (contrôle FOC/DShot)                │
│                                                      │
└────────────────────────────────────────────────────────┘

     ↓↓↓ (5G Husarnet VPN / LoRa / Herelink) ↓↓↓

┌────────────────────────────────────────────────────────┐
│      INFRASTRUCTURE SOL (Campus / Bureau)              │
├────���───────────────────────────────────────────────────┤
│                                                        │
│  [5G Gateway] ──→ JETSON AGX ORIN 64GB                │
│  (Husarnet VPN)   (TensorRT + Nav2 Global)            │
│                           │                            │
│  [LoRa Gateways] ──→ ChirpStack ──→ │                │
│  (Dragino Indoor +      (Local)      │                │
│   RAK7289 outdoor)                   │                │
│                                      ↓                 │
│  [Herelink Ground Unit HD BLUE] ←── Tous les données  │
│  (Écran Pilote)                                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🔄 Failover Automatique

**Ordre de priorité:**
1. **Mode 5G** (nominal) - Bande passante maximale via Husarnet VPN
2. **Mode LoRa** (dégradé) - Telemétrie critique seulement via ChirpStack
3. **Mode Herelink** (secours) - Pilote reprend contrôle direct

**Logique (Python):**
```python
# src/communication/failsafe_handler.py

class CommunicationFailover:
    def __init__(self):
        self.mode_5g = Mode5G()        # Husarnet VPN
        self.mode_lora = ModeLoRa()    # ChirpStack API
        self.mode_herelink = ModeHerelink()
        self.active_mode = self.mode_5g
    
    def monitor_link_quality(self):
        while True:
            if self.mode_5g.is_healthy():
                self.active_mode = self.mode_5g
                print("✓ 5G Nominal")
            elif self.mode_lora.is_healthy():
                self.active_mode = self.mode_lora
                print("⚠ LoRa Failover")
            else:
                self.active_mode = self.mode_herelink
                print("🚨 Herelink Emergency")
            
            time.sleep(1)
```

---

## 📊 Comparaison des trois modes

| Paramètre | 5G Quectel | LoRa SX1262 | Herelink |
|-----------|-----------|-----------|----------|
| **Débit** | 50-100 Mbps | 50 kbps | 2-4 Mbps |
| **Latence** | 20-50ms | 100-500ms | <200ms |
| **Portée** | Illimitée | 10-30+ km | 20+ km |
| **VPN** | Husarnet/ZeroTier | ChirpStack | Direct radio |
| **Priorité** | Nominal | Secours | Humain |
| **Bande** | 5G/4G public | 868 MHz ISM EU | 2.4 GHz ISM |
| **Intégration** | LattePanda | LattePanda | Cube Orange+ |

---

## 🛠️ Spécifications des composants clés

### **LattePanda Sigma 32GB (Calculateur Embarqué)**
- **CPU**: Intel Atom x6000 series (x86-64)
- **RAM**: 32 GB LPDDR5
- **Stockage**: 256-512 GB NVMe SSD
- **OS**: Ubuntu 22.04 LTS
- **ROS 2**: Humble (x86-64 native)
- **Poids**: ~150g
- **Puissance**: 15W TDP
- **Intégrations**: 
  - Modem 5G Quectel
  - Module LoRa SX1262
  - RealSense D435i (USB-C)

### **Modem 5G Quectel (Intégré)**
- **Modèle**: Quectel (référence complète à préciser)
- **Interface**: Intégré à LattePanda Sigma
- **Bande**: 5G NR (NSA/SA) + LTE multi-band
- **Antenne**: 2x MIMO externe
- **Forfait**: 1 To/mois

### **Module LoRa SX1262 (Intégré)**
- **Fréquence**: 868 MHz (EU ISM band)
- **Portée**: 10-30+ km (LoS)
- **Interface**: Intégré à LattePanda Sigma
- **Trame max**: 12 bytes
- **Puissance**: 2W TX

### **Passerelles LoRaWAN Campus**
- **Dragino Indoor**: Réception bâtiments, modèle DLOS8/DLWS74
- **RAK WisGate Edge Pro (RAK7289)**: Couverture outdoor longue distance
- **Backend**: ChirpStack (serveur local sur Jetson)

### **Récepteur Herelink Air Unit**
- **Attaché au**: Cube Orange+ (Flight Controller)
- **Connexion**: MAVLink + SBUS
- **Portée**: 20+ km LOS
- **Vidéo**: HDMI input

### **Cube Orange+**
- **Firmware**: ArduPilot / PX4
- **Communication**: micro-ROS Ethernet (vers LattePanda)
- **Capteurs**: IMU, Baromètre, Magnetomètre, GPS
- **Sorties**: 8x PWM (6 utilisés pour ESC)
- **Attachements**: Herelink Air Unit (MAVLink + SBUS)
- **Poids**: ~50g

### **NVIDIA Jetson AGX Orin 64GB (Station Sol)**
- **GPU**: 12-core NVIDIA GPU (384 CUDA cores)
- **CPU**: 12-core ARM CPU (up to 3.0 GHz)
- **RAM**: 64 GB LPDDR5
- **Stockage**: 1 TB NVMe SSD
- **Networking**: Gigabit Ethernet + USB Ethernet
- **Puissance**: 250W TDP
- **Performance**: 275 TFLOPS (FP32)
- **Rôle**: Planification globale, traitement vidéo TensorRT, ChirpStack LoRa

### **Station Herelink Ground Unit HD BLUE**
- **Rôle**: Poste de pilotage sol
- **Écran**: HD touchscreen
- **Liaison radio**: 2.4 GHz Herelink
- **Affichage**: Vidéo FPV HD + telemetry HUD
- **Contrôle**: Joysticks + boutons

---

## 🔒 Sécurité & Redondance

✅ **Triple redondance de communication**
✅ **Failover automatique en cas de perte**
✅ **Tunnel VPN Husarnet/ZeroTier pour 5G**
✅ **ChirpStack pour audit & stockage LoRa**
✅ **Contrôle humain prioritaire (Herelink)**
✅ **Return-to-Home (RTH) automatique**
✅ **OpenVINO optimisé pour perception embarquée**
✅ **TensorRT GPU-accéléré pour station sol**
