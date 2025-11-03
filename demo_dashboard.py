import streamlit as st
import numpy as np
import cv2
import time
from smart_signal.perception.detector import YOLODetector
from smart_signal.perception.tracker import IOUTracker

# -------------------------------
# Priority-based cycle controller
# -------------------------------
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

# -------------------------------
# 4-Lane Simulator
# -------------------------------
def run_four_lane():
    st.subheader("🚦 Adaptive 4-Lane Traffic Simulator")

    # Sidebar controls
    min_green = st.sidebar.slider("Min GREEN (s)", 3, 15, 5)
    max_green = st.sidebar.slider("Max GREEN (s)", 10, 60, 20)
    yellow_time = st.sidebar.slider("YELLOW (s)", 2, 10, 3)

    if "sim_running" not in st.session_state:
        st.session_state.sim_running = False
        st.session_state.fid = 0
        st.session_state.green_left = 0
        st.session_state.yellow_left = 0
        st.session_state.current_approach = None

    start_btn = st.sidebar.button("▶ Start Simulation")
    stop_btn = st.sidebar.button("⏸ Stop Simulation")

    if start_btn:
        st.session_state.sim_running = True
    if stop_btn:
        st.session_state.sim_running = False

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

    video_placeholder = st.empty()
    counts_placeholder = st.empty()

    if st.session_state.sim_running:
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

        # Overlay signals
        def prepare(img, width=640, height=360):
            if img is None:
                return np.zeros((height, width, 3), dtype=np.uint8)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            return cv2.resize(img, (width, height))

        for approach in processed_frames:
            frame = processed_frames[approach]
            if approach == st.session_state.current_approach and st.session_state.green_left > 0:
                color, status = (0, 255, 0), f"GREEN {st.session_state.green_left}s"
            else:
                color, status = (0, 0, 255), "RED"
            cv2.putText(frame, f"{approach}: {status} | Cars: {counts.get(approach, 0)}",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        n = prepare(processed_frames.get("N"))
        e = prepare(processed_frames.get("E"))
        s = prepare(processed_frames.get("S"))
        w = prepare(processed_frames.get("W"))

        top = cv2.hconcat([n, e])
        bottom = cv2.hconcat([s, w])
        grid = cv2.vconcat([top, bottom])
        grid_rgb = cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)

        video_placeholder.image(grid_rgb, caption="4-Lane CCTV Grid", use_column_width=True)
        with counts_placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("N", counts["N"])
            c2.metric("E", counts["E"])
            c3.metric("S", counts["S"])
            c4.metric("W", counts["W"])

        st.session_state.fid += 1
        time.sleep(0.5)

# -------------------------------
# Camera Detection (placeholder)
# -------------------------------
def run_camera():
    st.subheader("📷 Real-Time Vehicle Detection")
    st.info("This will stream annotated frames from your webcam or phone camera.")
    st.image(np.zeros((300, 500, 3), dtype=np.uint8), caption="Camera Feed")

# -------------------------------
# 2D Simulation (placeholder)
# -------------------------------
def run_sim2d():
    st.subheader("🕹️ 2D Traffic Simulation")
    st.info("This will render your 2D simulation frames.")
    st.image(np.zeros((400, 400, 3), dtype=np.uint8), caption="2D Simulation")

# -------------------------------
# Analytics
# -------------------------------
def run_analytics():
    st.subheader("📊 Analytics & Impact")
    st.metric("Avg Wait Time", "32s")
    st.metric("Vehicles Detected", 128)
    st.line_chart({"Cars": [5, 10, 15, 20], "Buses": [1, 2, 2, 3], "Trucks": [0, 1, 1, 2]})

# -------------------------------
# Streamlit App Layout
# -------------------------------
st.set_page_config(page_title="Smart Traffic AI Dashboard", layout="wide")

st.markdown("<h1 style='text-align:center;color:cyan;'>⚡ Smart Traffic Control Dashboard ⚡</h1>", unsafe_allow_html=True)
st.write("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a module:", [
    "4-Lane Simulator",
    "Vehicle Detection (Camera)",
    "2D Simulation",
    "Analytics"
])

# Route to selected module
if page == "4-Lane Simulator":
    run_four_lane()
elif page == "Vehicle Detection (Camera)":
    run_camera()
elif page == "2D Simulation":
    run_sim2d()
elif page == "Analytics":
    run_analytics()

# Footer
st.write("---")
st.markdown("<p style='text-align:center;color:gray;'>Team SmartCity • Hackathon 2025</p>", unsafe_allow_html=True)