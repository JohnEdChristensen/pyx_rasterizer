import pyxel
import math as m
import random
import dataclasses

WIDTH = 160
HEIGHT = 120
FPS = 15

BLUE = 1
PURPLE = 2
TEAL = 3
ORANGE = 9


@dataclasses.dataclass
class Point:
    x: float
    y: float


def argmin(a):
    return min(range(len(a)), key=lambda x: a[x])


def argmax(a):
    return max(range(len(a)), key=lambda x: a[x])


def pix(x, y, c):
    pyxel.pset(x + WIDTH / 2, -y + HEIGHT / 2, c)


def draw_tri(tri):
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])

    # you can chain things 0.o
    if p1.x == p2.x == p3.x:
        raise Exception("All 3 x values are equal. I can't draw that!")
    if p1.y == p2.y == p3.y:
        raise Exception("All 3 y values are equal. I can't draw that!")

    y_min = min(p1.y, p2.y, p3.y)
    y_max = max(p1.y, p2.y, p3.y)

    points_to_process = tri[:]

    bottom_vertex_index = argmin([p1.y, p2.y, p3.y])
    bot_x, bot_y = tri[bottom_vertex_index]
    del points_to_process[bottom_vertex_index]

    xs = [p[0] for p in points_to_process]
    left_vertex_index = argmin(xs)
    left_x, left_y = points_to_process[left_vertex_index]
    del points_to_process[left_vertex_index]

    right_x, right_y = points_to_process[0]

    x_min = min(p1.x, p2.x, p3.x)
    x_tri_max = max(p1.x, p2.x, p3.x)

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


def create_test_tris(num_tris: int) -> list[tuple[int, int]]:
    test_tris = []
    for i in range(num_tris):
        rand_x1 = random.randint(-WIDTH // 2, WIDTH // 2)
        rand_x2 = random.randint(-WIDTH // 2, WIDTH // 2)
        xmin = min(rand_x1, rand_x2)
        xmax = max(rand_x1, rand_x2)
        if xmin == xmax:
            xmax += 1

        rand_y1 = random.randint(-HEIGHT // 2, HEIGHT // 2)
        rand_y2 = random.randint(-HEIGHT // 2, HEIGHT // 2)
        ymin = min(rand_y1, rand_y2)
        ymax = max(rand_y1, rand_y2)
        if ymin == ymax:
            ymax += 1

        x1 = xmin
        y1 = ymax
        x2 = xmax
        y2 = ymax
        x3 = random.choice([xmax, xmin])
        y3 = ymin

        tri = [(x1, y1), (x2, y2), (x3, y3)]
        random.shuffle(tri)

        test_tris.append(tri)
    return test_tris


class App:
    t: float = 0
    p: Point = Point(0, 0)
    test_tris = create_test_tris(3)

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        ...

    def draw(self):
        pyxel.cls(13)

        # test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
        for tri in self.test_tris:
            draw_tri(tri)

        # debug
        # pyxel.pset(x1, y1, 12)
        # pyxel.pset(x2, y2, 12)
        # pyxel.pset(x3, y3, 12)


App()
