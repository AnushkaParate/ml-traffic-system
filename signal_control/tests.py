from django.test import TestCase

from .models import SignalLog
from .services import (
    AMBULANCE_GREEN_SECONDS, GREEN_BASE_SECONDS, MAX_GREEN_SECONDS,
    compute_cycle, decide_signal_states,
)


class ComputeCycleTests(TestCase):
    def test_ambulance_lane_goes_first_with_fixed_green_time(self):
        cycle = compute_cycle(
            {'north': 1, 'south': 10, 'east': 0, 'west': 5},
            ambulance_lane='south',
        )
        self.assertEqual(cycle[0]['lane'], 'south')
        self.assertEqual(cycle[0]['green_seconds'], AMBULANCE_GREEN_SECONDS)
        self.assertEqual(cycle[0]['reason'], 'ambulance')

    def test_rotation_resumes_anti_clockwise_after_ambulance_lane(self):
        # LANE_ORDER is north -> west -> south -> east. Ambulance in west
        # should mean the rotation continues south, then east (skipping
        # north since it wraps around past the ambulance's own turn).
        cycle = compute_cycle(
            {'north': 3, 'west': 2, 'south': 4, 'east': 1},
            ambulance_lane='west',
        )
        lanes_in_order = [phase['lane'] for phase in cycle]
        self.assertEqual(lanes_in_order, ['west', 'south', 'east', 'north'])

    def test_empty_lanes_are_skipped_entirely(self):
        cycle = compute_cycle({'north': 0, 'west': 3, 'south': 0, 'east': 2})
        lanes_in_cycle = [phase['lane'] for phase in cycle]
        self.assertNotIn('north', lanes_in_cycle)
        self.assertNotIn('south', lanes_in_cycle)
        self.assertIn('west', lanes_in_cycle)
        self.assertIn('east', lanes_in_cycle)

    def test_lanes_at_or_below_average_get_flat_base_green(self):
        # north=3, west=3: exactly equal, neither is denser than the other
        cycle = compute_cycle({'north': 3, 'west': 3, 'south': 0, 'east': 0})
        for phase in cycle:
            self.assertEqual(phase['green_seconds'], GREEN_BASE_SECONDS)
            self.assertEqual(phase['reason'], 'normal')

    def test_lane_denser_than_average_gets_bonus_time(self):
        # west=12 is far above the average of {2, 3, 12} -> should get a bonus
        cycle = compute_cycle({'north': 2, 'west': 12, 'south': 0, 'east': 3})
        west_phase = next(p for p in cycle if p['lane'] == 'west')
        self.assertGreater(west_phase['green_seconds'], GREEN_BASE_SECONDS)
        self.assertEqual(west_phase['reason'], 'density')

        north_phase = next(p for p in cycle if p['lane'] == 'north')
        self.assertEqual(north_phase['green_seconds'], GREEN_BASE_SECONDS)
        self.assertEqual(north_phase['reason'], 'normal')

    def test_busier_lane_gets_extra_green_time_capped_at_max(self):
        cycle = compute_cycle({'north': 100, 'west': 1, 'south': 0, 'east': 0})
        self.assertEqual(cycle[0]['green_seconds'], MAX_GREEN_SECONDS)
        self.assertEqual(cycle[0]['reason'], 'density')

    def test_anti_clockwise_order_preserved_with_no_ambulance(self):
        cycle = compute_cycle({'north': 2, 'west': 3, 'south': 4, 'east': 5})
        lanes_in_order = [phase['lane'] for phase in cycle]
        self.assertEqual(lanes_in_order, ['north', 'west', 'south', 'east'])

    def test_all_lanes_empty_produces_empty_cycle(self):
        cycle = compute_cycle({'north': 0, 'west': 0, 'south': 0, 'east': 0})
        self.assertEqual(cycle, [])


class DecideSignalStatesTests(TestCase):
    def test_first_lane_in_cycle_is_green_rest_are_red(self):
        states = decide_signal_states('Main Square', {'north': 2, 'west': 3, 'south': 4, 'east': 0})
        self.assertEqual(states['north'], 'green')  # first anti-clockwise, non-zero
        self.assertEqual(states['west'], 'red')
        self.assertEqual(states['south'], 'red')
        self.assertEqual(states['east'], 'off')

    def test_ambulance_lane_is_green_even_out_of_turn(self):
        states = decide_signal_states(
            'Main Square', {'north': 5, 'west': 5, 'south': 5, 'east': 5}, ambulance_lane='east',
        )
        self.assertEqual(states['east'], 'green')
        self.assertEqual(states['north'], 'red')

    def test_writes_a_signal_log_entry_per_lane(self):
        decide_signal_states('Main Square', {'north': 2, 'west': 0, 'south': 0, 'east': 0})
        self.assertEqual(SignalLog.objects.filter(intersection_id='Main Square').count(), 4)