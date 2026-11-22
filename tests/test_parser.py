import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lexer import tokenize
from src.parser import parse

source = """
int main(void) {
    int a = 10;
    int b = 20;

    if (a < b) {
        return a + b;
    }

    return 0;
}
"""

tokens = tokenize(source, "test.cm")
ast = parse(tokens)

print("PARSER TEST PASSED!")
print(ast)