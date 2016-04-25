import sys

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
