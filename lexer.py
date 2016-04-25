from enum import Enum

import ply.lex as lex


def preproc(s):
    s = s.replace("¹", "**(1)")
    s = s.replace("²", "**(2)")
    s = s.replace("³", "**(3)")

    return s


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

argcounts = {
    "+": 2,
    "/": 2,
    "-": 2,
    "*": 2,
    "**": 2,
    ">>": 2,
    "<<": 2,
    "=": 2,
    "==": 2,
    ">=": 2,
    "<=": 2,
    ">": 2,
    "<": 2,
    "!=": 2,
    "if": 2,

    "sin": 1,
    "cos": 1,
    "asin": 1,
    "acos": 1,
    "debug": 1,
}


tokens = (
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LSHIFT",
    "RSHIFT",
    "EXP",
    "ASSIGN",
    "COMPARE",
    "THEN",
    "NUMBER",
    "LPAREN",
    "RPAREN",
    "VAR",
    "FUNC",
    "FUNC_BASE",
    "COMMA",
)

funcs = [
    "PLUS", "MINUS", "TIMES", "DIVIDE", "LSHIFT", "RSHIFT", "EXP", "ASSIGN", "COMPARE"
]

# -=- lex code -=-


t_PLUS = "\+"
t_MINUS = "-"
t_TIMES = "\*"
t_DIVIDE = "/"
t_EXP = "\*\*"
t_ASSIGN = "="
t_COMPARE = "(==|>=|<=|!=|>|<)"

t_LPAREN = "\("
t_RPAREN = "\)"
t_VAR = "[A-Za-z]+"
# Similar to variables, but enforces that it ends in a (
# The ending parenthesis is not included in the token, however.
# This is a way of telling the difference between f4 (where f is a function) and f4 (where f is a
# number, and you're doing implicit multiplication)

# This is like a function, only the @ at the beginning makes parsing easier.

t_COMMA = ","


def t_NUMBER(t):
    "_?\d*\.?[\d]+"
    t.value = t.value.replace("_", "-")
    try:
        t.value = int(t.value)
    except:
        t.value = float(t.value)
    return t


# Done in a function to force priority over t_VAR as priority is determined by regex length,
# assuming they're both of the same type (Both functions/both plain strings). Functions take
# priority over strings, however.
def t_THEN(t):
    "then"
    return t


def t_LSHIFT(t):
    "<<"
    return t


def t_RSHIFT(t):
    ">>"
    return t


def t_FUNC(t):
    "@?[A-Za-z_]+(?=\()"
    if t.value.startswith("@"):
        t.value = t.value[1:]
        t.type = "FUNC_BASE"

    return t


t_ignore = " \t"


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def to_toks(instr):
    lexer = lex.lex()

    lexer.input(instr)

    toks = []

    for tok in lexer:
        toks.append(tok)

    return toks
