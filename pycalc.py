# vim: set fileencoding=utf-8

import sys

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
