# vim: set fileencoding=utf-8

import sys

try:
    import readline  # noqa: this is used simply by being imported.
    # No idea if this is a license violation. Hope it isn't.
except ImportError:
    print("Could not find readline, you will likely get no line editing functionality")

if sys.version_info.major < 3:
    print("This program is for python version 3 only.")
    sys.exit(3)

import lexer  # noqa:  These have to go here, as they use Unicode, which py2 can't handle.
import execute  # noqa

while True:
    instr = input("» ")
    toks = lexer.to_toks(instr)
    rpn = lexer.to_rpn(toks)

    result = None
    try:
        result = execute.eval_rpn(rpn)
    except RecursionError:
        print("Recursion limit hit, stopping.")
    except Exception as e:
        print(e)

    if result is not None:
        print(result)

    if len(sys.argv) >= 2:
        break
