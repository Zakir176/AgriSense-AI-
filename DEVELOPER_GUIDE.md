# 🛠️ AgriSense AI Developer & Operator Setup Guide

This guide provides step-by-step instructions for local development setup, database administration, verification, testing, and troubleshooting common issues.

---

## 1. Quick Local Setup

### OS-Specific Activation Command Reference
Follow the build steps based on your terminal and operating system:

| Environment / Shell | Folder | Setup & Run Commands |
|---|---|---|
| **Windows (PowerShell)** | `backend/` | `python -m venv venv`<br>`.\venv\Scripts\Activate.ps1`<br>`pip install -r requirements.txt`<br>`python seed_data.py`<br>`uvicorn app.main:app --reload --port 8000` |
| **Windows (CMD)** | `backend/` | `python -m venv venv`<br>`call venv\Scripts\activate.bat`<br>`pip install -r requirements.txt`<br>`python seed_data.py`<br>`uvicorn app.main:app --reload --port 8000` |
| **macOS / Linux (Bash/Zsh)** | `backend/` | `python3 -m venv venv`<br>`source venv/bin/activate`<br>`pip install -r requirements.txt`<br>`python seed_data.py`<br>`uvicorn app.main:app --reload --port 8000` |
| **Node.js (All OS)** | `frontend/` | `npm install`<br>`npm run dev` (Runs Vite server on `http://localhost:5173`) |

---

## 2. Database Administration

### PostgreSQL Docker Container Setup
The project uses PostgreSQL 15 for production-grade schema testing:
```bash
# Start the database container in the background
docker-compose up -d

# Verify that the container is running and healthy
docker ps
```

*   **Database Host**: `localhost`
*   **Database Port**: `5432`
*   **Username**: `postgres`
*   **Password**: `postgrespassword`
*   **Database Name**: `agrisense`

### Seeding Real-World Demo Data
To verify alerts, charts, and queries, populate your local database with Evans Kabwe's real-world pilot farm data:
```bash
cd backend
python seed_data.py
```
This inserts:
1.  **Prime Nest Poultry Farm** (Lusaka, Zambia).
2.  **Two Batches** of 200 Cobb 500 birds:
    *   `Batch 1` (Active, Day 22): Daily logs and weekly growth curves.
    *   `Batch 2` (Archived): Full 42-day cycle logs.
3.  **Consumption logs** with a built-in anomaly on Day 15 (22% feed intake drop) to trigger the rules engine alerts.
4.  **Medication cycles** ranging from Day-1 Marek's vaccinations to Day-18 Newcastle, Gumboro, and vitamin cycles.

---

## 3. Visual Tracking and Inference Engine

### Frame Limits & Optimization
Processing full-length poultry coop videos is computationally intensive. The [inference_service.py](file:///d:/code/GitHub/Personal/AgriSense-AI-/backend/app/services/inference_service.py) is optimized to:
1.  Read the uploaded file path.
2.  Process only the **first 150 frames** of the video (approx. 5 seconds of footage at 30 FPS).
3.  Calculate bird count statistics and movement velocity, then scale the metrics.

This frame boundary prevents backend API request timeouts and database lock freezes on consumer-grade servers lacking dedicated GPUs.

### Validating Custom Tracker Parameters
If you need to tweak the visual tracking parameters, edit [bytetrack_poultry.yaml](file:///d:/code/GitHub/Personal/AgriSense-AI-/backend/app/services/bytetrack_poultry.yaml). 
To run video tracking manually and verify the tracking outputs without uploading files via the API, execute our diagnostic benchmark script:
```bash
cd backend
.\venv\Scripts\python.exe -c "from app.services.inference_service import run_video_inference; print(run_video_inference('uploads/394edcf9-41b3-4284-8e02-3ba0fde117bb.mp4'))"
```

### 3.3 ByteTrack Parameter Calibration (`bytetrack_poultry.yaml`)
Key parameters to tune tracking performance inside crowded poultry environments:
*   `track_high_thresh` (default `0.12`): Detections above this confidence are matched directly. Lower this to maintain tracking on occluded or slightly dirty birds.
*   `track_low_thresh` (default `0.05`): Secondary matching threshold for weaker detections. Helps preserve the ID of a bird as it passes under feeders or behind water cups.
*   `new_track_thresh` (default `0.15`): Threshold required to initiate a new bird ID. Keep this relatively high to prevent dust, insects, or background noise from spawning false tracks.
*   `track_buffer` (default `60`): Number of frames to keep a lost tracking ID active in memory. At 30 FPS, `60` frames represents a 2-second grace window where a bird can be fully blocked from visual detection before its ID is released.
*   `match_thresh` (default `0.7`): IoU threshold for matching overlaps.

---

## 4. Role-Based Access Control Staged Testing

The [seed_data.py](file:///d:/code/GitHub/Personal/AgriSense-AI-/backend/seed_data.py) script seeds a pilot farm and a default user (`operator` / `prime_nest_2026`) associated as the farm **Owner** (via `UserFarmAssociation` model). 

To test role constraints during local development:
1.  **Add a Viewer/Operator account**: Connect to PostgreSQL using your favorite database visualizer (e.g. pgAdmin or DBeaver) or run a quick python script to create alternative users and associate them with the farm.
2.  **Verify API Response Limits**:
    *   Log in as an **Owner/Operator** and verify you can submit a POST request to `/api/v1/readings` to log daily feed intake.
    *   Log in as a **Viewer** and send the same POST request; verify that the endpoint returns `HTTP 403 Forbidden` ("Viewer role does not have permission to log readings").
3.  **Inspect Headers**: Verify that each route utilizes `Depends(get_user_farm)` to lock access strictly to authorized users.

---

## 5. Debugging IndexedDB & Offline Sync

AgriSense AI stores request payloads in the browser's IndexedDB when offline. You can inspect, modify, and delete cached entries using the developer tools:

### 5.1 Inspecting the Sync Queue & Cache
1.  Open your browser (Chrome/Edge preferred).
2.  Press `F12` to open DevTools, then select the **Application** tab.
3.  In the left sidebar, expand **IndexedDB**.
4.  You will find databases named `agrisense-db-[username]` (each operator has a unique database name based on their active token session).
5.  Expand the database and select:
    *   `api-cache`: Stores GET responses (keys are endpoint URLs).
    *   `sync-queue`: Stores pending mutations (`url`, `method`, `payload`, `timestamp`).

### 5.2 Emulating Offline Behavior for Verification
1.  In DevTools, select the **Network** tab.
2.  Locate the network throttling dropdown (defaults to `No throttling`).
3.  Select **Offline**.
4.  Log a feed/water reading in the app. Verify that the request is intercepted, added to the `sync-queue` store, and a red `Offline Mode` banner appears.
5.  Switch the dropdown back to `No throttling` (Online). Verify that the `online` event triggers, fires `syncOfflineData()`, and successfully syncs the queue to the backend.

---

## 6. Troubleshooting FAQ

### Q1: `AttributeError: 'IterableSimpleNamespace' object has no attribute 'fuse_score'`
*   **Cause**: This happens when a custom tracker config (e.g. `bytetrack_poultry.yaml`) is passed to YOLOv8 without specifying all mandatory attributes expected by the installed version of the `ultralytics` package.
*   **Solution**: Ensure that [bytetrack_poultry.yaml](file:///d:/code/GitHub/Personal/AgriSense-AI-/backend/app/services/bytetrack_poultry.yaml) contains all required fields, including `fuse_score: True`. You can verify your configuration parameters match the default template in `ultralytics/cfg/trackers/bytetrack.yaml`.

### Q2: CUDA out-of-memory or PyTorch taking too long to download
*   **Cause**: The standard `pip install ultralytics` pulls in the heavy GPU-enabled CUDA versions of PyTorch by default, which can exceed 2GB of disk space.
*   **Solution**: If running on a CPU-only server or machine, force a CPU-only PyTorch build to keep the container lightweight:
    ```bash
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --force-reinstall
    ```

### Q3: `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" failed`
*   **Cause**: The backend FastAPI server is trying to connect to PostgreSQL, but the Docker daemon is either not running or the DB container has crashed.
*   **Solution**:
    1. Check Docker status: `docker ps`.
    2. If container is missing, run: `docker-compose up -d`.
    3. If you want to fall back to a local SQLite database for quick mock testing, modify your `.env` file to use:
       ```env
       DATABASE_URL=sqlite:///./agrisense.db
       ```
       Then re-run the database seeder: `python seed_data.py`.

### Q4: What is `frontend/take_screenshots.js`?
*   **Answer**: `take_screenshots.js` is an optional developer utility script powered by Puppeteer used to capture automated documentation screenshots (`Docs/assets/`). It is a developer tool and not part of the application runtime.
