
import math
from dataclasses import dataclass

from fdf.model import Map, Point


@dataclass(frozen=True)
class ScreenPoint:
    x: float
    y: float


@dataclass(frozen=True)
class Camera:
    scale: float
    offset_x: float
    offset_y: float

    def project(self, point: Point) -> ScreenPoint:
        iso_angle = math.radians(30)

        projected_x = (
            point.x - point.y
        ) * math.cos(iso_angle)

        projected_y = (
            (point.x + point.y) * math.sin(iso_angle)
            - point.z
        )

        return ScreenPoint(
            x=projected_x * self.scale + self.offset_x,
            y=projected_y * self.scale + self.offset_y,
        )

    @classmethod
    def fit(
        cls,
        height_map: Map,
        width: int,
        height: int,
    ) -> "Camera":
        points = list(height_map)

        raw_camera = cls(
            scale=1.0,
            offset_x=0.0,
            offset_y=0.0,
        )

        projected = [
            raw_camera.project(point)
            for point in points
        ]

        min_x = min(point.x for point in projected)
        max_x = max(point.x for point in projected)
        min_y = min(point.y for point in projected)
        max_y = max(point.y for point in projected)

        map_width = max(max_x - min_x, 1.0)
        map_height = max(max_y - min_y, 1.0)

        scale = min(
            width / map_width,
            height / map_height,
        ) * 0.9

        offset_x = (
            width / 2
            - (min_x + max_x) * scale / 2
        )
        offset_y = (
            height / 2
            - (min_y + max_y) * scale / 2
        )

        return cls(
            scale=scale,
            offset_x=offset_x,
            offset_y=offset_y,
        )
