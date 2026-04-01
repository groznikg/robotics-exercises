import math

from ship_simulator import ShipSimulator


class CorridorSimulator(ShipSimulator):
    """ShipSimulator variant that combines two steering corrections:

    1. Crab angle  — rotates the nose into the wind so that the ground-velocity
                     vector points toward the goal, keeping the ship on the A–B line.
    2. Lateral correction — when a corridor half-width is given, adds a proportional
                     heading nudge back toward the centre line whenever the ship drifts
                     sideways.  Correction reaches MAX_LATERAL_CORRECTION_DEG at the
                     corridor boundary and stays clamped beyond it.
    """

    MAX_LATERAL_CORRECTION_DEG = 30.0

    def __init__(self, start_x: float, start_y: float,
                 goal_x: float, goal_y: float,
                 initial_heading_deg: float,
                 wind: WindData,
                 corridor_half_width_km: float | None = None,
                 use_crab_angle: bool = True) -> None:
        super().__init__(start_x, start_y, goal_x, goal_y, initial_heading_deg, wind)
        self.corridor_half_width_km = corridor_half_width_km
        self.use_crab_angle    = use_crab_angle
        self.max_deviation_km  = 0.0
        self.corridor_violated = False

    def _signed_deviation_km(self) -> float:
        """Signed perpendicular distance from the A–B line.
        Positive = ship is to the left of the A→B direction."""
        dx = self.goal_x - self.start_x
        dy = self.goal_y - self.start_y
        route_length = math.hypot(dx, dy)
        if route_length == 0.0:
            return 0.0
        return (dx * (self.y - self.start_y) - dy * (self.x - self.start_x)) / route_length

    def _step(self) -> float:
        """Advance state by one minute. Returns actual ground speed [km/h]."""
        # 1. Wind at current time
        wind_x, wind_y = self.wind.vector_at(self.elapsed_min)

        # 2. Goal direction + lateral corridor correction
        goal_dir_rad = math.atan2(self.goal_y - self.y, self.goal_x - self.x)
        if self.corridor_half_width_km is not None and self.corridor_half_width_km > 0.0:
            alpha = self._signed_deviation_km() / self.corridor_half_width_km
            alpha = max(-2.0, min(2.0, alpha))
            # Only correct when in the outer half of the corridor so that
            # a large corridor introduces no change to the unconstrained path.
            if abs(alpha) > 0.5:
                goal_dir_rad += -math.radians(self.MAX_LATERAL_CORRECTION_DEG) * alpha

        # 3. Crab angle to cancel perpendicular wind on the (corrected) goal direction
        if self.use_crab_angle and self.engine_speed_kmh > 0.0:
            w_perp   = -wind_x * math.sin(goal_dir_rad) + wind_y * math.cos(goal_dir_rad)
            sin_crab = max(-1.0, min(1.0, -w_perp / self.engine_speed_kmh))
            crab_rad = math.asin(sin_crab)
        else:
            crab_rad = 0.0
        desired_heading_deg = math.degrees(goal_dir_rad + crab_rad)

        # 4. Turn toward desired heading (capped at MAX_TURN_RATE deg/min)
        turn_deg         = max(-self.MAX_TURN_RATE,
                               min(self.MAX_TURN_RATE,
                                   self._angle_diff(desired_heading_deg, self.heading_deg)))
        self.heading_deg = (self.heading_deg + turn_deg) % 360.0

        # 5. Speed control — same logic as base class
        heading_rad  = math.radians(self.heading_deg)
        tailwind_kmh = wind_x * math.cos(heading_rad) + wind_y * math.sin(heading_rad)
        distance_km  = math.hypot(self.goal_x - self.x, self.goal_y - self.y)
        if self._stopping_distance_km(self.engine_speed_kmh) >= distance_km:
            min_engine_speed_kmh  = max(0.0, -tailwind_kmh + 1.0)
            self.engine_speed_kmh = max(min_engine_speed_kmh,
                                        self.engine_speed_kmh - self.MAX_ACCEL)
        else:
            self.engine_speed_kmh = min(self.MAX_SPEED_KMH,
                                        self.engine_speed_kmh + self.MAX_ACCEL)

        # 6. Update position
        total_vx         = self.engine_speed_kmh * math.cos(heading_rad) + wind_x
        total_vy         = self.engine_speed_kmh * math.sin(heading_rad) + wind_y
        ground_speed_kmh = math.hypot(total_vx, total_vy)
        self.x          += total_vx * self.DT_H
        self.y          += total_vy * self.DT_H
        self.elapsed_min += 1

        # 7. Track deviation and corridor violation
        dev = self._line_deviation_km()
        self.max_deviation_km = max(self.max_deviation_km, dev)
        if self.corridor_half_width_km is not None and dev > self.corridor_half_width_km:
            self.corridor_violated = True

        return ground_speed_kmh
