import numpy as np


def validate_numeric_answer(
    expected: float,
    candidate: float,
    tolerance: float = 1e-6
) -> bool:
    """
    Compare a candidate numerical answer against
    an independently calculated expected value.
    """

    return bool(
        np.isclose(
            expected,
            candidate,
            atol=tolerance,
            rtol=tolerance
        )
    )