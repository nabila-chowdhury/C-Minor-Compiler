class Diagnostic:
    def __init__(self, message, line=None, column=None, error_type="Error"):
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type

    def __str__(self):
        location = ""

        if self.line is not None:
            location = f" at line {self.line}"

            if self.column is not None:
                location += f", column {self.column}"

        return f"{self.error_type}{location}: {self.message}"


class DiagnosticEngine:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def report_error(self, message, line=None, column=None):
        diagnostic = Diagnostic(message, line, column, "Error")
        self.errors.append(diagnostic)
        print(diagnostic)

    def report_warning(self, message, line=None, column=None):
        diagnostic = Diagnostic(message, line, column, "Warning")
        self.warnings.append(diagnostic)
        print(diagnostic)

    def has_errors(self):
        return len(self.errors) > 0

    def error_count(self):
        return len(self.errors)

    def warning_count(self):
        return len(self.warnings)

    def show_summary(self):
        print("\n========== DIAGNOSTIC SUMMARY ==========")
        print(f"Total errors: {self.error_count()}")
        print(f"Total warnings: {self.warning_count()}")

        if self.has_errors():
            print("Compilation failed!")
        else:
            print("No errors found!")

        print("========================================")


def report_error(message, line=None, column=None):
    print(Diagnostic(message, line, column, "Error"))


def report_warning(message, line=None, column=None):
    print(Diagnostic(message, line, column, "Warning"))
