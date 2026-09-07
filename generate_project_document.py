#!/usr/bin/env python3
"""
Script pour générer un document Word complet du projet Autonomous Drone Station
Utilise python-docx avec images et mise en forme professionnelle
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import urllib.request
import os

def add_page_break(doc):
    """Ajoute un saut de page"""
    doc.add_page_break()

def add_heading_style(doc, text, level=1):
    """Ajoute un titre avec style"""
    heading = doc.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return heading

def add_table_border(table):
    """Ajoute des bordures à un tableau"""
    tbl = table._element
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border_el = OxmlElement(f'w:{border_name}')
        border_el.set(qn('w:val'), 'single')
        border_el.set(qn('w:sz'), '4')
        border_el.set(qn('w:space'), '0')
        border_el.set(qn('w:color'), '000000')
        tblBorders.append(border_el)
    
    tblPr.append(tblBorders)

def create_project_document():
    """Crée le document Word complet"""
    
    doc = Document()
    
    # ========== PAGE DE COUVERTURE ==========
    title = doc.add_heading('STATION AUTONOME DE DRONES', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph('Projet Master - Système d\'Intelligence Artificielle et Communication Redondante')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = Pt(14)
    subtitle.runs[0].font.color.rgb = RGBColor(31, 78, 121)
    
    doc.add_paragraph()  # Espace
    
    info = doc.add_paragraph('Auteur: Toura8\nDate: Septembre 2026\nLicence: MIT')
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.runs[0].font.size = Pt(12)
    
    add_page_break(doc)
    
    # ========== TABLE DES MATIERES ==========
    doc.add_heading('Table des Matières', level=1)
    toc_items = [
        '1. Vue d\'ensemble du projet',
        '2. Architecture système complète',
        '3. Composants matériels',
        '4. Modes de communication (3x redondance)',
        '5. Intelligence Artificielle embarquée',
        '6. Station au sol (NVIDIA Jetson AGX Orin)',
        '7. Flux de données complet',
        '8. Failover automatique',
        '9. Structure du projet',
        '10. Recommandations de sécurité'
    ]
    for item in toc_items:
        p = doc.add_paragraph(item, style='List Bullet')
    
    add_page_break(doc)
    
    # ========== 1. VUE D'ENSEMBLE ==========
    doc.add_heading('1. Vue d\'Ensemble du Projet', level=1)
    
    overview_text = """La Station Autonome de Drones est un système complet de contrôle et de planification pour des missions de drones longue distance. Le projet intègre:

✓ Un hexacoptère motorisé avec autopilotage intelligent (Cube Orange+)
✓ Une station au sol IA avec LattePanda Sigma (Ubuntu + ROS 2)
✓ Triple redondance de communication (5G, LoRa, Herelink)
✓ Planification de trajectoire autonome (Nav2 + OpenVINO)
✓ Perception 3D avec RealSense D435i
✓ Failover automatique en cas de perte de lien"""
    
    doc.add_paragraph(overview_text)
    
    # Télécharger et insérer image drone
    doc.add_heading('Hexacoptère Autonome', level=2)
    doc.add_paragraph('Plateforme de vol: Hexacoptère 6x moteurs T-Motor avec Cube Orange+ comme autopilote principal.')
    
    try:
        # Image d'un hexacoptère générique (URL publique)
        img_url = 'https://raw.githubusercontent.com/toura8/autonomous-drone-station/main/docs/images/hexacopter.png'
        urllib.request.urlretrieve(img_url, '/tmp/hexacopter.png')
        if os.path.exists('/tmp/hexacopter.png'):
            doc.add_picture('/tmp/hexacopter.png', width=Inches(5))
    except:
        doc.add_paragraph('[Image du hexacoptère - URL non disponible]')
    
    add_page_break(doc)
    
    # ========== 2. ARCHITECTURE SYSTÈME ==========
    doc.add_heading('2. Architecture Système Complète', level=1)
    
    arch_text = """L'architecture globale se compose de trois domaines principaux:

A. ÉQUIPEMENT EMBARQUÉ SUR LE DRONE
   • Caméra RealSense D435i (Perception 3D)
   • LattePanda Sigma (Cerveau IA)
   • Modem 5G Quectel (Lien nominal)
   • Module LoRa SX1262 (Secours)
   • Cube Orange+ (Autopilote PX4/ArduPilot)

B. RÉSEAUX DE COMMUNICATION
   • 5G Husarnet VPN (Haute bande passante)
   • LoRaWAN 868 MHz (Longue distance)
   • Herelink 2.4 GHz (Radio de secours)

C. INFRASTRUCTURE SOL
   • NVIDIA Jetson AGX Orin (Traitement IA + Planification)
   • Serveur ChirpStack (Gestion LoRa)
   • Station Herelink (Contrôle pilote)"""
    
    doc.add_paragraph(arch_text)
    
    add_page_break(doc)
    
    # ========== 3. COMPOSANTS MATÉRIELS ==========
    doc.add_heading('3. Composants Matériels Clés', level=1)
    
    # Tableau des composants
    table = doc.add_table(rows=9, cols=3)
    table.style = 'Light Grid Accent 1'
    add_table_border(table)
    
    headers = ['Composant', 'Spécifications', 'Rôle']
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header
        table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
    
    components = [
        ['LattePanda Sigma', 'Intel Atom x6000, 8-16GB RAM, Ubuntu 22.04', 'Calculateur embarqué (IA légère)'],
        ['RealSense D435i', 'Caméra 3D USB-C, YOLO + OpenVINO', 'Perception obstacle + détection'],
        ['Modem 5G Quectel', 'RG500Q-EA, USB 3.0, 5G/LTE', 'Lien nominal Husarnet VPN'],
        ['Module LoRa SX1262', '868 MHz ISM, 10-30 km portée', 'Failsafe critique'],
        ['Cube Orange+', 'PX4/ArduPilot, micro-ROS Ethernet', 'Autopilote principal'],
        ['6x T-Motor + ESC', 'FOC/DShot, contrôle décentralisé', 'Propulsion hexacoptère'],
        ['NVIDIA Jetson AGX Orin', '12-core GPU, 64GB RAM, 275 TFLOPS', 'Station sol (Planification globale)'],
        ['Herelink HD Blue', 'Video HD + MAVLink, 2.4 GHz', 'Contrôle d\'urgence pilote']
    ]
    
    for i, component in enumerate(components, 1):
        row = table.rows[i]
        for j, cell_text in enumerate(component):
            row.cells[j].text = cell_text
    
    add_page_break(doc)
    
    # ========== 4. MODES DE COMMUNICATION ==========
    doc.add_heading('4. Triple Redondance de Communication', level=1)
    
    # Mode 1: 5G
    doc.add_heading('Mode 1: 5G Quectel (Lien Nominal - Haute Bande Passante)', level=2)
    mode1_text = """Caractéristiques:
• Débit: 50-100 Mbps (5G) / 20-30 Mbps (LTE fallback)
• Latence: 20-50 ms
• Portée: Illimitée (selon couverture réseau)
• Enveloppe: 1 To par mois
• Tunneling: Husarnet/ZeroTier VPN sécurisé
• Cas d'usage: Streaming vidéo HD, ROS 2 topics temps réel, téléopération
• Implémentation: src/communication/5g_handler.py"""
    doc.add_paragraph(mode1_text)
    
    # Mode 2: LoRa
    doc.add_heading('Mode 2: LoRa SX1262 (Lien de Secours - Longue Distance)', level=2)
    mode2_text = """Caractéristiques:
• Débit: ~50 kbps (très faible mais fiable)
• Latence: 100-500 ms
• Portée: 10-30+ km (line-of-sight)
• Bande: 868 MHz (ISM EU)
• Trame max: 12 octets binaires standardisés
• Cas d'usage: Failsafe critique, position GPS, telemetry simple
• Intégration: ChirpStack (serveur local de décodage)
• Implémentation: src/communication/lora_handler.py"""
    doc.add_paragraph(mode2_text)
    
    doc.add_heading('Structure de Trame LoRa (12 bytes)', level=3)
    lora_frame = """Byte 0-1:   GPS Latitude (Int16, -90 to +90)
Byte 2-3:   GPS Longitude (Int16, -180 to +180)
Byte 4-5:   Altitude (Int16, 0-5000m)
Byte 6-7:   Battery Voltage (UInt16, mV)
Byte 8-9:   Flight Status (UInt16, flags)
Byte 10-11: Checksum CRC16"""
    doc.add_paragraph(lora_frame)
    
    # Mode 3: Herelink
    doc.add_heading('Mode 3: Herelink HD Blue (Secours Radio + FPV)', level=2)
    mode3_text = """Caractéristiques:
• Débit: 2-4 Mbps (vidéo + données)
• Latence: < 200 ms (vidéo HD)
• Portée: 20+ km (line-of-sight)
• Fréquence: 2.4 GHz ISM
• MAVLink + SBUS vers Cube Orange+
• Priorité absolue: Le pilote peut reprendre contrôle à tout moment
• Cas d'usage: FPV monitoring, override d'urgence
• Implémentation: src/communication/herelink_monitor.py"""
    doc.add_paragraph(mode3_text)
    
    add_page_break(doc)
    
    # ========== 5. INTELLIGENCE ARTIFICIELLE ==========
    doc.add_heading('5. Intelligence Artificielle Embarquée', level=1)
    
    ai_text = """La perception et la décision autonome utilisent:

A. MODÈLE: OpenVINO + YOLOv8-Nano (Embarqué sur LattePanda Sigma)
   • Détection d'obstacles en temps réel
   • Classification: personne, voiture, arbre, bâtiment
   • Latence: ~50-100 ms par frame
   • Optimisation CPU: OpenVINO quantisée

B. PLANIFICATION: ROS 2 Navigation Stack (Nav2)
   • Costmaps 2D/3D globales et locales
   • Planificateurs: Dijkstra, A*, RRT*
   • Intégration obstacle temps réel
   • Autonomie complète en perte de lien 5G

C. APPRENTISSAGE: Modèles ML pour classification obstacles
   • Entraînement hors-ligne (GPU Jetson Sol)
   • Déploiement en temps réel (CPU LattePanda)
   • Dataset: COCO + données custom drone"""
    doc.add_paragraph(ai_text)
    
    add_page_break(doc)
    
    # ========== 6. STATION AU SOL ==========
    doc.add_heading('6. Station Sol: NVIDIA Jetson AGX Orin', level=1)
    
    jetson_text = """Spécifications:
• GPU: 12-core NVIDIA (384 CUDA cores)
• CPU: 12-core ARM (jusqu'à 3.0 GHz)
• RAM: 64 GB LPDDR5
• Stockage: 1 TB NVMe SSD
• Performance: 275 TFLOPS (FP32)
• Networking: Gigabit Ethernet + USB Ethernet

Rôles:
1. Planification Globale A-B: Génération de trajectoires longue distance
2. Traitement Vidéo: TensorRT GPU-accéléré pour analyse temps réel
3. Gestion ChirpStack: Décodage et stockage des trames LoRa
4. Pilotage et Monitoring: Interface avec Herelink Ground Unit

Stack Software:
• OS: Ubuntu 22.04 LTS (ARM64)
• CUDA: 12.2 + cuDNN 8.x
• TensorRT: 8.x (inférence optimisée)
• ROS 2: Humble (build ARM)"""
    
    doc.add_paragraph(jetson_text)
    
    add_page_break(doc)
    
    # ========== 7. FLUX DE DONNÉES ==========
    doc.add_heading('7. Flux de Données Complet', level=1)
    
    doc.add_paragraph('DRONE EN VOL (Altitude 100m):')
    flow_drone = """
    RealSense D435i ──→ LattePanda Sigma (ROS 2)
     (Perception 3D)    (Décision IA légère)
         │                   │
      Profondeur       OpenVINO + Nav2 + LoRa
      USB-C               │
         │           ┌─────┼──────┐
         └───────────┤     │      │
                     ↓ 5G ↓ LoRa ↓
               Cube Orange+ (Autopilote)
                     │
               6x T-Motor (Contrôle FOC/DShot)"""
    doc.add_paragraph(flow_drone)
    
    doc.add_paragraph('Puis transmission via 5G / LoRa / Herelink vers:')
    flow_ground = """
    INFRASTRUCTURE SOL:
    
    [5G Gateway] ──→ JETSON AGX ORIN
    (Husarnet VPN)   (TensorRT + Nav2 Global)
    
    [LoRa Gateways] ──→ ChirpStack ──→ Tous telemetry
    (RAK/Dragino)      (Serveur Local)
    
    [Herelink Ground Unit] ←── Flux vidéo HD + Commandes"""
    doc.add_paragraph(flow_ground)
    
    add_page_break(doc)
    
    # ========== 8. FAILOVER AUTOMATIQUE ==========
    doc.add_heading('8. Failover Automatique', level=1)
    
    failover_text = """Ordre de Priorité:
1. MODE 5G (Nominal) 
   → Bande passante maximale via Husarnet VPN
   → Streaming vidéo HD, ROS 2 topics temps réel
   
2. MODE LORA (Dégradé)
   → Activation si 5G down > 2 secondes
   → Télémétrie critique uniquement
   → Mode autonome Nav2 avec évitement d'obstacles
   
3. MODE HERELINK (Secours)
   → Activation en dernier recours
   → Pilote reprend contrôle direct
   → Vidéo FPV en temps réel

Logique de Monitoring:
• Vérification de la qualité du lien toutes les 100 ms
• Timeouts configurables par mode
• Retour automatique au mode 5G si lien rétabli
• Logging de tous les switchovers pour audit"""
    
    doc.add_paragraph(failover_text)
    
    add_page_break(doc)
    
    # ========== 9. STRUCTURE DU PROJET ==========
    doc.add_heading('9. Structure du Projet', level=1)
    
    structure = """autonomous-drone-station/
│
├── docs/
│   ├── ARCHITECTURE.md          ← Architecture système complète
│   ├── HARDWARE_SETUP.md        ← Guide de câblage
│   ├── SIMULATION_GUIDE.md      ← Gazebo/AirSim
│   └── DEPLOYMENT.md            ← Checklist terrain
│
├── src/
│   ├── ground_station/
│   │   ├── ai_planner.py        ← ROS 2 node (Nav2)
│   │   ├── mission_manager.py   ← Contrôle mission
│   │   └── failsafe_handler.py  ← Triple redondance
│   │
│   ├── communication/
│   │   ├── 5g_handler.py        ← Mode 1 (Ethernet)
│   │   ├── lora_handler.py      ← Mode 2 (LoRa)
│   │   └── herelink_monitor.py  ← Mode 3 (Herelink)
│   │
│   ├── flight_controller/
│   │   ├── arducopter_config.param
│   │   └── failsafe_modes.txt
│   │
│   └── simulation/
│       ├── sitl_launcher.py     ← Gazebo SITL
│       └── test_missions.py     ← Tests automatisés
│
├── config/
│   ├── ros2_launch.yaml
│   ├── nav2_params.yaml
│   └── drone_params.yaml
│
├── tests/
│   ├── test_communication.py
│   ├── test_path_planning.py
│   └── test_failsafe.py
│
├── examples/
│   ├── basic_mission.py
│   ├── ai_obstacle_avoidance.py
│   └── long_distance_flight.py
│
└── README.md"""
    
    doc.add_paragraph(structure)
    
    add_page_break(doc)
    
    # ========== 10. TABLEAU COMPARATIF ==========
    doc.add_heading('10. Comparaison des Trois Modes de Communication', level=1)
    
    table_modes = doc.add_table(rows=9, cols=4)
    table_modes.style = 'Light Grid Accent 1'
    add_table_border(table_modes)
    
    headers_modes = ['Paramètre', '5G Quectel', 'LoRa SX1262', 'Herelink']
    for i, header in enumerate(headers_modes):
        table_modes.rows[0].cells[i].text = header
        table_modes.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
    
    modes_data = [
        ['Débit', '50-100 Mbps', '50 kbps', '2-4 Mbps'],
        ['Latence', '20-50 ms', '100-500 ms', '<200 ms'],
        ['Portée', 'Illimitée', '10-30 km', '20+ km'],
        ['Protocol', 'Husarnet VPN', 'ChirpStack', 'Direct radio'],
        ['Priorité', 'Nominal', 'Secours', 'Humain'],
        ['Bande', '5G/4G public', '868 MHz ISM', '2.4 GHz ISM'],
        ['Capacité', '1 To/mois', '50+ msgs/jour', 'Video HD + data'],
        ['Cas d\'usage', 'Temps réel', 'Failsafe', 'FPV + override']
    ]
    
    for i, row_data in enumerate(modes_data, 1):
        row = table_modes.rows[i]
        for j, cell_text in enumerate(row_data):
            row.cells[j].text = cell_text
    
    add_page_break(doc)
    
    # ========== RECOMMANDATIONS SÉCURITÉ ==========
    doc.add_heading('11. Recommandations de Sécurité & Testing', level=1)
    
    safety_text = """⚠️ AVANT TOUT VOL RÉEL:

✅ Phase 1 - Préparation (1-2 semaines)
   □ Compléter docs/DEPLOYMENT.md
   □ Tester tous les 3 modes de communication en simulation
   □ Valider les failsafe modes (RTH automatique)
   □ Inspecter le câblage mécanique et électrique

✅ Phase 2 - Tests en Simulation (1 semaine)
   □ Lancer Gazebo SITL avec py src/simulation/sitl_launcher.py
   □ Exécuter python examples/basic_mission.py --simulation
   □ Tester failover Mode 1 → Mode 2 → Mode 3
   □ Valider obstacle avoidance avec YOLO

✅ Phase 3 - Tests Locaux (2-3 semaines)
   □ Premiers vols en Mode Ethernet uniquement (< 50m)
   □ Tester stabilité et response autopilot
   □ Vérifier perception obstacle RealSense
   □ Tester failsafe: coupure moteur simulée

✅ Phase 4 - Étendre la Portée (2-3 semaines)
   □ Premiers vols en Mode 5G (200-500m)
   □ Tester Husarnet VPN latency impact
   □ Vérifier failover vers LoRa
   □ Tests avec Herelink en backup

✅ Phase 5 - Missions Longue Distance (3-4 semaines)
   □ Vols autonomes 1-5 km (Éthermet failover LoRa)
   □ Tester planification Nav2 avec obstacles réels
   □ Valider ChirpStack logging LoRa
   □ Performances thermaure: CPU/GPU/Battery

✨ RECOMMANDATIONS OPÉRATIONNELLES:
• Toujours tester en simulation avant terrain
• Avoir un pilote qualifié au contrôle Herelink
• Logger TOUS les télemetry pour post-analyse
• Augmenter progressivement distance et complexité
• Ne jamais compter sur une seule communication
• Maintenir failsafe Mode 3 opérationnel en permanence"""
    
    doc.add_paragraph(safety_text)
    
    add_page_break(doc)
    
    # ========== PAGE FINALE ==========
    doc.add_heading('Conclusion', level=1)
    
    conclusion = """La Station Autonome de Drones représente un système d'ingénierie complet intégrant:

✨ Robotique Embarquée: Hexacoptère + Autopilote PX4/ArduPilot
✨ Intelligence Artificielle: OpenVINO, YOLOv8, ROS 2 Nav2
✨ Communication Redondante: 5G + LoRa + Herelink
✨ Traitement Haute Performance: NVIDIA Jetson AGX Orin
✨ Sécurité & Failover: Triple redondance automatique

Ce projet est idéal pour les étudiants de master souhaitant:
• Approfondir l'autonomie robotique
• Maîtriser les systèmes embarqués temps réel
• Implémenter des algorithmes IA en production
• Gérer la redondance critique en robotique

Pour des questions supplémentaires, consultez:
📄 GitHub: https://github.com/toura8/autonomous-drone-station
📚 Documentation: docs/ARCHITECTURE.md
🚁 Simulations: python src/simulation/sitl_launcher.py

---
Licence: MIT
Auteur: Toura8
Septembre 2026"""
    
    doc.add_paragraph(conclusion)
    
    # ========== SAUVEGARDER ==========
    output_path = 'Autonomous_Drone_Station_Project_Description.docx'
    doc.save(output_path)
    
    print(f"✅ Document généré: {output_path}")
    print(f"📄 Format: Word (.docx)")
    print(f"📊 Pages: ~15-20")
    print(f"🎨 Contenu: Tableaux + Mise en forme professionnelle")

if __name__ == '__main__':
    create_project_document()
