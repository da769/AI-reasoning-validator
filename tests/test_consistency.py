from src.validators.consistency import (
    analyze_code_structure,
    analyze_reasoning_claims,
    evaluate_consistency
)


HASH_MAP_CODE = """
def two_sum(values, target):
    seen = {}

    for index, value in enumerate(values):
        complement = target - value

        if complement in seen:
            return [seen[complement], index]

        seen[value] = index

    return None
"""


NESTED_LOOP_CODE = """
def two_sum(values, target):
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] + values[j] == target:
                return [i, j]

    return None
"""


def test_dictionary_detection():

    result = analyze_code_structure(HASH_MAP_CODE)

    assert result["passed"] is True
    assert result["features"]["uses_dictionary"] is True


def test_nested_loop_detection():

    result = analyze_code_structure(NESTED_LOOP_CODE)

    assert result["features"]["uses_nested_loops"] is True


def test_hash_map_claim_detection():

    result = analyze_reasoning_claims(
        "This algorithm uses a hash map."
    )

    assert result["claims_hash_map"] is True


def test_linear_complexity_claim_detection():

    result = analyze_reasoning_claims(
        "The algorithm has O(n) time complexity."
    )

    assert result["claims_linear_time"] is True


def test_consistent_hash_map_implementation():

    answer = (
        "The algorithm uses a hash map "
        "and achieves O(n) time complexity."
    )

    result = evaluate_consistency(
        answer,
        HASH_MAP_CODE
    )

    assert result["score"] == 100
    assert result["verdict"] == "PASS"


def test_inconsistent_hash_map_claim():

    answer = (
        "The algorithm uses a hash map "
        "and achieves O(n) time complexity."
    )

    result = evaluate_consistency(
        answer,
        NESTED_LOOP_CODE
    )

    assert result["score"] < 100


def test_missing_two_sum_function():

    result = evaluate_consistency(
        "The algorithm uses a hash map.",
        "def find_pair(values, target): return None"
    )

    assert result["verdict"] == "FAIL"