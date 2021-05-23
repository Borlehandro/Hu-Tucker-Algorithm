from collections import Counter
from enum import Enum
from math import ceil


class NodeType(Enum):
    ALPHABETIC = 0
    TERMINAL = 1


class Node:
    level = None

    def __init__(self, left, right, weight, value, node_type: NodeType):
        self.left = left
        self.right = right
        self.weight = weight
        self.value = value
        self.type = node_type


def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    print("base", base, "shift", shift)
    return (data[base] & (1 << shift)) >> shift


def find_min_adjacent(nodes_list, index):
    min_adj = nodes_list[index].weight + nodes_list[index + 1].weight
    min_adj_index = index + 1
    for i in range(index + 1, len(nodes_list)):
        if nodes_list[i].weight + nodes_list[index].weight < min_adj:
            min_adj = nodes_list[i].weight + nodes_list[index].weight
            min_adj_index = i
        if nodes_list[i].type is NodeType.ALPHABETIC:
            break
    return min_adj_index


def combine(nodes_list):
    while len(nodes_list) > 1:
        min_sum = nodes_list[0].weight + nodes_list[1].weight
        min_left_index = 0
        min_right_index = 1
        for i in range(0, len(nodes_list) - 1):
            min_adj_index = find_min_adjacent(nodes_list, i)
            # print("Min adj for", i, ":", min_adj_index)
            if nodes_list[i].weight + nodes_list[min_adj_index].weight < min_sum:
                min_sum = nodes_list[i].weight + nodes_list[min_adj_index].weight
                min_left_index = i
                min_right_index = min_adj_index
        nodes_list[min_left_index] = Node(nodes_list[min_left_index], nodes_list[min_right_index], min_sum, None,
                                          NodeType.TERMINAL)
        nodes_list.pop(min_right_index)


# Levels counting
def count_levels(node):
    if node.left is not None:
        node.left.level = node.level + 1
        node.right.level = node.level + 1
        count_levels(node.left)
        count_levels(node.right)


# Restructuring
def restrict(nodes_list):
    stack = list()
    i = 0
    new_node = None
    while i <= len(nodes_list):
        if len(stack) < 2 or stack[-1].level != stack[-2].level:
            if i == len(nodes_list):
                break
            stack.append(nodes_list[i])
            i += 1
        else:
            left = stack.pop()
            right = stack.pop()
            new_node = Node(left, right, None, None, NodeType.TERMINAL)
            new_node.level = left.level - 1
            stack.append(new_node)
    return new_node


# Codes table generation
def generate_code_table(root_node: Node, table_dict, current_bits):
    if root_node.left is not None and root_node.right is not None:
        left_bits = current_bits.copy()
        right_bits = current_bits.copy()
        left_bits.append(0)
        right_bits.append(1)
        # print("right: ", right_bits, " left:", left_bits)
        generate_code_table(root_node.left, table_dict, left_bits)
        generate_code_table(root_node.right, table_dict, right_bits)
    else:
        table_dict[root_node.value] = current_bits


# Encode to file
def encode_to_file(table, input_file, output_file):
    ints_in_buffer = 256  # 1Kb
    real_bits_size = 0
    buffer = bytearray(ints_in_buffer * 4)
    buffer_len = 0
    current_int_len = 0
    buffer_int = int()  # 1 int = 4 bytes
    with input_file as f:
        file_content = f.read()
        for ch in file_content:
            bits_to_write = table.get(ch)
            for bit in bits_to_write[::-1]:
                if buffer_len == ints_in_buffer:
                    output_file.write(buffer)
                    buffer = bytearray(ints_in_buffer * 4)
                    real_bits_size += ints_in_buffer * 32
                    buffer_len = 0
                    print(".", sep="", end="")
                    if real_bits_size % (64 * 256) == 0:
                        print()
                if current_int_len == 32:
                    buffer[buffer_len * 4: ((buffer_len + 1) * 4) - 1:] = buffer_int.to_bytes(4, "big")
                    # print("Flush int:", buffer_int, buffer_int.to_bytes(4, "big"), "from:", buffer_len * 4, "to:", ((buffer_len + 1) * 4) - 1)
                    buffer_len += 1
                    buffer_int = 0
                    current_int_len = 0

                buffer_int |= (bit << current_int_len)
                current_int_len += 1
    if buffer_len > 0:
        output_file.write(buffer[:buffer_len * 4:])
        real_bits_size += buffer_len * 32
    if current_int_len > 0:
        # Todo optimize
        output_file.write(buffer_int.to_bytes(ceil(current_int_len / 8), "big"))
        real_bits_size += current_int_len
    output_file.write(real_bits_size.to_bytes(8, "big"))
    encode_table_info(table, output_file)


def encode_table_info(table, output_file):
    alph_len = len(table)
    config_len_bytes = 0
    for letter in table:
        output_file.write(letter.encode())
        code = 0
        code_len = 0
        for bit in table[letter][::-1]:
            code |= (bit << code_len)
            code_len += 1
        output_file.write(code_len.to_bytes(1, "big"))
        output_file.write(code.to_bytes(ceil(code_len / 8), "big"))
        # print(1 + ceil(code_len / 8))
        config_len_bytes += (2 + ceil(code_len / 8))
    output_file.write(config_len_bytes.to_bytes(4, "big"))


# Main encoding function
def encode(input_filename, output_filename):
    print("Start encoding...")
    input_file = open(input_filename, "r")
    print("Doing some math...")
    symbols_weights = Counter(input_file.read())
    sorted(symbols_weights.items())
    nodes_list = list(
        map(lambda symbol_weight: Node(None, None, symbol_weight[1], symbol_weight[0], NodeType.ALPHABETIC),
            sorted(symbols_weights.items())))
    leaves = nodes_list.copy()
    combine(nodes_list)
    root = nodes_list[0]
    root.level = 0
    count_levels(root)
    root = restrict(leaves)
    code_table = {}
    generate_code_table(root, code_table, [])
    # print(code_table)

    # Writing to file
    print("Start writing to file ", output_filename, ".huta", "...", sep="")
    input_file = open(input_filename, "r")
    out_file = open(output_filename + ".huta", "wb")
    encode_to_file(code_table, input_file, out_file)
    print("Encoding completed. Encoded file: ", output_filename, ".huta", sep="")
    out_file.close()


def decode(input_filename, output_filename):
    print("Start decoding...")
    input_file = open(input_filename, "rb")
    print("Doing some magic...")
    input_file.seek(-4, 2)
    config_bytes = int.from_bytes(input_file.read(4), "big")
    input_file.seek(-config_bytes-4-8, 1)
    bytes_to_read = config_bytes
    print(bytes_to_read)
    total_bits = int.from_bytes(input_file.read(8), "big")
    decode_table = {}
    while bytes_to_read > 0:
        symbol = input_file.read(1)
        code_size = int.from_bytes(input_file.read(1), "big")
        code_bytes = input_file.read(ceil(code_size / 8))
        code = [access_bit(code_bytes, i) for i in range(code_size)]
        print(symbol, code_size, code)
        decode_table[tuple(code)] = symbol
        bytes_to_read -= 2 + ceil(code_size / 8)
    print(decode_table)
    input_file.seek(0, 0)
    out = open(output_filename, "wb")
    decode_to_file(input_file, out, total_bits, decode_table)
    out.close()
    input_file.close()


def decode_to_file(input_file, output_file, total_bits, decode_table):
    bits_to_read = total_bits
    # Todo add buffering
    bits = []
    while bits_to_read > 0:
        byte = input_file.read(1)
        bits.extend(tuple([access_bit(byte, i) for i in range(8)]))
        bits_to_read -= 8
        for k in range(len(bits)):
            sub = tuple(bits[:k:])
            print(sub)
            if sub in decode_table:
                output_file.write(decode_table[sub])
                print("SYMBOL", decode_table[sub])
                bits = bits[k + 1::]
                print("cut", bits)


def main():
    print("Welcome to Hu-Tucker archiver.")
    mode = input("Enter \"code\" to encoding or \"decode\" to decoding\n")
    if mode == "code":
        in_filename = input("Enter input filename:")
        out_filename = input("Enter output filename (without extension):")
        encode(in_filename, out_filename)
    elif mode == "decode":
        in_filename = input("Enter input filename (with .huta extension):")
        out_filename = input("Enter output filename (with original file extension):")
        decode(in_filename, out_filename)


if __name__ == "__main__":
    main()
