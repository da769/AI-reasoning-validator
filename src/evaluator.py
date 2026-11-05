from src.validators.reasoning import evaluate_reasoning


def evaluate_response(response):

    answer = response["answer"]

    evaluation = evaluate_reasoning(answer)

    return {
        "problem_id": response["problem_id"],
        "score": evaluation["score"],
        "maximum": evaluation["maximum"],
        "verdict": evaluation["verdict"],
        "criteria": evaluation["criteria"]
    }