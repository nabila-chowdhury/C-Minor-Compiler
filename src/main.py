
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import tokenize
from src.parser import parse
from src.semantic import analyze
from src.ir import generate_ir
from src.codegen import generate_code
from src.diagnostics import DiagnosticEngine


def compile_file(source_file):
    diagnostics = DiagnosticEngine()
    source_path = Path(source_file)

    print("\n========== C MINOR COMPILER ==========")

    try:
        if not source_path.exists():
            diagnostics.report_error(
                f"File not found: {source_file}"
            )
            diagnostics.show_summary()
            return False

        source_code = source_path.read_text()

        print("\n[1] Lexical Analysis")
        tokens = tokenize(source_code)
        print(f"Tokens generated: {len(tokens)}")

        print("\n[2] Syntax Analysis")
        ast = parse(tokens)
        print("Parsing successful!")

        print("\n[3] Semantic Analysis")
        analyze(ast)
        print("Semantic analysis successful!")

        print("\n[4] Intermediate Representation")
        ir_code = generate_ir(ast)

        for instruction in ir_code:
            print(instruction)

        print("\n[5] LLVM Code Generation")
        llvm_code = generate_code(ir_code)

        build_folder = PROJECT_ROOT / "build"
        build_folder.mkdir(exist_ok=True)

        llvm_file = build_folder / "output.ll"
        llvm_file.write_text(llvm_code)
        print("LLVM code generated!")

        print("\n[6] LLVM Assembly")
        bitcode_file = build_folder / "output.bc"

        subprocess.run(
            ["llvm-as", str(llvm_file), "-o", str(bitcode_file)],
            check=True
        )
        print("LLVM assembly successful!")

        print("\n[7] Executable Generation")
        executable = build_folder / "compiler_output"

        subprocess.run(
            ["clang", str(bitcode_file), "-o", str(executable)],
            check=True
        )

        print("Executable generated successfully!")
        print("\n========== COMPILATION SUCCESSFUL ==========")
        print(f"Executable: {executable}")

        diagnostics.show_summary()
        return True

    except Exception as error:
        diagnostics.report_error(str(error))
        diagnostics.show_summary()
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/main.py <source_file.c>")
        sys.exit(1)

    if not compile_file(sys.argv[1]):
        sys.exit(1)


if __name__ == "__main__":
    main()
