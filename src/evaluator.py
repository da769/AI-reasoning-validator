import json

from src.validators.reasoning import evaluate_reasoning
from src.validators.algorithm import validate_two_sum_result
from src.validators.code_execution import evaluate_python_submission
from src.validators.consistency import evaluate_consistency


# -------------------------------------------------
# EVALUATION WEIGHTS
# -------------------------------------------------

REASONING_WEIGHT = 40
VALIDATION_WEIGHT = 20
EXECUTION_WEIGHT = 25
CONSISTENCY_WEIGHT = 15

PASS_THRESHOLD = 80
PARTIAL_THRESHOLD = 50


# -------------------------------------------------
# EXTRACT REASONING TEXT
# -------------------------------------------------

def get_reasoning_data(response):
    """
    Extract structured reasoning data.
    Preserves dictionaries for reasoning.py.
    """

    if isinstance(response, dict):

        answer = (
            response.get("answer")
            or response.get("reasoning")
            or response.get("explanation")
            or response.get("response")
            or ""
        )

        return answer

    return response


def get_reasoning_text(response):
    """
    Convert reasoning data into text for consistency analysis.
    """

    import json

    answer = get_reasoning_data(response)

    if isinstance(answer, str):
        return answer

    if isinstance(answer, (dict, list)):
        return json.dumps(answer, ensure_ascii=False)

    return str(answer)


# -------------------------------------------------
# EXTRACT CANDIDATE RESULTS
# -------------------------------------------------

def get_candidate_results(response):

    if not isinstance(response, dict):
        return []

    return response.get("candidate_results", [])


# -------------------------------------------------
# VALIDATE CLAIMED RESULTS
# -------------------------------------------------

def validate_claimed_results(response, problem):

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
                "feedback": (
                    "Candidate did not provide a result for this case."
                )
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


# -------------------------------------------------
# MAIN EVALUATION PIPELINE
# -------------------------------------------------

def evaluate_response(response, problem, source_code=None, timeout=5):

    """
    Evaluate an AI-generated computer science solution.

    Evaluation dimensions:

    1. Written reasoning: 40%
    2. Claimed-answer validation: 20%
    3. Actual code execution: 25%
    4. Reasoning-to-code consistency: 15%
    """

    # -------------------------------------------------
    # 1. EVALUATE WRITTEN REASONING
    # -------------------------------------------------

    #answer = get_reasoning_text(response)
    #preserve structured data for reasoning evaluation
    reasoning_data = get_reasoning_data(response)

    reasoning_result = evaluate_reasoning(reasoning_data)

    #convert the same data into text for consistency analysis
    answer = get_reasoning_text(response)

    reasoning_score = reasoning_result.get("score", 0)

    reasoning_score = max(
        0,
        min(100, reasoning_score)
    )

    weighted_reasoning_score = (
        reasoning_score * REASONING_WEIGHT / 100
    )

    # -------------------------------------------------
    # 2. VALIDATE CLAIMED ANSWERS
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
    # 3. EXECUTE SUBMITTED PYTHON CODE
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
    # 4. EVALUATE REASONING-TO-CODE CONSISTENCY
    # -------------------------------------------------

    if source_code is None or not source_code.strip():

        consistency_result = {
            "passed": False,
            "score": 0,
            "verdict": "NOT_EVALUATED",
            "feedback": (
                "Consistency evaluation requires a Python implementation."
            ),
            "findings": [],
            "code_features": {},
            "reasoning_claims": {}
        }

    else:

        consistency_result = evaluate_consistency(
            answer,
            source_code
        )

    consistency_score = consistency_result.get("score", 0)

    consistency_score = max(
        0,
        min(100, consistency_score)
    )

    weighted_consistency_score = (
        consistency_score * CONSISTENCY_WEIGHT / 100
    )

    # -------------------------------------------------
    # 5. CALCULATE OVERALL SCORE
    # -------------------------------------------------

    overall_score = (
        weighted_reasoning_score
        + weighted_validation_score
        + weighted_execution_score
        + weighted_consistency_score
    )

    overall_score = round(overall_score, 2)

    # -------------------------------------------------
    # 6. DETERMINE FINAL VERDICT
    # -------------------------------------------------

    if overall_score >= PASS_THRESHOLD:
        verdict = "PASS"

    elif overall_score >= PARTIAL_THRESHOLD:
        verdict = "PARTIAL"

    else:
        verdict = "FAIL"

    # -------------------------------------------------
    # 7. RETURN COMPLETE EVALUATION
    # -------------------------------------------------

    return {

        "score": overall_score,
        "maximum": 100,
        "verdict": verdict,

        # Individual scores

        "reasoning_score": round(reasoning_score, 2),
        "validation_score": round(validation_score, 2),
        "execution_score": round(execution_score, 2),
        "consistency_score": round(consistency_score, 2),

        # Weighted scores

        "weighted_reasoning_score": round(
            weighted_reasoning_score, 2
        ),

        "weighted_validation_score": round(
            weighted_validation_score, 2
        ),

        "weighted_execution_score": round(
            weighted_execution_score, 2
        ),

        "weighted_consistency_score": round(
            weighted_consistency_score, 2
        ),

        # Reasoning details

        "reasoning_details": reasoning_result,

        # Claimed-answer validation details

        "validation_details": validation_result,

        "passed_test_cases": validation_result["passed_cases"],
        "total_test_cases": validation_result["total_cases"],

        # Code execution details

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

        # Consistency details

        "consistency_details": consistency_result,

        # Evaluation criteria

        "criteria": reasoning_result.get("criteria", []),

        # Feedback

        "feedback": {
            "reasoning": reasoning_result.get("verdict"),
            "validation": validation_result["feedback"],
            "execution": execution_result["feedback"],
            "consistency": consistency_result["feedback"]
        }
    }