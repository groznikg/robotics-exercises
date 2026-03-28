"""Wind data parser and vector provider."""

import math


class WindData:
    """Parses and serves wind vectors from a wind data file."""

    def __init__(self, path: str) -> None:
        """
        Read wind file. Expected format (whitespace-separated):
            N   speed[km/h]   direction[deg]
            1   10            90
            ...
        Header lines (non-numeric first token) and blank lines are skipped.
        """
        self._winds: list[tuple[float, float]] = []
        with open(path, encoding="utf-8") as file:
            for line in file:
                tokens = line.split()
                if len(tokens) < 3:
                    continue
                try:
                    float(tokens[0])
                    speed_kmh   = float(tokens[1])
                    direction_deg = float(tokens[2])
                    self._winds.append((speed_kmh, direction_deg))
                except ValueError:
                    continue
        if not self._winds:
            raise ValueError(f"No valid wind data found in '{path}'.")

    def __len__(self) -> int:
        return len(self._winds)

    def vector_at(self, t_min: int) -> tuple[float, float]:
        """Return wind velocity (vx, vy) km/h at simulation time t_min [minutes]."""
        speed_kmh, direction_deg = self._winds[(t_min // 60) % len(self._winds)]
        direction_rad = math.radians(direction_deg)
        return speed_kmh * math.cos(direction_rad), speed_kmh * math.sin(direction_rad)
