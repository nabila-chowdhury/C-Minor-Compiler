
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from src.lexer import tokenize


source = """
int main(void) {
    int a = 10;
    int b = 20;
    return a + b;
}
"""

tokens = tokenize(source, "demo.cm")

for token in tokens:
    print(token)
