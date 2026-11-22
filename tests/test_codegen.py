
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
    int b = 20;
    int c = a + b;
    return c;
}
"""

tokens = tokenize(source)
ast = parse(tokens)

ir_code = generate_ir(ast)
llvm_code = generate_code(ir_code)

build_folder = Path("build")
build_folder.mkdir(exist_ok=True)

output_file = build_folder / "output.ll"
output_file.write_text(llvm_code)

print("LLVM CODE GENERATED SUCCESSFULLY!")
print(f"Saved to: {output_file}")
print("\nGenerated LLVM Code:")
print(llvm_code)
