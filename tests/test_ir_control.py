
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lexer import tokenize
from src.parser import parse
from src.ir import generate_ir


source = """
int main(void) {
    int a = 10;

    if (a > 5) {
        a = a + 1;
    } else {
        a = a - 1;
    }

    while (a < 15) {
        a = a + 1;
    }

    return a;
}
"""

tokens = tokenize(source)
ast = parse(tokens)
ir_code = generate_ir(ast)

print("IR CONTROL FLOW TEST")
print("--------------------")

for instruction in ir_code:
    print(instruction)

print("\nIR CONTROL FLOW TEST PASSED!")
