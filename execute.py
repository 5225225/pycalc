import numbers
import math

import ply.lex as lex

variables = {}
usr_funcs = {}
usr_basecases = {}

debug = False

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


def varr(x, lvars):
    if x is None:
        return None
    if isinstance(x, numbers.Real):
        return x
    elif x.type == "VAR" and x.value in lvars:
        return lvars[x.value]
    elif x.type == "NUMBER":
        return x.value
    else:
        return x


def eval_rpn(intoks, lvars=None):
    if lvars is None:
        lvars = variables

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
            elif t.type == "THEN":
                argcount = 1
            else:
                argcount = argcounts[t.value]
            args = []

            while len(args) < argcount:
                try:
                    args.append(stack.pop())
                except IndexError:
                    raise IndexError("Not enough arguments")

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
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 << x2
                stack.append(res)

            elif t.type == "RSHIFT":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 >> x2
                stack.append(res)

            elif t.type == "EXP":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)
                res = x1 ** x2
                stack.append(res)

            elif t.type == "COMPARE":
                x1 = varr(args[0], lvars)
                x2 = varr(args[1], lvars)

                if t.value == "==":
                    res = int(x1 == x2)
                if t.value == ">=":
                    res = int(x1 >= x2)
                if t.value == "<=":
                    res = int(x1 <= x2)
                if t.value == ">":
                    res = int(x1 > x2)
                if t.value == "<":
                    res = int(x1 < x2)
                if t.value == "!=":
                    res = int(x1 != x2)

                stack.append(res)

            elif t.type == "ASSIGN":
                lvars[args[0].value] = varr(args[1], {})

            elif t.type == "THEN":
                x1 = varr(args[0], lvars)
                if x1 > 0:
                    stack.append(eval_rpn(values, lvars))
                else:
                    return

            elif t.type == "FUNC":
                if t.value == "sin":
                    res = math.sin(varr(args[0], lvars))
                    stack.append(res)
                elif t.value == "cos":
                    res = math.cos(varr(args[0], lvars))
                    stack.append(res)
                elif t.value == "asin":
                    res = math.asin(varr(args[0], lvars))
                    stack.append(res)
                elif t.value == "acos":
                    res = math.acos(varr(args[0], lvars))
                    stack.append(res)
                elif t.value == "debug":
                    global debug
                    debug = not(debug)
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
                        raise ValueError("No function body given")
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
                    raise ValueError("No function body given")

                if funccode[-1].type == "ASSIGN":
                    funccode.pop()

                if funcname in usr_basecases:
                    usr_basecases[funcname][tuple([varr(x, {}) for x in args])] = funccode
                else:
                    usr_basecases[funcname] = {}
                    usr_basecases[funcname][tuple([varr(x, {}) for x in args])] = funccode

            else:
                raise TypeError("Unknown token")

    if len(stack) == 1:
        return varr(stack[0], lvars)

    elif len(stack) > 1:
        raise IndexError("Too many values!")
