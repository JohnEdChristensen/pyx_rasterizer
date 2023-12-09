import dataclasses
import math as m
import random
from enum import Enum
from typing import TypeVar, Any
import time

import pyxel

T = TypeVar("T")

WIDTH = 160
HEIGHT = 120
FPS = 15

BLUE = 1
PURPLE = 2
TEAL = 3
ORANGE = 9


@dataclasses.dataclass
class Buffer:
    contents: list[Any]
    width: int
    height: int

    def __init__(self, width: int, height: int, initial_value: Any):
        self.width = width
        self.height = height
        self.contents = [initial_value] * (width * height)

    def get_index(self, x: int, y: int):
        if x >= self.width or x < 0:
            raise Exception(f"x is out of range: {x=},{y=}")

        if y >= self.height or y < 0:
            raise Exception(f"y is out of range: {x=},{y=}")

        return y * self.width + x

    def set(self, x: int, y: int, value: Any):
        index = self.get_index(x, y)
        self.contents[index] = value

    def get(self, x: int, y: int) -> Any:
        index = self.get_index(x, y)
        return self.contents[index]

    def set_cartesian(self, cartX: int, cartY: int, value: Any):
        # may not work well, different behaviour coule happen with even/odd width/height
        x = cartX + self.width // 2
        y = (-1 * cartY) + self.height // 2
        self.set(x, y, value)

    def get_cartesian(self, cartX: int, cartY: int) -> Any:
        # may not work well, different behaviour coule happen with even/odd width/height
        x = cartX + self.width // 2
        y = (-1 * cartY) + self.height // 2
        # print(f"get_cartesian {cartX=}, {cartY=}, {x=},{y=}, {self.width=}")
        return self.get(x, y)

    # should we find min/max and only draw those pixels
    def draw(self):
        if isinstance(self.contents[0], int):
            for x in range(self.width):
                for y in range(self.height):
                    pyxel.pset(x, y, self.get(x, y))

        if isinstance(self.contents[0], float):
            for x in range(self.width):
                for y in range(self.height):
                    z = self.get(x, y)
                    if z == float("inf"):
                        color = 0
                    else:
                        color = int((z * 15) // 100)
                    pyxel.pset(x, y, color)


pixel_buffer = None
z_buffer = None


def pix(x: int, y: int, c: int):
    # print(f"{x=}\t {y=}\t {c=}")
    pixel_buffer.set_cartesian(x, y, c)


@dataclasses.dataclass
class Point:
    x: float
    y: float
    z: float

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def __sub__(self, other):
        deltaX = self.x - other.x
        deltaY = self.y - other.y
        deltaZ = self.z - other.z
        return Point(deltaX, deltaY, deltaZ)

    def length(self):
        return m.sqrt(self.x**2 + self.y**2 + self.z**2)


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


class TriType(Enum):
    UP = 0
    DOWN = 1
    STANDARD = 2
    HORIZONTAL_LINE = 3
    VERTICAL_LINE = 4


def tris_from_verts(vertices, faces) -> list[list[tuple[float, float, float]]]:
    tris = []
    for face in faces:
        tris.append([vertices[face[0]], vertices[face[1]], vertices[face[2]]])
    return tris


def characterize_tri(tri: list[tuple[float, float, float]]) -> TriType:
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])
    # you can chain things 0.o
    if p1.x == p2.x == p3.x:
        raise Exception("All 3 x values are equal. I can't draw that!")
    if p1.y == p2.y == p3.y:
        raise Exception("All 3 y values are equal. I can't draw that!")

    if p1.y == p2.y:
        pOffLine = p3
        line_y_location = p1.y
    elif p1.y == p3.y:
        pOffLine = p2
        line_y_location = p1.y
    elif p2.y == p3.y:
        pOffLine = p1
        line_y_location = p2.y
    else:
        return TriType.STANDARD

    if pOffLine.y > line_y_location:
        return TriType.UP
    else:
        return TriType.DOWN


def z_estimate(p1: Point, p2: Point, p3: Point, pUnkown: Point) -> float:
    deltaP1 = p1 - pUnkown
    distanceP1 = deltaP1.length()

    deltaP2 = p2 - pUnkown
    distanceP2 = deltaP2.length()

    deltaP3 = p3 - pUnkown
    distanceP3 = deltaP3.length()

    closestPointIndex = argmin([distanceP1, distanceP2, distanceP3])
    closestPoint = [p1, p2, p3][closestPointIndex]

    return closestPoint.z


def draw_tri(tri: list[tuple[float, float, float]], color: int):
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])

    y_min = min(p1.y, p2.y, p3.y)
    y_max = max(p1.y, p2.y, p3.y)

    points_to_process = tri[:]
    tri_type = characterize_tri(tri)

    if tri_type == TriType.DOWN:
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
    elif tri_type == TriType.STANDARD:
        points_sorted_vertically = sorted([p1, p2, p3], key=lambda p: p.y)
        pBottom = points_sorted_vertically[0]
        pMiddle = points_sorted_vertically[1]
        pTop = points_sorted_vertically[2]

        opposite_line = Line(pBottom, pTop)
        pNew = Point(
            opposite_line.x(pMiddle.y), pMiddle.y, pMiddle.z
        )  # TODO should this have a real z value?
        topTri = [pMiddle.as_tuple(), pNew.as_tuple(), pTop.as_tuple()]
        botTri = [pMiddle.as_tuple(), pNew.as_tuple(), pBottom.as_tuple()]
        draw_tri(topTri, color)
        draw_tri(botTri, color)
        return

    else:
        raise Exception("I don't know how to draw anything else")

    for y in range(m.floor(y_min), m.floor(y_max) + 1):
        # max of current scanline
        # z = triangle_lerp()
        # print(tri)
        # print(line_l)
        # print(line_r)
        x_min = line_l.x(y)
        x_max = line_r.x(y)

        for x in range(m.floor(x_min), m.floor(x_max) + 1):
            z = z_estimate(p1, p2, p3, Point(x, y, 0))
            if z <= z_buffer.get_cartesian(x, y):
                # print(f"{z=},{z_buffer[y][x]=}")
                pix(x, y, color)
                z_buffer.set_cartesian(x, y, z)
    print(set(z_buffer.contents))

    # pix(bottom.x, bottom.y, PURPLE)
    # if tri_type == TriType.UP:
    #     pix(top.x, top.y, PURPLE)
    # elif tri_type == TriType.DOWN:
    #     pix(bottom.x, bottom.y, PURPLE)
    # pix(left.x, left.y, TEAL)
    # pix(right.x, right.y, ORANGE)


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


def create_standard_tris(num_tris: int) -> list[list[tuple[int, int]]]:
    test_tris = []
    for _ in range(num_tris):
        x1 = random.randint(-WIDTH // 2, WIDTH // 2)
        x2 = random.randint(-WIDTH // 2, WIDTH // 2)
        x3 = random.randint(-WIDTH // 2, WIDTH // 2)

        y1 = random.randint(-HEIGHT // 2, HEIGHT // 2)
        y2 = random.randint(-HEIGHT // 2, HEIGHT // 2)
        y3 = random.randint(-HEIGHT // 2, HEIGHT // 2)

        tri = [(x1, y1), (x2, y2), (x3, y3)]
        random.shuffle(tri)

        test_tris.append(tri)
    return test_tris


# z pos
# back 100
# middle 60
# front 20
cube_verts = [
    (40, 30, 60),
    (0, -40, 20),
    (-40, -20, 60),
    (0, 0, 100),
    (40, -20, 60),
    (0, 10, 20),
    (-40, 30, 60),
    (0, 50, 100),
]


cube_faces = [
    [1, 4, 3],
    [1, 2, 3],  # bottom
    [5, 0, 4],
    [5, 1, 4],  # front right
    [5, 6, 2],
    [5, 1, 2],  # front left
    [2, 6, 7],
    [2, 3, 7],  # back left
    [3, 7, 0],
    [3, 4, 0],  # back right
    [5, 6, 7],
    [5, 0, 7],  # top
]
cube_colors = [
    pyxel.COLOR_PINK,
    pyxel.COLOR_PINK,
    pyxel.COLOR_LIGHT_BLUE,
    pyxel.COLOR_LIGHT_BLUE,
    pyxel.COLOR_LIME,
    pyxel.COLOR_LIME,
    pyxel.COLOR_YELLOW,
    pyxel.COLOR_YELLOW,
    pyxel.COLOR_PURPLE,
    pyxel.COLOR_PURPLE,
    pyxel.COLOR_GRAY,
    pyxel.COLOR_GRAY,
]

old_cube_tris = [
    [(0, 0), (0, -40), (40, -20)],
    [(0, 0), (0, -40), (-40, -20)],  # bottom
    [(0, 10), (40, 30), (40, -20)],
    [(0, 10), (0, -40), (40, -20)],  # front right
    [(0, 10), (-40, 30), (-40, -20)],
    [(0, 10), (0, -40), (-40, -20)],  # front left
    [(0, 0), (40, -20), (40, 30)],
    [(0, 0), (0, 50), (40, 30)],  # back right
    [(0, 0), (-40, -20), (-40, 30)],
    [(0, 0), (0, 50), (-40, 30)],  # back left
    [(0, 50), (0, 10), (40, 30)],
    [(0, 10), (0, 10), (-40, 30)],  # bottom
]

cube_tris = tris_from_verts(cube_verts, cube_faces)


class App:
    t: float = 0
    p: Point = Point(0, 0, 0)
    # test_tris = create_down_tris(30)
    # test_tris = [[(-25,-25),(50,50),(5,60)]]
    # test_tris = create_standard_tris(30)
    test_tris = cube_tris
    ran: bool = False
    show_z_buffer: bool = False

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        # pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_R):
            self.ran = False
        if pyxel.btnp(pyxel.KEY_Z):
            self.show_z_buffer = not self.show_z_buffer
            self.ran = False
        if pyxel.btnp(pyxel.KEY_S):
            pyxel.quit()

    def draw(self):
        global pixel_buffer, z_buffer
        if self.ran is False:
            # self.test_tris = create_down_tris(30)
            # self.ran = True
            pyxel.cls(0)

            pixel_buffer = Buffer(WIDTH, HEIGHT, 0)
            z_buffer = Buffer(WIDTH, HEIGHT, float("inf"))

            anim_count = pyxel.frame_count // 10 % len(cube_tris) + 1

            partialTris = cube_tris[0:anim_count]
            # test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
            for i, tri in enumerate(partialTris):
                draw_tri(tri, cube_colors[i])

            # draw what is currently in the buffer to the screen
            pixel_buffer.draw()
            if self.show_z_buffer:
                print(set(z_buffer.contents))
                z_buffer.draw()

            if anim_count == len(cube_tris):
                pyxel.text(0, 0, "Done drawing, press r to redraw", pyxel.COLOR_WHITE)
                self.ran = True

        # debug
        # pyxel.pset(x1, y1, 12)
        # pyxel.pset(x2, y2, 12)
        # pyxel.pset(x3, y3, 12)


App()
