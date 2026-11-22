
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from src.lexer import tokenize
from src.parser import parse
from src.semantic import analyze, SemanticError


def run_test(source):
    tokens = tokenize(source)
    ast = parse(tokens)
    return analyze(ast)


print("SEMANTIC ANALYZER TESTS")

# Test 1: Valid program
try:
    run_test("int main(void) { int a = 10; return a; }")
    print("Test 1: PASS - Valid program accepted")
except Exception as error:
    print("Test 1: FAIL -", error)


# Test 2: Undeclared variable
try:
    run_test("int main(void) { return a; }")
    print("Test 2: FAIL - Undeclared variable accepted")
except SemanticError:
    print("Test 2: PASS - Undeclared variable rejected")


# Test 3: Duplicate variable
try:
    run_test("int main(void) { int a = 10; int a = 20; return a; }")
    print("Test 3: FAIL - Duplicate variable accepted")
except SemanticError:
    print("Test 3: PASS - Duplicate variable rejected")


# Test 4: Function parameter
try:
    run_test("int add(int a) { return a; }")
    print("Test 4: PASS - Function parameter recognized")
except Exception as error:
    print("Test 4: FAIL -", error)


# Test 5: Nested scope
try:
    run_test(
        "int main(void) { "
        "int a = 10; "
        "{ int b = 20; } "
        "return a; "
        "}"
    )
    print("Test 5: PASS - Nested scope accepted")
except Exception as error:
    print("Test 5: FAIL -", error)


print("\nSemantic testing completed!")
