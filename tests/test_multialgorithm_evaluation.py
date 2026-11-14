from src.evaluator import evaluate_response
from src.validators.algorithm import (
    validate_problem_result,
    validate_two_sum_result
)


def test_two_sum_validation_rejects_boolean_indices():
    result = validate_two_sum_result([1, 2], 3, [False, 1])

    assert result["passed"] is False


def test_exact_output_validation_preserves_json_types():
    problem = {"validator": "exact"}

    result = validate_problem_result(
        problem,
        {"expected": True},
        1
    )

    assert result["passed"] is False


def test_reasoning_rubric_accepts_paraphrased_algorithm_explanation():
    problem = {
        "reasoning_rubric": {
            "criteria": [
                {
                    "name": "Hash map",
                    "concepts": ["hash_map"],
                    "maximum": 30
                },
                {
                    "name": "Distinct positions",
                    "concepts": ["distinct_indices"],
                    "maximum": 30
                },
                {
                    "name": "Linear average time",
                    "concepts": ["linear_average_time"],
                    "maximum": 40
                }
            ]
        }
    }

    result = evaluate_response(
        {
            "answer": (
                "Keep a mapping from values to their positions. "
                "The current position is different from the earlier "
                "position. The expected work grows linearly with input size."
            )
        },
        problem
    )

    assert result["reasoning_score"] == 100


def test_binary_search_problem_runs_and_validates_claims():
    problem = {
        "id": "binary-search",
        "title": "Binary Search",
        "function_name": "binary_search",
        "validator": "exact",
        "reasoning_rubric": {
            "criteria": [
                {
                    "name": "Search strategy",
                    "concepts": ["binary_search"],
                    "maximum": 100
                }
            ]
        },
        "validation_cases": [
            {
                "test_id": "first",
                "args": [[1, 3, 5, 7], 5],
                "expected": 2
            },
            {
                "test_id": "missing",
                "args": [[1, 3, 5, 7], 2],
                "expected": -1
            }
        ]
    }
    response = {
        "answer": {
            "algorithm": "Binary search",
            "explanation": (
                "Compare the middle item and halve the remaining "
                "sorted search range each step."
            ),
            "complexity": "O(log n)"
        },
        "candidate_results": [
            {"test_id": "first", "result": 2},
            {"test_id": "missing", "result": -1}
        ]
    }
    source_code = """
def binary_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1
"""

    result = evaluate_response(response, problem, source_code)

    assert result["validation_score"] == 100
    assert result["execution_score"] == 100
    assert result["reasoning_score"] == 100
    assert result["consistency_score"] == 100


def test_palindrome_problem_catches_incorrect_code_and_missing_claim():
    problem = {
        "id": "palindrome",
        "title": "Palindrome Check",
        "function_name": "is_palindrome",
        "validator": "exact",
        "reasoning_rubric": {
            "criteria": [
                {
                    "name": "Palindrome property",
                    "concepts": ["palindrome"],
                    "maximum": 100
                }
            ]
        },
        "validation_cases": [
            {"case_id": "yes", "args": ["level"], "expected": True},
            {"case_id": "no", "args": ["python"], "expected": False}
        ]
    }
    response = {
        "answer": "",
        "candidate_results": [
            {"case_id": "yes", "result": True},
            {"case_id": "no", "result": True}
        ]
    }
    source_code = """
def is_palindrome(value):
    return True
"""

    result = evaluate_response(response, problem, source_code)

    assert result["reasoning_score"] == 0
    assert result["validation_score"] == 50
    assert result["execution_score"] == 50
    assert result["consistency_details"]["verdict"] == "NOT_EVALUATED"
