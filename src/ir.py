
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


class IRGenerator:

    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, program):
        for declaration in program.declarations:

            if isinstance(declaration, Function):
                self.emit(f"function {declaration.name}:")
                self.generate_statement(declaration.body)
                self.emit(f"end function {declaration.name}")

            elif isinstance(declaration, VariableDeclaration):
                self.generate_statement(declaration)

        return self.instructions

    def generate_statement(self, statement):

        if isinstance(statement, CompoundStatement):

            for item in statement.statements:
                self.generate_statement(item)

        elif isinstance(statement, VariableDeclaration):

            if statement.initializer is not None:
                value = self.generate_expression(
                    statement.initializer
                )
                self.emit(f"{statement.name} = {value}")

        elif isinstance(statement, ReturnStatement):

            if statement.expression is None:
                self.emit("return")
            else:
                value = self.generate_expression(
                    statement.expression
                )
                self.emit(f"return {value}")

        elif isinstance(statement, ExpressionStatement):

            self.generate_expression(statement.expression)

        elif isinstance(statement, IfStatement):

            condition = self.generate_expression(
                statement.condition
            )

            else_label = self.new_label()
            end_label = self.new_label()

            self.emit(f"ifFalse {condition} goto {else_label}")

            self.generate_statement(statement.then_branch)

            if statement.else_branch is not None:
                self.emit(f"goto {end_label}")

            self.emit(f"{else_label}:")

            if statement.else_branch is not None:
                self.generate_statement(statement.else_branch)
                self.emit(f"{end_label}:")

        elif isinstance(statement, WhileStatement):

            start_label = self.new_label()
            end_label = self.new_label()

            self.emit(f"{start_label}:")

            condition = self.generate_expression(
                statement.condition
            )

            self.emit(f"ifFalse {condition} goto {end_label}")

            self.generate_statement(statement.body)

            self.emit(f"goto {start_label}")
            self.emit(f"{end_label}:")

        elif isinstance(statement, EmptyStatement):
            pass

    def generate_expression(self, expression):

        if isinstance(expression, Number):
            return str(expression.value)

        if isinstance(expression, Identifier):
            return expression.name

        if isinstance(expression, UnaryExpression):

            operand = self.generate_expression(
                expression.operand
            )

            temp = self.new_temp()

            self.emit(
                f"{temp} = {expression.operator}{operand}"
            )

            return temp

        if isinstance(expression, BinaryExpression):

            left = self.generate_expression(expression.left)
            right = self.generate_expression(expression.right)

            if expression.operator == "=":
                self.emit(f"{left} = {right}")
                return left

            temp = self.new_temp()

            self.emit(
                f"{temp} = {left} {expression.operator} {right}"
            )

            return temp

        return ""


def generate_ir(program):
    generator = IRGenerator()
    return generator.generate(program)
