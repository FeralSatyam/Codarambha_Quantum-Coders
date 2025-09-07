from typing import Dict, List
from smart_signal.types import LaneStat, Splits

def webster_splits(lane_stats: List[LaneStat], lost_time_s: float, min_green: float, max_green: float) -> Splits:
    # Estimate flow ratios y_i from arrivals; simple normalization
    by_phase = {}  # phase key we’ll map later, placeholder
    Y = 0.0
    # Here we assume a single phase per movement later; will refine in Step 8
    # Use arrivals scaled to saturation (assume 1800 vph per lane)
    phase_key = "PH_ALL"  # placeholder
    y = sum(max(ls.arrival_rate_vph, 1.0)/1800.0 for ls in lane_stats)
    Y = min(max(y, 0.05), 0.95)
    cycle = (1.5*lost_time_s + 5.0) / (1.0 - Y)
    effective_green = max(cycle - lost_time_s, min_green * len(lane_stats))
    # naive equal split
    g_each = max(min(effective_green / max(len(lane_stats),1), max_green), min_green)
    return Splits(cycle_s=cycle, greens_s={phase_key: g_each})