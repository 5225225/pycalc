from enum import Enum

import ply.lex as lex


class assoc(Enum):
    left = 0
    right = 1


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
    "SEMICOLON",
    "IF",
)

# -=- lex code -=-


t_PLUS = "\+"
t_MINUS = "-"
t_TIMES = "\*"
t_DIVIDE = "/"
t_EXP = "\*\*"
t_ASSIGN = "="
t_COMPARE = "(==|>=|<=|!=|>|<)"

t_LPAREN = "(\(|{)"
t_RPAREN = "(\)|})"
t_VAR = "[A-Za-z]+"

t_COMMA = ","
t_SEMICOLON = ";"


def t_NUMBER(t):
    "_?\d*\.?[\d]+"
    t.value = t.value.replace("_", "-")
    try:
        t.value = int(t.value)
    except:
        t.value = float(t.value)
    return t


# Done in a function to force priority over t_VAR as priority is determined by
# regex length, assuming they're both of the same type (Both functions/both
# plain strings). Functions take priority over strings, however.
def t_THEN(t):
    "then"
    return t


def t_IF(t):
    "if"
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
invalid_raise = False


def t_newline(t):
    "\\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    if invalid_raise:
        raise ValueError("Illegal character {}".format(t.value[0]))
    else:
        print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def to_toks(instr, inv_raise=False):
    global invalid_raise
    invalid_raise = inv_raise
    lexer = lex.lex()

    lexer.input(instr)

    toks = []

    for tok in lexer:
        toks.append(tok)

    return toks
