import pyxel
import math as m
import random
import dataclasses
from enum import Enum

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


@dataclasses.dataclass
class Line:
    p1: Point
    p2: Point

    def x(self, y: float) -> float:
        p1 = self.p1
        p2 = self.p2
        if p1.x == p2.x:
            return p1.x

        slope = (p1.y - p2.y) / (p1.x - p2.x)
        b = p2.y - (slope * p2.x)
        return (y - b) / slope


def argmin(a):
    return min(range(len(a)), key=lambda x: a[x])


def argmax(a):
    return max(range(len(a)), key=lambda x: a[x])


def pix(x: float, y: float, c: int):
    real_x = x + WIDTH / 2  # shift
    real_y = -y  # flip
    real_y = real_y + HEIGHT / 2  # shift

    pyxel.pset(real_x, real_y, c)

class TriType(Enum):
    UP = 0
    DOWN =  1
    STANDARD =  2
    HORIZONTAL_LINE = 3
    VERTICAL_LINE = 4


def characterize_tri(tri: list[tuple[float,float]])-> TriType:
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])
    # you can chain things 0.o
    if p1.x == p2.x == p3.x:
        raise Exception("All 3 x values are equal. I can't draw that!")
    if p1.y == p2.y == p3.y:
        raise Exception("All 3 y values are equal. I can't draw that!")

     
    if p1.y==p2.y :
        pOffLine = p3
        line_y_location = p1.y
    elif p1.y==p3.y :
        pOffLine = p2
        line_y_location = p1.y
    elif p2.y==p3.y :
        pOffLine=p1
        line_y_location = p2.y
    else:
        return TriType.STANDARD

    if pOffLine.y > line_y_location:
        return TriType.UP 
    else:
        return TriType.DOWN 



def draw_tri(tri: list[tuple[float, float]]):
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])


    y_min = min(p1.y, p2.y, p3.y)
    y_max = max(p1.y, p2.y, p3.y)

    points_to_process = tri[:]
    tri_type = characterize_tri(tri)
    if tri_type== TriType.DOWN:
        bottom_vertex_index = argmin([p1.y, p2.y, p3.y])
        bottom = Point(*tri[bottom_vertex_index])
        del points_to_process[bottom_vertex_index]

        xs = [p[0] for p in points_to_process]
        left_vertex_index = argmin(xs)
        left = Point(*points_to_process[left_vertex_index])
        del points_to_process[left_vertex_index]

        right = Point(*points_to_process[0])

        # Find line on the left side
        line_l = Line(left, bottom)
        # Find line on the right side
        line_r = Line(bottom, right)
    elif tri_type == TriType.UP:
        top_vertex_index = argmax([p1.y, p2.y, p3.y])
        top = Point(*tri[top_vertex_index])
        del points_to_process[top_vertex_index]

        xs = [p[0] for p in points_to_process]
        left_vertex_index = argmin(xs)
        left = Point(*points_to_process[left_vertex_index])
        del points_to_process[left_vertex_index]

        right = Point(*points_to_process[0])

        # Find line on the left side
        line_l = Line(left, top)
        # Find line on the right side
        line_r = Line(top, right)
    else:
        raise Exception("I can't draw that non up-down tris!!")


    color = random.randint(0, 15)
    for y in range(m.floor(y_min), m.floor(y_max) + 1):
        # max of current scanline
        print(tri)
        print(line_l)
        print(line_r)
        x_min = line_l.x(y)
        x_max = line_r.x(y)

        for x in range(m.floor(x_min), m.floor(x_max) + 1):
            pix(x, y, color)

    #pix(bottom.x, bottom.y, PURPLE)
    if tri_type == TriType.UP:
        pix(top.x, top.y, PURPLE)
    elif tri_type == TriType.DOWN:
        pix(bottom.x, bottom.y, PURPLE)
    pix(left.x, left.y, TEAL)
    pix(right.x, right.y, ORANGE)


def create_down_square_tris(num_tris: int) -> list[list[tuple[int, int]]]:
    test_tris = []
    for _ in range(num_tris):
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


def create_down_tris(num_tris: int) -> list[list[tuple[int, int]]]:
    test_tris = []
    for _ in range(num_tris):
        rand_x1 = random.randint(-WIDTH // 2, WIDTH // 2)
        rand_x2 = random.randint(-WIDTH // 2, WIDTH // 2)
        rand_x3 = random.randint(-WIDTH // 2, WIDTH // 2)
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
        x3 = rand_x3
        y3 = ymin

        tri = [(x1, y1), (x2, y2), (x3, y3)]
        random.shuffle(tri)

        test_tris.append(tri)
    return test_tris

def create_up_tris(num_tris: int) -> list[list[tuple[int, int]]]:
    test_tris = []
    for _ in range(num_tris):
        rand_x1 = random.randint(-WIDTH // 2, WIDTH // 2)
        rand_x2 = random.randint(-WIDTH // 2, WIDTH // 2)
        rand_x3 = random.randint(-WIDTH // 2, WIDTH // 2)
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
        y1 = ymin
        x2 = xmax
        y2 = ymin
        x3 = rand_x3
        y3 = ymax

        tri = [(x1, y1), (x2, y2), (x3, y3)]
        random.shuffle(tri)

        test_tris.append(tri)
    return test_tris


class App:
    t: float = 0
    p: Point = Point(0, 0)
    test_tris = create_down_tris(30)
    ran: bool = False

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        #pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_R):
            self.ran = False

    def draw(self):
        if self.ran is False:
            self.test_tris = create_up_tris(30)
            self.ran = True
            pyxel.cls(13)


            # test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
            for tri in self.test_tris:
                draw_tri(tri)

        # debug
        # pyxel.pset(x1, y1, 12)
        # pyxel.pset(x2, y2, 12)
        # pyxel.pset(x3, y3, 12)


App()
