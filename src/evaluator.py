from src.validators.reasoning import evaluate_reasoning
from src.validators.algorithm import validate_two_sum_result
from src.validators.code_execution import evaluate_python_submission


# Evaluation weights
REASONING_WEIGHT = 50
VALIDATION_WEIGHT = 25
EXECUTION_WEIGHT = 25

PASS_THRESHOLD = 80
PARTIAL_THRESHOLD = 50


def get_reasoning_text(response):
    """
    Extract the written explanation from an AI response.

    Supports common response field names.
    """

    if isinstance(response, str):
        return response

    if not isinstance(response, dict):
        return ""

    return (
        response.get("answer")
        or response.get("reasoning")
        or response.get("explanation")
        or response.get("response")
        or ""
    )


def get_candidate_results(response):
    """
    Extract independently claimed results from the response.

    Expected format:

    {
        "candidate_results": [
            {
                "case_id": "case_001",
                "indices": [0, 1]
            }
        ]
    }
    """

    if not isinstance(response, dict):
        return []

    return response.get("candidate_results", [])


def validate_claimed_results(response, problem):
    """
    Independently validate the candidate's claimed Two Sum answers.

    Each claimed result is checked against its corresponding
    problem validation case.
    """

    validation_cases = problem.get("validation_cases", [])
    candidate_results = get_candidate_results(response)

    if not validation_cases:
        return {
            "score": 0,
            "maximum": 100,
            "passed_cases": 0,
            "total_cases": 0,
            "feedback": "No validation cases were provided.",
            "results": []
        }

    # Support candidate results provided as a list or dictionary.
    if isinstance(candidate_results, dict):
        normalized_results = []

        for case_id, result in candidate_results.items():
            if isinstance(result, dict):
                normalized_results.append({
                    "case_id": case_id,
                    **result
                })
            else:
                normalized_results.append({
                    "case_id": case_id,
                    "indices": result
                })

        candidate_results = normalized_results

    if not isinstance(candidate_results, list):
        candidate_results = []

    # Index candidate results by case ID.
    results_by_id = {}

    for index, result in enumerate(candidate_results):

        if not isinstance(result, dict):
            continue

        case_id = result.get("case_id")

        if case_id is None:
            case_id = f"case_{index + 1:03d}"

        results_by_id[case_id] = result

    validated_results = []
    passed_cases = 0

    for index, case in enumerate(validation_cases):

        case_id = case.get(
            "case_id",
            f"case_{index + 1:03d}"
        )

        candidate = results_by_id.get(case_id)

        if candidate is None:
            validation = {
                "passed": False,
                "feedback": "Candidate did not provide a result for this case."
            }

            indices = None

        else:
            indices = candidate.get(
                "indices",
                candidate.get("returned_indices")
            )

            validation = validate_two_sum_result(
                case["values"],
                case["target"],
                indices
            )

        if validation["passed"]:
            passed_cases += 1

        validated_results.append({
            "case_id": case_id,
            "passed": validation["passed"],
            "indices": indices,
            "feedback": validation["feedback"]
        })

    total_cases = len(validation_cases)

    score = (passed_cases / total_cases) * 100

    return {
        "score": round(score, 2),
        "maximum": 100,
        "passed_cases": passed_cases,
        "total_cases": total_cases,
        "feedback": (
            "All claimed results passed validation."
            if passed_cases == total_cases
            else "Some claimed results failed validation."
        ),
        "results": validated_results
    }


def evaluate_response(response, problem, source_code=None, timeout=5):
    """
    Evaluate an AI-generated computer science solution.

    Evaluation dimensions:

    1. Written reasoning: 50%
    2. Independent claimed-result validation: 25%
    3. Actual submitted Python code execution: 25%

    Parameters:
        response (dict or str): AI-generated explanation and claimed results.
        problem (dict): Problem statement and independent validation cases.
        source_code (str): Submitted Python implementation.
        timeout (int): Maximum execution time in seconds.

    Returns:
        dict: Combined evaluation score and detailed results.
    """

    # -------------------------------------------------
    # 1. Evaluate written reasoning
    # -------------------------------------------------

    answer = get_reasoning_text(response)

    reasoning_result = evaluate_reasoning(answer)

    reasoning_score = reasoning_result.get("score", 0)

    reasoning_score = max(
        0,
        min(100, reasoning_score)
    )

    weighted_reasoning_score = (
        reasoning_score * REASONING_WEIGHT / 100
    )

    # -------------------------------------------------
    # 2. Independently validate claimed answers
    # -------------------------------------------------

    validation_result = validate_claimed_results(
        response,
        problem
    )

    validation_score = validation_result["score"]

    weighted_validation_score = (
        validation_score * VALIDATION_WEIGHT / 100
    )

    # -------------------------------------------------
    # 3. Execute submitted Python implementation
    # -------------------------------------------------

    if source_code is None or not source_code.strip():

        execution_result = {
            "status": "NOT_PROVIDED",
            "passed": False,
            "score": 0,
            "passed_cases": 0,
            "total_cases": len(
                problem.get("validation_cases", [])
            ),
            "feedback": "No Python implementation was provided.",
            "results": []
        }

    else:

        execution_result = evaluate_python_submission(
            source_code,
            problem.get("validation_cases", []),
            timeout=timeout
        )

    execution_score = execution_result.get("score", 0)

    # Only completed executions receive execution points.
    if execution_result.get("status") != "COMPLETED":
        execution_score = 0

    execution_score = max(
        0,
        min(100, execution_score)
    )

    weighted_execution_score = (
        execution_score * EXECUTION_WEIGHT / 100
    )

    # -------------------------------------------------
    # 4. Calculate combined evaluation score
    # -------------------------------------------------

    overall_score = (
        weighted_reasoning_score
        + weighted_validation_score
        + weighted_execution_score
    )

    overall_score = round(overall_score, 2)

    # -------------------------------------------------
    # 5. Determine final verdict
    # -------------------------------------------------

    if overall_score >= PASS_THRESHOLD:
        verdict = "PASS"

    elif overall_score >= PARTIAL_THRESHOLD:
        verdict = "PARTIAL"

    else:
        verdict = "FAIL"

    # -------------------------------------------------
    # 6. Prepare evaluation summary
    # -------------------------------------------------

    return {
        "score": overall_score,
        "maximum": 100,
        "verdict": verdict,

        # Individual evaluation scores
        "reasoning_score": round(reasoning_score, 2),
        "validation_score": round(validation_score, 2),
        "execution_score": round(execution_score, 2),

        # Weighted contributions
        "weighted_reasoning_score": round(
            weighted_reasoning_score, 2
        ),

        "weighted_validation_score": round(
            weighted_validation_score, 2
        ),

        "weighted_execution_score": round(
            weighted_execution_score, 2
        ),

        # Reasoning details
        "reasoning_details": reasoning_result,

        # Claimed-answer validation details
        "validation_details": validation_result,

        "passed_test_cases": validation_result["passed_cases"],
        "total_test_cases": validation_result["total_cases"],

        # Actual code execution details
        "execution_details": execution_result,

        "execution_status": execution_result["status"],

        "execution_passed_cases": execution_result.get(
            "passed_cases",
            execution_result.get("passed_test_cases", 0)
        ),

        "execution_total_cases": execution_result.get(
            "total_cases",
            execution_result.get("total_test_cases", 0)
        ),

        # Evaluation criteria
        "criteria": reasoning_result.get("criteria", []),

        # Overall feedback
        "feedback": {
            "reasoning": reasoning_result.get("verdict"),
            "validation": validation_result["feedback"],
            "execution": execution_result["feedback"]
        }
    }