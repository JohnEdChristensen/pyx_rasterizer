import pyxel
import math as m
from src.utils import Point
from dataclasses import dataclass
from PIL import Image

# !!!!STATUS:!!!!! never finished :(
WIDTH = 160
HEIGHT = 120
FPS = 120

NUM_CIRCLES = 10


@dataclass
class circle:
    p = Point(0, 0)
    color: int = 1
    radius: int = 2


def loadImageRGBA(path):
    # Open the image file
    with Image.open(path) as img:
        # Convert the image to RGBA if it is not already in that mode
        img = img.convert("RGBA")

        # Extract ARGB data as a list of lists
    pixel_data = list(img.getdata())

    # Convert each pixel to hex
    hex_data = [f"{a:02x}{r:02x}{g:02x}{b:02x}" for r, g, b, a in pixel_data]

    # Reshape the flat list into a 2D list where each row corresponds to a row of pixels
    width, height = img.size
    hex_2d = [hex_data[i * width : (i + 1) * width] for i in range(height)]

    return hex_2d


def RGBAToHex(rgba):
    return rgba


def RGBAToIndex(rgba):
    for x in range(len(rgba)):
        for y in range(len(rgba[0])):
            print(rgba[x][y])


def testRGBA():
    rgba = loadImageRGBA("../assests/Link_NES.png")
    RGBAToIndex(rgba)


# argb_2d is now a list of lists of ARGB values


class App:
    t: float = 0
    p: Point = Point(0, 0)
    circle_cords: list[Point] = [Point(0, 0)] * NUM_CIRCLES
    circle_cords_past: list[Point] = [Point(0, 0)] * NUM_CIRCLES

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, fps=FPS)
        self.pixels = loadImageRGBA("../assests/Link_NES.png")

        print(self.pixels)
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
            pyxel.circ(e.x + WIDTH / 2, e.y + HEIGHT / 2, 6, (i + 1) % 16)

        for i, e in enumerate(self.circle_cords_past):
            scale = 0.25
            pyxel.circ(
                e.x * scale + WIDTH / 2, e.y * scale + HEIGHT / 2, 1, (i + 1) % 16
            )


App()
