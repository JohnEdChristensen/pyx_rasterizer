import pyxel
import math as m
from src.utils import Point

WIDTH = 160
HEIGHT = 120
FPS = 120

NUM_CIRCLES = 10


class App:
    t: float = 0
    p: Point = Point(0, 0)
    circle_cords: list[Point] = [Point(0, 0)] * NUM_CIRCLES
    circle_cords_past: list[Point] = [Point(0, 0)] * NUM_CIRCLES

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.circle_cords_past = self.circle_cords[:]
        self.t = self.t + (1 / FPS) * 2
        w = WIDTH / 4
        for i in range(NUM_CIRCLES):
            radians = i / NUM_CIRCLES * 2 * m.pi
            x = m.sin(radians + self.t) * (w * m.sin(self.t))
            y = m.cos(radians + self.t) * (w * m.cos(self.t))
            self.circle_cords[i] = Point(x, y)

    def draw(self):
        pyxel.cls(0)
        # convert to screen space
        for i, e in enumerate(self.circle_cords):
            pyxel.circ(e.x + WIDTH / 2, e.y + HEIGHT / 2, 5, (i + 1) % 16)

        for i, e in enumerate(self.circle_cords_past):
            scale = 0.25
            pyxel.circ(
                e.x * scale + WIDTH / 2, e.y * scale + HEIGHT / 2, 1, (i + 1) % 16
            )


App()
