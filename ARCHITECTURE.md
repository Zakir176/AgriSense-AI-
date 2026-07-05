# 🏗️ AgriSense AI Architecture

AgriSense AI uses a classic, decoupled three-tier architecture designed to run efficiently on low-cost hardware in low-connectivity poultry environments. This document details the components, database structures, system flows, and our custom AI visual monitoring implementation.

---

## 1. System Topology

```mermaid
graph TD
    subgraph Client [Presentation Tier - Vue 3 SPA]
        UI[Vite + Vue 3 App]
        DB_Cache[IndexedDB / local storage]
        Charts[Chart.js 4 / Vue Charts]
    end

    subgraph Server [Logic Tier - FastAPI]
        API[FastAPI Application]
        Rules[Rules & Anomaly Engine]
        Inference[Visual Inference Service]
    end

    subgraph Data [Data Tier]
        Postgres[(PostgreSQL 15)]
        YOLO[YOLOv8 Model Weights]
    end

    UI <-->|JSON over HTTP/HTTPS| API
    UI <--> DB_Cache
    API <-->|SQLAlchemy ORM| Postgres
    Inference <--> YOLO
    Inference <-->|Uploaded MP4| UI
```

---

## 2. Component Directory Structure

The repository is divided into two primary subdirectories:

*   **`frontend/`** (Presentation Tier):
    *   **`src/views/`**: Page components (`Dashboard.vue`, `FeedWater.vue`, `AIVisualMonitor.vue`, etc.)
    *   **`src/components/`**: Reusable custom UI components (`Toast.vue`, `AgriProgressBar.vue`, etc.)
    *   **`src/services/`**: API wrapper clients and the IndexedDB local offline cache handlers.
*   **`backend/`** (Logic Tier & Database):
    *   **`app/routers/`**: REST API endpoints for farms, batches, daily logs, growth curves, and video uploads.
    *   **`app/models/`**: Declarative SQLAlchemy models.
    *   **`app/schemas/`**: Pydantic serialization and validation schemas.
    *   **`app/services/`**: Business logic modules (alert engines, custom trackers).

---

## 3. Database Entity Relationship Model

The relational database structure supports multi-farm scaling and role-based access controls (RBAC) linked to users:

```mermaid
erDiagram
    User ||--o{ UserFarmAssociation : belongs
    Farm ||--o{ UserFarmAssociation : has
    Farm ||--o{ Batch : contains
    Batch ||--o{ FeedWaterReading : logs
    Batch ||--o{ GrowthSample : records
    Batch ||--o{ MedicationEntry : logs
    Batch ||--o{ Alert : triggers
    Batch ||--o{ MediaClip : uploads
    MediaClip ||--|| InferenceResult : generates

    User {
        int id PK
        string username
        string hashed_password
        string full_name
    }

    UserFarmAssociation {
        int id PK
        int user_id FK
        int farm_id FK
        string role "owner | operator | viewer"
    }

    Farm {
        int id PK
        string name
        string location
    }

    Batch {
        int id PK
        int farm_id FK
        date start_date
        int bird_count
        string breed
        string status "active | archived"
    }

    FeedWaterReading {
        int id PK
        int batch_id FK
        date date
        float feed_kg
        float water_litres
        int mortality_count
        boolean flagged_abnormal
    }

    GrowthSample {
        int id PK
        int batch_id FK
        date date
        float avg_weight_g
        int sample_size
    }

    MedicationEntry {
        int id PK
        int batch_id FK
        date date
        string medicine_type
        float dosage
        string outcome_note
    }

    Alert {
        int id PK
        int batch_id FK
        string type "mortality | consumption | visual | manual"
        string message
        string severity "critical | warning | info"
        timestamp created_at
        boolean acknowledged
    }

    MediaClip {
        int id PK
        int batch_id FK
        string file_url
        timestamp uploaded_at
    }

    InferenceResult {
        int id PK
        int media_clip_id FK
        int bird_count_est
        float movement_score
        json low_activity_windows
        json tracked_birds
        string discrepancy_note
    }
```

---

## 4. Key System Flows

### 4.1 Daily Consumption Log & Alert Engine
When a farmer logs daily feed/water metrics, the rule-based anomaly engine computes rolling statistics to identify anomalies:

```mermaid
sequenceDiagram
    autonumber
    actor Farmer
    participant UI as Vue 3 Client
    participant API as FastAPI Router
    participant DB as PostgreSQL
    participant Engine as Rules Engine

    Farmer->>UI: Enter feed/water log
    UI->>API: POST /api/v1/readings
    API->>DB: Store Reading
    API->>Engine: Run evaluation
    Engine->>DB: Query last 7 days of readings
    DB-->>Engine: Readings data
    Engine->>Engine: Compute rolling average
    alt Current Reading deviates > 20% from rolling average
        Engine->>DB: Store Alert (Severity: Warning/Critical)
        Engine-->>API: Flag abnormal = True
    else Normal
        Engine-->>API: Flag abnormal = False
    end
    API-->>UI: Return updated Reading record
    UI->>Farmer: Render confirmation & display alert badge (if triggered)
```

---

### 4.2 AI Video Monitoring Pipeline
To assess the health and population of a chicken flock, pre-recorded video clips are analyzed:

```mermaid
sequenceDiagram
    autonumber
    actor Farmer
    participant UI as Vue 3 Client
    participant API as FastAPI Router
    participant Service as Inference Service
    participant YOLO as YOLOv8 (yolov8n.pt)
    participant DB as PostgreSQL

    Farmer->>UI: Select and upload MP4 coop video
    UI->>API: POST /api/v1/inference/video (Form: batch_id, file)
    API->>API: Save video file to disk
    API->>DB: Store MediaClip record (retrieves ID)
    API->>Service: run_video_inference(video_path)
    
    Service->>YOLO: Initialize YOLOv8 tracker with bytetrack_poultry.yaml
    loop Process frames (up to 150 frames limit)
        YOLO->>Service: Return frame boxes (confs, classes, track_ids)
        Service->>Service: Filter noise, match centroids, calculate displacement
    end
    
    Service->>Service: Compute bird_count_est, movement_score, low_activity_windows
    Service-->>API: Return structured inference dictionary
    
    API->>DB: Query batch expected count & mortality records
    DB-->>API: Expected count (Initial count - cumulative deaths)
    
    alt bird_count_est < expected_count
        API->>DB: Trigger population discrepancy / mortality Alert
    end
    
    API->>DB: Store InferenceResult record
    API-->>UI: Return MediaClipResponse (contains clip and inference details)
    UI->>Farmer: Display results (chicken count, activity score, alert warnings)
```

### 4.3 Offline Caching & Background Synchronization Flow
To support low-connectivity coop environments, the client application caches GET data and queues POST/PUT requests using browser IndexedDB storage:

```mermaid
sequenceDiagram
    autonumber
    actor Farmer
    participant UI as Vue 3 Client
    participant Cache as IndexedDB (db.js)
    participant Network as Browser Network Status
    participant API as FastAPI Router

    Farmer->>UI: Enter and save daily metric (offline)
    UI->>Network: Check online status
    Note over UI, Network: navigator.onLine is false
    UI->>Cache: addToSyncQueue(url, method, payload)
    Cache-->>UI: Request queued successfully
    UI->>Farmer: Toggle "Offline Mode" banner & confirm local save
    
    Note over Farmer, Network: Internet connection restored
    Network->>UI: Trigger window "online" listener event
    UI->>UI: Run syncOfflineData()
    UI->>Cache: getSyncQueue()
    Cache-->>UI: Return list of queued operations
    loop For each queued operation in chronological order
        UI->>API: Execute HTTP Request (url, method, payload)
        API-->>UI: Return HTTP response (200 OK / 201 Created)
        UI->>Cache: removeFromSyncQueue(id)
    end
    UI->>UI: Re-run initApp() to fetch fresh server state
    UI->>Farmer: Display "Sync successful" notification toast
```

---

## 5. Optimized AI Visual Monitoring Implementation

The core AI visual monitoring system uses a pretrained `yolov8n.pt` detector. To adapt it to dusty, crowded poultry coops without costly custom training, we decoupled the detection wrapper and tuned tracking parameters:

### 5.1 Custom ByteTrack Settings (`bytetrack_poultry.yaml`)
To prevent low-confidence detections from being discarded and improve tracking overlap, we configure:
*   **`track_high_thresh: 0.12`**: Lowers the match confidence required for primary detection association.
*   **`track_low_thresh: 0.05`**: Keeps track of highly occluded or dim background chickens.
*   **`new_track_thresh: 0.15`**: Sets the minimum threshold for starting a new track.
*   **`track_buffer: 60`**: Keeps lost tracks active for 60 frames (2 seconds at 30 FPS) to bridge periods when chickens block one another.
*   **`match_thresh: 0.7`**: Sets IoU matching overlap parameters.

### 5.2 Dynamic Noise Filtering & Post-Processing
*   **Centroid Lookup Lookup Bounds**: The fallback centroid tracker is restricted to look back at most 15 frames. This ensures that new chickens appearing do not inherit the IDs of long-disappeared chickens.
*   **Track Length Filtering**: Detections are divided into *transient tracks* (active for < 10 frames) and *stable tracks* (active for $\ge$ 10 frames). Transient tracks are treated as model detection noise (e.g. dust, feeders, brief mismatches) and are ignored in flock count calculations.
*   **Filtered Activity Index (Movement Score)**: Movement speeds are computed strictly on stable tracks. Frame-to-frame coordinate jitters under `1.5` pixels are treated as `0.0` (static) to prevent detection jitter from inflating the score, while jumps over `50.0` pixels are capped to prevent tracking swaps from causing score spikes.
