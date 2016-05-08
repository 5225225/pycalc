from astnode import node, node_type
from enum import Enum
import lexer
import execute


def parsetoks(tokens):
    toks = tokens[:]
    # Make a copy to prevent mutation of original.

    ast = node(node_type.BODY, "body")

    while len(toks) > 0:
        currtok = toks.pop(0)

        if currtok.type == "IF":
            cond = []
            while currtok.type != "RPAREN":
                currtok = toks.pop(0)
                cond.append(currtok)

            bodies = [[]]
            while True:
                currtok = toks.pop(0)
                if currtok.type == "SEMICOLON":
                    bodies.append([])
                elif currtok.type == "RPAREN" and currtok.value == "}":
                    break
                elif currtok.type == "LPAREN" and currtok.value == "{":
                    pass
                else:
                    bodies[-1].append(currtok)
            if bodies[-1] == []:
                bodies = bodies[:-1]

            astbodies = []
            for item in bodies:
                astbodies.append(parsetoks(item))
            
            if len(toks) > 0:
                else_stmt = toks.pop(0)
                false_bodies = [[]]
                while True:
                    currtok = toks.pop(0)
                    if currtok.type == "SEMICOLON":
                        false_bodies.append([])
                    elif currtok.type == "RPAREN" and currtok.value == "}":
                        break
                    elif currtok.type == "LPAREN" and currtok.value == "{":
                        pass
                    else:
                        false_bodies[-1].append(currtok)
                if false_bodies[-1] == []:
                    false_bodies = false_bodies[:-1]

                ast_false_bodies = []
                for item in false_bodies:
                    ast_false_bodies.append(parsetoks(item))

            else:
                ast_false_bodies = []


            astcond = to_ast(to_rpn(cond))


            condnode = node(node_type.BODY, "condition", [astcond])
            bodiesnode = node(node_type.BODY, "body", astbodies)
            elsenode = node(node_type.BODY, "else", ast_false_bodies)


            if_node = node(node_type.IF, "if", [condnode, bodiesnode, elsenode])
            
            ast.children.append(if_node)


        elif currtok.type == "FUNC":
            func = currtok
            args = [[]]
            while currtok.type != "SEMICOLON":
                try:
                    currtok = toks.pop(0)
                except IndexError:
                    break
                if currtok.type == "COMMA":
                    args.append([])
                elif currtok.value in ("(", ";", ")"):
                    pass
                else:
                    args[-1].append(currtok)
            for a in args:
                print(a)

            ast_args = []
            for arg in args:
                ast_args.append(to_ast(to_rpn(arg)))
            
            func_node = node(node_type.FUNC, func, ast_args)
            ast.children.append(func_node)

        else:
            body = [currtok]
            while True:
                try:
                    currtok = toks.pop(0)
                except IndexError:
                    break
                if currtok.type == "SEMICOLON":
                    break
                else:
                    body.append(currtok)
            
            ast.children.append(to_ast(to_rpn(body)))

    return ast

funcs = [
    "PLUS", "MINUS", "TIMES", "DIVIDE", "LSHIFT", "RSHIFT", "EXP", "ASSIGN", "COMPARE"
] 

class assoc(Enum):
    left = 0
    right = 1

operassoc = {
    "PLUS": assoc.left,
    "MINUS": assoc.left,
    "DIVIDE": assoc.left,
    "TIMES": assoc.left,
    "LSHIFT": assoc.left,
    "RSHIFT": assoc.left,

    "COMPARE": assoc.left,

    "EXP": assoc.right,
    "ASSIGN": assoc.right,

}

prec = {
    "EXP": 100,

    "TIMES": 50,
    "DIVIDE": 50,

    "PLUS": 25,
    "MINUS": 25,

    "LSHIFT": 20,
    "RSHIFT": 20,

    "COMPARE": 15,

    "ASSIGN": 10,
}


def to_rpn(toks):
    toks = toks[:]
    # Make a copy of this so we DON'T update the original.
    output = []
    stack = []

    while len(toks) > 0:
        t = toks.pop(0)

        if t.type in ("NUMBER", "VAR"):
            output.append(t)

        elif t.type == "THEN":
            output.append(t)

        elif t.type == "FUNC":
            stack.append(t)

        elif t.type == "FUNC_BASE":
            stack.append(t)

        elif t.type == "COMMA":
            while stack[-1].type != "LPAREN":
                output.append(stack.pop())

        elif t.type in funcs:
            o1 = t
            while len(stack) > 0 and stack[-1].type in funcs:
                o2 = stack[-1]
                if (operassoc[o1.type] == assoc.left and prec[o1.type] <= prec[o2.type]) or \
                   (operassoc[o1.type] == assoc.right and prec[o1.type] < prec[o2.type]):

                    output.append(stack.pop())
                else:
                    break

            stack.append(o1)

        elif t.type == "LPAREN":
            stack.append(t)
        elif t.type == "RPAREN":
            while stack[-1].type != "LPAREN":
                output.append(stack.pop())
            stack.pop()
            if len(stack) > 0 and stack[-1].type in ("FUNC", "FUNC_BASE"):
                output.append(stack.pop())
        else:
            raise ValueError("Unknown token type {}".format(t))

    while len(stack) > 0:
        output.append(stack.pop())

    return output

def to_ast(rpntoks):
    rpntoks = rpntoks[:]
    # Make a copy, avoid mutation.
    stack = []

    while len(rpntoks) > 0:
        currtok = rpntoks.pop(0)
        if currtok.type in ("NUMBER", "VAR"):
            stack.append(node(currtok.type, currtok))
        elif currtok.type in funcs:
            try:
                arg2 = stack.pop()
                arg1 = stack.pop()
            except IndexError:
                print("Syntax error on line {}".format(currtok.lineno))
                print("Not enough arguments for function `{}`".format(currtok.value))
                raise

            stack.append(node("BINOP", currtok, [arg1, arg2]))

    assert len(stack) == 1
    return stack[0]

if __name__ == "__main__":
    # UGLY HACK: REMOVE

    prog = """
    if (2 - 1) {
        print(4)
    } else {
        print(2)
    }
    """


    toks = lexer.to_toks(prog)
    ast = parsetoks(toks)

    print("=== tokens ===")
    for tok in toks:
        print(tok)

    print("=== AST ===")
    ast.output()

    print("=== result ===")
    print(execute.eval_ast(ast))
