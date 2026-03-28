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

    def __init__(self, ax: float, ay: float,
                 bx: float, by: float,
                 phi0: float,
                 wind: WindData) -> None:
        self.ax, self.ay = ax, ay
        self.bx, self.by = bx, by
        self.wind = wind

        # State
        self.x, self.y = ax, ay
        self.phi = phi0
        self.v   = 0.0
        self.t   = 0

    @staticmethod
    def _angle_diff(target: float, current: float) -> float:
        """Signed shortest difference (target - current) in (-180, +180]."""
        return ((target - current + 180.0) % 360.0) - 180.0

    @staticmethod
    def _stopping_distance_km(speed_kmh: float) -> float:
        """Minimum distance needed to decelerate from speed_kmh to 0."""
        return speed_kmh * (speed_kmh + ShipSimulator.MAX_ACCEL) / (2.0 * ShipSimulator.MAX_ACCEL * 60.0)

    def _line_deviation_km(self) -> float:
        """Perpendicular distance from current position to the A-B line [km]."""
        px, py = self.x, self.y
        ax, ay, bx, by = self.ax, self.ay, self.bx, self.by
        ab = math.hypot(bx - ax, by - ay)
        if ab == 0.0:
            return math.hypot(px - ax, py - ay)
        return abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / ab

    def _make_table_header(self) -> tuple[str, str, str]:
        col = [
            ("Čas",             "[min]",    10),
            ("Pozicija X",      "[100 km]", 12),
            ("Pozicija Y",      "[100 km]", 12),
            ("Hitrost",         "[km/h]",   10),
            ("Dejanska hitrost","[km/h]",   16),
            ("Smer",            "[°]",       8),
            ("Razdalja do B",   "[100 km]", 14),
            ("Odmik od trase",  "[100 km]", 15),
        ]
        header = "  ".join(f"{name:>{w}}" for name, _, w in col)
        units  = "  ".join(f"{unit:>{w}}" for _, unit, w in col)
        sep    = "-" * len(header)
        return header, units, sep

    def _format_row(self, dist: float, dev: float, actual_speed: float) -> str:
        vals = [self.t, self.x/100, self.y/100, self.v, actual_speed,
                self.phi, dist/100, dev/100]
        fmts = [">10d", ">12.4f", ">12.4f", ">10.2f", ">16.2f",
                ">8.1f", ">14.5f", ">15.6f"]
        return "  ".join(format(val, f) for val, f in zip(vals, fmts))

    def _step(self) -> float:
        """Advance state by one minute. Returns actual ground speed [km/h]."""
        bx, by = self.bx, self.by

        # 1. Desired heading toward B
        desired_phi = math.degrees(math.atan2(by - self.y, bx - self.x))

        # 2. Turn toward desired heading (max MAX_TURN_RATE deg/min)
        turn     = max(-self.MAX_TURN_RATE,
                       min(self.MAX_TURN_RATE, self._angle_diff(desired_phi, self.phi)))
        self.phi = (self.phi + turn) % 360.0

        # 3. Wind at current time
        wx, wy = self.wind.vector_at(self.t)

        # 4. Speed control
        phi_rad  = math.radians(self.phi)
        tailwind = wx * math.cos(phi_rad) + wy * math.sin(phi_rad)
        v_ground = self.v + tailwind
        dist     = math.hypot(bx - self.x, by - self.y)
        if self._stopping_distance_km(max(0.0, v_ground)) >= dist:
            min_v    = max(0.0, -tailwind + 1.0)
            self.v   = max(min_v, self.v - self.MAX_ACCEL)
        else:
            self.v = min(self.MAX_SPEED_KMH, self.v + self.MAX_ACCEL)

        # 5. Update position
        vx_total     = self.v * math.cos(phi_rad) + wx
        vy_total     = self.v * math.sin(phi_rad) + wy
        actual_speed = math.hypot(vx_total, vy_total)
        self.x      += vx_total * self.DT_H
        self.y      += vy_total * self.DT_H
        self.t      += 1

        return actual_speed

    def run(self, log_path: str) -> None:
        """Run the simulation and write results to log_path and stdout."""
        header, units, sep = self._make_table_header()
        actual_speed = 0.0
        last_print_t = -1

        with open(log_path, "w", encoding="utf-8") as log:
            for line in (header, units, sep):
                log.write(line + "\n")
                print(line)

            while True:
                dist = math.hypot(self.bx - self.x, self.by - self.y)
                dev  = self._line_deviation_km()

                if self.t != last_print_t:
                    row = self._format_row(dist, dev, actual_speed)
                    log.write(row + "\n")
                    if self.t % 60 == 0 or dist < self.ARRIVAL_KM:
                        print(row)
                    last_print_t = self.t

                if dist < self.ARRIVAL_KM:
                    break

                actual_speed = self._step()

                if self.t > 500_000:
                    print("WARNING: Simulation exceeded 500 000 minutes — aborting.")
                    break

            log.write(sep + "\n")
            h, m  = divmod(self.t, 60)
            dist  = math.hypot(self.bx - self.x, self.by - self.y)
            footer = (
                f"\nArrival time  : {self.t} min  ({h} h {m} min)\n"
                f"Final position: ({self.x/100:.5f}, {self.y/100:.5f})  [units of 100 km]\n"
                f"Distance to B : {dist/100:.5f} units  ({dist:.3f} km)"
            )
            log.write(footer + "\n")
            print(sep)
            print(footer)
