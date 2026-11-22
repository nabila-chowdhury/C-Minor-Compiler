
from dataclasses import dataclass


KEYWORDS = {
    "int", "void", "if", "else", "while",
    "for", "break", "continue", "return"
}

OPERATORS = [
    "==", "!=", "<=", ">=", "&&", "||",
    "+", "-", "*", "/", "%", "<", ">",
    "!", "="
]

SEPARATORS = {
    "(", ")", "{", "}", ";", ","
}

UNSUPPORTED_OPERATORS = {
    "++", "--", "+=", "-=", "*=", "/=",
    "%=", "<<", ">>", "&=", "|=", "^=",
    "->"
}

MAX_INT = 2147483647


@dataclass
class Token:
    type: str
    value: str
    path: str
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.type}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )


class LexError(Exception):
    def __init__(self, message, path, line, column, code="LEXICAL_ERROR"):
        self.code = code
        self.path = path
        self.line = line
        self.column = column

        super().__init__(
            f"{path}:{line}:{column}: {code}: {message}"
        )


class Lexer:

    def __init__(self, source, path="<input>"):
        self.source = source
        self.path = path
        self.pos = 0
        self.line = 1
        self.column = 1
        self.line_has_item = False

        self.tokens = []

    def current(self):
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek(self, offset=1):
        index = self.pos + offset

        if index >= len(self.source):
            return None

        return self.source[index]

    def advance(self):
        char = self.current()

        if char is None:
            return None

        if char == "\r" and self.peek() == "\n":
            self.pos += 2
            self.line += 1
            self.column = 1
            self.line_has_item = False
            return "\n"

        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
            self.line_has_item = False
        else:
            self.column += 1

        return char

    def add_token(self, token_type, value, line, column):
        self.tokens.append(
            Token(
                token_type,
                value,
                self.path,
                line,
                column
            )
        )

    def error(self, message, code="LEXICAL_ERROR"):
        raise LexError(
            message,
            self.path,
            self.line,
            self.column,
            code
        )

    def is_letter(self, char):
        return char is not None and (
            "a" <= char <= "z" or
            "A" <= char <= "Z"
        )

    def is_digit(self, char):
        return char is not None and "0" <= char <= "9"

    def is_identifier_char(self, char):
        return (
            self.is_letter(char) or
            self.is_digit(char) or
            char == "_"
        )

    def skip_whitespace(self):
        while self.current() is not None:
            char = self.current()

            if char in " \t\v\f":
                self.advance()

            elif char == "\n":
                self.advance()

            elif char == "\r" and self.peek() == "\n":
                self.advance()

            else:
                break

    def skip_line_comment(self):
        while self.current() is not None:
            if self.current() in "\r\n":
                break

            self.advance()

    def skip_block_comment(self):
        start_line = self.line
        start_column = self.column

        self.advance()
        self.advance()

        while self.current() is not None:

            if self.current() == "*" and self.peek() == "/":
                self.advance()
                self.advance()
                return

            self.advance()

        raise LexError(
            "Unterminated block comment",
            self.path,
            start_line,
            start_column
        )

    def read_identifier(self):

        start = self.pos
        line = self.line
        column = self.column

        self.advance()

        while self.is_identifier_char(self.current()):
            self.advance()

        value = self.source[start:self.pos]

        if value in KEYWORDS:
            token_type = "KEYWORD"

        else:
            token_type = "IDENTIFIER"

        self.add_token(token_type, value, line, column)

    def read_number(self):

        start = self.pos
        line = self.line
        column = self.column

        while self.is_digit(self.current()):
            self.advance()

        # Consume attached letters, digits and dots
        # so malformed literals cannot become valid
        # adjacent tokens.

        if (
            self.is_letter(self.current()) or
            self.current() == "_" or
            self.current() == "."
        ):

            while (
                self.is_identifier_char(self.current()) or
                self.current() == "."
            ):
                self.advance()

            self.error(
                "Unsupported or malformed integer literal",
                "UNSUPPORTED_FEATURE"
            )

        value = self.source[start:self.pos]

        if len(value) > 1 and value.startswith("0"):
            self.error(
                "Leading-zero integer literals are unsupported",
                "UNSUPPORTED_FEATURE"
            )

        number = int(value)

        if number > MAX_INT:
            self.error(
                "Integer literal exceeds 2147483647",
                "UNSUPPORTED_FEATURE"
            )

        self.add_token("INTEGER", value, line, column)

    def read_operator(self):

        line = self.line
        column = self.column

        two_chars = (
            (self.current() or "") +
            (self.peek() or "")
        )

        if two_chars in UNSUPPORTED_OPERATORS:
            self.error(
                f"Unsupported operator: {two_chars}",
                "UNSUPPORTED_OPERATOR"
            )

        for operator in OPERATORS:
            if self.source.startswith(operator, self.pos):
                for _ in operator:
                    self.advance()

                self.add_token(
                    "OPERATOR",
                    operator,
                    line,
                    column
                )
                return

        self.error("Unknown operator or character")

    def tokenize(self):

        while self.current() is not None:

            self.skip_whitespace()

            char = self.current()

            if char is None:
                break

            # Comments
            if char == "/" and self.peek() == "/":
                self.advance()
                self.advance()
                self.skip_line_comment()
                continue

            if char == "/" and self.peek() == "*":
                self.skip_block_comment()
                continue

            line = self.line
            column = self.column

            # Line splicing is not supported
            if char == "\\" and self.peek() in ("\n", "\r"):
                self.error(
                    "Backslash-newline splicing is unsupported",
                    "UNSUPPORTED_LINE_SPLICING"
                )

            # Preprocessor directives
            if char == "#" or (
                char == "%" and self.peek() == ":"
            ):

                if not self.line_has_item:
                    self.error(
                        "Preprocessing directives are unsupported",
                        "UNSUPPORTED_PREPROCESSING_DIRECTIVE"
                    )

                self.error(
                    "Unexpected preprocessing character"
                )

            # Non-ASCII characters
            if ord(char) > 127:
                self.error("Non-ASCII character is unsupported")

            # Identifier
            if self.is_letter(char) or char == "_":
                self.read_identifier()
                self.line_has_item = True
                continue

            # Integer
            if self.is_digit(char):
                self.read_number()
                self.line_has_item = True
                continue

            # Separators
            if char in SEPARATORS:
                self.advance()

                self.add_token(
                    "SEPARATOR",
                    char,
                    line,
                    column
                )

                self.line_has_item = True
                continue

            # String and character literals
            if char in ('"', "'"):
                self.error(
                    "String and character literals are unsupported",
                    "UNSUPPORTED_FEATURE"
                )

            # Operators
            if char in "+-*/%<>=!&|?^":
                self.read_operator()
                self.line_has_item = True
                continue

            self.error(f"Unknown character: {char}")

        return self.tokens


def tokenize(source, path="<input>"):
    lexer = Lexer(source, path)
    return lexer.tokenize()
