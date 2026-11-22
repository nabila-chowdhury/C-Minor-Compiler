
from dataclasses import dataclass
from typing import Optional


@dataclass
class Program:
    declarations: list


@dataclass
class Function:
    return_type: str
    name: str
    parameters: list
    body: object


@dataclass
class VariableDeclaration:
    var_type: str
    name: str
    initializer: Optional[object] = None


@dataclass
class CompoundStatement:
    statements: list


@dataclass
class ReturnStatement:
    expression: Optional[object] = None


@dataclass
class IfStatement:
    condition: object
    then_branch: object
    else_branch: Optional[object] = None


@dataclass
class WhileStatement:
    condition: object
    body: object


@dataclass
class BinaryExpression:
    left: object
    operator: str
    right: object


@dataclass
class UnaryExpression:
    operator: str
    operand: object


@dataclass
class Number:
    value: int


@dataclass
class Identifier:
    name: str


@dataclass
class ExpressionStatement:
    expression: object


@dataclass
class EmptyStatement:
    pass


@dataclass
class FunctionCall:
    name: str
    arguments: list
