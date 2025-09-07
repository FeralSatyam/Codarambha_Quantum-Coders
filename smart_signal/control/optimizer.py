from typing import List
from smart_signal.types import LaneStat, Splits, EmergencyEvent

class SignalOptimizer:
    def __init__(self, min_green_s=7, max_green_s=60, lost_time_s=4):
        self.min_green_s = min_green_s
        self.max_green_s = max_green_s
        self.lost_time_s = lost_time_s

    def compute_splits(self, lane_stats: List[LaneStat]) -> Splits:
        """
        Simple max-pressure: allocate green time proportional to queue length.
        """
        total_queue = sum(ls.queue_len for ls in lane_stats)
        if total_queue == 0:
            # No traffic — equal split
            equal_time = max(self.min_green_s, (self.max_green_s + self.min_green_s) / 2)
            return Splits(cycle_s=60, greens_s={ls.lane_id: equal_time for ls in lane_stats})

        greens = {}
        for ls in lane_stats:
            share = ls.queue_len / total_queue
            green_time = max(self.min_green_s, min(self.max_green_s, share * 60))
            greens[ls.lane_id] = green_time

        return Splits(cycle_s=60, greens_s=greens)

    def apply_emergency_priority(self, splits: Splits, emergencies: List[EmergencyEvent]) -> Splits:
        """
        If an emergency vehicle is detected, give its lane max green.
        """
        if not emergencies:
            return splits

        # For now, prioritise the first emergency event
        emg_lane = emergencies[0].approach_id  # could map to lane_id if needed
        for lane_id in splits.greens_s.keys():
            if lane_id.startswith(emg_lane):
                splits.greens_s[lane_id] = self.max_green_s
            else:
                splits.greens_s[lane_id] = self.min_green_s
        return splits