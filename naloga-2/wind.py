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
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                parts = raw.split()
                if len(parts) < 3:
                    continue
                try:
                    float(parts[0])
                    self._winds.append((float(parts[1]), float(parts[2])))
                except ValueError:
                    continue
        if not self._winds:
            raise ValueError(f"No valid wind data found in '{path}'.")

    def __len__(self) -> int:
        return len(self._winds)

    def vector_at(self, t_min: int) -> tuple[float, float]:
        """Return wind velocity (vx, vy) km/h at simulation time t_min [minutes]."""
        speed, deg = self._winds[(t_min // 60) % len(self._winds)]
        rad = math.radians(deg)
        return speed * math.cos(rad), speed * math.sin(rad)
