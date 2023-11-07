import pyxel
import math as m
from src.utils import Point

WIDTH = 160
HEIGHT = 120
FPS = 15


def draw_tri(tri):
    x1, y1 = tri[0]
    x2, y2 = tri[1]
    x3, y3 = tri[2]

    y_min = min(y1, y2, y3)
    y_max = max(y1, y2, y3)

    # top_vertex =
    # bottom_left_vertex
    # bottome_right_vertex

    for y in range(y_min, y_max + 1):
        x_min = min(x1, x2, x3)
        x_line_max = max(x1, x2, x3)
        slope = (y_max - y_min) / (x_line_max - x_min)
        line_offset = y_min - (slope * x_min)
        x_max = m.floor((y - line_offset) / slope)
        for x in range(x_min, x_max + 1):
            pyxel.pset(x, y, 1)


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

        test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
        for tri in test_tris:
            draw_tri(tri)

        # debug
        # pyxel.pset(x1, y1, 12)
        # pyxel.pset(x2, y2, 12)
        # pyxel.pset(x3, y3, 12)


App()
