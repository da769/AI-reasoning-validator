from src.validators.algorithm import validate_two_sum_result


def test_valid_pair():
    result = validate_two_sum_result([2, 7, 11, 15], 9, [0, 1])
    assert result["passed"] is True


def test_invalid_sum():
    result = validate_two_sum_result([2, 7, 11, 15], 9, [1, 2])
    assert result["passed"] is False


def test_same_index():
    result = validate_two_sum_result([3, 3], 6, [0, 0])
    assert result["passed"] is False


def test_out_of_range_index():
    result = validate_two_sum_result([2, 7], 9, [0, 5])
    assert result["passed"] is False


def test_no_solution_returned():
    result = validate_two_sum_result([1, 2, 3], 10, None)
    assert result["passed"] is False


def test_negative_numbers():
    result = validate_two_sum_result([-3, 4, 7], 1, [0, 1])
    assert result["passed"] is True


def test_duplicate_values():
    result = validate_two_sum_result([3, 3], 6, [0, 1])
    assert result["passed"] is True