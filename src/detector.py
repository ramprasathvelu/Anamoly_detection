import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Any
from src.pose_analyzer import PoseAnalyzer, SuspiciousAction


class AdvancedPersonDetector:
    def __init__(self, min_detection_confidence: float = 0.5, enable_pose_analysis: bool = True):
        print("🚀 Loading Advanced DSTPS Detection...")
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )

        self.pose_analyzer = PoseAnalyzer() if enable_pose_analysis else None
        self.detection_history = []

        print("✅ Advanced Detection System Ready!")

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced detection with pose analysis"""
        detections = []

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False

            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                h, w = frame.shape[:2]
                landmarks = results.pose_landmarks.landmark

                # Calculate bounding box from pose landmarks
                x_coords = [lm.x * w for lm in landmarks]
                y_coords = [lm.y * h for lm in landmarks]

                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))

                # Add padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)

                # Pose analysis
                pose_analysis = {"action": SuspiciousAction.NORMAL, "confidence": 0.0}
                if self.pose_analyzer:
                    pose_analysis = self.pose_analyzer.analyze_pose(frame)

                center_x = (x_min + x_max) // 2
                center_y = (y_min + y_max) // 2

                detection = {
                    'bbox': (x_min, y_min, x_max, y_max),
                    'confidence': 0.8,
                    'class_name': 'person',
                    'center': (center_x, center_y),
                    'pose_analysis': pose_analysis,
                    'skeleton_image': pose_analysis.get('skeleton_image', frame)
                }
                detections.append(detection)

        except Exception as e:
            print(f"Detection error: {e}")

        return detections

    def check_restricted_zone_breach(self, detection: Dict, restricted_zones: List) -> bool:
        cx, cy = detection['center']

        for zone in restricted_zones:
            x1, y1, x2, y2 = zone
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return True
        return False

    def is_suspicious_action(self, detection: Dict) -> bool:
        """Check if detection involves suspicious actions"""
        pose_analysis = detection.get('pose_analysis', {})
        action = pose_analysis.get('action', SuspiciousAction.NORMAL)
        confidence = pose_analysis.get('confidence', 0.0)

        return action != SuspiciousAction.NORMAL and confidence > 0.5

    def release(self):
        if hasattr(self, 'pose'):
            self.pose.close()