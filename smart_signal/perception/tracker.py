# smart_signal/perception/tracker.py
from typing import List, Optional, Tuple
import numpy as np
from smart_signal.types import Detection, Track
from smart_signal.utils.geometry import iou

# ---------- Existing IOUTracker kept as-is ----------
class IOUTracker:
    def __init__(self, iou_thresh=0.3, max_age=10):
        self.iou_thresh = iou_thresh
        self.max_age = max_age
        self.tracks: List[Track] = []
        self.next_id = 1

    def update(self, detections: List[Detection], frame_id: int) -> List[Track]:
        updated_tracks = []
        for det in detections:
            best_iou = 0
            best_track = None
            for track in self.tracks:
                if track.cls != det.cls:  # class-aware association
                    continue
                s = iou(track.bbox, det.bbox)
                if s > best_iou:
                    best_iou, best_track = s, track
            if best_iou >= self.iou_thresh and best_track:
                best_track.bbox = det.bbox
                best_track.last_seen_frame = frame_id
                updated_tracks.append(best_track)
            else:
                new_track = Track(
                    track_id=self.next_id, bbox=det.bbox, cls=det.cls,
                    approach_id=det.approach_id, last_seen_frame=frame_id
                )
                self.next_id += 1
                updated_tracks.append(new_track)

        # age-out
        self.tracks = [t for t in updated_tracks if frame_id - t.last_seen_frame <= self.max_age]
        return self.tracks

# ---------- SORT-style tracker ----------
# Minimal Kalman filter utilities (state: x,y,w,h,vx,vy,vw,vh)
class KalmanBox:
    def __init__(self, bbox: Tuple[float,float,float,float]):
        self._init_state(bbox)

    def _init_state(self, bbox):
        x1, y1, x2, y2 = bbox
        w, h = (x2 - x1), (y2 - y1)
        x, y = x1 + w/2, y1 + h/2
        self.x = np.array([x, y, w, h, 0, 0, 0, 0], dtype=float)  # state
        self.P = np.eye(8) * 10.0  # covariance

        # Constant velocity model
        self.F = np.eye(8)
        dt = 1.0
        for i in range(4):
            self.F[i, i+4] = dt

        self.Q = np.eye(8) * 0.01
        self.H = np.zeros((4, 8))
        self.H[0,0] = self.H[1,1] = self.H[2,2] = self.H[3,3] = 1.0
        self.R = np.eye(4) * 1.0

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, bbox: Tuple[float,float,float,float]):
        x1, y1, x2, y2 = bbox
        z = np.array([ (x1+x2)/2, (y1+y2)/2, (x2-x1), (y2-y1) ], dtype=float)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        y = z - self.H @ self.x
        self.x = self.x + K @ y
        I = np.eye(8)
        self.P = (I - K @ self.H) @ self.P

    def bbox(self) -> Tuple[float,float,float,float]:
        x, y, w, h = self.x[0], self.x[1], self.x[2], self.x[3]
        x1, y1 = x - w/2, y - h/2
        x2, y2 = x + w/2, y + h/2
        return (float(x1), float(y1), float(x2), float(y2))

class _STrack:
    def __init__(self, track_id: int, det: Detection):
        self.id = track_id
        self.cls = det.cls
        self.approach_id = det.approach_id
        self.kf = KalmanBox(det.bbox)
        self.last_seen_frame = det.frame_id

    def predict(self):
        self.kf.predict()

    def update(self, det: Detection):
        self.kf.update(det.bbox)
        self.last_seen_frame = det.frame_id

    def bbox(self) -> Tuple[float,float,float,float]:
        return self.kf.bbox()

class SORTTracker:
    def __init__(self, iou_thresh=0.3, max_age=15):
        self.iou_thresh = iou_thresh
        self.max_age = max_age
        self._tracks: List[_STrack] = []
        self._next_id = 1

    def update(self, detections: List[Detection], frame_id: int) -> List[Track]:
        # Predict all
        for t in self._tracks:
            t.predict()

        # Build IoU cost matrix class-aware
        if len(self._tracks) and len(detections):
            cost = np.zeros((len(self._tracks), len(detections)), dtype=float)
            for i, t in enumerate(self._tracks):
                tb = t.bbox()
                for j, d in enumerate(detections):
                    if t.cls != d.cls:
                        cost[i, j] = 1.0  # low IoU => force non-match
                    else:
                        cost[i, j] = 1.0 - iou(tb, d.bbox)
        else:
            cost = np.empty((0, 0))

        # Greedy assign (for simplicity)
        assigned_t, assigned_d = set(), set()
        pairs = []
        if cost.size:
            flat = [(cost[i, j], i, j) for i in range(cost.shape[0]) for j in range(cost.shape[1])]
            for c, i, j in sorted(flat):
                if i in assigned_t or j in assigned_d:
                    continue
                iou_ = 1.0 - c
                if iou_ >= self.iou_thresh:
                    pairs.append((i, j))
                    assigned_t.add(i)
                    assigned_d.add(j)

        # Update matched
        for i, j in pairs:
            self._tracks[i].update(detections[j])

        # Unmatched detections => new tracks
        for j, d in enumerate(detections):
            if j not in assigned_d:
                nt = _STrack(self._next_id, d)
                self._next_id += 1
                self._tracks.append(nt)

        # Prune aged tracks
        alive = []
        for t in self._tracks:
            if frame_id - t.last_seen_frame <= self.max_age:
                alive.append(t)
        self._tracks = alive

        # Return public Track list
        out: List[Track] = []
        for t in self._tracks:
            out.append(Track(
                track_id=t.id, bbox=t.bbox(), cls=t.cls,
                approach_id=t.approach_id, last_seen_frame=t.last_seen_frame
            ))
        return out