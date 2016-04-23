import traceback
import os.path
import sys
import numbers
import math

from enum import Enum

import ply.lex as lex
import ply.yacc as yacc
import readline

def preproc(s):
    s = s.replace("¹", "**(1)")
    s = s.replace("²", "**(2)")
    s = s.replace("³", "**(3)")

    return s

def assert_eq(x1, x2):
    if x1 == x2:
        return
    else:
        print("=== Assertion FAILED ===")
        print(x1)
        print(x2)
        raise AssertionError

def test(infix, rpn, result):
    lexer = lex.lex()
    lexer.input(infix)
    toks = []
    for tok in lexer:
        toks.append(tok)
    if rpn is not None:
        assert_eq(" ".join([str(t.value) for t in to_rpn(toks)]), rpn)
    if result is not None:
        assert_eq(eval_rpn(to_rpn(toks), {}), result)

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

    "sin": 1,
    "cos": 1,
    "asin": 1,
    "acos": 1,
}

def varr(x, lvars):
    if isinstance(x, numbers.Real):
        return x
    elif x.type == "VAR" and x.value in lvars:
        return lvars[x.value]
    elif x.type == "NUMBER":
        return x.value
    else:
        return x
    
def eval_rpn(intoks, lvars):

    values = [x for x in intoks]

    stack = []
    while len(values) > 0:
        t = values.pop(0)
        if (isinstance(t, lex.LexToken) and t.type in ("VAR", "NUMBER")) or \
           (isinstance(t, numbers.Real)):
            stack.append(t)
        else:
            if t.type == "FUNC" and t.value not in usr_funcs:
                argcount = len(stack)
            else:
                argcount = argcounts[t.value]
            
            args = []

            while len(args) < argcount:
                try:
                    args.append(stack.pop())
                except IndexError:
                    print("Not enough arguments!")
                    return

            args = args[::-1]

            # Need to reverse it.
            if t.type == "PLUS":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 + x2
                stack.append(res)

            elif t.type == "MINUS":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 - x2
                stack.append(res)

            elif t.type == "TIMES":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 * x2
                stack.append(res)

            elif t.type == "DIVIDE":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 / x2
                stack.append(res)

            elif t.type == "LSHIFT":
                res = args[0] << args[1]
                stack.append(res)

            elif t.type == "RSHIFT":
                res = args[0] >> args[1]
                stack.append(res)

            elif t.type == "EXP":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 ** x2
                stack.append(res)

            elif t.type == "ASSIGN":
                variables[args[0].value] = varr(args[1], {})

            elif t.type == "FUNC":
                if t.value == "sin":
                    res = math.sin(varr(args[0], lvars))
                    stack.append(res)
                if t.value == "cos":
                    res = math.cos(varr(args[0], lvars))
                    stack.append(res)
                if t.value == "asin":
                    res = math.asin(varr(args[0], lvars))
                    stack.append(res)
                if t.value == "acos":
                    res = math.acos(varr(args[0], lvars))
                    stack.append(res)
                elif t.value in usr_funcs:
                    func = usr_funcs[t.value]
                    fargs = {}
                    for index, item in enumerate(func[0]):
                        fargs[item.value] = varr(args[index], lvars)
                    if (t.value in usr_basecases) and \
                    (tuple(varr(x, {}) for x in args) in usr_basecases[t.value]):
                        r = usr_basecases[t.value][tuple(varr(x, {}) for x in args)]
                        stack.append(r[0])
                    else:
                        stack.append(eval_rpn(func[1], fargs))
                    

                else:
                    newfunc = t
                    funccode = []
                    while len(values) > 0:
                        t = values.pop(0)
                        funccode.append(varr(t, {}))
                    if len(funccode) == 0:
                        print("No function body given")
                        return
                    if funccode[-1].type == "ASSIGN":
                        funccode.pop()

                    usr_funcs[newfunc.value] = (args, funccode)
                    argcounts[newfunc.value] = len(args)
                    
                    return
            elif t.type == "FUNC_BASE":
                funcname = t.value.replace("@", "")
                funccode = []

                while len(values) > 0:
                    t = values.pop(0)
                    funccode.append(varr(t, {}))

                if len(funccode) == 0:
                    print("No function body given")
                    return

                if funccode[-1].type == "ASSIGN":
                    funccode.pop()
                
                if funcname in usr_basecases:
                    usr_basecases[funcname][tuple([varr(x, {}) for x in args])] = funccode
                else:
                    usr_basecases[funcname] = {}
                    usr_basecases[funcname][tuple([varr(x, {}) for x in args])] = funccode
                print(usr_basecases)

            else:
                print("Unknown token")
                print(t)
                return

    if len(stack) == 1:
        return varr(stack[0], lvars)

    elif len(stack) > 1:
        print("Too many values!")
        print(stack)
        return

            

tokens = (
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LSHIFT",
    "RSHIFT",
    "EXP",
    "ASSIGN",
    "NUMBER",
    "LPAREN",
    "RPAREN",
    "VAR",
    "FUNC",
    "FUNC_BASE",
    "COMMA",
)

funcs = [
    "PLUS", "MINUS", "TIMES", "DIVIDE", "LSHIFT", "RSHIFT", "EXP", "ASSIGN",
]

# -=- lex code -=-


t_PLUS = "\+"
t_MINUS = "-"
t_TIMES = "\*"
t_DIVIDE = "/"
t_LSHIFT = "<<"
t_RSHIFT = ">>"
t_EXP = "\*\*"
t_ASSIGN = "="

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

def t_FUNC(t):
    "@?[A-Za-z_]+(?=\()"
    if t.value.startswith("@"):
        t.value = t.value[1:]
        t.type = "FUNC_BASE"

    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore  = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)




# Test cases slightly modified from https://en.wikipedia.org/wiki/Shunting-yard_algorithm



variables = {}
variables["e"] = math.e

usr_funcs = {}
usr_basecases = {}

try:
    for line in open(os.path.expanduser("~/.config/pycalc_init")).readlines():
        lexer = lex.lex()
        lexer.input(preproc(line))
        toks = []
        for tok in lexer:
            toks.append(tok)
        print(toks)
        eval_rpn(to_rpn(toks), variables)
except FileNotFoundError:
    pass

test("3 + 4", "3 4 +", 7)
test("5 + ((1 + 2) * 4) - 3", "5 1 2 + 4 * + 3 -", 14)
test("3 + 4 * 2 / (1/2) ** 2 ** 3", "3 4 2 * 1 2 / 2 3 ** ** / +", 2051)

test("fac(4)", None, 24)

while True:
    lexer = lex.lex()

    if len(sys.argv) == 2:
        instr = sys.argv[1]
    else:
        instr = input("» ")

    instr = preproc(instr)

    lexer.input(instr)

    toks = []

    for tok in lexer:
        toks.append(tok)

    result = None

    try:
        result = eval_rpn(to_rpn(toks), variables)
    except Exception as e:
        traceback.print_exc()

    if result is not None:
        print(result)
        


    if len(sys.argv) >= 2:
        break
