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

    if (
        isinstance(first, bool)
        or isinstance(second, bool)
        or not isinstance(first, int)
        or not isinstance(second, int)
    ):
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


def _strictly_equal(actual, expected):
    if type(actual) is not type(expected):
        return False

    if isinstance(actual, list):
        return (
            len(actual) == len(expected)
            and all(
                _strictly_equal(left, right)
                for left, right in zip(actual, expected)
            )
        )

    if isinstance(actual, dict):
        return (
            actual.keys() == expected.keys()
            and all(
                _strictly_equal(actual[key], expected[key])
                for key in actual
            )
        )

    return actual == expected


def validate_problem_result(problem, case, result):
    validator = problem.get("validator", "two_sum")

    if validator == "two_sum":
        if "values" not in case or "target" not in case:
            return {
                "passed": False,
                "feedback": (
                    "Two Sum test cases require values and target."
                )
            }

        return validate_two_sum_result(
            case["values"],
            case["target"],
            result
        )

    if validator == "exact":
        if "expected" not in case:
            return {
                "passed": False,
                "feedback": "Exact-match test cases require expected output."
            }

        passed = _strictly_equal(result, case["expected"])
        return {
            "passed": passed,
            "feedback": (
                "Returned value matches the expected output."
                if passed
                else "Returned value does not match the expected output."
            )
        }

    return {
        "passed": False,
        "feedback": f"Unsupported result validator: {validator}."
    }
