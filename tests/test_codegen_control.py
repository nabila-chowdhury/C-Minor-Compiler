
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.lexer import tokenize
from src.parser import parse
from src.ir import generate_ir
from src.codegen import generate_code


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
llvm_code = generate_code(ir_code)

build_folder = Path("build")
build_folder.mkdir(exist_ok=True)

output_file = build_folder / "control.ll"
output_file.write_text(llvm_code)

print("CONTROL FLOW LLVM CODE")
print("----------------------")
print(llvm_code)

print("\nLLVM CODE SAVED SUCCESSFULLY!")
