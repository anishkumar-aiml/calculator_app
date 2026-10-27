
import tkinter as tk
from tkinter import messagebox
import ast
import operator


# Safe mathematical operations
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}


def safe_calculate(expression):
    """Calculate a mathematical expression safely."""

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            return OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    result = evaluate(tree)

    if isinstance(result, float) and not (-float("inf") < result < float("inf")):
        raise ValueError("Invalid result")

    return result


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Calculator")
        self.root.geometry("360x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.expression = ""
        self.just_calculated = False

        self.display = tk.StringVar(value="0")

        # Display
        display_frame = tk.Frame(root, bg="#1e1e2e", padx=15, pady=20)
        display_frame.pack(fill="x")

        display_entry = tk.Entry(
            display_frame,
            textvariable=self.display,
            font=("Arial", 28),
            justify="right",
            state="readonly",
            readonlybackground="#313244",
            fg="#ffffff",
            bd=0,
            relief="flat"
        )
        display_entry.pack(fill="x", ipady=18)

        # Button layout
        buttons = [
            ["C", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
        ]

        button_frame = tk.Frame(root, bg="#1e1e2e", padx=10, pady=5)
        button_frame.pack(fill="both", expand=True)

        for row_index, row in enumerate(buttons):
            button_frame.grid_rowconfigure(row_index, weight=1)

            for col_index, label in enumerate(row):
                button_frame.grid_columnconfigure(col_index, weight=1)

                is_operator = label in ["÷", "×", "−", "+"]
                is_special = label in ["C", "⌫", "%", "±"]
                is_equal = label == "="

                if is_equal:
                    color = "#89b4fa"
                    text_color = "#11111b"
                elif is_operator:
                    color = "#45475a"
                    text_color = "#f9e2af"
                elif is_special:
                    color = "#585b70"
                    text_color = "#ffffff"
                else:
                    color = "#313244"
                    text_color = "#ffffff"

                button = tk.Button(
                    button_frame,
                    text=label,
                    font=("Arial", 17, "bold"),
                    bg=color,
                    fg=text_color,
                    activebackground="#a6adc8",
                    activeforeground="#11111b",
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    command=lambda value=label: self.on_button_click(value)
                )

                button.grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                    ipadx=3,
                    ipady=10
                )

        # Keyboard support
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Return>", lambda event: self.calculate())
        self.root.bind("<Escape>", lambda event: self.clear())
        self.root.bind("<BackSpace>", lambda event: self.backspace())

    def update_display(self):
        self.display.set(self.expression if self.expression else "0")

    def on_button_click(self, value):
        if value == "C":
            self.clear()
        elif value == "⌫":
            self.backspace()
        elif value == "=":
            self.calculate()
        elif value == "±":
            self.toggle_sign()
        elif value == "%":
            self.percentage()
        else:
            self.add_value(value)

    def add_value(self, value):
        if self.just_calculated:
            if value in ["+", "−", "×", "÷"]:
                self.just_calculated = False
            else:
                self.expression = ""
                self.just_calculated = False

        mapping = {
            "×": "*",
            "÷": "/",
            "−": "-",
        }

        value = mapping.get(value, value)

        if value == ".":
            # Prevent multiple decimal points in the current number.
            current_number = self.expression.replace("+", " ")
            for symbol in ["-", "*", "/", "%"]:
                current_number = current_number.replace(symbol, " ")

            last_number = current_number.split()[-1] if current_number.split() else ""

            if "." in last_number:
                return

            if not last_number:
                self.expression += "0"

        if value in ["+", "-", "*", "/", "%"]:
            if not self.expression:
                if value == "-":
                    self.expression = "-"
                    self.update_display()
                return

            if self.expression[-1] in ["+", "-", "*", "/", "%"]:
                self.expression = self.expression[:-1]

        self.expression += value
        self.update_display()

    def calculate(self):
        if not self.expression:
            return

        try:
            result = safe_calculate(self.expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.expression = str(result)
            self.display.set(self.expression)
            self.just_calculated = True

        except ZeroDivisionError:
            self.display.set("Cannot divide by zero")
            self.expression = ""
            self.just_calculated = True

        except (ValueError, SyntaxError, TypeError, OverflowError):
            self.display.set("Invalid expression")
            self.expression = ""
            self.just_calculated = True

    def clear(self):
        self.expression = ""
        self.just_calculated = False
        self.display.set("0")

    def backspace(self):
        if self.just_calculated:
            self.clear()
            return

        self.expression = self.expression[:-1]
        self.update_display()

    def toggle_sign(self):
        if not self.expression:
            self.expression = "-"
        elif self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression

        self.just_calculated = False
        self.update_display()

    def percentage(self):
        if not self.expression:
            return

        try:
            result = safe_calculate(self.expression) / 100
            self.expression = str(result)
            self.display.set(self.expression)
            self.just_calculated = True
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            self.display.set("Invalid expression")
            self.expression = ""
            self.just_calculated = True

    def on_key_press(self, event):
        char = event.char

        if char in "0123456789.":
            self.add_value(char)
        elif char == "+":
            self.add_value("+")
        elif char == "-":
            self.add_value("−")
        elif char == "*":
            self.add_value("×")
        elif char == "/":
            self.add_value("÷")


if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()

