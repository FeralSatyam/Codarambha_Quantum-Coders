import cv2
from typing import Generator, Optional
import time

class CameraStream:
    """
    Handles video capture from file or RTSP/USB camera.
    Yields frames with timestamps and frame IDs.
    """

    def __init__(self, source: str, fps: Optional[int] = None, warmup_time: float = 1.0):
        """
        :param source: Path to video file or RTSP/USB camera index (e.g., 0, 1)
        :param fps: Target FPS (None = use source FPS)
        :param warmup_time: Seconds to wait before starting capture
        """
        self.source = source
        self.fps = fps
        self.cap = None
        self.frame_id = 0
        self.warmup_time = warmup_time

    def open(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")
        if self.fps is None:
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 15
        time.sleep(self.warmup_time)

    def frames(self) -> Generator[tuple, None, None]:
        """
        Generator yielding (frame_id, timestamp, frame_bgr)
        """
        if self.cap is None:
            self.open()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            ts = time.time()
            self.frame_id += 1
            yield self.frame_id, ts, frame

            # Optional: throttle to target FPS
            if self.fps:
                time.sleep(1.0 / self.fps)

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None