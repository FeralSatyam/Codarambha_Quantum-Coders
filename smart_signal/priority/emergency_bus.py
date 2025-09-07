# smart_signal/priority/emergency_bus.py
import json
import time
from pathlib import Path
from typing import List
from smart_signal.types import EmergencyEvent

class FileEmergencyBus:
    """
    Polls a JSON file containing a list of emergency events.
    Schema:
    [
      {"vehicle_id":"AMB1","vehicle_type":"ambulance","approach_id":"N","eta_s":15,"siren_on":true}
    ]
    """
    def __init__(self, json_path: str, poll_interval_s: float = 1.0):
        self.path = Path(json_path)
        self.poll_interval_s = poll_interval_s
        self._last_mtime = 0.0

    def read_recent(self) -> List[EmergencyEvent]:
        if not self.path.exists():
            time.sleep(self.poll_interval_s)
            return []
        mtime = self.path.stat().st_mtime
        if mtime == self._last_mtime:
            time.sleep(self.poll_interval_s)
            return []
        self._last_mtime = mtime
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []
        events = []
        for item in data:
            try:
                events.append(EmergencyEvent(**item))
            except Exception:
                continue
        return events