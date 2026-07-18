# 📖 AgriSense AI User & Operator Manual

Welcome to **AgriSense AI**, a mobile-friendly, offline-first farm management tool. This guide helps farm owners, operators, and viewers understand how to use the dashboard, record daily metrics, read AI analysis reports, and manage data when internet connection is limited.

---

## 👥 1. User Roles & Permissions

AgriSense AI enforces role-based access control (RBAC) to ensure security and task division. Each user is associated with specific farms and assigned one of three roles:

| Feature / Action | 👑 Farm Owner | 🚜 Farm Operator | 👁️ Viewer |
|---|:---:|:---:|:---:|
| **Toggle between farms** | Yes | Yes | Yes |
| **View Dashboard, Charts, & History** | Yes | Yes | Yes |
| **Log daily metrics & growth** | Yes | Yes | Read-only |
| **Upload video / Run AI Inference** | Yes | Yes | Read-only |
| **Acknowledge anomaly alerts** | Yes | Yes | Read-only |
| **Update farm details (name/location)** | Yes | Read-only | Read-only |
| **Delete batches or farms** | Yes | Read-only | Read-only |

### How to Toggle Farms
If you belong to multiple farms, use the **Farm Selector** dropdown in the navigation header. The system will load the selected farm's active batches, history, alerts, and reports.

---

## 📝 2. Daily Logging & Anomaly Alerts

A crucial part of poultry management is recording feed intake, water consumption, and mortality.

### 2.1 Daily Logging
1. Select **Feed & Water** from the sidebar.
2. Click **Log Today's Metrics** (not available for *Viewer* role).
3. Enter:
    *   **Feed Consumed (kg)**
    *   **Water Consumed (litres)**
    *   **Daily Mortality (bird deaths count)**
4. Click **Save**.

### 2.2 Growth Sampling
To keep track of growth progress vs. target breed curves:
1. Select **Flock Growth** from the sidebar.
2. Select **Log Weight Sample**.
3. Input the **Average Weight (g)** and the **Sample Size** (number of birds weighed).
4. Save the entry to display it on the growth chart alongside the standard **Cobb 500** benchmark curve.

### 2.3 Anomaly Alerts (Threshold Rules)
When a daily consumption reading or mortality count is logged, the internal **Rules Engine** evaluates it instantly:
*   📉 **Consumption Drop/Spike**: If today's feed or water intake deviates by **more than 20%** compared to the rolling average of the **previous 7 days**, a warning alert is triggered.
*   ⚠️ **High Mortality Event**: If the daily mortality count is **greater than 0.5%** of the flock's initial count (e.g. >1 death in a 200-bird flock), a **Critical Alert** is raised.

Alerts are displayed in red (Critical) or amber (Warning) badges on the main dashboard. Click **Acknowledge** to mark alerts as read once you have inspected the coop.

---

## 👁️ 3. AI Visual Monitoring

The **AI Visual Monitor** lets you upload short video files (MP4 format) of your coop to perform an automated flock audit.

### 3.1 Uploading Coop Footage
1. Navigate to **AI Visual Monitor** in the navigation menu.
2. Select the active **Batch**.
3. Choose an MP4 video file and click **Run Visual Scan**.
4. The system will process the video and generate a tracking overlay.

### 3.2 Interpreting AI Reports
The analysis report provides three main metrics:

1.  **Estimated Bird Count**: The number of unique birds detected and tracked in the video.
2.  **Movement Score**: A scale from `0.1` (lethargic/still) to `10.0` (highly active). This is calculated from average speed displacement, filtering out model jitter.
3.  **Low Activity Windows**: Highlights specific time ranges (in seconds) where birds showed minimal movement, noting the reason (e.g. lethargic zones or static birds).

### 3.3 Visual Discrepancy Alerts
The AI compares the estimated bird count against the **expected count** (initial count minus cumulative mortalities logged so far):
*   🚨 **Missing Birds with Static Detection**: If the count is low and an inactive/static bird is detected in the video, a **Critical Anomaly Alert** is raised ("Lethargic/dead bird detected in visual").
*   ⚠️ **Population Deficit**: If birds are missing but no inactive birds are identified, a **Warning Anomaly Alert** is raised ("Suspected theft or undocumented loss").

---

## 🎤 4. Audio Telemetry & Distress Call Classifier

The **Audio Insight** panel allows you to use your device's microphone to monitor the flock's acoustic environment for respiratory illnesses or stress.

### 4.1 Running an Audio Scan
1. Navigate to **Audio Insight** from the sidebar.
2. Select your active batch and ensure microphone permissions are granted.
3. Click **Start Recording** to capture a 3-second audio slice of the coop.
4. The audio is processed by the heuristic classifier to analyze RMS volume and spectral centroids.

### 4.2 Interpreting Results
*   **Respiratory Distress**: Detected via short, sharp spikes in amplitude (coughing/sneezing).
*   **Environmental Stress**: Prolonged high-volume frequencies (loud chirping) suggesting temperature spikes or predators.
*   Results are evaluated against the custom sensitivity thresholds (configurable by Farm Owners).

---

## 📅 5. Interactive Treatment Calendar

Proactively plan vaccinations and vitamin cycles rather than just logging them after the fact.

1. Navigate to **Flock Health** from the sidebar.
2. In the Treatment Planner tab, click **Schedule Treatment**.
3. Input the treatment type (e.g., Vaccination, Vitamin), date, dosage, and notes.
4. (Optional) Set a browser push notification reminder.
5. When the scheduled date arrives, click **Complete** to automatically execute the treatment and archive it into the batch's historical medication log.

---

## 🔌 6. Offline Mode & Mobile Native App

AgriSense AI is built for remote environments with poor cellular connectivity.

### 6.1 How Offline Mode Works
*   **Local Caching**: The app stores data locally in the browser's secure database (**IndexedDB**), keeping a separate database instance for each operator username.
*   **Offline Data Entry**: You can submit daily logs, growth updates, scheduled treatments, and medication records while offline.

### 6.2 Sync Indicator & Verification
*   **Offline Status**: A red badge labeled `Offline Mode` appears in the navigation bar when connection is lost.
*   **Online Status & Syncing**: When internet access is restored, the badge changes to `Online` and flashes a `Syncing...` icon. The queue of offline-logged events is processed sequentially.

### 6.3 Android and iOS Mobile Shell
AgriSense AI can be installed as a standalone native application on your phone, powered by Capacitor.js.
*   **Android**: Install the `.apk` directly to your Android device.
*   The native shell provides deeper integration with local storage and background processes, ensuring maximum reliability for offline queueing at remote farms.
