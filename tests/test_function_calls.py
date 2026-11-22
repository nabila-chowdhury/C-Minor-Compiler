
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import tokenize
from src.parser import parse
from src.semantic import analyze
from src.ir import generate_ir
from src.codegen import generate_code

Path("build").mkdir(exist_ok=True)

source = """
int add(int a, int b) {
    return a + b;
}

int main(void) {
    int result;
    result = add(10, 20);
    return result;
}
"""

print("FUNCTION CALL TEST")

try:
    tokens = tokenize(source)
    ast = parse(tokens)
    analyze(ast)

    ir = generate_ir(ast)

    print("\nGenerated IR:")
    for instruction in ir:
        print(instruction)

    llvm_code = generate_code(ir)

    print("\nGenerated LLVM:")
    print(llvm_code)

    with open("build/function_test.ll", "w") as file:
        file.write(llvm_code)

    print("\nFunction call test passed!")

except Exception as error:
    print("\nFunction call test failed:")
    print(error)
    raise
