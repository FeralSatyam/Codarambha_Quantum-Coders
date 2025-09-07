from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from typing import Dict, Any, Tuple, Optional, List

def iou(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    x_left = max(ax1, bx1)
    y_top = max(ay1, by1)
    x_right = min(ax2, bx2)
    y_bottom = min(ay2, by2)
    if x_right <= x_left or y_bottom <= y_top:
        return 0.0
    inter = (x_right - x_left) * (y_bottom - y_top)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / max(area_a + area_b - inter, 1e-6)

def point_to_line_distance(point: Tuple[float,float], line: LineString) -> float:
    return line.distance(Point(point))

def box_centroid(b):
    x1,y1,x2,y2 = b
    return ((x1+x2)/2.0, (y1+y2)/2.0)