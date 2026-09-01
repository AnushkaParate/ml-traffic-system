"""Core decision logic for a 4-way intersection ('square').

Priority order (matches real Indian traffic signal convention):
1. Ambulance / emergency vehicle in any lane -> that lane gets green
   immediately, pre-empting the normal rotation.
2. Otherwise, lanes rotate ANTI-CLOCKWISE (North -> West -> South -> East
   -> North...), each getting a fixed 15s green + 5s amber by default.
3. Density-based priority: a lane with more waiting vehicles gets EXTRA
   green time (beyond the 15s base), up to a capped maximum -- it does not
   jump the anti-clockwise order, only gets a longer turn when its turn
   comes. This mirrors how real adaptive signals work: timing changes,
   sequence doesn't.
4. A lane with 0 vehicles is skipped entirely (0 seconds allocated) --
   the rotation moves straight to the next lane anti-clockwise.

This is deliberately separated from views.py so that once the ML
teammate's vehicle-counting model is ready, it can call compute_cycle()
directly with real counts instead of the manual admin form.

Note on rule 4 / "shut off mid-green if a lane empties out": this
implementation only checks vehicle counts at the moment the cycle is
computed (i.e. when the form is submitted, or whenever the detection
pipeline calls this with a fresh count). It does not continuously
re-check counts second-by-second during an already-running green phase.
Doing that properly needs a live, continuously-updating video feed --
worth revisiting once the detection app is actually running.
"""

from .models import SignalLog

# Anti-clockwise order, matching Indian traffic convention.
LANE_ORDER = ['north', 'west', 'south', 'east']

GREEN_BASE_SECONDS = 15
AMBER_SECONDS = 5
MAX_GREEN_SECONDS = 30
AMBULANCE_GREEN_SECONDS = 20


def compute_cycle(lane_counts, ambulance_lane=None):
    """
    lane_counts: dict like {'north': 5, 'south': 0, 'east': 3, 'west': 2}
    ambulance_lane: the lane name an ambulance was detected in, or None

    Returns an ordered list of phases, each:
        {'lane': ..., 'vehicle_count': ..., 'green_seconds': ..., 'reason': ...}
    'reason' is 'ambulance', 'density' (got extra time), or 'normal' (base 15s).
    Lanes with 0 vehicles are left out of the list entirely -- they're off.
    """
    cycle = []

    if ambulance_lane and ambulance_lane in lane_counts:
        cycle.append({
            'lane': ambulance_lane,
            'vehicle_count': lane_counts[ambulance_lane],
            'green_seconds': AMBULANCE_GREEN_SECONDS,
            'reason': 'ambulance',
        })
        # Resume the anti-clockwise rotation starting right after the
        # ambulance's lane, rather than restarting from North every time.
        start_idx = (LANE_ORDER.index(ambulance_lane) + 1) % len(LANE_ORDER)
        rotation = LANE_ORDER[start_idx:] + LANE_ORDER[:start_idx]
        rotation = [lane for lane in rotation if lane != ambulance_lane]
    else:
        rotation = LANE_ORDER

    active_counts = {lane: lane_counts.get(lane, 0) for lane in rotation if lane_counts.get(lane, 0) > 0}
    average_count = sum(active_counts.values()) / len(active_counts) if active_counts else 0

    for lane in rotation:
        count = lane_counts.get(lane, 0)
        if count == 0:
            continue  # skipped entirely -- stays off, rotation moves on

        if count > average_count:
            # Denser than the other currently-active lanes -> bonus time
            # proportional to how far above average it is.
            bonus = round((count - average_count) * 2)
            green = min(MAX_GREEN_SECONDS, GREEN_BASE_SECONDS + bonus)
            reason = 'density' if green > GREEN_BASE_SECONDS else 'normal'
        else:
            green = GREEN_BASE_SECONDS
            reason = 'normal'

        cycle.append({
            'lane': lane,
            'vehicle_count': count,
            'green_seconds': green,
            'reason': reason,
        })

    return cycle


def decide_signal_states(intersection_id, lane_counts, ambulance_lane=None):
    """Returns a snapshot dict {lane: state} for the CURRENT moment --
    whichever lane is first in the computed cycle is 'green' right now,
    every other active lane is 'red' (waiting its turn), and any lane left
    out of the cycle entirely is 'off'. Also logs one SignalLog row per
    lane for history.

    Built on top of compute_cycle() so there's a single source of truth
    for the rotation/priority rules -- this function only reads off "what's
    true right now" from that rotation.
    """
    cycle = compute_cycle(lane_counts, ambulance_lane)
    active_lanes = {phase['lane'] for phase in cycle}
    current_lane = cycle[0]['lane'] if cycle else None

    states = {}
    for lane in lane_counts:
        if lane not in active_lanes:
            states[lane] = 'off'
        elif lane == current_lane:
            states[lane] = 'green'
        else:
            states[lane] = 'red'

    for lane, state in states.items():
        SignalLog.objects.create(
            intersection_id=intersection_id,
            lane=lane,
            vehicle_count=lane_counts.get(lane, 0),
            ambulance_detected=(lane == ambulance_lane),
            signal_state=state,
        )

    return states