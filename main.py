import json

from src.evaluator import evaluate_response
from src.report import generate_report


def load_response(path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    response = load_response(
        "data/responses/problem_001_correct.json"
    )

    evaluation = evaluate_response(response)

    generate_report(
        response["problem_id"],
        evaluation
    )


if __name__ == "__main__":
    main()
    