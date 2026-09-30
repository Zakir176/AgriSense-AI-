# Dahua DH-H3D-3F (Hero Dual) Camera Integration Guide for AgriSense-AI

This guide provides step-by-step instructions to configure, connect, and stream live video feeds from the **Dahua DH-H3D-3F** (Hero Dual series) 6MP Dual-Lens Wi-Fi Camera directly into **AgriSense-AI** for real-time poultry monitoring, YOLOv8 object detection, and flock telemetry.

---

## 1. Camera Overview & Technical Specifications

| Feature                | Specification                                                                 |
| :--------------------- | :---------------------------------------------------------------------------- |
| **Model**              | Dahua Hero Dual `DH-H3D-3F`                                                   |
| **Resolution**         | 6MP Total (3MP Fixed Lens + 3MP Pan & Tilt Lens)                              |
| **Video Compression**  | H.265 / H.264                                                                 |
| **Network Interfaces** | Wi-Fi 6 (IEEE 802.11a/b/g/n/ac/ax 2.4GHz) & RJ-45 Ethernet Port (10/100 Mbps) |
| **Protocols**          | RTSP, ONVIF (Profile S/G/T), CGI, HTTP/HTTPS                                  |
| **AI Features**        | Human Detection, Pet Detection, Auto-Tracking (PT Lens), Motion Detection     |
| **Storage & Audio**    | MicroSD Slot (up to 256GB), 2-Way Audio (Built-in Mic & Speaker)              |
| **Power Input**        | 5V DC / 1.5A                                                                  |

---

## 2. Pre-Requisites & Network Setup

### Step A: Initialize the Camera

1. Power on the **DH-H3D-3F** camera using the provided 5V power adapter.
2. Download and open the **DMSS** mobile app (iOS / Android) or **Dahua ConfigTool** on Windows.
3. Add the camera to your network via QR code scan (Wi-Fi 6) or direct Ethernet connection.
4. Set a strong admin password (e.g. `AgriFarm#2026`).

### Step B: Reserve Static IP Address

To ensure uninterrupted RTSP streaming:

1. Log into your farm router configuration page.
2. Find the connected Dahua camera under DHCP client list.
3. Assign a **Static IP Reservation** (e.g., `192.168.1.120`).

---

## 3. Dahua RTSP URL Formats

The Dahua DH-H3D-3F features **two camera channels** (Channel 1 = Fixed Lens, Channel 2 = Pan/Tilt Lens). Standard Dahua RTSP syntax:

```text
rtsp://<username>:<password>@<camera_ip>:554/cam/realmonitor?channel=<channel_id>&subtype=<stream_type>
```

### Stream Matrix

| Lens              | Stream Type              | Channel ID | Subtype | Recommended RTSP URL Format                                                      |
| :---------------- | :----------------------- | :--------- | :------ | :------------------------------------------------------------------------------- |
| **Fixed Lens**    | Main (3MP High-Res)      | `1`        | `0`     | `rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=1&subtype=0` |
| **Fixed Lens**    | Sub (VGA/D1 Low Latency) | `1`        | `1`     | `rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=1&subtype=1` |
| **Pan-Tilt Lens** | Main (3MP High-Res)      | `2`        | `0`     | `rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=2&subtype=0` |
| **Pan-Tilt Lens** | Sub (VGA/D1 Low Latency) | `2`        | `1`     | `rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=2&subtype=1` |

> [!TIP]
> **Performance Recommendation:** For AI real-time object tracking over WebSockets, use **Substream (`subtype=1`)** to minimize network bandwidth and frame decoding latency on the server.

---

## 4. Testing the Stream with VLC Player

Before configuring AgriSense-AI, verify the RTSP stream locally:

1. Open **VLC Media Player**.
2. Go to **Media** -> **Open Network Stream...** (Ctrl+N).
3. Enter your camera URL:
   `rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=1&subtype=1`
4. Click **Play**. You should see live video from the fixed lens. Repeat with `channel=2` for the Pan-Tilt lens feed.

---

## 5. Integrating Stream into AgriSense-AI

### Step 1: Add Camera URL to Backend `.env`

In `backend/.env`, set the active camera stream URL:

```env
DAHUA_CAMERA_RTSP_URL="rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=1&subtype=1"
```

### Step 2: Python RTSP Ingestion with OpenCV & YOLOv8

The AgriSense-AI backend (`backend/app/services/rtsp_simulator.py` or live stream service) connects to OpenCV:

```python
import cv2

# Connect to Dahua Live RTSP Stream
camera_url = "rtsp://admin:Password123@192.168.1.120:554/cam/realmonitor?channel=1&subtype=1"
cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

# Set buffer size to minimize stream latency
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Camera feed interrupted. Reconnecting...")
        break

    # Pass frame to YOLOv8 model for poultry counting & density analysis
    # ...
```

### Step 3: Frontend View (`AIVisualMonitor.vue`)

Open the AgriSense-AI web dashboard:

1. Navigate to **AI Visual Monitor** (`/ai-monitor`).
2. Select **Live Feed** mode toggle.
3. View real-time live frames streamed from your Dahua DH-H3D-3F camera alongside YOLOv8 bounding box overlays, active bird node counts, and activity heatmaps.

---

## 6. Troubleshooting Common Issues

> [!WARNING]
> **Issue 1: Stream Connection Timeout / Refused (Port 554)**
>
> - Verify that ONVIF / RTSP protocol is enabled in Dahua camera security settings.
> - Ensure your server and camera are on the same subnet (e.g. `192.168.1.x`).
> - Ensure firewall rules allow inbound traffic on port `554`.

> [!NOTE]
> **Issue 2: Audio/Video Lag**
>
> - Lower the resolution/fps in DMSS camera settings to 15 FPS / H.264.
> - Use stream `subtype=1` (substream) for smooth AI computer vision processing.

> [!TIP]
> **Issue 3: Dual Lens Viewing**
>
> - To monitor both fixed and PT angles simultaneously, spawn two stream worker instances in AgriSense-AI: one pointing to `channel=1` and another to `channel=2`.
