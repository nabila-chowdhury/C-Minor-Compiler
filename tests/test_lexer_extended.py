
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from src.lexer import tokenize, LexError


# POSITIVE TESTS

valid_tests = [
    (
        "int a = 10;",
        ["int", "a", "=", "10", ";"]
    ),
    (
        "int x = 10 + 20;",
        ["int", "x", "=", "10", "+", "20", ";"]
    ),
    (
        "if (a >= 10) return a;",
        ["if", "(", "a", ">=", "10", ")", "return", "a", ";"]
    ),
    (
        "int a = 5; // comment",
        ["int", "a", "=", "5", ";"]
    ),
    (
        "/* comment */ int b = 20;",
        ["int", "b", "=", "20", ";"]
    )
]

print("POSITIVE TESTS")

for i, (source, expected) in enumerate(valid_tests, 1):

    tokens = tokenize(source)

    actual = [token.value for token in tokens]

    assert actual == expected, (
        f"Test {i} failed: {actual}"
    )

    print(f"Test {i}: PASS")


# NEGATIVE TESTS

invalid_tests = [
    "int a = 012;",
    "int a = 2147483648;",
    "int a = 10++;",
    "int a = 123abc;",
    'int a = "hello";',
    "/* unfinished comment"
]

print("\nNEGATIVE TESTS")

for i, source in enumerate(invalid_tests, 1):

    try:
        tokenize(source)

        print(f"Test {i}: FAIL - Invalid input accepted")

    except LexError:
        print(f"Test {i}: PASS - Invalid input rejected")


print("\nLexer testing completed!")
