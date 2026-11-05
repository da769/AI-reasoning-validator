from src.validators.numerical import validate_numeric_answer
from src.validators.algorithm import two_sum


def test_numeric_validation():
    assert validate_numeric_answer(10.0, 10.0000001)


def test_numeric_validation_failure():
    assert not validate_numeric_answer(10.0, 15.0)


def test_two_sum():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]


def test_two_sum_duplicates():
    assert two_sum([3, 3], 6) == [0, 1]


def test_two_sum_no_solution():
    assert two_sum([1, 2, 3], 10) is None


def test_two_sum_negative_numbers():
    assert two_sum([-3, 4, 7], 1) == [0, 1]