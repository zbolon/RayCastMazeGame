class Player:

    def __init__(self, x, y, angle, speed, FOV=60):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.FOV = FOV