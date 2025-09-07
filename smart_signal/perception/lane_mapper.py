import json
from shapely.geometry import Polygon, Point

from shapely.geometry import Point

from typing import Dict, List
from smart_signal.types import Track, LaneStat

class LaneMapper:
    """
    Maps tracked vehicles to lanes using lane polygons from a GeoJSON file.
    """
    def __init__(self, geojson_path: str):
        self.lane_polygons: Dict[str, Polygon] = {}
        self.lane_meta: Dict[str, dict] = {}
        self._load_geojson(geojson_path)

    def _load_geojson(self, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        for feat in data["features"]:
            if feat["properties"].get("type") == "lane":
                lane_id = feat["properties"]["lane_id"]
                approach_id = feat["properties"]["approach_id"]
                movement = feat["properties"]["movement"]
                poly = Polygon(feat["geometry"]["coordinates"][0])
                self.lane_polygons[lane_id] = poly
                self.lane_meta[lane_id] = {
                    "approach_id": approach_id,
                    "movement": movement
                }

    def assign_tracks(self, tracks: List[Track]) -> Dict[str, List[Track]]:
        """
        Returns a dict: lane_id -> list of tracks inside that lane polygon.
        """
        lane_assignments: Dict[str, List[Track]] = {lid: [] for lid in self.lane_polygons}
        for tr in tracks:
            cx = (tr.bbox[0] + tr.bbox[2]) / 2
            cy = (tr.bbox[1] + tr.bbox[3]) / 2
            point = Point(cx, cy)
            for lane_id, poly in self.lane_polygons.items():
                if poly.contains(point):
                    lane_assignments[lane_id].append(tr)
                    break
        return lane_assignments

     

    def compute_lane_stats(self, lane_assignments: Dict[str, List[Track]]) -> List[LaneStat]:
        stats = []
        for lane_id, tracks in lane_assignments.items():
            meta = self.lane_meta[lane_id]
            queue_len = len(tracks)
            arrival_rate = queue_len * 3600 / 60
            occupancy = min(queue_len / 10.0, 1.0)
            spillback = queue_len > 8
            stats.append(
                LaneStat(
                    approach_id=meta["approach_id"],
                    lane_id=lane_id,
                    movement=meta["movement"],
                    queue_len=queue_len,
                    arrival_rate_vph=arrival_rate,
                    occupancy=occupancy,
                    spillback=spillback
                )
            )
        return stats

    def get_approach_for_point(self, x: float, y: float) -> str:
        """
        Given a point (pixel coords), return the approach_id of the lane polygon it falls into.
        Returns 'unknown' if no match.
        """
        pt = Point(x, y)
        for lane_id, poly in self.lane_polygons.items():
            if poly.contains(pt):
                return self.lane_meta[lane_id]["approach_id"]
        return "unknown"