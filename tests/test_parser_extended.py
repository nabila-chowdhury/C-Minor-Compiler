
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lexer import tokenize
from src.parser import parse, ParseError


valid_tests = [
    "int main(void) { return 0; }",

    "int main(void) { int x = 2 + 3 * 4; return x; }",

    "int main(void) { if (1 == 1) return 1; else return 0; }",

    "int main(void) { while (1 > 0) { return 0; } return 1; }"
]

print("POSITIVE TESTS")

for i, source in enumerate(valid_tests, 1):
    try:
        parse(tokenize(source))
        print(f"Test {i}: PASS")
    except ParseError as error:
        print(f"Test {i}: FAIL - {error}")


invalid_tests = [
    "int main(void) { int a = 10 return a; }",

    "int main(void) { if (1 < ) return 0; }",

    "int main(void) { return 0;",

    "int main(void { return 0; }"
]

print("\nNEGATIVE TESTS")

for i, source in enumerate(invalid_tests, 1):
    try:
        parse(tokenize(source))
        print(f"Test {i}: FAIL - Invalid syntax accepted")
    except ParseError:
        print(f"Test {i}: PASS - Invalid syntax rejected")

print("\nParser testing completed!")
