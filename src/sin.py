import pyxel
import math as m
from src.utils import Point
import src.palette as palette

XMIN, XMAX = -45, 45
WIDTH = XMAX - XMIN
YMIN, YMAX = -30, 30
HEIGHT = YMAX - YMIN
FPS = 120

NUM_CIRCLES = 10


def pix(x: float, y: float, c: int):
    real_x = x + WIDTH / 2
    real_y = -y  # flip first, then shift!
    real_y = real_y + HEIGHT / 2

    pyxel.pset(m.floor(real_x), m.floor(real_y), c)


def line(x1, y1, x2, y2, c):
    x1 += WIDTH / 2

    y1 = -y1
    y1 += HEIGHT / 2

    x2 += WIDTH / 2

    y2 = -y2
    y2 += HEIGHT / 2

    pyxel.line(x1, y1, x2, y2, c)


class App:
    t: float = 0
    p: Point = Point(0, 0)

    def __init__(self) -> None:
        print(f"{WIDTH=}")
        print(f"{HEIGHT=}")
        pyxel.init(WIDTH + 1, HEIGHT + 1, fps=FPS)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.t += 0.02

    def draw(self):
        pyxel.cls(palette.BLUE2)
        # grid
        for i in range(XMIN, XMAX + 1, 15):
            line(i, YMIN, i, YMAX, palette.LIGHT_BLUE)

        for i in range(YMIN, YMAX + 1, 15):
            line(XMIN, i, XMAX, i, palette.LIGHT_BLUE)

        for x in range(XMIN, XMAX + 1):
            y = m.sin(x * 0.1 - self.t) * 10
            pix(x, y, palette.PURPLE)

        for x in range(XMIN, XMAX + 1):
            y = x
            pix(x, y, palette.YELLOW)
            y = x * x * 0.03
            pix(x, y, palette.ORANGE)
            y = 0
            pix(x, y, palette.TEAL)
        # line(XMIN, YMIN, XMIN, YMAX, palette.PURPLE)
        # line(XMAX, YMIN, XMAX, YMAX, palette.YELLOW)
        # line(XMIN, YMIN, XMAX, YMIN, palette.ORANGE)
        # line(XMIN, YMAX, XMAX, YMAX, palette.PINK)


App()
