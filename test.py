import lexer
import execute
import parser


class mock_token:
    pass


def assert_eq(x1, x2, accuracy=None):
    if accuracy is None:
        if x1 == x2:
            return
    else:
        if abs(x1 - x2) < accuracy:
            return

    print("=== Assertion FAILED ===")
    print("Expected: ", x1)
    print("Actual:   ", x2)
    raise AssertionError


def assert_raises(to_execute, exception):
    try:
        exec(to_execute)
    except BaseException as ex:
        if isinstance(ex, exception):
            return

    raise AssertionError


def test(infix, expect_result=None, expect_rpn=None, accuracy=None, inv_raise=True):
    toks = lexer.to_toks(infix, inv_raise=inv_raise)
    rpn = " ".join([str(x.value) for x in parser.to_rpn(toks)])

    result = execute.eval_rpn(parser.to_rpn(toks))

    if expect_rpn is not None:
        assert_eq(expect_rpn, rpn)
    if expect_result is not None:
        assert_eq(expect_result, result, accuracy)

# Testing basic arithmetic operations.
test("3 + 4", 7, "3 4 +")
test("5 + ((1 + 2) * 4) - 3", 14, "5 1 2 + 4 * + 3 -")
test("3 + 4 * 2 / (1/2) ** 2 ** 3", 2051, "3 4 2 * 1 2 / 2 3 ** ** / +")

test("3 << 5", 96)

test("5121 >> 5", 160)

# Testing basic functions.
test("inc(n) = n + 1")
test("inc(5)", 6)

# Testing nested functions
test("inc(inc(5))", 7)

# Testing recursive functions with basecases.
test("fib(n) = fib(n-1) + fib(n-2)")
test("@fib(0) = 1")
test("@fib(1) = 1")

test("fib(10)", 89)


test("fac(n) = n * fac(n-1)")
test("@fac(0) = 1")

test("fac(7)", 5040)

# Testing if statements

test("1 then testtrue = 1")
test("0 then testunset = 1")

test("testtrue", 1)
test("testunset", None)

test("testtrue", 1)
test("testunset", None)

# Testing comparisons

test("4 == 2", 0)
test("4 == 4", 1)
test("4 == 7", 0)

test("4 >= 2", 1)
test("4 >= 4", 1)
test("4 >= 7", 0)

test("4 <= 2", 0)
test("4 <= 4", 1)
test("4 <= 7", 1)

test("4 > 2", 1)
test("4 > 4", 0)
test("4 > 7", 0)

test("4 < 2", 0)
test("4 < 4", 0)
test("4 < 7", 1)

test("4 != 2", 1)
test("4 != 4", 0)
test("4 != 7", 1)

# Testing built-in functions

test("sin(1)", 0.8414709848078965, accuracy=1E-8)
test("cos(1)", 0.5403023058681398, accuracy=1E-8)

test("asin(1)", 1.5707963267948966, accuracy=1E-8)
test("acos(0.5)", 1.0471975511965979, accuracy=1E-8)

assert_eq(execute.debug, False)
test("debug()")
assert_eq(execute.debug, True)
test("debug()")
assert_eq(execute.debug, False)

# Functions with multiple arguments

test("sum(x,y,z) = x + y+z")
test("sum(4,2+(1),0)", 7)

# Creating a function with no body
assert_raises("test('f(x)')", ValueError)

# Trying to add a basecase to a non-existent function
assert_raises("test('@f(0) = 4')", NameError)

# Trying to add a basecase with no body
test("f(x) = x")
assert_raises("test('@f(x)')", ValueError)

# Invalid token type.

test_token = mock_token

test_token.type = "_INVALID_TOKEN_TYPE_"
test_token.value = "INVALID"

execute.argcounts[test_token.value] = 0
# This prevents a failure earlier with
# KeyError: 'INVALID'

assert_raises("execute.eval_rpn([test_token])", TypeError)

assert_raises("parser.to_rpn([test_token])", ValueError)

assert_raises("test('4 4 + 4')", IndexError)

# Testing the tests

assert_raises("test('4 +')", IndexError)

print("***  Now testing the self test. This should throw an assertion error.***")

assert_raises("test('2 + 2', 5)", AssertionError)

print("***  End self test ***")

assert_raises("4/0", ZeroDivisionError)
assert_raises("assert_raises('4/0', IndexError)", AssertionError)


# Testing various library functions directly.

assert_eq(execute.varr(None, {}), None)

# Testing the lexer's preprocessor

assert_eq(lexer.preproc("foo¹bar"), "foo**(1)bar")
assert_eq(lexer.preproc("foo²bar"), "foo**(2)bar")
assert_eq(lexer.preproc("foo³bar"), "foo**(3)bar")

assert_raises('test("4 +» 4", 8)', ValueError)

print("*** This should print an Illegal Character warning ***")
test("4 +» 4", 8, inv_raise=False)
print("*** End test ***")
