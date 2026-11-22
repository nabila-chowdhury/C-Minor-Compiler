
from src.ast_nodes import (
    Program,
    Function,
    VariableDeclaration,
    CompoundStatement,
    ReturnStatement,
    IfStatement,
    WhileStatement,
    BinaryExpression,
    UnaryExpression,
    Number,
    Identifier,
    ExpressionStatement,
    EmptyStatement
)


class ParseError(Exception):
    pass


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def check(self, value):
        token = self.current()
        return token is not None and token.value == value

    def match(self, value):
        if self.check(value):
            self.position += 1
            return True
        return False

    def expect(self, value):
        if not self.match(value):
            token = self.current()
            if token:
                raise ParseError(
                    f"Expected '{value}' at line {token.line}, "
                    f"column {token.column}"
                )
            raise ParseError(f"Expected '{value}' at end of input")

    def expect_type(self, token_type):
        token = self.current()

        if token is None or token.type != token_type:
            raise ParseError(f"Expected {token_type}")

        self.position += 1
        return token

    def parse_type(self):
        if self.check("int") or self.check("void"):
            return self.tokens[self.position].value

        raise ParseError("Expected a type")

    def parse_program(self):
        declarations = []

        while self.current() is not None:
            declarations.append(self.parse_declaration())

        return Program(declarations)

    def parse_declaration(self):
        var_type = self.parse_type()
        self.position += 1

        name = self.expect_type("IDENTIFIER").value

        if self.match("("):
            parameters = self.parse_parameters()
            self.expect(")")
            body = self.parse_compound_statement()

            return Function(
                var_type, name, parameters, body
            )

        initializer = None

        if self.match("="):
            initializer = self.parse_expression()

        self.expect(";")

        return VariableDeclaration(
            var_type, name, initializer
        )

    def parse_parameters(self):
        parameters = []

        if self.check("void"):
            self.position += 1
            return parameters

        if self.check(")"):
            return parameters

        while True:
            param_type = self.parse_type()
            self.position += 1

            param_name = self.expect_type("IDENTIFIER").value

            parameters.append(
                VariableDeclaration(param_type, param_name)
            )

            if not self.match(","):
                break

        return parameters

    def parse_compound_statement(self):
        self.expect("{")
        statements = []

        while not self.check("}"):
            if self.current() is None:
                raise ParseError("Missing closing '}'")

            if self.check("int"):
                statements.append(self.parse_local_declaration())
            else:
                statements.append(self.parse_statement())

        self.expect("}")

        return CompoundStatement(statements)

    def parse_local_declaration(self):
        var_type = self.parse_type()
        self.position += 1

        name = self.expect_type("IDENTIFIER").value

        initializer = None

        if self.match("="):
            initializer = self.parse_expression()

        self.expect(";")

        return VariableDeclaration(
            var_type, name, initializer
        )

    def parse_statement(self):

        if self.check("{"):
            return self.parse_compound_statement()

        if self.match("if"):
            self.expect("(")
            condition = self.parse_expression()
            self.expect(")")

            then_branch = self.parse_statement()
            else_branch = None

            if self.match("else"):
                else_branch = self.parse_statement()

            return IfStatement(
                condition, then_branch, else_branch
            )

        if self.match("while"):
            self.expect("(")
            condition = self.parse_expression()
            self.expect(")")

            body = self.parse_statement()

            return WhileStatement(condition, body)

        if self.match("return"):
            expression = None

            if not self.check(";"):
                expression = self.parse_expression()

            self.expect(";")

            return ReturnStatement(expression)

        if self.match(";"):
            return EmptyStatement()

        expression = self.parse_expression()
        self.expect(";")

        return ExpressionStatement(expression)

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()

        if self.match("="):
            right = self.parse_assignment()
            return BinaryExpression(left, "=", right)

        return left

    def parse_logical_or(self):
        left = self.parse_logical_and()

        while self.match("||"):
            right = self.parse_logical_and()
            left = BinaryExpression(left, "||", right)

        return left

    def parse_logical_and(self):
        left = self.parse_equality()

        while self.match("&&"):
            right = self.parse_equality()
            left = BinaryExpression(left, "&&", right)

        return left

    def parse_equality(self):
        left = self.parse_relational()

        while self.check("==") or self.check("!="):
            operator = self.current().value
            self.position += 1

            right = self.parse_relational()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_relational(self):
        left = self.parse_additive()

        while (
            self.check("<") or self.check(">") or
            self.check("<=") or self.check(">=")
        ):
            operator = self.current().value
            self.position += 1

            right = self.parse_additive()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_additive(self):
        left = self.parse_multiplicative()

        while self.check("+") or self.check("-"):
            operator = self.current().value
            self.position += 1

            right = self.parse_multiplicative()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_multiplicative(self):
        left = self.parse_unary()

        while (
            self.check("*") or self.check("/") or
            self.check("%")
        ):
            operator = self.current().value
            self.position += 1

            right = self.parse_unary()
            left = BinaryExpression(left, operator, right)

        return left

    def parse_unary(self):
        if self.check("!") or self.check("-") or self.check("+"):
            operator = self.current().value
            self.position += 1

            operand = self.parse_unary()

            return UnaryExpression(operator, operand)

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if token is None:
            raise ParseError("Unexpected end of input")

        if token.type == "INTEGER":
            self.position += 1
            return Number(int(token.value))

        if token.type == "IDENTIFIER":
            self.position += 1
            return Identifier(token.value)

        if self.match("("):
            expression = self.parse_expression()
            self.expect(")")
            return expression

        raise ParseError(
            f"Unexpected token '{token.value}' "
            f"at line {token.line}, column {token.column}"
        )


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse_program()
