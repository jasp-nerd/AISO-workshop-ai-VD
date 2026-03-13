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
        a: The first number (or the only number for "sqrt").
        b: The second number (pass 0 when using "sqrt").

    Returns:
        The numeric result as a string, or an error message.
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
    elif operation == "power":
        return str(a ** b)
    elif operation == "sqrt":
        if a < 0:
            return "Error: square root of a negative number"
        return str(math.sqrt(a))
    else:
        return f"Error: unknown operation '{operation}'. Use add, subtract, multiply, divide, power, or sqrt."
