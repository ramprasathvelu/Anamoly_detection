import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum


class SuspiciousAction(Enum):
    NORMAL = "normal"
    CLIMBING = "climbing"
    FALLING = "falling"
    FIGHTING = "fighting"
    CRAWLING = "crawling"


class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.action_history = []

    def analyze_pose(self, frame: np.ndarray) -> Dict:
        """Analyze human pose for suspicious actions"""
        results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return {"action": SuspiciousAction.NORMAL, "confidence": 0.0}

        landmarks = results.pose_landmarks.landmark
        h, w = frame.shape[:2]

        # Extract key points
        points = {}
        for idx, lm in enumerate(landmarks):
            points[idx] = (int(lm.x * w), int(lm.y * h))

        # Analyze poses
        action, confidence = self._detect_suspicious_actions(points, h)

        return {
            "action": action,
            "confidence": confidence,
            "landmarks": points,
            "skeleton_image": self._draw_skeleton(frame, points)
        }

    def _detect_suspicious_actions(self, points: Dict, image_height: int) -> Tuple[SuspiciousAction, float]:
        """Detect specific suspicious actions"""

        # Get key points (MediaPipe indices)
        nose = points[0]
        left_shoulder = points[11]
        right_shoulder = points[12]
        left_hip = points[23]
        right_hip = points[24]
        left_ankle = points[27]
        right_ankle = points[28]

        # Calculate body angles and positions
        shoulder_avg_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_avg_y = (left_hip[1] + right_hip[1]) / 2
        ankle_avg_y = (left_ankle[1] + right_ankle[1]) / 2

        body_height = ankle_avg_y - shoulder_avg_y

        # Climbing detection (arms above shoulders, crouched position)
        if (nose[1] < shoulder_avg_y and
                hip_avg_y > shoulder_avg_y + body_height * 0.3):
            return SuspiciousAction.CLIMBING, 0.8

        # Falling detection (horizontal body position)
        body_angle = abs(hip_avg_y - shoulder_avg_y)
        if body_angle < body_height * 0.2:
            return SuspiciousAction.FALLING, 0.7

        # Crawling detection (low to ground)
        if ankle_avg_y > image_height * 0.8 and hip_avg_y > image_height * 0.6:
            return SuspiciousAction.CRAWLING, 0.6

        return SuspiciousAction.NORMAL, 0.0

    def _draw_skeleton(self, frame: np.ndarray, points: Dict) -> np.ndarray:
        """Draw pose skeleton on frame"""
        skeleton_frame = frame.copy()

        # Define connections (MediaPipe pose connections)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
            (9, 10), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
            (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28)
        ]

        # Draw connections
        for connection in connections:
            if connection[0] in points and connection[1] in points:
                pt1 = points[connection[0]]
                pt2 = points[connection[1]]
                cv2.line(skeleton_frame, pt1, pt2, (0, 255, 0), 2)

        # Draw points
        for point in points.values():
            cv2.circle(skeleton_frame, point, 5, (0, 0, 255), -1)

        return skeleton_frame