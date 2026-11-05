from src.validators.reasoning import evaluate_reasoning


def evaluate_response(response):

    answer = response["answer"]

    reasoning_results = evaluate_reasoning(answer)

    score = sum(
        1 for result in reasoning_results
        if result["passed"]
    )

    maximum = len(reasoning_results)

    if score == maximum:
        verdict = "PASS"
    elif score >= maximum / 2:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    return {
        "score": score,
        "maximum": maximum,
        "verdict": verdict,
        "criteria": reasoning_results
    }
