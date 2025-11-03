import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import YOLODetector
from smart_signal.perception.tracker import IOUTracker

# Categories we want to track cumulatively
CATEGORIES = ["car", "bus", "truck", "motorcycle", "bicycle", "pedestrian"]

class TrackerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🚦 Multi-Class Tracking Dashboard")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Layout
        self.grid_columnconfigure(0, weight=0)  # left controls
        self.grid_columnconfigure(1, weight=1)  # right video+chart
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        control_frame = ctk.CTkFrame(self, width=280)
        control_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        control_frame.grid_propagate(False)

        title = ctk.CTkLabel(control_frame, text="Live Tracker",
                             font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(15, 10))

        self.status_label = ctk.CTkLabel(control_frame, text="Ready",
                                         font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)

        # Category counts (cumulative)
        self.count_labels = {}
        for cat in CATEGORIES:
            lab = ctk.CTkLabel(control_frame, text=f"{cat.capitalize()}: 0",
                               font=ctk.CTkFont(size=14))
            lab.pack(pady=2)
            self.count_labels[cat] = lab

        self.track_count_label = ctk.CTkLabel(control_frame, text="Active Tracks: 0",
                                              font=ctk.CTkFont(size=14))
        self.track_count_label.pack(pady=15)

        # Buttons
        self.start_btn = ctk.CTkButton(control_frame, text="▶ Start", command=self.start_cam)
        self.start_btn.pack(pady=6, padx=10, fill="x")

        self.stop_btn = ctk.CTkButton(control_frame, text="⏸ Stop", command=self.stop_cam)
        self.stop_btn.pack(pady=6, padx=10, fill="x")

        self.reset_btn = ctk.CTkButton(control_frame, text="🔄 Reset Counts", command=self.reset_counts)
        self.reset_btn.pack(pady=6, padx=10, fill="x")

        self.quit_btn = ctk.CTkButton(control_frame, text="❌ Exit", fg_color="red",
                                      hover_color="#aa0000", command=self.quit)
        self.quit_btn.pack(pady=20, padx=10, fill="x")

        # Right panel: split into video (row 0) and chart (row 1)
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=3)  # video gets more space
        right_panel.grid_rowconfigure(1, weight=2)  # chart gets good space too

        # Video feed
        self.video_label = ctk.CTkLabel(right_panel, text="")
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Chart area
        fig = Figure(figsize=(6,3), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Cumulative Counts")
        self.ax.set_ylim(0, 10)
        self.bar_container = self.ax.bar(CATEGORIES, [0]*len(CATEGORIES), color="skyblue")

        self.canvas = FigureCanvasTkAgg(fig, master=right_panel)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        # State
        self.cam = None
        self.detector = None
        self.tracker = None
        self.running = False
        self._last_imgtk = None

        # Persistent storage
        self.total_counts = {cat: 0 for cat in CATEGORIES}
        self.seen_ids = {cat: set() for cat in CATEGORIES}

    def start_cam(self):
        if not self.running:
            self.running = True
            self.status_label.configure(text="Running...")
            self.detector = YOLODetector(model_path="yolov8n.pt", conf_thresh=0.3)
            self.tracker = IOUTracker(iou_thresh=0.3, max_age=10)
            self.cam = CameraStream(1, fps=30)  # webcam or video path
            threading.Thread(target=self.loop, daemon=True).start()

    def stop_cam(self):
        self.running = False
        self.status_label.configure(text="Stopped")
        if self.cam:
            self.cam.release()
            self.cam = None

    def reset_counts(self):
        self.total_counts = {cat: 0 for cat in CATEGORIES}
        self.seen_ids = {cat: set() for cat in CATEGORIES}
        for cat in CATEGORIES:
            self.count_labels[cat].configure(text=f"{cat.capitalize()}: 0")
        self.update_chart(self.total_counts)

    def update_chart(self, counts):
        values = [counts.get(cat, 0) for cat in CATEGORIES]
        for rect, val in zip(self.bar_container, values):
            rect.set_height(val)
        self.ax.set_ylim(0, max(10, max(values)+2))
        self.canvas.draw_idle()

    def loop(self):
        for fid, ts, frame in self.cam.frames():
            if not self.running:
                break
            detections = self.detector.infer(frame, fid, "N")
            tracks = self.tracker.update(detections, fid)

            # Update persistent counts
            for tr in tracks:
                cls = tr.cls.lower()
                if cls in self.total_counts:
                    if tr.track_id not in self.seen_ids[cls]:
                        self.seen_ids[cls].add(tr.track_id)
                        self.total_counts[cls] += 1

                # Draw tracks
                x1, y1, x2, y2 = map(int, tr.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, f"ID {tr.track_id}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            # Update side panel with cumulative counts
            for cat in CATEGORIES:
                self.count_labels[cat].configure(text=f"{cat.capitalize()}: {self.total_counts[cat]}")
            self.track_count_label.configure(text=f"Active Tracks: {len(tracks)}")

            # Update chart with cumulative counts
            self.update_chart(self.total_counts)

            # Convert to Tkinter image
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=pil_img)
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
            self._last_imgtk = imgtk

            if not self.running:
                break

        self.stop_cam()


if __name__ == "__main__":
    app = TrackerUI()
    app.mainloop()