from enum import Enum

class node_type(Enum):
    BODY = 0
    IF = 1
    FUNC = 2


class node:
    def __init__(self, ntype, nval, children=None):
        self.ntype = ntype
        self.nval = nval
        if children is None:
            children = []

        self.children = children

    def output(self, indent=0):
        if self is None:
            return
        print("{}{} »<{}>".format(" "*indent, self.nval, self.ntype))
        if self.children is not None:
            for child in self.children:
                node.output(child, indent=indent+2)

    def from_tokens(tokenlist):
        pass
