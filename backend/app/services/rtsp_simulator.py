import asyncio
import cv2
import numpy as np
import base64
import random
import time

class RTSPSimulator:
    def __init__(self, expected_count: int = 50):
        self.width = 640
        self.height = 480
        self.fps = 15
        self.expected_count = expected_count
        
        # Initialize birds
        self.birds = []
        for i in range(self.expected_count):
            self.birds.append({
                "id": i + 1,
                "x": random.randint(20, self.width - 20),
                "y": random.randint(20, self.height - 20),
                "dx": random.uniform(-2, 2),
                "dy": random.uniform(-2, 2),
                "state": "active" if random.random() > 0.05 else "inactive",
                "radius": random.randint(6, 10)
            })
            
    async def stream_frames(self):
        """
        Async generator yielding base64 frames and telemetry data.
        """
        frame_idx = 0
        while True:
            # 1. Create base frame (coop background)
            # A dark brownish-green floor color
            frame = np.full((self.height, self.width, 3), (90, 110, 100), dtype=np.uint8)
            
            # 2. Update bird positions & draw
            active_count = 0
            lethargic_count = 0
            
            for bird in self.birds:
                if bird["state"] == "active":
                    # Random walk
                    bird["dx"] += random.uniform(-0.5, 0.5)
                    bird["dy"] += random.uniform(-0.5, 0.5)
                    # Speed limit
                    speed = (bird["dx"]**2 + bird["dy"]**2)**0.5
                    if speed > 3:
                        bird["dx"] = (bird["dx"]/speed)*3
                        bird["dy"] = (bird["dy"]/speed)*3
                        
                    bird["x"] += bird["dx"]
                    bird["y"] += bird["dy"]
                    
                    # Bounce off walls
                    if bird["x"] < 20 or bird["x"] > self.width - 20:
                        bird["dx"] *= -1
                        bird["x"] = max(20, min(self.width - 20, bird["x"]))
                    if bird["y"] < 20 or bird["y"] > self.height - 20:
                        bird["dy"] *= -1
                        bird["y"] = max(20, min(self.height - 20, bird["y"]))
                        
                    color = (200, 230, 240)  # whitish chicken
                    active_count += 1
                else:
                    # Inactive bird
                    color = (150, 150, 180)
                    lethargic_count += 1
                    
                # Draw bird
                cv2.circle(frame, (int(bird["x"]), int(bird["y"])), bird["radius"], color, -1)
                
                # Draw simulated YOLO bounding box
                box_color = (0, 255, 0) if bird["state"] == "active" else (0, 0, 255)
                top_left = (int(bird["x"] - bird["radius"] - 2), int(bird["y"] - bird["radius"] - 2))
                bottom_right = (int(bird["x"] + bird["radius"] + 2), int(bird["y"] + bird["radius"] + 2))
                cv2.rectangle(frame, top_left, bottom_right, box_color, 1)
                
                # Draw ID tag
                cv2.putText(frame, f"id:{bird['id']}", (top_left[0], top_left[1]-3), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, box_color, 1)

            # Draw overlay timestamp
            timestamp_str = f"CAM02 | LIVE | {time.strftime('%Y-%m-%d %H:%M:%S')}"
            cv2.putText(frame, timestamp_str, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw telemetry on frame
            cv2.putText(frame, f"Tracked: {len(self.birds)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # 3. Encode to JPEG asynchronously to prevent blocking event loop
            _, buffer = await asyncio.to_thread(cv2.imencode, '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # 4. Generate Telemetry JSON
            telemetry = {
                "bird_count_est": len(self.birds),
                "movement_score": 85 if lethargic_count < 5 else 60,
                "lethargic_count": lethargic_count,
                "timestamp": time.time(),
                "frame_idx": frame_idx
            }
            
            yield {
                "frame": frame_b64,
                "telemetry": telemetry
            }
            
            frame_idx += 1
            await asyncio.sleep(1 / self.fps)
