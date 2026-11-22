
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

from src.symbol_table import Symbol, SymbolTable


class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, program):
        for declaration in program.declarations:
            if isinstance(declaration, VariableDeclaration):
                self.check_variable_declaration(declaration)

            elif isinstance(declaration, Function):
                self.check_function(declaration)

        return True

    def check_variable_declaration(self, declaration):

        symbol = Symbol(
            declaration.name,
            declaration.var_type,
            "variable"
        )

        if not self.symbol_table.declare(symbol):
            raise SemanticError(
                f"Duplicate variable declaration: {declaration.name}"
            )

        if declaration.initializer is not None:
            self.check_expression(declaration.initializer)

    def check_function(self, function):

        symbol = Symbol(
            function.name,
            function.return_type,
            "function"
        )

        if not self.symbol_table.declare(symbol):
            raise SemanticError(
                f"Duplicate function declaration: {function.name}"
            )

        self.symbol_table.enter_scope()

        try:
            for parameter in function.parameters:
                self.check_variable_declaration(parameter)

            self.check_statement(function.body)

        finally:
            self.symbol_table.exit_scope()

    def check_statement(self, statement):

        if isinstance(statement, CompoundStatement):
            self.symbol_table.enter_scope()

            try:
                for item in statement.statements:
                    self.check_statement(item)
            finally:
                self.symbol_table.exit_scope()

        elif isinstance(statement, VariableDeclaration):
            self.check_variable_declaration(statement)

        elif isinstance(statement, ReturnStatement):
            if statement.expression is not None:
                self.check_expression(statement.expression)

        elif isinstance(statement, IfStatement):
            self.check_expression(statement.condition)
            self.check_statement(statement.then_branch)

            if statement.else_branch is not None:
                self.check_statement(statement.else_branch)

        elif isinstance(statement, WhileStatement):
            self.check_expression(statement.condition)
            self.check_statement(statement.body)

        elif isinstance(statement, ExpressionStatement):
            self.check_expression(statement.expression)

        elif isinstance(statement, EmptyStatement):
            pass

    def check_expression(self, expression):

        if isinstance(expression, Number):
            return

        elif isinstance(expression, Identifier):
            symbol = self.symbol_table.lookup(expression.name)

            if symbol is None:
                raise SemanticError(
                    f"Undeclared variable: {expression.name}"
                )

        elif isinstance(expression, BinaryExpression):
            self.check_expression(expression.left)
            self.check_expression(expression.right)

        elif isinstance(expression, UnaryExpression):
            self.check_expression(expression.operand)


def analyze(program):
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
