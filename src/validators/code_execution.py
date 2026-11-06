import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from src.validators.algorithm import validate_two_sum_result
from src.validators.code_quality import check_code_security


def evaluate_python_submission(source_code, test_cases, timeout=5):
    """
    Evaluate a submitted Python implementation of Two Sum.

    The function:
    1. Checks whether source code is provided.
    2. Checks Python syntax.
    3. Performs preliminary static security screening.
    4. Executes the submission in a temporary working directory.
    5. Validates returned indices against independent test cases.
    6. Returns structured evaluation results.

    IMPORTANT:
    This implementation is NOT a secure sandbox.
    Do not use it to execute arbitrary untrusted code.
    """

    # 1. Check whether source code is provided
    if not isinstance(source_code, str) or not source_code.strip():
        return {
            "status": "REJECTED",
            "passed": False,
            "feedback": "No Python source code was provided.",
            "results": []
        }

    # 2. Check syntax before security screening
    try:
        compile(source_code, "<candidate_submission>", "exec")

    except SyntaxError as error:
        return {
            "status": "SYNTAX_ERROR",
            "passed": False,
            "feedback": str(error),
            "results": []
        }

    # 3. Perform preliminary security checks
    security_result = check_code_security(source_code)

    if not security_result["passed"]:
        return {
            "status": "REJECTED",
            "passed": False,
            "feedback": "Preliminary security screening detected issues.",
            "security_findings": security_result["findings"],
            "results": []
        }

    # 4. Validate test case structure
    if not isinstance(test_cases, list) or not test_cases:
        return {
            "status": "REJECTED",
            "passed": False,
            "feedback": "Test cases must be a non-empty list.",
            "results": []
        }

    for case in test_cases:
        if (
            not isinstance(case, dict)
            or "values" not in case
            or "target" not in case
        ):
            return {
                "status": "REJECTED",
                "passed": False,
                "feedback": "Each test case must contain values and target.",
                "results": []
            }

    # 5. Create a temporary execution workspace
    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            workspace = Path(temp_dir)

            candidate_path = workspace / "candidate.py"
            test_cases_path = workspace / "test_cases.json"
            runner_path = workspace / "runner.py"
            output_path = workspace / "results.json"

            # Save candidate source code
            candidate_path.write_text(
                source_code,
                encoding="utf-8"
            )

            # Save test cases
            test_cases_path.write_text(
                json.dumps(test_cases),
                encoding="utf-8"
            )

            # 6. Generate the execution runner
            runner_code = r'''
import importlib.util
import json
import sys
import time
from pathlib import Path

workspace = Path(__file__).parent

candidate_path = workspace / "candidate.py"
test_cases_path = workspace / "test_cases.json"
output_path = workspace / "results.json"

results = []

try:
    # Load candidate module
    spec = importlib.util.spec_from_file_location(
        "candidate",
        candidate_path
    )

    if spec is None or spec.loader is None:
        raise ImportError("Unable to load candidate module.")

    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)

    # Check required function
    if not hasattr(candidate, "two_sum"):
        raise AttributeError(
            "Required function 'two_sum(values, target)' was not found."
        )

    if not callable(candidate.two_sum):
        raise TypeError(
            "'two_sum' must be a callable function."
        )

    # Load test cases
    with open(test_cases_path, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    # Execute candidate function for each test case
    for case in test_cases:

        start_time = time.perf_counter()

        try:
            returned_indices = candidate.two_sum(
                case["values"],
                case["target"]
            )

            elapsed_time = time.perf_counter() - start_time

            results.append({
                "returned_indices": returned_indices,
                "execution_time": elapsed_time,
                "error": None
            })

        except Exception as error:

            elapsed_time = time.perf_counter() - start_time

            results.append({
                "returned_indices": None,
                "execution_time": elapsed_time,
                "error": str(error)
            })

    # Save results
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file)

except Exception as error:

    print(str(error), file=sys.stderr)
    sys.exit(1)
'''

            runner_path.write_text(
                runner_code,
                encoding="utf-8"
            )

            # 7. Execute runner in a separate process
            try:
                process = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        str(runner_path)
                    ],
                    cwd=str(workspace),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            except subprocess.TimeoutExpired:
                return {
                    "status": "TIMEOUT",
                    "passed": False,
                    "feedback": (
                        f"Submission exceeded the {timeout}-second "
                        "execution time limit."
                    ),
                    "results": []
                }

            # 8. Handle process execution failures
            if process.returncode != 0:
                return {
                    "status": "EXECUTION_ERROR",
                    "passed": False,
                    "feedback": (
                        process.stderr.strip()
                        or "The submitted program failed during execution."
                    ),
                    "results": []
                }

            # 9. Read execution results
            if not output_path.exists():
                return {
                    "status": "EXECUTION_ERROR",
                    "passed": False,
                    "feedback": "Execution completed without producing results.",
                    "results": []
                }

            try:
                execution_results = json.loads(
                    output_path.read_text(encoding="utf-8")
                )

            except (json.JSONDecodeError, OSError) as error:
                return {
                    "status": "EXECUTION_ERROR",
                    "passed": False,
                    "feedback": f"Unable to read execution results: {error}",
                    "results": []
                }

            # 10. Ensure result count matches test case count
            if (
                not isinstance(execution_results, list)
                or len(execution_results) != len(test_cases)
            ):
                return {
                    "status": "EXECUTION_ERROR",
                    "passed": False,
                    "feedback": "Execution returned an unexpected number of results.",
                    "results": []
                }

            # 11. Independently validate returned indices
            validated_results = []

            passed_cases = 0

            for index, (case, execution_result) in enumerate(
                zip(test_cases, execution_results),
                start=1
            ):

                returned_indices = execution_result.get(
                    "returned_indices"
                )

                execution_error = execution_result.get("error")

                if execution_error:
                    validation = {
                        "passed": False,
                        "feedback": f"Execution error: {execution_error}"
                    }

                else:
                    validation = validate_two_sum_result(
                        case["values"],
                        case["target"],
                        returned_indices
                    )

                case_passed = validation["passed"]

                if case_passed:
                    passed_cases += 1

                validated_results.append({
                    "test_case": index,
                    "passed": case_passed,
                    "returned_indices": returned_indices,
                    "execution_time": execution_result.get(
                        "execution_time"
                    ),
                    "feedback": validation["feedback"]
                })

            # 12. Calculate final execution score
            total_cases = len(test_cases)

            all_passed = passed_cases == total_cases

            return {
    "status": "COMPLETED",
    "passed": all_passed,

    # Test case statistics
    "passed_cases": passed_cases,
    "passed_test_cases": passed_cases,
    "total_cases": total_cases,
    "total_test_cases": total_cases,

    # Execution score
    "score": round(
        (passed_cases / total_cases) * 100,
        2
    ),

    "feedback": (
        "All test cases passed."
        if all_passed
        else "Some test cases failed."
    ),

    "security_findings": [],
    "results": validated_results
}

    except Exception as error:
        return {
            "status": "EXECUTION_ERROR",
            "passed": False,
            "feedback": f"Unexpected evaluation error: {error}",
            "results": []
        }