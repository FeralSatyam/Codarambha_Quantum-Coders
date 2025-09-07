import cv2
from smart_signal.perception.camera import CameraStream
from smart_signal.perception.detector import YOLODetector
from smart_signal.perception.tracker import IOUTracker
from smart_signal.perception.lane_mapper import LaneMapper

def main():
    #cam = CameraStream(0, fps=15)  # webcam or video
    cam = CameraStream("assets/car_moving.mp4", fps=15)
    detector = YOLODetector(model_path="yolov8n.pt", conf_thresh=0.3)
    tracker = IOUTracker(iou_thresh=0.3, max_age=10)
    lane_mapper = LaneMapper("data/lanes/example_intersection.geojson")

    for fid, ts, frame in cam.frames():
        detections = detector.infer(frame, fid, "N")
        tracks = tracker.update(detections, fid)
        lane_assignments = lane_mapper.assign_tracks(tracks)
        lane_stats = lane_mapper.compute_lane_stats(lane_assignments)

        # Draw lanes and IDs
        for lane_id, tracks_in_lane in lane_assignments.items():
            for tr in tracks_in_lane:
                x1, y1, x2, y2 = map(int, tr.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{lane_id} ID{tr.track_id}",
                            (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show lane stats in console
        for stat in lane_stats:
            print(stat)

        cv2.imshow("Lane Mapping", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()