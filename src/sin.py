import pyxel
import math as m
from src.utils import Point

WIDTH = 90
HEIGHT = 60
FPS = 120

NUM_CIRCLES = 10


def pix(x: float, y: float, c: int):
    pyxel.pset(x + WIDTH / 2, y + HEIGHT / 2, c)


class App:
    t: float = 0
    p: Point = Point(0, 0)

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        pyxel.run(self.update, self.draw)

    def update(self):
        ...

    def draw(self):
        pyxel.cls(0)
        for x in range(-WIDTH // 2, WIDTH // 2):
            y = m.sin(x * 0.1) * 10
            pix(x, y, 1)


App()
