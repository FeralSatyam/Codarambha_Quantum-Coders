import cv2
from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import YOLODetector  # or StubDetector
from smart_signal.perception.tracker import IOUTracker

def main():
    cam = CameraStream(0, fps=15)  # webcam or video path
    #cam = CameraStream("assets/vehicle.mp4", fps=15)
    detector = YOLODetector(model_path="yolov8n.pt", conf_thresh=0.3)
    tracker = IOUTracker(iou_thresh=0.3, max_age=10)

    for fid, ts, frame in cam.frames():
        detections = detector.infer(frame, fid, "N")
        tracks = tracker.update(detections, fid)

        for tr in tracks:
            x1, y1, x2, y2 = map(int, tr.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {tr.track_id} {tr.cls}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Tracker Output", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()