import cv2
import numpy as np
from typing import Optional, Tuple


class VideoHandler:
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.cap = None

    def start_stream(self) -> bool:
        """Initialize video capture"""
        try:
            # If stream_url is a number, convert to int (for webcam)
            if self.stream_url.isdigit():
                self.stream_url = int(self.stream_url)

            self.cap = cv2.VideoCapture(self.stream_url)
            return self.cap.isOpened()
        except Exception as e:
            print(f"Error starting stream: {e}")
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame from the stream"""
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def release(self):
        """Release video capture resources"""
        if self.cap is not None:
            self.cap.release()

    def draw_restricted_zones(self, frame, zones: list):
        """Draw restricted zones on the frame"""
        for zone in zones:
            x1, y1, x2, y2 = zone
            # Draw semi-transparent red rectangle
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            # Draw border
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, "RESTRICTED", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)