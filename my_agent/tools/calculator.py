import math


def calculator(operation: str, a: float, b: float) -> str:
    """Performs arithmetic on numbers. Use this for ALL numeric calculations.

    Never compute math yourself — always call this tool instead.

    Args:
        operation: The operation to perform. One of:
            "add"        — a + b
            "subtract"   — a - b
            "multiply"   — a * b
            "divide"     — a / b
            "power"      — a raised to the power of b (e.g. 2^47: a=2, b=47)
            "sqrt"       — square root of a (pass b=0)
            "modulo"     — a % b
        a: The first number (or the only number for "sqrt").
        b: The second number (pass 0 when using "sqrt").

    Returns:
        The numeric result as a string, or an error message.
    """
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero."
        result = a / b
    elif operation == "power":
        result = a ** b
    elif operation == "sqrt":
        if a < 0:
            return "Error: square root of a negative number"
        result = math.sqrt(a)
    elif operation == "modulo":
        if b == 0:
            return "Error: Division by zero."
        result = a % b
    else:
        return f"Error: Unknown operation '{operation}'. Use add, subtract, multiply, divide, power, sqrt, or modulo."
    return str(result)
