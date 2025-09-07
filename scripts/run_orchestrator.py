from smart_signal.runtime.orchestrator import Orchestrator

def main():
    use_video = True  # toggle webcam vs video
    config = {
        "camera_source": "assets/car_moving.mp4" if use_video else 0,
        "fps": None,
        "model_path": "yolov8n.pt",
        "conf_thresh": 0.3,
        "lane_geojson": "data/lanes/example_intersection.geojson",
        "min_green_s": 7,
        "max_green_s": 60,
        "use_stub": False,          # set True to test without YOLO
        "tracker": "sort",          # "sort" or "iou"
        "emergency_json": "emergency_events.json"
    }
    orch = Orchestrator(config)
    orch.run()

if __name__ == "__main__":
    main()