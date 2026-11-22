
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from src.symbol_table import Symbol, SymbolTable


table = SymbolTable()

print("SYMBOL TABLE TESTS")

# Test 1: Declare a variable
symbol = Symbol("a", "int", "variable")
assert table.declare(symbol) == True
print("Test 1: PASS - Variable declared")


# Test 2: Find a declared variable
assert table.lookup("a") is not None
print("Test 2: PASS - Variable found")


# Test 3: Duplicate declaration
duplicate = Symbol("a", "int", "variable")
assert table.declare(duplicate) == False
print("Test 3: PASS - Duplicate rejected")


# Test 4: Undeclared variable
assert table.lookup("b") is None
print("Test 4: PASS - Undeclared variable not found")


# Test 5: Create a new scope
table.enter_scope()

symbol2 = Symbol("b", "int", "variable")
assert table.declare(symbol2) == True
print("Test 5: PASS - New scope created")


# Test 6: Exit scope
table.exit_scope()

assert table.lookup("b") is None
print("Test 6: PASS - Scope removed")


# Test 7: Outer scope still exists
assert table.lookup("a") is not None
print("Test 7: PASS - Outer variable preserved")


print("\nSymbol Table testing completed!")
