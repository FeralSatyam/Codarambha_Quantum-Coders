# smart_signal/control/controller.py
import time
from typing import Dict, Optional

class VisualController:
    """
    Plays out green times per lane_id over time and exposes current 'green' lanes.
    This is a simple visual simulator, not a hardware controller.
    """
    def __init__(self):
        self._schedule: Dict[str, float] = {}
        self._start_ts: Optional[float] = None
        self._order: Optional[list] = None

    def load_splits(self, greens_s: Dict[str, float]):
        # Define a deterministic order for playback
        self._order = sorted(greens_s.keys())
        self._schedule = greens_s
        self._start_ts = time.time()

    def current_green(self) -> Optional[str]:
        if not self._order or not self._start_ts:
            return None
        t = time.time() - self._start_ts
        # cycle through lanes by their green durations
        elapsed = 0.0
        for lane_id in self._order:
            g = self._schedule.get(lane_id, 0.0)
            if t < elapsed + g:
                return lane_id
            elapsed += g
        # if cycle finished, restart
        self._start_ts = time.time()
        return self._order[0] if self._order else None