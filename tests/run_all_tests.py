
import subprocess
import sys
from pathlib import Path

test_files = [
    "test_lexer.py",
    "test_lexer_extended.py",
    "test_parser.py",
    "test_parser_extended.py",
    "test_symbol_table.py",
    "test_semantic.py",
    "test_diagnostics.py",
    "test_ir.py",
    "test_ir_control.py",
    "test_codegen.py",
    "test_codegen_control.py"
]

test_folder = Path(__file__).parent

passed = 0
failed = 0

print("\n================================")
print("     C MINOR COMPILER TESTS")
print("================================\n")

for test_file in test_files:

    print(f"\nRunning {test_file}...")
    print("--------------------------------")

    result = subprocess.run(
        [sys.executable, str(test_folder / test_file)],
        cwd=test_folder.parent
    )

    if result.returncode == 0:
        print(f"PASS: {test_file}")
        passed += 1
    else:
        print(f"FAIL: {test_file}")
        failed += 1

print("\n================================")
print("          TEST SUMMARY")
print("================================")

print(f"Total test files: {len(test_files)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print("\nALL TEST FILES PASSED!")
else:
    print("\nSOME TEST FILES FAILED!")
