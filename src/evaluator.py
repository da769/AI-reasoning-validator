from src.validators.reasoning import evaluate_reasoning
from src.validators.algorithm import validate_two_sum_result


def evaluate_response(response, problem):

    # ------------------------------------------------
    # 1. Evaluate the written reasoning
    # ------------------------------------------------

    answer = response.get("answer", {})

    reasoning = evaluate_reasoning(answer)

    # Reasoning contributes 70% of the final score.
    reasoning_weight = 0.70

    weighted_criteria = []

    for criterion in reasoning["criteria"]:

        weighted_criteria.append({
            "name": criterion["name"],
            "score": criterion["score"] * reasoning_weight,
            "maximum": criterion["maximum"] * reasoning_weight,
            "passed": criterion["passed"]
        })

    reasoning_score = reasoning["score"] * reasoning_weight

    # ------------------------------------------------
    # 2. Independently validate candidate results
    # ------------------------------------------------

    validation_cases = problem.get("validation_cases", [])

    candidate_results = response.get("candidate_results", [])

    result_lookup = {
        item.get("test_id"): item
        for item in candidate_results
        if isinstance(item, dict)
    }

    validation_feedback = []
    passed_cases = 0

    for case in validation_cases:

        test_id = case["test_id"]

        candidate = result_lookup.get(test_id)

        indices = (
            candidate.get("indices")
            if candidate is not None
            else None
        )

        result = validate_two_sum_result(
            case["values"],
            case["target"],
            indices
        )

        if result["passed"]:
            passed_cases += 1

        validation_feedback.append({
            "test_id": test_id,
            "passed": result["passed"],
            "feedback": result["feedback"]
        })

    # ------------------------------------------------
    # 3. Calculate independent validation score
    # ------------------------------------------------

    maximum_validation_score = 30

    if validation_cases:

        validation_score = (
            passed_cases / len(validation_cases)
        ) * maximum_validation_score

    else:
        validation_score = 0

    validation_passed = (
        len(validation_cases) > 0
        and passed_cases == len(validation_cases)
    )

    weighted_criteria.append({
        "name": "Independent result validation",
        "score": validation_score,
        "maximum": maximum_validation_score,
        "passed": validation_passed,
        "feedback": validation_feedback
    })

    # ------------------------------------------------
    # 4. Calculate combined score
    # ------------------------------------------------

    total_score = round(
        reasoning_score + validation_score,
        2
    )

    maximum_score = 100

    if total_score >= 80:
        verdict = "PASS"

    elif total_score >= 50:
        verdict = "PARTIAL"

    else:
        verdict = "FAIL"

    # ------------------------------------------------
    # 5. Return complete evaluation
    # ------------------------------------------------

    return {
        "problem_id": response.get("problem_id"),
        "score": total_score,
        "maximum": maximum_score,
        "verdict": verdict,
        "reasoning_score": round(reasoning_score, 2),
        "validation_score": round(validation_score, 2),
        "passed_test_cases": passed_cases,
        "total_test_cases": len(validation_cases),
        "validation_feedback": validation_feedback,
        "criteria": weighted_criteria
    }