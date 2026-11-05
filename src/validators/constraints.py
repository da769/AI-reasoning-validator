def validate_constraint(
    condition: bool,
    message: str
) -> dict:

    return {
        "passed": condition,
        "message": message
    }
