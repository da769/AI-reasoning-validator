from src.validators.code_execution import (
    evaluate_python_submission
)


TEST_CASES = [
    {
        "test_id": "case_001",
        "values": [2, 7, 11, 15],
        "target": 9
    },
    {
        "test_id": "case_002",
        "values": [3, 3],
        "target": 6
    },
    {
        "test_id": "case_003",
        "values": [-3, 4, 7],
        "target": 1
    },
    {
        "test_id": "case_004",
        "values": [1, 2, 3, 4],
        "target": 7
    }
]


CORRECT_CODE = """
def two_sum(values, target):

    seen = {}

    for index, value in enumerate(values):

        complement = target - value

        if complement in seen:
            return [seen[complement], index]

        seen[value] = index

    return None
"""


INCORRECT_CODE = """
def two_sum(values, target):

    return [0, 1]
"""


def test_correct_submission():

    result = evaluate_python_submission(
        CORRECT_CODE,
        TEST_CASES
    )

    assert result["status"] == "COMPLETED"

    assert result["passed"] is True

    assert result["passed_cases"] == 4


def test_incorrect_submission():

    result = evaluate_python_submission(
        INCORRECT_CODE,
        TEST_CASES
    )

    assert result["status"] == "COMPLETED"

    assert result["passed"] is False


def test_missing_function():

    code = """
def add(a, b):
    return a + b
"""

    result = evaluate_python_submission(
        code,
        TEST_CASES
    )

    assert result["status"] == "EXECUTION_ERROR"


def test_syntax_error():

    code = """
def two_sum(values, target
    return [0, 1]
"""

    result = evaluate_python_submission(
        code,
        TEST_CASES
    )

    assert result["status"] == "SYNTAX_ERROR"


def test_security_screening():

    code = """
def two_sum(values, target):
    return eval("2 + 2")
"""

    result = evaluate_python_submission(
        code,
        TEST_CASES
    )

    assert result["status"] == "REJECTED"