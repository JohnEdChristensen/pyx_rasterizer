# following https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
from numpy import bytes_
import struct

# header = b'\x47\x49\x46\x38\x39\x61'
#            G,     I,   F,    8,     9,   a, # 89a is the version alternatives are 87a
header = b"GIF89a"


def logical_screen_descriptor(canvas_width, canvas_height):
    # bytes 0,1
    canvas_width = struct.pack("<H", canvas_width)
    # bytes 2,3
    canvas_height = struct.pack("<H", canvas_height)

    # byte 4
    global_color_table = b"1"
    color_resolution = b"001"
    sort_flag = b"0"
    size_of_global_color_table = b"001"

    byte_4 = global_color_table + color_resolution + sort_flag + size_of_global_color_table

    hex_4 = struct.pack("<B", int(byte_4, 2))

    # byte 5
    background_color_index = b"\x00"

    # byte 6
    pixel_aspect_ratio = b"\x00"
    return canvas_width + canvas_height + hex_4 + background_color_index + pixel_aspect_ratio


def color_table():
    # TODO match color resolution in logical_screen_descriptor
    color_1 = b"\xFF\xFF\xFF"
    color_2 = b"\xFF\x00\x00"
    color_3 = b"\x00\xFF\x00"
    color_4 = b"\x00\x00\x00"

    return color_1 + color_2 + color_3 + color_4


def graphic_control_extension():
    extension_introducer = b"\x21"
    graphic_control_label = b"\xF9"
    block_size = b"\x04"  # in bytes
    packed_field = b"\x00"  # many flags in here
    delay_time = b"\x00\x00"
    transparent_color_index = b"\x00"
    block_terminator = b"\x00"

    return (
        extension_introducer
        + graphic_control_label
        + block_size
        + packed_field
        + delay_time
        + transparent_color_index
        + block_terminator
    )


gif_hex_array=[0x2C, 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0A, 0x00, 0x00, 0x02, 0x16, 0x8C, 0x2D, 0x99, 0x87, 0x2A, 0x1C, 0xDC, 0x33, 0xA0, 0x02, 0x75, 0xEC, 0x95, 0xFA, 0xA8, 0xDE, 0x60, 0x8C, 0x04, 0x91, 0x4C, 0x01, 0x00, 0x3B]  # fmt: skip

with open("by_hand_gif.gif", "wb", buffering=0) as f:
    f.write(
        header + logical_screen_descriptor(10, 10) + color_table() + graphic_control_extension() + bytes(gif_hex_array)
    )
    # byte_string = ""
    # for b in gif_hex_array:
    #     s = hex(b)[2:]
    #     print(s)
    #     f.write(bytes.fromhex(s))
# struct.pack('<H', 10).fromhex()
