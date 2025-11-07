import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import threading

from smart_signal.perception.detector import YOLODetector
from smart_signal.perception.tracker import IOUTracker


# -------------------------------
# UI
# -------------------------------
class TrafficUI(ctk.CTk):
    def __init__(self, detector, tracker, video_path):
        super().__init__()
        self.title("🚦 Traffic Detection")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel
        control_frame = ctk.CTkFrame(self, width=300)
        control_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        control_frame.grid_propagate(False)

        title = ctk.CTkLabel(control_frame, text="Smart Traffic System",
                             font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(15, 10))

        self.status_label = ctk.CTkLabel(control_frame, text="Simulation Ready",
                                         font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(control_frame)
        btn_frame.pack(pady=15, fill="x")
        self.start_btn = ctk.CTkButton(btn_frame, text="▶ Start", command=self.start_sim)
        self.start_btn.pack(pady=6, padx=10, fill="x")
        self.stop_btn = ctk.CTkButton(btn_frame, text="⏸ Stop", command=self.stop_sim)
        self.stop_btn.pack(pady=6, padx=10, fill="x")
        self.quit_btn = ctk.CTkButton(btn_frame, text="❌ Exit", fg_color="red",
                                      hover_color="#aa0000", command=self.quit)
        self.quit_btn.pack(pady=10, padx=10, fill="x")

        # Right panel: video
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Simulation state
        self.running = False
        self.detector = detector
        self.tracker = tracker
        self.video_path = video_path
        self.fid = 0
        self._last_imgtk = None

    # -------------------------------
    # Controls
    # -------------------------------
    def start_sim(self):
        if not self.running:
            self.running = True
            self.status_label.configure(text="Simulation Running...")
            threading.Thread(target=self.loop, daemon=True).start()

    def stop_sim(self):
        self.running = False
        self.status_label.configure(text="Simulation Paused")

    # -------------------------------
    # Core simulation loop
    # -------------------------------
    def loop(self):
        cap = cv2.VideoCapture(self.video_path)
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detector.infer(frame, self.fid, "Main")
            tracks = self.tracker.update(detections, self.fid)
            count = len(tracks)

            # Draw detections
            for tr in tracks:
                x1, y1, x2, y2 = map(int, tr.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID {tr.track_id} {tr.cls}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Overlay vehicle count only
            cv2.putText(frame, f"Cars detected: {count}",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show in UI
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=pil_img)
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
            self._last_imgtk = imgtk

            self.fid += 1
            self.after(50)  # ~20 FPS

        cap.release()


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    detector = YOLODetector("yolov8n.pt", conf_thresh=0.35)
    tracker = IOUTracker(iou_thresh=0.3, max_age=10)

    VIDEO_PATH = "videos/traffic.mp4"  # replace with your video file
    app = TrafficUI(detector, tracker, VIDEO_PATH)
    app.mainloop()