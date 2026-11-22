
import re


class CodeGenerator:

    def __init__(self):
        self.output = []
        self.register_count = 0
        self.variables = {}
        self.arguments = []
        self.functions = {}

    def new_register(self):
        self.register_count += 1
        return f"%r{self.register_count}"

    def get_value(self, value):

        value = value.strip()

        if re.fullmatch(r"-?\d+", value):
            return value

        if value not in self.variables:
            raise ValueError(f"Unknown variable: {value}")

        register = self.variables[value]
        loaded = self.new_register()

        self.output.append(
            f"  {loaded} = load i32, ptr {register}"
        )

        return loaded

    def store_variable(self, name, value):

        if name not in self.variables:
            raise ValueError(f"Unknown variable: {name}")

        self.output.append(
            f"  store i32 {value}, ptr {self.variables[name]}"
        )

    def generate(self, ir_instructions):

        self.output = []
        self.register_count = 0
        self.functions = {}

        current_function = None

        for instruction in ir_instructions:

            instruction = instruction.strip()

            if instruction.startswith("function "):

                match = re.fullmatch(
                    r"function\s+(\w+)\((.*?)\):",
                    instruction
                )

                if not match:
                    raise ValueError(
                        f"Invalid function declaration: {instruction}"
                    )

                name, parameters = match.groups()

                parameter_list = [
                    item.strip()
                    for item in parameters.split(",")
                    if item.strip()
                ]

                self.functions[name] = {
                    "parameters": parameter_list,
                    "instructions": []
                }

                current_function = name

            elif instruction.startswith("end function"):
                current_function = None

            elif current_function is not None:

                self.functions[current_function]["instructions"].append(
                    instruction
                )

        if "main" not in self.functions:
            raise ValueError("Program must contain main function")

        for name, function in self.functions.items():
            self.generate_function(name, function)

        return "\n".join(self.output)

    def generate_function(self, name, function):

        instructions = function["instructions"]
        parameters = function["parameters"]

        self.variables = {}
        self.arguments = []

        # Collect parameters and local variables
        for parameter in parameters:
            self.variables[parameter] = None

        for instruction in instructions:

            if " = " in instruction and not instruction.startswith("ifFalse"):

                left = instruction.split(" = ", 1)[0].strip()

                if re.fullmatch(r"[A-Za-z_]\w*", left):
                    self.variables[left] = None

        # Find labels
        labels = {}

        for index, instruction in enumerate(instructions):

            if instruction.endswith(":"):
                labels[instruction[:-1]] = index

        # Function definition
        llvm_arguments = []

        for index, parameter in enumerate(parameters):
            llvm_arguments.append(f"i32 %arg{index}")

        argument_text = ", ".join(llvm_arguments)

        self.output.append(
            f"define i32 @{name}({argument_text}) {{"
        )

        self.output.append("entry:")

        # Allocate variables
        for variable in self.variables:

            register = self.new_register()
            self.variables[variable] = register

            self.output.append(
                f"  {register} = alloca i32"
            )

        # Store parameters
        for index, parameter in enumerate(parameters):

            self.output.append(
                f"  store i32 %arg{index}, "
                f"ptr {self.variables[parameter]}"
            )

        if instructions:
            self.output.append("  br label %bb0")
        else:
            self.output.append("  ret i32 0")

        # Generate basic blocks
        for index, instruction in enumerate(instructions):

            self.output.append(f"bb{index}:")

            self.generate_instruction(
                instruction,
                index,
                instructions,
                labels
            )

        self.output.append("}")

    def generate_instruction(
        self,
        instruction,
        index,
        instructions,
        labels
    ):

        next_block = f"bb{index + 1}"

        # Label
        if instruction.endswith(":"):

            if index + 1 < len(instructions):
                self.output.append(f"  br label %{next_block}")
            else:
                self.output.append("  ret i32 0")

            return

        # Function parameters
        if instruction.startswith("param "):

            value = instruction[6:].strip()
            self.arguments.append(self.get_value(value))

            if index + 1 < len(instructions):
                self.output.append(f"  br label %{next_block}")
            else:
                self.output.append("  ret i32 0")

            return

        # Return
        if instruction == "return":
            self.output.append("  ret i32 0")
            return

        if instruction.startswith("return "):

            value = self.get_value(instruction[7:].strip())

            self.output.append(
                f"  ret i32 {value}"
            )
            return

        # Unconditional jump
        if instruction.startswith("goto "):

            label = instruction[5:].strip()

            if label not in labels:
                raise ValueError(f"Unknown label: {label}")

            self.output.append(
                f"  br label %bb{labels[label]}"
            )
            return

        # Conditional jump
        if instruction.startswith("ifFalse "):

            match = re.fullmatch(
                r"ifFalse\s+(.+?)\s+goto\s+(\w+)",
                instruction
            )

            if not match:
                raise ValueError("Invalid conditional instruction")

            condition, label = match.groups()

            if label not in labels:
                raise ValueError(f"Unknown label: {label}")

            value = self.get_value(condition)
            comparison = self.new_register()

            self.output.append(
                f"  {comparison} = icmp ne i32 {value}, 0"
            )

            self.output.append(
                f"  br i1 {comparison}, "
                f"label %{next_block}, "
                f"label %bb{labels[label]}"
            )

            return

        # Assignment
        if " = " in instruction:

            left, right = instruction.split(" = ", 1)

            left = left.strip()
            right = right.strip()

            # Function call
            call_match = re.fullmatch(
                r"call\s+(\w+),\s*(\d+)",
                right
            )

            if call_match:

                function_name, count = call_match.groups()
                count = int(count)

                if function_name not in self.functions:
                    raise ValueError(
                        f"Unknown function: {function_name}"
                    )

                expected = len(
                    self.functions[function_name]["parameters"]
                )

                if count != expected or count != len(self.arguments):
                    raise ValueError(
                        "Function argument count mismatch"
                    )

                arguments = ", ".join(
                    f"i32 {argument}"
                    for argument in self.arguments
                )

                result = self.new_register()

                self.output.append(
                    f"  {result} = call i32 "
                    f"@{function_name}({arguments})"
                )

                self.arguments = []
                self.store_variable(left, result)

            else:

                # Unary operation
                unary = re.fullmatch(
                    r"([!+\-])([A-Za-z_]\w*|-?\d+)",
                    right
                )

                if unary:

                    operator, operand = unary.groups()
                    value = self.get_value(operand)
                    result = self.new_register()

                    if operator == "-":

                        self.output.append(
                            f"  {result} = sub i32 0, {value}"
                        )

                    elif operator == "!":

                        comparison = self.new_register()

                        self.output.append(
                            f"  {comparison} = icmp eq i32 {value}, 0"
                        )

                        self.output.append(
                            f"  {result} = zext i1 {comparison} to i32"
                        )

                    else:
                        result = value

                    self.store_variable(left, result)

                else:

                    # Binary operation
                    binary = re.fullmatch(
                        r"([A-Za-z_]\w*|-?\d+)\s*"
                        r"(==|!=|<=|>=|<|>|[+\-*/])\s*"
                        r"([A-Za-z_]\w*|-?\d+)",
                        right
                    )

                    if binary:

                        first, operator, second = binary.groups()

                        first_value = self.get_value(first)
                        second_value = self.get_value(second)

                        arithmetic = {
                            "+": "add",
                            "-": "sub",
                            "*": "mul",
                            "/": "sdiv"
                        }

                        comparisons = {
                            "==": "eq",
                            "!=": "ne",
                            "<": "slt",
                            ">": "sgt",
                            "<=": "sle",
                            ">=": "sge"
                        }

                        result = self.new_register()

                        if operator in arithmetic:

                            self.output.append(
                                f"  {result} = {arithmetic[operator]} "
                                f"i32 {first_value}, {second_value}"
                            )

                            self.store_variable(left, result)

                        elif operator in comparisons:

                            self.output.append(
                                f"  {result} = icmp {comparisons[operator]} "
                                f"i32 {first_value}, {second_value}"
                            )

                            extended = self.new_register()

                            self.output.append(
                                f"  {extended} = zext i1 {result} to i32"
                            )

                            self.store_variable(left, extended)

                    else:

                        value = self.get_value(right)
                        self.store_variable(left, value)

        if index + 1 < len(instructions):
            self.output.append(f"  br label %{next_block}")
        else:
            self.output.append("  ret i32 0")


def generate_code(ir_instructions):
    generator = CodeGenerator()
    return generator.generate(ir_instructions)
