from smart_signal.types import LaneStat, EmergencyEvent
from smart_signal.control.optimizer import SignalOptimizer

def main():
    # Fake lane stats for testing
    lane_stats = [
        LaneStat(approach_id="N", lane_id="N1", movement="through", queue_len=10, arrival_rate_vph=600, occupancy=0.5, spillback=False),
        LaneStat(approach_id="E", lane_id="E1", movement="through", queue_len=5, arrival_rate_vph=300, occupancy=0.3, spillback=False),
        LaneStat(approach_id="S", lane_id="S1", movement="through", queue_len=2, arrival_rate_vph=120, occupancy=0.1, spillback=False),
        LaneStat(approach_id="W", lane_id="W1", movement="through", queue_len=8, arrival_rate_vph=480, occupancy=0.4, spillback=False)
    ]

    optimizer = SignalOptimizer(min_green_s=7, max_green_s=60)
    splits = optimizer.compute_splits(lane_stats)
    print("Normal splits:", splits)

    # Simulate emergency vehicle on North approach
    emergencies = [EmergencyEvent(vehicle_id="AMB123", vehicle_type="ambulance", approach_id="N", eta_s=15)]
    priority_splits = optimizer.apply_emergency_priority(splits, emergencies)
    print("Priority splits:", priority_splits)

if __name__ == "__main__":
    main()