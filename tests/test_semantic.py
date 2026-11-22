
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lexer import tokenize
from src.parser import parse
from src.semantic import analyze


print("SEMANTIC ANALYZER TESTS")


# Test 1: Valid program
try:
    source = """
    int main(void) {
        int a = 10;
        int b = 20;
        return a + b;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 1: PASS - Valid program accepted")

except Exception as error:
    print("Test 1: FAIL -", error)


# Test 2: Undeclared variable
try:
    source = """
    int main(void) {
        return x;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 2: FAIL - Undeclared variable accepted")

except Exception:
    print("Test 2: PASS - Undeclared variable rejected")


# Test 3: Duplicate variable
try:
    source = """
    int main(void) {
        int a = 10;
        int a = 20;
        return a;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 3: FAIL - Duplicate variable accepted")

except Exception:
    print("Test 3: PASS - Duplicate variable rejected")


# Test 4: Function parameter recognized
try:
    source = """
    int main(int a) {
        return a;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 4: PASS - Function parameter recognized")

except Exception as error:
    print("Test 4: FAIL -", error)


# Test 5: Nested scope
try:
    source = """
    int main(void) {
        int a = 10;

        {
            int b = 20;
        }

        return a;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 5: PASS - Nested scope accepted")

except Exception as error:
    print("Test 5: FAIL -", error)


# Test 6: Parameter redeclaration
try:
    source = """
    int main(int a) {
        int a = 20;
        return a;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 6: FAIL - Parameter redeclaration accepted")

except Exception:
    print("Test 6: PASS - Parameter redeclaration rejected")


# Test 7: Invalid void variable
try:
    source = """
    int main(void) {
        void a;
        return 0;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 7: FAIL - Void variable accepted")

except Exception:
    print("Test 7: PASS - Void variable rejected")


# Test 8: Valid integer return
try:
    source = """
    int main(void) {
        return 10;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 8: PASS - Integer return accepted")

except Exception as error:
    print("Test 8: FAIL -", error)


# Test 9: Void function returning a value
try:
    source = """
    void display(void) {
        return 10;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 9: FAIL - Invalid void return accepted")

except Exception:
    print("Test 9: PASS - Invalid void return rejected")


# Test 10: Int function without return value
try:
    source = """
    int main(void) {
        return;
    }
    """

    ast = parse(tokenize(source))
    analyze(ast)

    print("Test 10: FAIL - Missing return value accepted")

except Exception:
    print("Test 10: PASS - Missing return value rejected")


print("\nSemantic testing completed!")
