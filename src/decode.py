from math import ceil


def to_bits(data, bits_len):
    res = []
    for b in data:
        for bit_number in range(7, -1, -1):
            res.append((b & (1 << (bit_number % 8))) >> (bit_number % 8))
    return res[:bits_len:]


def decode(input_filename, output_filename):
    print("Start decoding...")
    input_file = open(input_filename, "rb")
    print("Doing some magic...")
    input_file.seek(-4, 2)
    config_bytes = int.from_bytes(input_file.read(4), "big")
    input_file.seek(-config_bytes-4-8, 1)
    bytes_to_read = config_bytes
    total_bits = int.from_bytes(input_file.read(8), "big")
    decode_table = {}
    while bytes_to_read > 0:
        symbol = input_file.read(1)
        code_size = int.from_bytes(input_file.read(1), "big")
        code_bytes = input_file.read(ceil(code_size / 8))
        code = to_bits(code_bytes, code_size)
        decode_table[tuple(code)] = symbol
        bytes_to_read -= 2 + ceil(code_size / 8)
    # print(decode_table)
    input_file.seek(0, 0)
    out = open(output_filename, "wb")
    decode_to_file(input_file, out, total_bits, decode_table)
    out.close()
    input_file.close()


def decode_to_file(input_file, output_file, total_bits, decode_table):
    bits_to_read = total_bits
    # Todo add buffering
    buffer = []
    while bits_to_read > 0:
        byte = input_file.read(1)
        bits = tuple(to_bits(byte, 8))
        bits_to_read -= 8
        for k in range(len(bits)):
            buffer.append(bits[k])
            if tuple(buffer) in decode_table:
                output_file.write(decode_table[tuple(buffer)])
                buffer = []
