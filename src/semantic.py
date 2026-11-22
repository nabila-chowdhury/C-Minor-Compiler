
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
        self.current_function_return_type = None

    def analyze(self, program):

        self.symbol_table = SymbolTable()

        for declaration in program.declarations:

            if isinstance(declaration, VariableDeclaration):
                self.check_variable_declaration(declaration)

            elif isinstance(declaration, Function):
                self.check_function(declaration)

        return True

    def check_variable_declaration(self, declaration):

        if declaration.var_type != "int":
            raise SemanticError(
                f"Invalid variable type: {declaration.var_type}"
            )

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

            value_type = self.check_expression(
                declaration.initializer
            )

            if value_type != declaration.var_type:
                raise SemanticError(
                    f"Type mismatch in variable: {declaration.name}"
                )

    def check_function(self, function):

        if function.return_type not in ("int", "void"):
            raise SemanticError(
                f"Invalid function return type: {function.return_type}"
            )

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

        previous_return_type = self.current_function_return_type
        self.current_function_return_type = function.return_type

        try:

            for parameter in function.parameters:
                self.check_variable_declaration(parameter)

            if isinstance(function.body, CompoundStatement):

                for item in function.body.statements:
                    self.check_statement(item)

            else:
                self.check_statement(function.body)

        finally:
            self.current_function_return_type = previous_return_type
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

            if self.current_function_return_type == "void":

                if statement.expression is not None:
                    raise SemanticError(
                        "Void function cannot return a value"
                    )

            elif self.current_function_return_type == "int":

                if statement.expression is None:
                    raise SemanticError(
                        "Int function must return a value"
                    )

                return_type = self.check_expression(
                    statement.expression
                )

                if return_type != "int":
                    raise SemanticError(
                        "Return type mismatch"
                    )

        elif isinstance(statement, IfStatement):

            condition_type = self.check_expression(
                statement.condition
            )

            if condition_type != "int":
                raise SemanticError(
                    "Invalid if condition type"
                )

            self.check_statement(statement.then_branch)

            if statement.else_branch is not None:
                self.check_statement(statement.else_branch)

        elif isinstance(statement, WhileStatement):

            condition_type = self.check_expression(
                statement.condition
            )

            if condition_type != "int":
                raise SemanticError(
                    "Invalid while condition type"
                )

            self.check_statement(statement.body)

        elif isinstance(statement, ExpressionStatement):
            self.check_expression(statement.expression)

        elif isinstance(statement, EmptyStatement):
            pass

    def check_expression(self, expression):

        # Integer number
        if isinstance(expression, Number):
            return "int"

        # Variable checking
        elif isinstance(expression, Identifier):

            symbol = self.symbol_table.lookup(expression.name)

            if symbol is None:
                raise SemanticError(
                    f"Undeclared variable: {expression.name}"
                )

            if symbol.kind != "variable":
                raise SemanticError(
                    f"Function used as variable: {expression.name}"
                )

            return symbol.symbol_type

        # Binary expression checking
        elif isinstance(expression, BinaryExpression):

            operator = expression.operator

            # Assignment
            if operator == "=":

                if not isinstance(expression.left, Identifier):
                    raise SemanticError(
                        "Invalid assignment target"
                    )

                left_type = self.check_expression(
                    expression.left
                )

                right_type = self.check_expression(
                    expression.right
                )

                if left_type != right_type:
                    raise SemanticError(
                        "Assignment type mismatch"
                    )

                return left_type

            # Arithmetic operators
            elif operator in ("+", "-", "*", "/", "%"):

                left_type = self.check_expression(expression.left)
                right_type = self.check_expression(expression.right)

                if left_type != "int" or right_type != "int":
                    raise SemanticError(
                        "Invalid arithmetic operand type"
                    )

                return "int"

            # Comparison operators
            elif operator in ("<", ">", "<=", ">=", "==", "!="):

                left_type = self.check_expression(expression.left)
                right_type = self.check_expression(expression.right)

                if left_type != "int" or right_type != "int":
                    raise SemanticError(
                        "Invalid comparison operand type"
                    )

                return "int"

            # Logical operators
            elif operator in ("&&", "||"):

                left_type = self.check_expression(expression.left)
                right_type = self.check_expression(expression.right)

                if left_type != "int" or right_type != "int":
                    raise SemanticError(
                        "Invalid logical operand type"
                    )

                return "int"

            else:
                raise SemanticError(
                    f"Unsupported binary operator: {operator}"
                )

        # Unary expression checking
        elif isinstance(expression, UnaryExpression):

            operand_type = self.check_expression(
                expression.operand
            )

            if operand_type != "int":
                raise SemanticError(
                    "Invalid unary operand type"
                )

            if expression.operator not in ("!", "-", "+"):
                raise SemanticError(
                    f"Unsupported unary operator: {expression.operator}"
                )

            return "int"

        raise SemanticError(
            "Unsupported expression"
        )


def analyze(program):
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)
