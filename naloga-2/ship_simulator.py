"""Ship navigation simulator — kinematics and control logic."""

import math

from wind import WindData


class ShipSimulator:
    """Minute-by-minute ship navigation simulator."""

    MAX_SPEED_KMH = 30.0        # km/h
    MAX_ACCEL     = 2.0         # km/h per minute
    MAX_TURN_RATE = 5.0         # degrees per minute
    DT_H          = 1.0 / 60.0 # time step: 1 minute in hours
    ARRIVAL_KM    = 0.5         # arrival threshold [km]

    def __init__(self, start_x: float, start_y: float,
                 goal_x: float, goal_y: float,
                 initial_heading_deg: float,
                 wind: WindData) -> None:
        self.start_x, self.start_y = start_x, start_y
        self.goal_x,  self.goal_y  = goal_x,  goal_y
        self.wind = wind

        # State
        self.x, self.y        = start_x, start_y
        self.heading_deg      = initial_heading_deg
        self.engine_speed_kmh = 0.0
        self.elapsed_min      = 0
        self.max_deviation_km = 0.0

    @staticmethod
    def _angle_diff(target_deg: float, current_deg: float) -> float:
        """Signed shortest difference (target - current) in (-180, +180]."""
        return ((target_deg - current_deg + 180.0) % 360.0) - 180.0

    @staticmethod
    def _stopping_distance_km(speed_kmh: float) -> float:
        """Minimum distance needed to decelerate from speed_kmh to 0."""
        return speed_kmh * (speed_kmh + ShipSimulator.MAX_ACCEL) / (2.0 * ShipSimulator.MAX_ACCEL * 60.0)

    def _line_deviation_km(self) -> float:
        """Perpendicular distance from current position to the start-goal line [km]."""
        route_length_km = math.hypot(self.goal_x - self.start_x, self.goal_y - self.start_y)
        if route_length_km == 0.0:
            return math.hypot(self.x - self.start_x, self.y - self.start_y)
        return abs(
            (self.goal_x - self.start_x) * (self.start_y - self.y)
            - (self.start_x - self.x) * (self.goal_y - self.start_y)
        ) / route_length_km

    def _make_table_header(self) -> tuple[str, str, str]:
        columns = [
            ("Čas",             "[min]",    10),
            ("Pozicija X",      "[100 km]", 12),
            ("Pozicija Y",      "[100 km]", 12),
            ("Hitrost",         "[km/h]",   10),
            ("Dejanska hitrost","[km/h]",   16),
            ("Smer",            "[°]",       8),
            ("Razdalja do B",   "[100 km]", 14),
            ("Odmik od trase",  "[100 km]", 15),
        ]
        header    = "  ".join(f"{name:>{width}}" for name, _, width in columns)
        units     = "  ".join(f"{unit:>{width}}" for _, unit, width in columns)
        separator = "-" * len(header)
        return header, units, separator

    def _format_row(self, distance_km: float, deviation_km: float, ground_speed_kmh: float) -> str:
        vals = [self.elapsed_min, self.x/100, self.y/100, self.engine_speed_kmh,
                ground_speed_kmh, self.heading_deg, distance_km/100, deviation_km/100]
        fmts = [">10d", ">12.4f", ">12.4f", ">10.2f", ">16.2f",
                ">8.1f", ">14.5f", ">15.6f"]
        return "  ".join(format(val, fmt) for val, fmt in zip(vals, fmts))

    def _step(self) -> float:
        """Advance state by one minute. Returns actual ground speed [km/h]."""
        # 1. Desired heading toward goal
        desired_heading_deg = math.degrees(
            math.atan2(self.goal_y - self.y, self.goal_x - self.x)
        )

        # 2. Turn toward desired heading (capped at MAX_TURN_RATE deg/min)
        turn_deg         = max(-self.MAX_TURN_RATE,
                               min(self.MAX_TURN_RATE,
                                   self._angle_diff(desired_heading_deg, self.heading_deg)))
        self.heading_deg = (self.heading_deg + turn_deg) % 360.0

        # 3. Wind at current time
        wind_x, wind_y = self.wind.vector_at(self.elapsed_min)

        # 4. Speed control — deceleration decision based on engine speed only,
        #    so wind doesn't cause premature braking or unnecessary re-acceleration.
        heading_rad  = math.radians(self.heading_deg)
        tailwind_kmh = wind_x * math.cos(heading_rad) + wind_y * math.sin(heading_rad)
        distance_km  = math.hypot(self.goal_x - self.x, self.goal_y - self.y)
        if self._stopping_distance_km(self.engine_speed_kmh) >= distance_km:
            # Braking: keep enough engine thrust to avoid being pushed backward by headwind.
            min_engine_speed_kmh  = max(0.0, -tailwind_kmh + 1.0)
            self.engine_speed_kmh = max(min_engine_speed_kmh,
                                        self.engine_speed_kmh - self.MAX_ACCEL)
        else:
            self.engine_speed_kmh = min(self.MAX_SPEED_KMH,
                                        self.engine_speed_kmh + self.MAX_ACCEL)

        # 5. Update position
        total_vx      = self.engine_speed_kmh * math.cos(heading_rad) + wind_x
        total_vy      = self.engine_speed_kmh * math.sin(heading_rad) + wind_y
        ground_speed_kmh = math.hypot(total_vx, total_vy)
        self.x          += total_vx * self.DT_H
        self.y          += total_vy * self.DT_H
        self.elapsed_min += 1

        return ground_speed_kmh

    def run(self, log_path: str) -> None:
        """Run the simulation and write results to log_path and stdout."""
        header, units, separator = self._make_table_header()
        ground_speed_kmh = 0.0
        last_logged_min  = -1

        with open(log_path, "w", encoding="utf-8") as log:
            for line in (header, units, separator):
                log.write(line + "\n")
                print(line)

            while True:
                distance_km  = math.hypot(self.goal_x - self.x, self.goal_y - self.y)
                deviation_km = self._line_deviation_km()
                self.max_deviation_km = max(self.max_deviation_km, deviation_km)

                if self.elapsed_min != last_logged_min:
                    row = self._format_row(distance_km, deviation_km, ground_speed_kmh)
                    log.write(row + "\n")
                    if self.elapsed_min % 60 == 0 or distance_km < self.ARRIVAL_KM:
                        print(row)
                    last_logged_min = self.elapsed_min

                if distance_km < self.ARRIVAL_KM:
                    break

                ground_speed_kmh = self._step()

                if self.elapsed_min > 500_000:
                    print("WARNING: Simulation exceeded 500 000 minutes — aborting.")
                    break

            log.write(separator + "\n")
            hours, minutes = divmod(self.elapsed_min, 60)
            distance_km    = math.hypot(self.goal_x - self.x, self.goal_y - self.y)
            footer = (
                f"\nArrival time  : {self.elapsed_min} min  ({hours} h {minutes} min)\n"
                f"Final position: ({self.x/100:.5f}, {self.y/100:.5f})  [units of 100 km]\n"
                f"Distance to B : {distance_km/100:.5f} units  ({distance_km:.3f} km)"
            )
            log.write(footer + "\n")
            print(separator)
            print(footer)
