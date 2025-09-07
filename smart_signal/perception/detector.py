import random
from typing import List
from smart_signal.types import Detection
from ultralytics import YOLO

class StubDetector:
    """
    Fake detector for testing the pipeline without a real ML model.
    Generates random bounding boxes and classes.
    """
    def __init__(self, classes=None, conf_thresh=0.3):
        self.classes = classes or ["car", "bus", "truck", "motorcycle"]
        self.conf_thresh = conf_thresh

    def infer(self, frame, frame_id: int, approach_id: str) -> List[Detection]:
        h, w, _ = frame.shape
        detections = []
        num_vehicles = random.randint(0, 5)
        for _ in range(num_vehicles):
            x1 = random.randint(0, w // 2)
            y1 = random.randint(0, h // 2)
            x2 = x1 + random.randint(30, 100)
            y2 = y1 + random.randint(30, 100)
            cls = random.choice(self.classes)
            score = round(random.uniform(self.conf_thresh, 1.0), 2)
            detections.append(
                Detection(
                    bbox=(x1, y1, x2, y2),
                    score=score,
                    cls=cls,
                    frame_id=frame_id,
                    approach_id=approach_id
                )
            )
        return detections


class YOLODetector:
    """
    Real YOLOv8 detector for actual vehicle detection.
    """
    def __init__(self, model_path="yolov8n.pt", conf_thresh=0.3):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh
        self.class_map = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }

    def infer(self, frame, frame_id: int, approach_id: str) -> List[Detection]:
        results = self.model.predict(frame, conf=self.conf_thresh, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls)
                if cls_id not in self.class_map:
                    continue

                # Map YOLO label to our allowed types
                label = self.class_map[cls_id]
                if label == "person":
                    label = "pedestrian"

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                score = float(box.conf)

                detections.append(
                    Detection(
                        bbox=(x1, y1, x2, y2),
                        score=score,
                        cls=label,
                        frame_id=frame_id,
                        approach_id=approach_id
                    )
                )
        return detections