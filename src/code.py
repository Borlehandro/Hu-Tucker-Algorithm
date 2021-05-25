from collections import Counter
from math import ceil
from node import NodeType
from node import Node


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


# Combining (#1)
def combine(nodes_list):
    while len(nodes_list) > 1:
        min_sum = nodes_list[0].weight + nodes_list[1].weight
        min_left_index = 0
        min_right_index = 1
        for i in range(0, len(nodes_list) - 1):
            min_adj_index = find_min_adjacent(nodes_list, i)
            if nodes_list[i].weight + nodes_list[min_adj_index].weight < min_sum:
                min_sum = nodes_list[i].weight + nodes_list[min_adj_index].weight
                min_left_index = i
                min_right_index = min_adj_index
        nodes_list[min_left_index] = Node(nodes_list[min_left_index], nodes_list[min_right_index], min_sum, None,
                                          NodeType.TERMINAL)
        nodes_list.pop(min_right_index)


# Levels counting (#2)
def count_levels(node):
    if node.left is not None:
        node.left.level = node.level + 1
        node.right.level = node.level + 1
        count_levels(node.left)
        count_levels(node.right)


# Restructuring (#3)
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


# Codes table generation (#4)
def generate_code_table(root_node: Node, table_dict, current_bits):
    if root_node.left is not None and root_node.right is not None:
        left_bits = current_bits.copy()
        right_bits = current_bits.copy()
        left_bits.append(0)
        right_bits.append(1)
        generate_code_table(root_node.left, table_dict, left_bits)
        generate_code_table(root_node.right, table_dict, right_bits)
    else:
        table_dict[root_node.value] = current_bits


# Encoding and write to file
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
            bits_to_write = table.get(bytes([ch]))
            for bit in bits_to_write:
                if buffer_len == ints_in_buffer:
                    output_file.write(buffer[:ints_in_buffer * 4:])
                    buffer = bytearray(ints_in_buffer * 4)
                    real_bits_size += ints_in_buffer * 32
                    buffer_len = 0
                    print(".", sep="", end="")
                    if real_bits_size % (64 * 1024) == 0:
                        print()
                if current_int_len == 32:
                    buffer[buffer_len * 4: ((buffer_len + 1) * 4) - 1:] = buffer_int.to_bytes(4, "big")
                    buffer_len += 1
                    buffer_int = 0
                    current_int_len = 0

                buffer_int |= (bit << (31 - current_int_len))
                current_int_len += 1
    if buffer_len > 0:
        output_file.write(buffer[:buffer_len * 4:])
        real_bits_size += buffer_len * 32
    if current_int_len > 0:
        # Todo optimize
        output_file.write(buffer_int.to_bytes(4, "big"))
        real_bits_size += current_int_len
    output_file.write(real_bits_size.to_bytes(8, "big"))
    encode_table_info(table, output_file)


# Encode and write table info
def encode_table_info(table, output_file):
    config_len_bytes = 0
    for letter in table:
        output_file.write(letter)
        code = 0
        code_len = 0
        for bit in table[letter][::-1]:
            code |= (bit << code_len)
            code_len += 1
        shift = (8 * ceil(code_len / 8) - code_len)
        if shift > 0:
            code <<= shift
        output_file.write(code_len.to_bytes(1, "big"))
        output_file.write(code.to_bytes(ceil(code_len / 8), "big"))
        config_len_bytes += (2 + ceil(code_len / 8))
    output_file.write(config_len_bytes.to_bytes(4, "big"))


# Main encoding function
def encode(input_filename, output_filename):
    print("Start encoding...")
    print("Doing some math...")
    symbols_weights = Counter()
    with open(input_filename, "rb") as f:
        byte = f.read(1)
        while byte:
            symbols_weights[byte] += 1
            byte = f.read(1)
    print(symbols_weights)
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
    print(code_table)

    # Writing to file
    print("Start writing to file ", output_filename, ".huta", "...", sep="")
    input_file = open(input_filename, "rb")
    out_file = open(output_filename + ".huta", "wb")
    encode_to_file(code_table, input_file, out_file)
    print("Encoding completed. Encoded file: ", output_filename, ".huta", sep="")
    out_file.close()
