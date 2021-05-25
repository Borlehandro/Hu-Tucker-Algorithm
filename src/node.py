from enum import Enum


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