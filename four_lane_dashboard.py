import streamlit as st
import numpy as np
import cv2
import time
from smart_signal.perception.detector import YOLODetector
from smart_signal.perception.tracker import IOUTracker

class PriorityCycleController:
    def __init__(self, approaches=["N", "E", "S", "W"], min_green=5, max_green=20, yellow=3):
        self.approaches = approaches
        self.min_green = min_green
        self.max_green = max_green
        self.yellow = yellow
        self.priority_list = []
        self.current_idx = 0

    def start_cycle(self, counts):
        self.priority_list = sorted(self.approaches, key=lambda a: counts.get(a, 0), reverse=True)
        self.current_idx = 0

    def next_phase(self, counts):
        if not self.priority_list:
            self.start_cycle(counts)
        approach = self.priority_list[self.current_idx]
        count = counts.get(approach, 0)
        green = max(self.min_green, min(self.max_green, count * 2))
        yellow = self.yellow
        self.current_idx += 1
        if self.current_idx >= len(self.priority_list):
            self.priority_list = []
        return approach, green, yellow

def run_four_lane():
    st.subheader("🚦 Adaptive 4-Lane Traffic Simulator")

    # Sidebar controls
    min_green = st.sidebar.slider("Min GREEN (s)", 3, 15, 5)
    max_green = st.sidebar.slider("Max GREEN (s)", 10, 60, 20)
    yellow_time = st.sidebar.slider("YELLOW (s)", 2, 10, 3)
    start = st.sidebar.button("▶ Start Simulation")

    # Initialize session state
    if "fid" not in st.session_state:
        st.session_state.fid = 0
        st.session_state.green_left = 0
        st.session_state.yellow_left = 0
        st.session_state.current_approach = None
        st.session_state.running = False

    if start:
        st.session_state.running = True

    if not st.session_state.running:
        st.info("Click ▶ Start Simulation to begin.")
        return

    # Load static images
    IMAGE_PATHS = {
        "N": "test_images/north.png",
        "E": "test_images/east.png",
        "S": "test_images/south.png",
        "W": "test_images/west.png",
    }
    frames = {k: cv2.imread(v) for k, v in IMAGE_PATHS.items()}

    detector = YOLODetector("yolov8n.pt", conf_thresh=0.35)
    tracker = IOUTracker(iou_thresh=0.3, max_age=10)
    controller = PriorityCycleController(["N", "E", "S", "W"], min_green, max_green, yellow_time)

    counts, processed_frames = {}, {}
    for approach, frame in frames.items():
        detections = detector.infer(frame, st.session_state.fid, approach)
        tracks = tracker.update(detections, st.session_state.fid)
        counts[approach] = len(tracks)
        fcopy = frame.copy()
        for tr in tracks:
            x1, y1, x2, y2 = map(int, tr.bbox)
            cv2.rectangle(fcopy, (x1, y1), (x2, y2), (0, 255, 0), 2)
        processed_frames[approach] = fcopy

    # Phase control
    if st.session_state.green_left > 0:
        st.session_state.green_left -= 1
    elif st.session_state.yellow_left > 0:
        st.session_state.yellow_left -= 1
        if st.session_state.yellow_left == 0:
            ap, g, y = controller.next_phase(counts)
            st.session_state.current_approach = ap
            st.session_state.green_left = g
            st.session_state.yellow_left = 0
    else:
        ap, g, y = controller.next_phase(counts)
        st.session_state.current_approach = ap
        st.session_state.green_left = g
        st.session_state.yellow_left = 0

    # Overlay signal state
    def prepare(img, width=640, height=360):
        if img is None:
            return np.zeros((height, width, 3), dtype=np.uint8)
        return cv2.resize(img, (width, height))

    for approach in processed_frames:
        frame = processed_frames[approach]
        if approach == st.session_state.current_approach and st.session_state.green_left > 0:
            color, status = (0, 255, 0), f"GREEN {st.session_state.green_left}s"
        else:
            color, status = (0, 0, 255), "RED"
        cv2.putText(frame, f"{approach}: {status} | Cars: {counts.get(approach, 0)}",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Build 2x2 grid
    n = prepare(processed_frames.get("N"))
    e = prepare(processed_frames.get("E"))
    s = prepare(processed_frames.get("S"))
    w = prepare(processed_frames.get("W"))
    top = cv2.hconcat([n, e])
    bottom = cv2.hconcat([s, w])
    grid = cv2.vconcat([top, bottom])
    grid_rgb = cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)

    # Display
    st.image(grid_rgb, caption="4-Lane CCTV Grid", use_container_width=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("North", counts["N"])
    c2.metric("East", counts["E"])
    c3.metric("South", counts["S"])
    c4.metric("West", counts["W"])

    st.session_state.fid += 1
    time.sleep(0.5)
    st.rerun()