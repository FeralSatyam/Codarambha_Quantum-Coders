import cv2
from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import StubDetector
from smart_signal.perception.detector import StubDetector, YOLODetector

def main():
    #cam = CameraStream(0, fps=15)  # webcam
    cam = CameraStream("assets/car_moving.mp4", fps=15)
    detector = StubDetector()

    for fid, ts, frame in cam.frames():
        detections = detector.infer(frame, fid, "N")

        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{det.cls} {det.score}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Stub Detector", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()