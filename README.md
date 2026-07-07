# NIT Agartala AI-HCI-LAB — Summer Internship 2026

![Status](https://img.shields.io/badge/status-active-success)
![Duration](https://img.shields.io/badge/duration-7%20weeks-blue)
![Program](https://img.shields.io/badge/program-Summer%20Project%20%26%20Skill%202026-lightgrey)

**Intern:** Anurag Debnath and Abhilash Ghosh \
**Supervisor:** Dr. Suman Deb  
**Institution:** NIT Agartala — CSE Department AI HCI Lab  
**Duration:** June 1, 2026 – July 20, 2026 (7 Weeks)  
**Program:** Summer Project and Skill Program 2026  

---

## Program Modules

| Module | Topic | Status |
|--------|-------|--------|
| Module 1 | Web Technologies | 🟡 In Progress |
| Module 2 | Embedded Systems & TinyML | 🟡 In Progress |
| Module 3 | Intelligent Robotics | 🟡 In Progress |
| Module 4 | IoT Dashboard & Autonomous Control | ⬜ Upcoming |
| Module 5 | Capstone Group Project | ⬜ Upcoming |

#### Repository Navigation
 
This repository is organized by topic. Detailed weekly documentation — including observations, implementations, and visual references — is maintained in [`Daily_Logs/`](./Daily_Logs/). Topic-specific source code is located in the corresponding folders like -`Arduino/`, `LiDAR/`, `Raspberry/`...

---

## Repository Structure
 
```
AI-HCI-LAB-Internship-2026/
│
├── Arduino/
│   ├── temp_humidity                  ← Temperature & humidity monitoring via DHT22 sensor
│   ├── led_control_python_serial      ← Real-time Arduino LED control via Python serial
│   └── lcd_ip_display                 ← Host-relayed LAN IP display on I2C LCD via Python
│
├── Daily_Logs/                        ← 📖 Main internship journal (start here)
│   ├── Week-1.md
│   ├── Week-2.md
│   ├── Week-3.md
│   ├── Week-4.md
│   ├── Week-5.md
│   └── assets/                        ← Photos, wiring diagrams, screenshots
│
├── LiDAR/                             ← Python scripts for RPLIDAR C1
│   └── other codes/
│
├── Raspberry/
│   └── Object Detection/              ← OpenCV object detection on Raspberry Pi
│
├── google_sheet.html                  ← Serverless HTML + Google Forms/Sheets frontend
└── README.md
```
---

## Weekly Progress & Quick Log

| Week | Focus | Highlights |
|------|-------|------------|
| [Week&nbsp;1](./Daily_Logs/Week-1.md) | Web Tech & Networking | Ubuntu VM static IP setup + SSH and Python HTTP server deployment |
| [Week&nbsp;2](./Daily_Logs/Week-2.md) | Embedded Systems | Arduino Uno + DHT22 integration & software calibration |
| [Week&nbsp;3](./Daily_Logs/Week-3.md) | Robotics & Web Arch | RPLIDAR C1 live 2D mapping + Serverless HTML to Google Sheets |
| [Week&nbsp;4](./Daily_Logs/Week-4.md) | Intelligent Robotics | LiDAR obstacle navigation interface & Raspberry Pi real-time object detection |
| [Week&nbsp;5](./Daily_Logs/Week-5.md) | Embedded Systems & Interfacing | Python serial control of Arduino LED & Host-relayed LAN IP display via I2C LCD |
---

## Key Tools & Technologies
 
| Category | Details |
|----------|---------|
| **Languages** | Python, C++, HTML, CSS, JavaScript |
| **Hardware** | SLAMTEC RPLIDAR C1, Arduino Uno, DHT22 Sensor, Raspberry Pi (Arm64), EMEET SmartCam S600, JHD629-204A 20x4 LCD, HW-61 I2C Backpack |
| **Libraries** | PySerial, Matplotlib, NumPy, OpenCV, Adafruit DHT, Adafruit Unified Sensor, pynput, LiquidCrystal_I2C |
| **Platforms** | macOS (M1/Tahoe), Ubuntu 26.04 LTS (UTM VM), Raspberry Pi OS (Debian Bookworm), Windows PC |
| **Tools** | Arduino IDE, VS Code, OpenSSH Server, NetworkManager (`nmcli`), Python `http.server`, Python `venv` |
| **Architecture** | Serverless web workflow with Google Forms + Sheets |
