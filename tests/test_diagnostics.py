import sys
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.diagnostics import Diagnostic, DiagnosticEngine

print("DIAGNOSTICS TESTS")

d = Diagnostic("Invalid variable", 5, 3)
assert "line 5" in str(d)
print("Test 1: PASS - Error location")

engine = DiagnosticEngine()
engine.report_error("Undeclared variable", 5, 3)
assert engine.error_count() == 1
print("Test 2: PASS - Error reporting")

engine.report_warning("Unused variable", 6, 1)
assert engine.warning_count() == 1
print("Test 3: PASS - Warning reporting")

assert engine.has_errors()
print("Test 4: PASS - Error detection")

output = StringIO()
with redirect_stdout(output):
    engine.show_summary()

assert "Total errors: 1" in output.getvalue()
assert "Total warnings: 1" in output.getvalue()
print("Test 5: PASS - Diagnostic summary")

print("\nAll diagnostic tests completed!")
