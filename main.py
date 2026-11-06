import json

from pathlib import Path

from src.evaluator import evaluate_response
from src.report import generate_report


def load_json(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():

    base_directory = Path(__file__).resolve().parent

    problem_path = (
        base_directory
        / "data"
        / "problems"
        / "problem_001.json"
    )

    response_path = (
        base_directory
        / "data"
        / "responses"
        / "problem_001_correct.json"
    )

    problem = load_json(problem_path)

    response = load_json(response_path)

    evaluation = evaluate_response(
        response,
        problem
    )

    generate_report(
        response["problem_id"],
        evaluation
    )


if __name__ == "__main__":
    main()