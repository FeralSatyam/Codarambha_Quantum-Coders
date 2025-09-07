import cv2
from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import StubDetector, YOLODetector

# --- Choose which detector to use ---
# For fake random boxes (testing pipeline without a real model):
detector = StubDetector()

# For real YOLO detections (requires `pip install ultralytics` and yolov8n.pt weights):
detector = YOLODetector(model_path="yolov8n.pt", conf_thresh=0.3)
# -------------------------------------

def main():
    cam = CameraStream(0, fps=15)  # 0 = webcam, or replace with video path

    for fid, ts, frame in cam.frames():
        detections = detector.infer(frame, fid, "N")

        # Draw boxes
        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{det.cls} {det.score:.2f}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Detector Output", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()