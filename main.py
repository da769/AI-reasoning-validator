import json

from pathlib import Path

from src.evaluator import evaluate_response
from src.report import generate_report


def load_json(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_python_code(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def main():

    # -------------------------------------------------
    # 1. Define project directory
    # -------------------------------------------------

    base_directory = Path(__file__).resolve().parent

    # -------------------------------------------------
    # 2. Define input file paths
    # -------------------------------------------------

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

    code_path = (
        base_directory
        / "data"
        / "responses"
        / "problem_001_code.py"
    )

    # -------------------------------------------------
    # 3. Check whether input files exist
    # -------------------------------------------------

    required_files = [
        problem_path,
        response_path,
        code_path
    ]

    for file_path in required_files:

        if not file_path.exists():

            raise FileNotFoundError(
                f"Required project file not found: {file_path}"
            )

    # -------------------------------------------------
    # 4. Load problem, response and submitted code
    # -------------------------------------------------

    problem = load_json(problem_path)

    response = load_json(response_path)

    source_code = load_python_code(code_path)

    # -------------------------------------------------
    # 5. Run integrated evaluation
    # -------------------------------------------------

    print("\n")
    print("=" * 55)
    print("       AI COMPUTER SCIENCE REASONING VALIDATOR")
    print("=" * 55)

    print("\nProblem:", problem.get("title", "Two Sum"))

    print("\nEvaluating AI submission...")

    evaluation = evaluate_response(
        response=response,
        problem=problem,
        source_code=source_code,
        timeout=5
    )

    # -------------------------------------------------
    # 6. Generate evaluation report
    # -------------------------------------------------

    generate_report(
        response.get("problem_id", "problem_001"),
        evaluation
    )


if __name__ == "__main__":
    main()