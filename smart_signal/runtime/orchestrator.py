import time
import cv2
import numpy as np
from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import YOLODetector, StubDetector
from smart_signal.perception.tracker import IOUTracker
from smart_signal.perception.lane_mapper import LaneMapper
from smart_signal.control.optimizer import SignalOptimizer
from smart_signal.types import EmergencyEvent

class Orchestrator:
    def __init__(self, config):
        self.cfg = config
        self.cam = CameraStream(config["camera_source"], fps=config.get("fps", None))
        # Choose detector type
        if config.get("use_stub", False):
            self.detector = StubDetector()
        else:
            self.detector = YOLODetector(model_path=config.get("model_path", "yolov8n.pt"),
                                         conf_thresh=config.get("conf_thresh", 0.3))
        self.tracker = IOUTracker(iou_thresh=0.3, max_age=10)
        self.lane_mapper = LaneMapper(config["lane_geojson"])
        self.optimizer = SignalOptimizer(min_green_s=7, max_green_s=60)

    def run(self):
        print("Starting orchestrator loop...")
        for fid, ts, frame in self.cam.frames():
            # 1) Detect vehicles
            detections = self.detector.infer(frame, fid, "N")  # TODO: map approach_id per camera

            # 2) Track vehicles
            tracks = self.tracker.update(detections, fid)

            # 3) Map to lanes
            lane_assignments = self.lane_mapper.assign_tracks(tracks)
            lane_stats = self.lane_mapper.compute_lane_stats(lane_assignments)

            # 4) Get emergency events (placeholder: none for now)
            emergencies = []  # Could be populated from GPS/V2X feed

            # 5) Optimise signal timings
            splits = self.optimizer.compute_splits(lane_stats)
            splits = self.optimizer.apply_emergency_priority(splits, emergencies)

            # 6) Draw overlay
            self._draw_overlay(frame, lane_assignments, splits)

            # 7) Show frame
            cv2.imshow("Traffic AI Orchestrator", frame)

            # 8) Quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Stopping orchestrator...")
                break

        self.cam.release()
        cv2.destroyAllWindows()

    def _draw_overlay(self, frame, lane_assignments, splits):
        # Draw lane polygons
        for lane_id, poly in self.lane_mapper.lane_polygons.items():
            pts = [(int(x), int(y)) for x, y in poly.exterior.coords]
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
            # Show green time decision
            green_time = splits.greens_s.get(lane_id, 0)
            cv2.putText(frame, f"{lane_id}: {green_time:.1f}s",
                        pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw tracked vehicles
        for lane_id, tracks in lane_assignments.items():
            for tr in tracks:
                x1, y1, x2, y2 = map(int, tr.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{tr.cls} ID{tr.track_id}",
                            (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)