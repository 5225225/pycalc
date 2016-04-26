# vim: set fileencoding=utf-8

import sys

try:
    import readline
    # No idea if this is a license violation. Hope it isn't.
except ImportError:
    print("Could not find readline, you will likely get no line editing functionality")

if sys.version_info.major < 3:
    print("This program is for python version 3 only.")
    sys.exit(3)

import lexer
import execute

while True:
    instr = input("» ")
    toks = lexer.to_toks(instr)
    rpn = lexer.to_rpn(toks)

    result = execute.eval_rpn(rpn)

    if result is not None:
        print(result)

    if len(sys.argv) >= 2:
        break
