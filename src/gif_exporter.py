# following https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
import math as m
from typing import List
import numpy as np

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
    byte_4 = (
        global_color_table + color_resolution + sort_flag + size_of_global_color_table
    )

    hex_4 = int(byte_4, 2).to_bytes(1, "little")

    # byte 5
    background_color_index = int.to_bytes(0, 1, "little")

    # byte 6
    pixel_aspect_ratio = b"\x00"  # most modern gif viewers ignore this :(
    return (
        canvas_width
        + canvas_height
        + hex_4
        + background_color_index
        + pixel_aspect_ratio
    )


def iter_to_bytes(iter: Iterable) -> bytes:
    """iterable values must fit in 1 byte"""
    return b"".join(x.to_bytes(1, "little") for x in iter)


def color_table(colors, table_bit_size):
    # TODO match color resolution in logical_screen_descriptor
    num_to_pad = 2**table_bit_size - len(colors)
    colors += [(0, 0, 0)] * num_to_pad

    return b"".join([iter_to_bytes(color) for color in colors])


def application_control_extension():
    extension_introducer = b"\x21"  # always 0x21
    application_extension_label = b"\xff"
    application_data_length = int.to_bytes(11, 1, "little")
    application_data_name = b"NETSCAPE"  # always 0xF9
    application_data_version = b"2.0"  # always 0xF9
    length_of_sublock = int.to_bytes(3, 1, "little")
    one = int.to_bytes(1, 1, "little")
    num_loop = int.to_bytes(0, 2, "little")
    block_terminator = b"\x00"  # always 0

    return (
        extension_introducer
        + application_extension_label
        + application_data_length
        + application_data_name
        + application_data_version
        + length_of_sublock
        + one
        + num_loop
        + block_terminator
    )


def graphic_control_extension(delay):
    """delay in hundreths of seconds"""
    extension_introducer = b"\x21"  # always 0x21
    graphic_control_label = b"\xf9"  # always 0xF9
    block_size = int.to_bytes(4, 1, "little")
    # packed_field = b"\x01"  # many flags in here, last bit is transparency
    # disposal_method = "010"  # clear entire screen
    disposal_method = "001"  # leaves previous frame drawn
    transparency_flag = "0"
    user_input_flag = "0"  # rarely used and might not be widely supported
    packed_field_string = "000" + disposal_method + user_input_flag + transparency_flag
    packed_field = int(packed_field_string, 2).to_bytes(1, "little")

    delay_time = int.to_bytes(delay, 2, "little")
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


def image_descriptor(x, y, width, height):
    image_seperator = b"\x2c"  # always 0x2C
    image_left = int.to_bytes(x, 2, "little")
    image_top = int.to_bytes(y, 2, "little")
    image_width = int.to_bytes(width, 2, "little")
    image_height = int.to_bytes(height, 2, "little")
    # If adding local color table, add local_color_table implementation
    packed_field = b"\x00"  # lots of flags, interlace, sort, local color table

    return (
        image_seperator
        + image_left
        + image_top
        + image_width
        + image_height
        + packed_field
    )


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
def data_to_codes(indexStream, num_color_bits: int) -> tuple[list[int], list[int]]:
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
    code_table_len_stream = []

    # Code_table_len_stream will track the size of the code table
    # when each code is added
    code_stream += [clear_code]
    code_table_len_stream += [len(code_table)]

    # Keep track of the range of indices until we know what their code is
    index_buffer = []
    old_table_len = len(code_table)

    for i, k in enumerate(indexStream):
        if i == 0:
            index_buffer += [k]
        else:
            if tuple(index_buffer + [k]) in code_table:
                index_buffer += [k]
            else:
                code_table_len_stream += [old_table_len]
                old_table_len = len(code_table)

                code_table.append(tuple(index_buffer + [k]))
                code = code_table.index(tuple(index_buffer))
                code_stream += [code]
                index_buffer = [k]

    # handle what remains in index buffer
    code = code_table.index(tuple(index_buffer))
    code_stream += [code]
    code_table_len_stream += [len(code_table)]
    code_stream += [end_info_code]
    code_table_len_stream += [len(code_table)]

    return code_stream, code_table_len_stream


def image_data(data, num_color_bits):
    lzw_min_code_size = int.to_bytes(num_color_bits, 1, "little")

    codes, code_table_sizes = data_to_codes(data, num_color_bits)

    encoded_data = ""
    for code, code_table_size in zip(codes, code_table_sizes):
        num_code_bits = m.floor(m.log2(code_table_size) + 1)
        encoded_data = f"{code:0{num_code_bits}b}" + encoded_data
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
        sub_block_data_as_bytes = int(sub_block_data, 2).to_bytes(
            sub_block_size_int, "little"
        )

        output_bytes += sub_block_size + sub_block_data_as_bytes

    block_terminator = b"\x00"  # always 0
    output_bytes += block_terminator

    return output_bytes


def comment_extension(): ...


def findBoundingBox(data):
    (column_nz_indices, row_nz_indices) = np.nonzero(data)

    left = int(min(row_nz_indices))
    right = int(max(row_nz_indices))
    top = int(min(column_nz_indices))
    bottom = int(max(column_nz_indices))

    x = left
    y = top
    width = right - left + 1
    height = bottom - top + 1

    return (x, y, width, height)


def find_frame_diff(prev_frame, next_frame):
    # x = 80
    # y = 60
    # width = 20
    # height = 40

    mask = prev_frame != next_frame

    return findBoundingBox(mask)


def export_image(file_name, frame_data, width, height, fps, colors):
    """frame data is a list of frames of data. a frame is a 1d list of color indicies"""
    # delay is measured in hundreths of seconds
    delay_hms = m.ceil((1 / fps) * 0.01)
    num_colors = len(colors)
    num_color_bits = m.ceil(m.log2(num_colors))
    file_contents = (
        header
        + logical_screen_descriptor(
            width, height, num_color_bits
        )  # TODO make this color size a reasonable input
        + color_table(colors, num_color_bits)
        + application_control_extension()
    )

    for i, frame in enumerate(frame_data):
        if i != 0:
            np_frame = np.reshape(frame, (height, width))
            np_prev_frame = np.reshape(frame_data[i - 1], (height, width))

            (x, y, diff_width, diff_height) = find_frame_diff(np_prev_frame, np_frame)

            npDiff_frame = np_frame[y : y + diff_height, x : x + diff_width]

            diff_frame = npDiff_frame.ravel()
        else:
            x = 0
            y = 0
            diff_width = width
            diff_height = height
            diff_frame = frame
            #
            # print("unaltered frame")
            # print(frame)
            # np_frame = np.reshape(frame, (height, width))
            # print("np unaltered frame")
            # print(np_frame)
            #
            # npDiff_frame = np_frame[y : y + diff_height, x : x + diff_width]
            # print("np diff frame")
            # print(npDiff_frame)
            #
            # diff_frame = npDiff_frame.ravel()
            # print("diff frame")
            # print(diff_frame)
        file_contents += (
            graphic_control_extension(delay_hms)
            + image_descriptor(x, y, diff_width, diff_height)
            + image_data(diff_frame, num_color_bits)  # frmt:skip
        )
    file_contents += b"\x3b"

    with open(file_name, "wb", buffering=0) as f:
        f.write( file_contents)  # fmt: skip


if __name__ == "__main__":
    # data = ([1] * 5 + [4] * 5) * 3
    # data += ([1] * 3 + [0] * 4 + [4] * 3) * 2
    # data += ([2] * 3 + [0] * 4 + [3] * 3) * 2
    # data += ([2] * 5 + [3] * 5) * 3
    data = [[], []]
    data[0] = ([1] * 5 + [3] * 5) * 3
    data[0] += ([1] * 3 + [0] * 4 + [2] * 3) * 2
    data[0] += ([2] * 3 + [0] * 4 + [1] * 3) * 2
    data[0] += ([2] * 5 + [1] * 5) * 3
    data[0] += [2] * 5 + [1] * 5
    print_img_data(data[0])
    data[1] = ([4] * 5 + [3] * 5) * 3
    data[1] += ([1] * 3 + [0] * 4 + [2] * 3) * 2
    data[1] += ([2] * 3 + [0] * 4 + [1] * 3) * 2
    data[1] += ([2] * 5 + [1] * 5) * 3
    data[1] += [2] * 5 + [1] * 5
    print_img_data(data[1])
    # print(len(data[1]))

    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    colors = [white, red, blue, black, green]

    export_image("by_hand.gif", data, 10, 11, 100, colors)
