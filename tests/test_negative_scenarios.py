import pytest

from src.evaluator import evaluate_response


# -----------------------------------------
# SAMPLE PROBLEM
# -----------------------------------------

PROBLEM = {
    "title": "Two Sum",
    "validation_cases": [
        {
            "case_id": "case_001",
            "values": [2, 7, 11, 15],
            "target": 9
        },
        {
            "case_id": "case_002",
            "values": [3, 2, 4],
            "target": 6
        }
    ]
}


# -----------------------------------------
# CORRECT REASONING
# -----------------------------------------

CORRECT_RESPONSE = {
    "answer": {
        "algorithm": "hash map",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "explanation": (
            "Use a hash map to store previously "
            "visited values and their indices."
        )
    },
    "candidate_results": [
        {
            "case_id": "case_001",
            "indices": [0, 1]
        },
        {
            "case_id": "case_002",
            "indices": [1, 2]
        }
    ]
}


# -----------------------------------------
# CORRECT PYTHON IMPLEMENTATION
# -----------------------------------------

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


# -----------------------------------------
# SCENARIO 1:
# INCORRECT PYTHON IMPLEMENTATION
# -----------------------------------------

def test_incorrect_python_implementation():

    incorrect_code = """
def two_sum(values, target):
    return [0, 1]
"""

    result = evaluate_response(
        CORRECT_RESPONSE,
        PROBLEM,
        incorrect_code
    )

    assert result["execution_score"] < 100
    assert result["execution_status"] == "COMPLETED"


# -----------------------------------------
# SCENARIO 2:
# EXPLANATION CLAIMS HASH MAP,
# IMPLEMENTATION USES NESTED LOOPS
# -----------------------------------------

def test_reasoning_code_contradiction():

    nested_loop_code = """
def two_sum(values, target):
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] + values[j] == target:
                return [i, j]

    return None
"""

    result = evaluate_response(
        CORRECT_RESPONSE,
        PROBLEM,
        nested_loop_code
    )

    assert result["consistency_score"] < 100


# -----------------------------------------
# SCENARIO 3:
# INVALID CLAIMED ANSWERS
# -----------------------------------------

def test_invalid_claimed_answers():

    invalid_response = {
        "answer": {
            "algorithm": "hash map",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "explanation": "Use a hash map."
        },
        "candidate_results": [
            {
                "case_id": "case_001",
                "indices": [0, 2]
            },
            {
                "case_id": "case_002",
                "indices": [0, 1]
            }
        ]
    }

    result = evaluate_response(
        invalid_response,
        PROBLEM,
        CORRECT_CODE
    )

    assert result["validation_score"] < 100


# -----------------------------------------
# SCENARIO 4:
# MISSING CANDIDATE ANSWERS
# -----------------------------------------

def test_missing_candidate_answers():

    incomplete_response = {
        "answer": {
            "algorithm": "hash map",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "explanation": "Use a hash map."
        },
        "candidate_results": []
    }

    result = evaluate_response(
        incomplete_response,
        PROBLEM,
        CORRECT_CODE
    )

    assert result["validation_score"] == 0
    assert result["passed_test_cases"] == 0


# -----------------------------------------
# SCENARIO 5:
# MISSING REQUIRED FUNCTION
# -----------------------------------------

def test_missing_required_function():

    incorrect_code = """
def find_pair(values, target):
    return [0, 1]
"""

    result = evaluate_response(
        CORRECT_RESPONSE,
        PROBLEM,
        incorrect_code
    )

    assert result["execution_status"] == "EXECUTION_ERROR"
    assert result["execution_score"] == 0


# -----------------------------------------
# SCENARIO 6:
# COMPLETELY CORRECT SUBMISSION
# -----------------------------------------

def test_correct_submission_baseline():

    result = evaluate_response(
        CORRECT_RESPONSE,
        PROBLEM,
        CORRECT_CODE
    )

    print("\n--- BASELINE SCORE DIAGNOSTICS ---")

    print("Overall:", result["score"])

    print("Reasoning:", result["reasoning_score"])
    print("Validation:", result["validation_score"])
    print("Execution:", result["execution_score"])
    print("Consistency:", result["consistency_score"])

    print("\nReasoning details:")
    print(result["reasoning_details"])

    print("\nConsistency details:")
    print(result["consistency_details"])

    assert result["score"] == 100