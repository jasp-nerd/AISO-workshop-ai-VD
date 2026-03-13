def calculator(operation: str, a: float, b: float) -> str:
    """Performs basic arithmetic on two numbers.

    Use this tool for any arithmetic calculation instead of computing yourself.

    Args:
        operation: The operation to perform. One of: "add", "subtract",
            "multiply", "divide".
        a: The first number (left operand).
        b: The second number (right operand).

    Returns:
        The result as a string, or an error message if the operation is invalid
        or division by zero is attempted.
    """
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    elif operation == "multiply":
        return str(a * b)
    elif operation == "divide":
        if b == 0:
            return "Error: division by zero"
        return str(a / b)
    else:
        return f"Error: unknown operation '{operation}'. Use add, subtract, multiply, or divide."
