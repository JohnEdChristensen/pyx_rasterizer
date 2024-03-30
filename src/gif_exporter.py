# following https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
import math as m
from typing import List

from itertools import islice

# header = b'\x47\x49\x46\x38\x39\x61'
#            G,     I,   F,    8,     9,   a, # 89a is the version alternatives are 87a
from collections.abc import Iterable


header = b"GIF89a"


def logical_screen_descriptor(canvas_width, canvas_height, global_color_table_size):
    # bytes 0,1
    canvas_width = canvas_width.to_bytes(2, "little")
    # bytes 2,3
    canvas_height = canvas_height.to_bytes(2, "little")

    # byte 4
    global_color_table = "1"
    color_resolution = "001"
    sort_flag = "0"
    size_of_global_color_table = f"{global_color_table_size-1:03b}"
    byte_4 = global_color_table + color_resolution + sort_flag + size_of_global_color_table

    hex_4 = int(byte_4, 2).to_bytes(1, "little")

    # byte 5
    background_color_index = int.to_bytes(0, 1, "little")

    # byte 6
    pixel_aspect_ratio = b"\x00"  # most modern gif viewers ignore this :(
    return canvas_width + canvas_height + hex_4 + background_color_index + pixel_aspect_ratio


def iter_to_bytes(iter: Iterable) -> bytes:
    """iterable values must fit in 1 byte"""
    return b"".join(x.to_bytes(1, "little") for x in iter)


def color_table(colors, table_bit_size):
    # TODO match color resolution in logical_screen_descriptor
    num_to_pad = 2**table_bit_size - len(colors)
    colors += [(0, 0, 0)] * num_to_pad

    return b"".join([iter_to_bytes(color) for color in colors])


def graphic_control_extension():
    extension_introducer = b"\x21"  # always 0x21
    graphic_control_label = b"\xf9"  # always 0xF9
    block_size = int.to_bytes(4, 1, "little")
    packed_field = b"\x00"  # many flags in here
    delay_time = int.to_bytes(0, 2, "little")
    transparent_color_index = int.to_bytes(0, 1, "little")
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


def image_descriptor(width, height):
    image_seperator = b"\x2c"  # always 0x2C
    image_left = int.to_bytes(0, 2, "little")
    image_top = int.to_bytes(0, 2, "little")
    image_width = int.to_bytes(width, 2, "little")
    image_height = int.to_bytes(height, 2, "little")
    # If adding local color table, add local_color_table implementation
    packed_field = b"\x00"  # lots of flags, interlace, sort, local color table

    return image_seperator + image_left + image_top + image_width + image_height + packed_field


def local_color_table(): ...


def print_img_data(data):
    for i in range(0, len(data), 10):
        print(data[i : i + 10])


def print_codes(codes):
    for i in range(0, len(codes), 20):
        print(codes[i : i + 20])


# Index = int
# IndexStream = list[Index]
# Code = int
# CodeStream = list[Code]


# index stream to code stream
def data_to_codes(indexStream, num_color_bits: int) -> list[int]:
    clear_code = 2**num_color_bits
    end_info_code = clear_code + 1

    # Has Sequences of colors, and special control codes
    # Code table is a list of tuples
    initial_code_table = [(i,) for i in range(0, 2**num_color_bits)]
    initial_code_table += [(clear_code,), (end_info_code,)]

    # Dynamically create the code table, decoding will be able to build the same table
    code_table = initial_code_table.copy()

    # Codes are indices into code_table
    # this is our output data
    code_stream = []
    code_stream += [clear_code]

    # Keep track of the range of indices until we know what their code is
    index_buffer = []

    for i, k in enumerate(indexStream):
        if i == 0:
            index_buffer += [k]
        else:
            if tuple(index_buffer + [k]) in code_table:
                index_buffer += [k]
            else:
                code_table.append(tuple(index_buffer + [k]))
                code = code_table.index(tuple(index_buffer))
                code_stream += [code]
                index_buffer = [k]

    # handle what remains in index buffer
    code = code_table.index(tuple(index_buffer))
    code_stream += [code]
    code_stream += [end_info_code]

    print(f"{code_table=}")
    for i, code in enumerate(code_table):
        print(f"{i} {code}")
    print(f"{code_stream=}")

    return code_stream


def image_data(data, num_color_bits):
    lzw_min_code_size = int.to_bytes(num_color_bits, 1, "little")

    codes = data_to_codes(data, num_color_bits)

    encoded_data = ""
    for code in codes:
        encoded_data = f"{code:0{num_color_bits+1}b}" + encoded_data

    num_bits = len(encoded_data)
    num_bits_to_add = 8 - (num_bits % 8)

    encoded_data = ("0" * num_bits_to_add) + encoded_data

    num_bytes = len(encoded_data) // 8

    # gif image data sub-blocks can not be larger
    # than 255 bytes
    sub_block_max = 255
    num_sub_blocks = m.ceil(num_bytes / sub_block_max)

    output_bytes = lzw_min_code_size
    for i in range(num_sub_blocks):
        if i < num_sub_blocks - 1:
            sub_block_size_int = sub_block_max
            start_index = len(encoded_data) - 8 * sub_block_max * (i + 1)
            end_index = len(encoded_data) - 8 * sub_block_max * i
            sub_block_data = encoded_data[start_index:end_index]
        else:
            start_index = 0
            end_index = len(encoded_data) - 8 * sub_block_max * i
            sub_block_data = encoded_data[:end_index]
            sub_block_size_int = len(sub_block_data) // 8

        sub_block_size = int.to_bytes(sub_block_size_int, 1, "little")
        sub_block_bytes = int(sub_block_data, 2).to_bytes(sub_block_size_int, "little")

        output_bytes += sub_block_size + sub_block_bytes

    block_terminator = b"\x00"  # always 0
    output_bytes += block_terminator

    return output_bytes


def comment_extension(): ...


def export_image(file_name, data, width, height, colors):
    num_colors = len(colors)
    num_color_bits = m.ceil(m.log2(num_colors))
    print("num_color_bits:", num_color_bits)
    with open(file_name, "wb", buffering=0) as f:
        f.write(
            header
            + logical_screen_descriptor(width,height,num_color_bits)#TODO make this color size a reasonable input
            + color_table(colors,num_color_bits)
            + graphic_control_extension()
            + image_descriptor(width,height)
            + image_data(data,num_color_bits)
            # + comment_extension()
            + b"\x3B"
        )  # fmt: skip


if __name__ == "__main__":
    # data = ([1] * 5 + [4] * 5) * 3
    # data += ([1] * 3 + [0] * 4 + [4] * 3) * 2
    # data += ([2] * 3 + [0] * 4 + [3] * 3) * 2
    # data += ([2] * 5 + [3] * 5) * 3
    data = ([1] * 5 + [2] * 5) * 3
    data += ([1] * 3 + [0] * 4 + [2] * 3) * 2
    data += ([2] * 3 + [0] * 4 + [1] * 3) * 2
    data += ([2] * 5 + [1] * 5) * 3
    print_img_data(data)

    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    colors = [white, red, blue, black]

    export_image("by_hand.gif", data, 10, 10, colors)
