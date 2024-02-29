import dataclasses
import math as m
import random
from enum import Enum
from typing import TypeVar, Any, Iterable, Annotated, Literal
import itertools
import traceback
import copy
import numpy as np
import numpy.typing as npt

import src.obj_parser as obj # pyright: ignore
import src.gif_exporter as gif_exporter

import pyxel


T = TypeVar("T")

DType = TypeVar("DType", bound=np.generic)
Mat4 = Annotated[npt.NDArray[DType], Literal[4, 4]]
Vec3 = Annotated[npt.NDArray[DType], Literal[3]]
Vec4 = Annotated[npt.NDArray[DType], Literal[4]]


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
            print(f"x is out of range: {x=},{y=}")
            raise Exception(f"x is out of range: {x=},{y=}")

        if y >= self.height or y < 0:
            print(f"x is out of range: {x=},{y=}")
            raise Exception(f"y is out of range: {x=},{y=}")

        return y * self.width + x

    def set(self, x: int, y: int, value: Any):
        try:
            index = self.get_index(x, y)
            self.contents[index] = value
        except:
            print(f"tried to set x or y out of range: {x=},{y=}")

    def get(self, x: int, y: int) -> Any:
        try:
            index = self.get_index(x, y)
        except ():
            print(f"tried to get x or y out of range: {x=},{y=}")
            traceback.print_exc()
            return 0
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
                        color = z_pallette[int((z/6 % len(z_pallette) ))]
                    pyxel.pset(x, y, color)
z_pallette = [8,9,10,11,12,5,1,2]

@dataclasses.dataclass
class Point:
    x: float
    y: float
    z: float

    def __repr__(self):
        return f" x  = {self.x:10.2f} y = {self.y:10.2f} z = {self.z:10.2f}"

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


def tris_from_verts(
    vertices: list[Vec4], faces: list[list[int]]
) -> list[list[tuple[float, float, float]]]:
    tris = []
    for face in faces:
        tris.append(
            [
                vertices[face[0]][:3],
                vertices[face[1]][:3],
                vertices[face[2]][:3],
            ]
        )
    return tris


def mat_times_vec(
    mat: list[list[float]], vec: tuple[float, float, float, float]
) -> list[float]:
    xp = dot(vec, mat[0])
    yp = dot(vec, mat[1])
    zp = dot(vec, mat[2])
    wp = dot(vec, mat[3])
    return [xp, yp, zp, wp]


def transform_verts(verts: list[Vec4], transform: Mat4):
    new_verts = [v.copy() for v in verts]
    for i, v in enumerate(verts):
        new_verts[i] = transform @ v
    return new_verts


def tranpose(mat: list[list[float]]) -> list[list[float]]:
    # does not work :(
    return [[mat[j][i] for i, j in itertools.product(range(4), repeat=2)]]


def dot(v1: Iterable[float], v2: Iterable[float]) -> float:
    elementwise = [a * b for a, b in zip(v1, v2)]
    return sum(elementwise)


def create_test_mat(size: int):
    mat = [list((i, i + size)) for i in range(0, size**2, size)]
    return [float(mat[i][j]) for i, j in itertools.product(range(4), repeat=2)]


def characterize_tri(tri: list[tuple[float, float, float]]) -> TriType:
    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])
    # you can chain things 0.o
    if p1.x == p2.x == p3.x:
        print("All 3 x values are equal. I can't draw that!")
        raise Exception("All 3 x values are equal. I can't draw that!")
    if p1.y == p2.y == p3.y:
        print("All 3 y values are equal. I can't draw that!")
        print(f"{p1=}\n{p2=}\n{p3=}")
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


def z_vornoi_estimate(
    p1: Point, p2: Point, p3: Point, pUnkown: Point
) -> float:
    deltaP1 = p1 - pUnkown
    distanceP1 = deltaP1.length()

    deltaP2 = p2 - pUnkown
    distanceP2 = deltaP2.length()

    deltaP3 = p3 - pUnkown
    distanceP3 = deltaP3.length()

    closestPointIndex = argmin([distanceP1, distanceP2, distanceP3])
    closestPoint = [p1, p2, p3][closestPointIndex]
    return closestPoint.z


def z_estimate(p1: Point, p2: Point, p3: Point, pUnkown: Point) -> float:
    w1 = (
        (p2.y - p3.y) * (pUnkown.x - p3.x) + (p3.x - p2.x) * (pUnkown.y - p3.y)
    ) / ((p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y))

    w2 = (
        (p3.y - p1.y) * (pUnkown.x - p3.x) + (p1.x - p3.x) * (pUnkown.y - p3.y)
    ) / ((p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y))

    w3 = 1 - w1 - w2

    z_weighted_average = p1.z * w1 + p2.z * w2 + p3.z * w3
    # print(f"{w1=} {w2=} {w3=}")
    # print(f"{z_weighted_average=}")
    return z_weighted_average


def draw_tri(tri: list[tuple[float, float, float]], color: int):
    
    #trying to sort for debugging z value dependence on order
    tri = sorted(tri, key=lambda p: p[1])
    points_to_process = tri[:]

    p1 = Point(*tri[0])
    p2 = Point(*tri[1])
    p3 = Point(*tri[2])

    y_min = min(p1.y, p2.y, p3.y)
    y_max = max(p1.y, p2.y, p3.y)

    try:
        tri_type = characterize_tri(tri)
    except:
        print("couldn't characterize triangle to a drawable type")
        print("unidentifiable triangle:")
        print(p1, p2, p3, sep="\n")
        return

    # print(f"{tri_type=}")
    # print(p1,p2,p3,sep="\n")

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
            opposite_line.x(pMiddle.y), pMiddle.y, ((pTop.z +pMiddle.z + pBottom.z)/3)
        )  # TODO use a weighted average (by distance), this will proabably break in some cases
        topTri = [pMiddle.as_tuple(), pNew.as_tuple(), pTop.as_tuple()]
        botTri = [pMiddle.as_tuple(), pNew.as_tuple(), pBottom.as_tuple()]

        draw_tri(topTri, color)
        draw_tri(botTri, color)
        return

    else:
        raise Exception("I don't know how to draw anything else")

    for y in range(m.ceil(y_min), m.floor(y_max) + 1):
        x_min = line_l.x(y)
        x_max = line_r.x(y)

        for x in range(m.ceil(x_min), m.floor(x_max) + 1):
            z = z_estimate(p1, p2, p3, Point(x, y, 0.0))
            if z <= z_buffer.get_cartesian(x, y):
                pixel_buffer.set_cartesian(x, y, color)
                z_buffer.set_cartesian(x, y, z)


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
niave_cube_verts: list[Vec4] = [
    np.array((*vec, 1.0), dtype=float)
    for vec in [
        (40, 30, 60),
        (0, -40, 20),
        (-40, -20, 60),
        (0, 0, 100),
        (40, -20, 60),
        (0, 10, 20),
        (-40, 30, 60),
        (0, 50, 100),
    ]
]

niave_cube_faces = [
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

cube_verts: list[Vec4] = [
    np.array((*vec, 1.0), dtype=float)
    for vec in [
        (0, 0, 0),
        (0, 0, 1),
        (0, 1, 0),
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 1, 1),
    ]
]


cube_faces = [
    [0, 1, 2],  # x 0 face
    [1, 2, 3],
    [4, 5, 6],  # x 1 face
    [5, 6, 7],
    [0, 1, 4],  # y 0 face
    [1, 4, 5],
    [2, 3, 6],  # y 1 face
    [3, 6, 7],
    [0, 2, 4],  # z 0 face
    [2, 4, 6],
    [1, 3, 5],  # z 1 face
    [3, 5, 7],
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

test_colors = [
    pyxel.COLOR_PINK,
    pyxel.COLOR_PURPLE,
]

test_faces = [
    [0,1,2],
    [0,2,4],
]

# old_cube_tris = [
#     [(0, 0), (0, -40), (40, -20)],
#     [(0, 0), (0, -40), (-40, -20)],  # bottom
#     [(0, 10), (40, 30), (40, -20)],
#     [(0, 10), (0, -40), (40, -20)],  # front right
#     [(0, 10), (-40, 30), (-40, -20)],
#     [(0, 10), (0, -40), (-40, -20)],  # front left
#     [(0, 0), (40, -20), (40, 30)],
#     [(0, 0), (0, 50), (40, 30)],  # back right
#     [(0, 0), (-40, -20), (-40, 30)],
#     [(0, 0), (0, 50), (-40, 30)],  # back left
#     [(0, 50), (0, 10), (40, 30)],
#     [(0, 10), (0, 10), (-40, 30)],  # bottom
# ]

# test_tris = [[(11, 11), (1, 11), (1, 1)], [(20, 60), (0, 60), (20, 20)]]
# test_tris = create_down_tris(30)
# test_tris = [[(-25,-25),(50,50),(5,60)]]
# test_tris = create_standard_tris(30)



def createRotationX(angle):
    return np.array(
        [
            [m.cos(angle), m.sin(angle), 0.0,0.0],
            [-m.sin(angle), m.cos(angle), 0.0,0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

def createRotationZ(angle):
    return np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, m.cos(angle), m.sin(angle), 0.0],
            [0.0, -m.sin(angle), m.cos(angle), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def createRotationY(angle):
    return np.array(
        [
            [m.cos(angle), 0.0, m.sin(angle), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-m.sin(angle), 0.0, m.cos(angle), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def createTranslation(x, y, z):
    return np.array(
        [
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def createScale(xf, yf, zf):
    return np.array(
        [
            [xf, 0.0, 0.0, 0.0],
            [0.0, yf, 0.0, 0.0],
            [0.0, 0.0, zf, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

identity = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
rot90z = np.array(
    [
        [0.0, 1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)

rot90x = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)

colors_rgb = [
(22, 23, 26)
,(127, 6, 34)
,(214, 36, 17)
,(255, 132, 38)
,(255, 209, 0)
,(250, 253, 255)
,(255, 128, 164)
,(255, 38, 116)
,(148, 33, 106)
,(67, 0, 103)
,(35, 73, 117)
,(104, 174, 212)
,(191, 255, 60)
,(16, 210, 117)
,(0, 120, 153)
,(0, 40, 89)
]
transform = rot90x

obj_tris,obj_faces = obj.load("./assets/porygon/model.obj")
print(obj_tris,obj_faces)
class App:
    t: float = 0
    p: Point = Point(0, 0, 0)
    ran: bool = False
    show_z_buffer: bool = False
    animate_construction: bool = False
    src_verts: list[Vec4] = obj_tris
    #render_verts: list[Vec4] = copy.deepcopy(src_verts) # TODO do we need th raw vertices?
    faces: list[list[int]] = obj_faces
    transformed_verts: list[Vec4] = []
    render_tris = []
    frame_count: int = 0
    step_through_mode: bool = False
    mouse_z = 0



    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)

        self.render_tris = tris_from_verts(self.src_verts, self.faces)
        #self.render_tris = tris_from_verts(cube_verts, test_faces)
        #pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_R):
            self.ran = False
        if pyxel.btnp(pyxel.KEY_D):
            self.animate_construction = not self.animate_construction
        if pyxel.btnp(pyxel.KEY_Z):
            self.show_z_buffer = not self.show_z_buffer
            self.ran = False
        if pyxel.btnp(pyxel.KEY_S):
            self.step_through_mode = not self.step_through_mode
            self.ran=False
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.ran = False
            self.frame_count += 1
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.frame_count -= 1
            self.ran = False
        if pyxel.btnp(pyxel.KEY_P):
            try:
                gif_exporter.export_image("pyx_raster.gif",pixel_buffer.contents,WIDTH,HEIGHT,colors_rgb )

                # data = ([1] * 5 + [4] * 5) * 3
                # data += ([1] * 3 + [0] * 4 + [4] * 3) * 2
                # data += ([2] * 3 + [0] * 4 + [3] * 3) * 2
                # data += ([2] * 5 + [3] * 5) * 3
                #
                # white = (255, 255, 255)
                # red = (255, 0, 0)
                # blue = (0, 0, 255)
                # green = (0, 255, 0)
                # yellow = (255, 255,0 )
                # black = (0, 0, 0)
                # colors = [white,red,blue,green,yellow]
                #
                # gif_exporter.export_image("by_hand.gif", data,20,5,colors)
            except Exception as e:
                print(e)
                raise e
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = pyxel.mouse_x
            y = pyxel.mouse_y + 200
            if x >= WIDTH or x < 0:
                print(f"x is out of range: {x=},{y=}")
            else:
                if y >= HEIGHT or y < 0:
                    print(f"x is out of range: {x=},{y=}")
                else:
                    z_buff = z_buffer.get(x,y)
                    print(f"{z_buff}=")



        self.mouse_z += pyxel.mouse_wheel
        #print(pyxel.mouse_wheel)
        #print(self.mouse_z)


        self.render_tris = self.model_rotate(self.src_verts,self.faces)
        #self.render_tris = self.cube_update(self.src_verts,self.faces)
        #self.render_tris = self.test_update(self.cube_verts,test_faces)

    def draw(self):
        global pixel_buffer, z_buffer
        if self.ran is False:
            if self.step_through_mode:
                self.ran = True
            else:
                self.frame_count += 1
            pyxel.cls(0)

            pixel_buffer = Buffer(WIDTH, HEIGHT, 0)
            z_buffer = Buffer(WIDTH, HEIGHT, float("inf"))

            anim_count = self.frame_count // 10 % len(self.render_tris) + 1

            if self.animate_construction:
                # only render a subset
                partialTris = self.render_tris[0:anim_count]
            else:
                partialTris = self.render_tris

            for i, tri in enumerate(partialTris[:]):
                try:
                    draw_tri(tri, cube_colors[i % len(cube_colors)])
                except Exception as e:
                    print(f"couldn't draw tri: {tri=}")
                    print(f"an error occured: {e}")
                    # traceback.print_exc()

            # draw what is currently in the buffer to the screen
            pixel_buffer.draw()
            if self.show_z_buffer:
                # print(set(z_buffer.contents))
                z_buffer.draw()

            if self.animate_construction and anim_count == len(
                self.render_tris
            ):
                pyxel.text(
                    0, 0, "Done drawing, press r to redraw", pyxel.COLOR_WHITE
                )
                self.ran = True

    def test_update(self, verts,faces):
        total_scale = 40.0
        # matrix multiplaction order is left to right
        common_tranform = (
            createRotationZ((pyxel.mouse_y/HEIGHT) * 2 *np.pi)
                @ createRotationX((pyxel.mouse_x/WIDTH) * 2 *np.pi)
                @ createRotationY(self.mouse_z * .25)
                @ createScale(total_scale, total_scale, total_scale)
                @ createTranslation(-0.5, -0.5, -0.5)
        )

        right_transform = (
            createTranslation(total_scale, 0, -200)
                @ common_tranform
        )

        # left_cube= transform_verts(left_cube,createRotationZ(m.pi/50*self.frame_count+10))
        left_transform = (
            createTranslation(-total_scale, 0, -200)
                @ common_tranform
        )

        right_cube = copy.deepcopy(verts)
        left_cube = copy.deepcopy(verts)

        # apply all transforms
        right_cube = transform_verts(right_cube, right_transform)
        left_cube = transform_verts(left_cube, left_transform)

        render_right = tris_from_verts(right_cube, faces)
        render_left = tris_from_verts(left_cube, faces)
        return render_right + render_left

    def model_rotate(self, verts,faces):
        total_scale = 80.0
        # matrix multiplaction order is left to right
        transform = (
            createRotationY(m.pi / 50 * self.frame_count + 10)
                @ createScale(total_scale, total_scale, total_scale)
        )


        render_verts = copy.deepcopy(verts)

        render_verts = transform_verts(render_verts, transform)
        render_tris = tris_from_verts(render_verts, faces)
        return render_tris

    def cube_update(self, verts,faces):
        total_scale = 40.0
        # matrix multiplaction order is left to right
        common_tranform = (
            createRotationY(m.pi / 50 * self.frame_count + 10)
                @ createRotationZ(m.pi / 50 * self.frame_count + 10)
                @ createScale(total_scale, total_scale, total_scale)
                @ createTranslation(-0.5, -0.5, -0.5)
        )

        right_transform = (
            createTranslation(total_scale, 0, -200)
                @ createRotationZ(m.pi / 50 * self.frame_count + 10)
                @ common_tranform
        )

        # left_cube= transform_verts(left_cube,createRotationZ(m.pi/50*self.frame_count+10))
        left_transform = (
            createTranslation(-total_scale, 0, -200)
                @ createRotationZ(-m.pi / 50 * self.frame_count + 10)
                @ common_tranform
        )

        right_cube = copy.deepcopy(verts)
        left_cube = copy.deepcopy(verts)

        # apply all transforms
        right_cube = transform_verts(right_cube, right_transform)
        left_cube = transform_verts(left_cube, left_transform)

        render_right = tris_from_verts(right_cube, faces)
        render_left = tris_from_verts(left_cube, faces)
        return render_right + render_left

App()
