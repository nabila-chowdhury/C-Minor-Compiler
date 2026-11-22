
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from src.lexer import tokenize
from src.parser import parse
from src.ir import generate_ir


source = """
int main(void) {
    int a = 10;
    int b = 20;
    int c = a + b;
    return c;
}
"""

# Step 1: Convert source code into tokens
tokens = tokenize(source)

# Step 2: Convert tokens into AST
ast = parse(tokens)

# Step 3: Generate Intermediate Representation
ir_code = generate_ir(ast)

print("INTERMEDIATE REPRESENTATION (IR)")
print("--------------------------------")

for instruction in ir_code:
    print(instruction)

print("\nIR TEST PASSED!")
