# following https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html

# header = b'\x47\x49\x46\x38\x39\x61'
#            G,     I,   F,    8,     9,   a, # 89a is the version alternatives are 87a
from collections.abc import Iterable


header = b"GIF89a"


def logical_screen_descriptor(canvas_width, canvas_height):
    # bytes 0,1
    canvas_width = canvas_width.to_bytes(2, "little")
    # bytes 2,3
    canvas_height = canvas_height.to_bytes(2, "little")

    # byte 4
    global_color_table = b"1"
    color_resolution = b"001"
    sort_flag = b"0"
    size_of_global_color_table = b"001"

    byte_4 = global_color_table + color_resolution + sort_flag + size_of_global_color_table

    hex_4 = int(byte_4, 2).to_bytes()

    # byte 5
    background_color_index = int.to_bytes(0)

    # byte 6
    pixel_aspect_ratio = b"\x00"  # most modern gif viewers ignore this :(
    return canvas_width + canvas_height + hex_4 + background_color_index + pixel_aspect_ratio


def iter_to_bytes(iter: Iterable) -> bytes:
    """iterable values must fit in 1 byte"""
    return b"".join(x.to_bytes() for x in iter)


def color_table():
    # TODO match color resolution in logical_screen_descriptor
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    black = (0, 0, 0)
    color_1 = iter_to_bytes(white)
    color_2 = iter_to_bytes(red)
    color_3 = iter_to_bytes(blue)
    color_4 = iter_to_bytes(black)

    return color_1 + color_2 + color_3 + color_4


def graphic_control_extension():
    extension_introducer = b"\x21"  # always 0x21
    graphic_control_label = b"\xF9"  # always 0xF9
    block_size = int.to_bytes(4)
    packed_field = b"\x00"  # many flags in here
    delay_time = int.to_bytes(0, 2, "little")
    transparent_color_index = int.to_bytes(0)
    block_terminator = b"\x00"  # always 0

    return (
        extension_introducer
        + graphic_control_label
        + block_size
        + packed_field
        + delay_time
        + transparent_color_index
        + block_terminator
    )


def image_descriptor():
    image_seperator = b"\x2C"  # always 0x2C
    image_left = int.to_bytes(0, 2, "little")
    image_top = int.to_bytes(0, 2, "little")
    image_width = int.to_bytes(10, 2, "little")
    image_height = int.to_bytes(10, 2, "little")
    # If adding local color table, add local_color_table implementation
    packed_field = b"\x00"  # lots of flags, interlace, sort, local color table

    return image_seperator + image_left + image_top + image_width + image_height + packed_field


def local_color_table():
    ...


def image_data():
    lzw_min_code_size = int.to_bytes(2)
    block_size = int.to_bytes(22)
    data = bytes([0x8C, 0x2D, 0x99, 0x87, 0x2A, 0x1C, 0xDC, 0x33, 0xA0, 0x02, 0x75, 0xEC, 0x95, 0xFA, 0xA8, 0xDE, 0x60, 0x8C, 0x04, 0x91, 0x4C, 0x01])  # fmt: skip
    block_terminator = b"\x00"  # always 0

    return lzw_min_code_size + block_size + data + block_terminator


def comment_extension():
    ...


with open("by_hand_gif.gif", "wb", buffering=0) as f:
    f.write(
        header
        + logical_screen_descriptor(10, 10)
        + color_table()
        + graphic_control_extension()
        + image_descriptor()
        + image_data()
        # + comment_extension()
        + b"\x3B"
    )
    # byte_string = ""
    # for b in gif_hex_array:
    #     s = hex(b)[2:]
    #     print(s)
    #     f.write(bytes.fromhex(s))
# struct.pack('<H', 10).fromhex()
