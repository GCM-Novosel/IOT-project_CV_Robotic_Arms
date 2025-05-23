# 🤖 CV & Cloud Controlled Robotic Hands

This repository showcases a dual-approach robotic hand project, combining **Computer Vision** and **MQTT-based cloud control**. Designed as part of a IoT Essentials Class, the goal was to explore and demonstrate multiple interfaces and technologies commonly used in modern IoT and robotics education.

[![Watch the Demo Video](https://img.youtube.com/vi/kYk10_oYDqU/0.jpg)](https://www.youtube.com/watch?v=kYk10_oYDqU)

## 🧠 Project Overview

Two different robotic hands were developed:

1. **Computer Vision Hand (MediaPipe + USB Serial)**  
2. **MQTT-Controlled Hand (Touchscreen UI + Ubidots + WiFi)**

Each finger is individually controlled by a servo motor. The systems differ in input method and communication interface, offering flexible interaction and remote control scenarios.

---

## 📦 Features

- **MediaPipe Hand Landmark Detection**  
- **Real-Time Servo Movement with USB Serial**  
- **Tkinter Touchscreen UI (Orange Pi)**  
- **Gesture Mapping to Servo Angles**  
- **Cloud Communication via Ubidots MQTT Broker**  
- **PWM Servo Control via Pico W (CircuitPython)**  
- **Custom 3D-Printed Hand Design**  
- **Educational Use Case as IoT Kit for Students**

---

## 📷 System 1: Computer Vision Robotic Hand

- Uses a webcam and [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html) to detect 21 hand landmarks.
- Calculates the “openness” of each finger relative to a palm reference.
- Normalizes values to 0–180° servo angles.
- Sends values via USB to an **Arduino** or **Pico (PyFirmata)**.
- Controls servos in real time.

### Code Highlights
- `opencv_mediapipe_hand.py`
- `pyfirmata_control.py`

---

## ☁️ System 2: MQTT-Controlled Robotic Hand

- UI runs on an **Orange Pi** with a touchscreen (Tkinter).
- User can control individual fingers or send predefined gestures.
- Gesture → Angle mapping like:

```python
POSES = {
    "peace":    [0, 0, 180, 180, 120],
    "rock_on":  [0, 180, 180, 0, 120],
    "fist":     [180, 180, 180, 180, 120],
    ...
}
