import pyxel
import math as m
from src.utils import Point

WIDTH = 160
HEIGHT = 120
FPS = 15

BLUE = 1
PURPLE = 2
TEAL = 3
ORANGE = 9


def argmin(a):
    return min(range(len(a)), key=lambda x: a[x])


def argmax(a):
    return max(range(len(a)), key=lambda x: a[x])


def pix(x, y, c):
    pyxel.pset(x + WIDTH / 2, -y + HEIGHT / 2, c)


def draw_tri(tri):
    x1, y1 = tri[0]
    x2, y2 = tri[1]
    x3, y3 = tri[2]

    y_min = min(y1, y2, y3)
    y_max = max(y1, y2, y3)

    points_to_process = tri[:]

    bottom_vertex_index = argmin([y1, y2, y3])
    bot_x, bot_y = tri[bottom_vertex_index]
    del points_to_process[bottom_vertex_index]

    xs = [p[0] for p in points_to_process]
    left_vertex_index = argmin(xs)
    left_x, left_y = points_to_process[left_vertex_index]
    del points_to_process[left_vertex_index]

    right_x, right_y = points_to_process[0]

    x_min = min(x1, x2, x3)
    x_tri_max = max(x1, x2, x3)

    drawLeft = bot_x == right_x
    target_y = 0
    target_x = 0
    if drawLeft:
        target_y = left_y
        target_x = left_x
    else:
        target_y = right_y
        target_x = right_x

    # find the slope of the line starting from (bot_x,bot_y) that is not vertical
    slope = (target_y - bot_y) / (target_x - bot_x)
    line_offset = bot_y - (slope * bot_x)

    # bottom_left_vertex
    # bottome_right_vertex

    for y in range(y_min, y_max + 1):
        # max of current scanline
        if drawLeft:
            x_min = m.floor((y - line_offset) / slope)
            x_max = x_tri_max
        else:
            x_max = m.floor((y - line_offset) / slope)
            x_min = x_min

        for x in range(x_min, x_max + 1):
            pix(x, y, BLUE)

    pix(bot_x, bot_y, PURPLE)
    pix(left_x, left_y, TEAL)
    pix(right_x, right_y, ORANGE)


class App:
    t: float = 0
    p: Point = Point(0, 0)

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        ...

    def draw(self):
        pyxel.cls(13)

        test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
        for tri in test_tris:
            draw_tri(tri)

        # debug
        # pyxel.pset(x1, y1, 12)
        # pyxel.pset(x2, y2, 12)
        # pyxel.pset(x3, y3, 12)


App()
