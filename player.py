import math


class Player:
    def __init__(
        self,
        x: float,
        y: float,
        angle: float,
        speed: float,
        FOV: float = 60,
    ) -> None:
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.FOV = FOV

    @property
    def camera_plane(self) -> tuple[float, float]:
        direction_x = math.cos(self.angle)
        direction_y = math.sin(self.angle)
        plane_length = math.tan(math.radians(self.FOV) / 2.0)
        return -direction_y * plane_length, direction_x * plane_length