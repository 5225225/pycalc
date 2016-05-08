import math

from astnode import node, node_type

def eval_ast(node):
    if node.ntype == node_type.BODY:
        if len(node.children) == 1:
            return eval_ast(node.children[0])
        else:
            for ch in node.children:
                eval_ast(ch)
    elif node.ntype == "BINOP":
        if node.nval.type == "PLUS":
            arg1 = eval_ast(node.children[0])
            arg2 = eval_ast(node.children[1])
            return arg1 + arg2
        elif node.nval.type == "MINUS":
            arg1 = eval_ast(node.children[0])
            arg2 = eval_ast(node.children[1])
            return arg1 - arg2
        elif node.nval.type == "TIMES":
            arg1 = eval_ast(node.children[0])
            arg2 = eval_ast(node.children[1])
            return arg1 * arg2
        elif node.nval.type == "DIVIDE":
            arg1 = eval_ast(node.children[0])
            arg2 = eval_ast(node.children[1])
            return arg1 / arg2
    elif node.ntype == "NUMBER":
        return node.nval.value
    elif node.ntype == node_type.IF:
        cond = node.children[0]
        true_body = node.children[1]
        false_body = node.children[2]

        if eval_ast(cond) != 0:
            eval_ast(true_body)
        else:
            eval_ast(false_body)

    elif node.ntype == node_type.FUNC:
        if node.nval.value == "print":
            for arg in node.children:
                print(eval_ast(arg))
        elif node.nval.value == "factorial":
            return math.factorial(node.children[0])
    else:
        print(node)
        raise ValueError("Unknown node type {}".format(node.ntype))
