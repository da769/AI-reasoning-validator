import numpy as np
from scipy import stats


def independent_t_test(group_a, group_b):
    result = stats.ttest_ind(
        group_a,
        group_b,
        equal_var=False
    )

    return {
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue)
    }