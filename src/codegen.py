
import re


class CodeGenerator:
    def __init__(self):
        self.output = []
        self.register_count = 0
        self.variables = {}

    def new_register(self):
        self.register_count += 1
        return f"%r{self.register_count}"

    def generate(self, ir_instructions):
        self.output = []
        self.register_count = 0
        self.variables = {}

        instructions = []

        for instruction in ir_instructions:
            instruction = instruction.strip()

            if instruction.startswith("function "):
                continue

            if instruction.startswith("end function"):
                continue

            if instruction:
                instructions.append(instruction)

        # Collect variables and temporary values
        for instruction in instructions:
            if " = " in instruction and not instruction.startswith("ifFalse"):
                left = instruction.split(" = ", 1)[0].strip()

                if re.fullmatch(r"[A-Za-z_]\w*", left):
                    if left not in self.variables:
                        self.variables[left] = None

        # Find labels
        labels = {}

        for index, instruction in enumerate(instructions):
            if instruction.endswith(":"):
                label = instruction[:-1]
                labels[label] = index

        self.output.append("define i32 @main() {")
        self.output.append("entry:")

        # Allocate memory for all variables
        for name in self.variables:
            register = self.new_register()
            self.variables[name] = register
            self.output.append(f"  {register} = alloca i32")

        if instructions:
            self.output.append("  br label %bb0")
        else:
            self.output.append("  ret i32 0")

        # Generate LLVM basic blocks
        for index, instruction in enumerate(instructions):
            self.output.append(f"bb{index}:")

            self.generate_instruction(
                instruction,
                index,
                instructions,
                labels
            )

        self.output.append("}")

        return "\n".join(self.output)

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

        register = self.variables[name]

        self.output.append(
            f"  store i32 {value}, ptr {register}"
        )

    def generate_instruction(self, instruction, index, instructions, labels):

        next_block = f"bb{index + 1}"

        # Label
        if instruction.endswith(":"):
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
            value = instruction[7:].strip()
            result = self.get_value(value)

            self.output.append(f"  ret i32 {result}")
            return

        # Unconditional jump
        if instruction.startswith("goto "):
            label = instruction[5:].strip()

            if label not in labels:
                raise ValueError(f"Unknown label: {label}")

            target = f"bb{labels[label]}"
            self.output.append(f"  br label %{target}")
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

            target = f"bb{labels[label]}"

            self.output.append(
                f"  br i1 {comparison}, label %{next_block}, label %{target}"
            )
            return

        # Assignment
        if " = " in instruction:
            left, right = instruction.split(" = ", 1)

            left = left.strip()
            right = right.strip()

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

                arithmetic_operations = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "/": "sdiv"
                }

                comparison_operations = {
                    "==": "eq",
                    "!=": "ne",
                    "<": "slt",
                    ">": "sgt",
                    "<=": "sle",
                    ">=": "sge"
                }

                result = self.new_register()

                if operator in arithmetic_operations:
                    operation = arithmetic_operations[operator]

                    self.output.append(
                        f"  {result} = {operation} i32 "
                        f"{first_value}, {second_value}"
                    )

                    self.store_variable(left, result)

                elif operator in comparison_operations:
                    operation = comparison_operations[operator]

                    self.output.append(
                        f"  {result} = icmp {operation} i32 "
                        f"{first_value}, {second_value}"
                    )

                    extended = self.new_register()

                    self.output.append(
                        f"  {extended} = zext i1 {result} to i32"
                    )

                    self.store_variable(left, extended)

            else:
                # Simple assignment
                value = self.get_value(right)
                self.store_variable(left, value)

        # Move to next basic block
        if index + 1 < len(instructions):
            self.output.append(f"  br label %{next_block}")
        else:
            self.output.append("  ret i32 0")


def generate_code(ir_instructions):
    generator = CodeGenerator()
    return generator.generate(ir_instructions)
