import dataclasses
import math as m
import unittest


@dataclasses.dataclass
class Point:
    x: float
    y: float


@dataclasses.dataclass
class Vec:
    x: float
    y: float


@dataclasses.dataclass
class Tri:
    p1: Point
    p2: Point
    p3: Point


def rotate_point(p: Point, angle_rad: float) -> Point:
    """rotate point (x,y) about origin by angle_rad"""
    p_rotated = Point(
        p.x * m.cos(angle_rad) - p.y * m.sin(angle_rad),
        p.x * m.sin(angle_rad) + p.y * m.cos(angle_rad),
    )
    return p_rotated


def same_side(line_p1: Point, line_p2: Point, test_p1: Point, test_p2: Point) -> bool:
    cp1 = (line_p2.y - line_p1.y) * (test_p1.x - line_p1.x) - (
        line_p2.x - line_p1.x
    ) * (test_p1.y - line_p1.y)
    cp2 = (line_p2.y - line_p1.y) * (test_p2.x - line_p1.x) - (
        line_p2.x - line_p1.x
    ) * (test_p2.y - line_p1.y)
    return cp1 * cp2 >= -75


def rotate_about_point(p_to_rotate: Point, p_about: Point, angle_rad: float) -> Point:
    """rotate point (x,y) about point (aboutX,aboutY) by angle_rad"""
    # treat aboutX,aboutY as origin
    p_relative = Point(p_about.x - p_to_rotate.x, p_about.y - p_to_rotate.y)
    # apply rotation about origin
    p_relative_rotated = rotate_point(p_relative, angle_rad)
    # convert back to original coordinate space and return
    p_rotated = Point(
        p_relative_rotated.x + p_about.x, p_relative_rotated.y + p_about.y
    )
    return p_rotated


class TestRotatePoint(unittest.TestCase):
    def test_rotate_by_zero(self):
        point = Point(1, 0)
        rotated = rotate_point(point, 0)
        self.assertEqual(rotated, point)

    def test_rotate_by_90_degrees(self):
        point = Point(1, 0)
        rotated = rotate_point(point, np.pi / 2)
        self.assertAlmostEqual(rotated.x, 0)
        self.assertAlmostEqual(rotated.y, 1)


class TestSameSide(unittest.TestCase):
    def test_on_same_side(self):
        p1 = Point(0, 0)
        p2 = Point(0, 1)

        p3 = Point(1, 0)
        test_point = Point(2, 0)
        self.assertTrue(same_side(p1, p2, p3, test_point))

    def test_on_diff_side(self):
        p1 = Point(0, 0)
        p2 = Point(0, 1)

        p3 = Point(-1, -1)
        test_point = Point(2, 0)
        self.assertFalse(same_side(p1, p2, p3, test_point))

    def test_on_line(self):
        p1 = Point(0, 0)
        p2 = Point(0, 1)

        p3 = Point(0, 0.5)
        test_point = Point(0, -1)
        test_point2 = Point(0, 1)
        self.assertTrue(same_side(p1, p2, p3, test_point))
        self.assertTrue(same_side(p1, p2, p3, test_point2))
