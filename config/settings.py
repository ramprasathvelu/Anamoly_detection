import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CameraConfig:
    name: str
    stream_url: str
    location: str
    restricted_zones: List[Tuple[int, int, int, int]]
    alert_emails: List[str]


@dataclass
class DetectionConfig:
    min_detection_confidence: float = 0.6
    pose_detection_enabled: bool = True
    sms_alerts_enabled: bool = True
    alert_cooldown: int = 60


# Camera configuration
CAMERAS = [
    CameraConfig(
        name="Main Entrance",
        stream_url="0",  # Webcam
        location="Building A - Front Door",
        restricted_zones=[(100, 100, 400, 400)],
        alert_emails=["ram.source18@gmail.com"]
    )
]

DETECTION_CONFIG = DetectionConfig()