def two_sum(values, target):
    seen = {}

    for index, value in enumerate(values):
        complement = target - value

        if complement in seen:
            return [seen[complement], index]

        seen[value] = index

    return None

def validate_two_sum_result(values, target, indices):
    """
    Independently verify whether returned indices
    satisfy the Two Sum problem requirements.
    """

    if indices is None:
        return {
            "passed": False,
            "feedback": "No solution was returned."
        }

    if not isinstance(indices, (list, tuple)) or len(indices) != 2:
        return {
            "passed": False,
            "feedback": "Exactly two indices must be returned."
        }

    first, second = indices

    if not isinstance(first, int) or not isinstance(second, int):
        return {
            "passed": False,
            "feedback": "Indices must be integers."
        }

    if first == second:
        return {
            "passed": False,
            "feedback": "The same element cannot be used twice."
        }

    if not (0 <= first < len(values)):
        return {
            "passed": False,
            "feedback": "First index is outside the array."
        }

    if not (0 <= second < len(values)):
        return {
            "passed": False,
            "feedback": "Second index is outside the array."
        }

    if values[first] + values[second] != target:
        return {
            "passed": False,
            "feedback": "Returned elements do not sum to the target."
        }

    return {
        "passed": True,
        "feedback": "Valid pair of distinct indices returned."
    }
