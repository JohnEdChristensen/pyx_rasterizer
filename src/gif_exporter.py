# following https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
import math as m

from itertools import islice

# header = b'\x47\x49\x46\x38\x39\x61'
#            G,     I,   F,    8,     9,   a, # 89a is the version alternatives are 87a
from collections.abc import Iterable


header = b"GIF89a"


def logical_screen_descriptor(canvas_width, canvas_height,global_color_table_size):
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
    
    hex_4 = int(byte_4, 2).to_bytes()

    # byte 5
    background_color_index = int.to_bytes(0)

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
    return b"".join(x.to_bytes() for x in iter)


def color_table(colors,table_bit_size):
    #TODO match color resolution in logical_screen_descriptor
    num_colors_to_add = 2**table_bit_size -len(colors)
    colors += [(0,0,0)]*num_colors_to_add

    return b"".join([iter_to_bytes(color) for color in colors])


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


def image_descriptor(width,height):
    image_seperator = b"\x2C"  # always 0x2C
    image_left = int.to_bytes(0, 2, "little")
    image_top = int.to_bytes(0, 2, "little")
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


def local_color_table():
    ...


def print_img_data(data):
    for i in range(0, len(data), 10):
        print(data[i : i + 10])


def print_codes(codes):
    for i in range(0, len(codes), 20):
        print(codes[i : i + 20])


def data_to_codes(data:list[int],num_color_bits)->list[int]:

    clear_code = 2**num_color_bits
    end_info_code = clear_code+1

    encoded_data =[] 
    for value in data:
        encoded_data += [clear_code,value]

    encoded_data += [end_info_code]
    return encoded_data


def image_data(data,num_color_bits):
    lzw_min_code_size = int.to_bytes(num_color_bits,1,"little")

    codes = data_to_codes(data,num_color_bits)
    
    encoded_data = ""
    for code in codes:
        encoded_data = f"{code:0{num_color_bits+1}b}" + encoded_data


    num_bits = len(encoded_data)
    num_bits_to_add = 8 - (num_bits % 8)

    
    encoded_data = ("0" * num_bits_to_add) + encoded_data

    num_bytes = len(encoded_data) // 8

    final_bytes = int(encoded_data, 2).to_bytes(num_bytes, "little")

    block_size = int.to_bytes(num_bytes, 1, "little")
    block_terminator = b"\x00"  # always 0
    return lzw_min_code_size + block_size + final_bytes + block_terminator


def comment_extension():
    ...



def export_image(file_name, data, width, height, colors):
    num_colors = len(colors)
    num_color_bits = m.ceil(m.log2(num_colors))
    print("num_color_bits:",num_color_bits)
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
    data = ([1] * 5 + [4] * 5) * 3
    data += ([1] * 3 + [0] * 4 + [4] * 3) * 2
    data += ([2] * 3 + [0] * 4 + [3] * 3) * 2
    data += ([2] * 5 + [3] * 5) * 3
    print_img_data(data)

    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    green = (0, 255, 0)
    yellow = (255, 255,0 )
    black = (0, 0, 0)
    colors = [white,red,blue,green,yellow]

    export_image("by_hand.gif", data,20,5,colors)

