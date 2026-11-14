import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from src.validators.algorithm import validate_problem_result
from src.validators.code_quality import check_code_security


def evaluate_python_submission(
    source_code,
    test_cases,
    timeout=5,
    problem=None
):
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
    problem = problem or {}
    function_name = problem.get("function_name", "two_sum")
    validator = problem.get("validator", "two_sum")

    if not isinstance(function_name, str) or not function_name.isidentifier():
        return {
            "status": "REJECTED",
            "passed": False,
            "feedback": "The required function name is invalid.",
            "results": []
        }

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
        if not isinstance(case, dict):
            return {
                "status": "REJECTED",
                "passed": False,
                "feedback": "Each test case must be an object.",
                "results": []
            }

        if "args" in case:
            if (
                not isinstance(case["args"], list)
                or not isinstance(case.get("kwargs", {}), dict)
            ):
                return {
                    "status": "REJECTED",
                    "passed": False,
                    "feedback": (
                        "Test case args must be a list and kwargs an object."
                    ),
                    "results": []
                }
        elif validator == "two_sum" and not all(
            key in case for key in ("values", "target")
        ):
            return {
                "status": "REJECTED",
                "passed": False,
                "feedback": "Two Sum test cases require values and target.",
                "results": []
            }

        if validator == "exact" and "expected" not in case:
            return {
                "status": "REJECTED",
                "passed": False,
                "feedback": "Exact-match test cases require expected output.",
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
            configuration_path = workspace / "configuration.json"

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
            configuration_path.write_text(
                json.dumps({"function_name": function_name}),
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
configuration_path = workspace / "configuration.json"

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

    # Load test cases
    with open(test_cases_path, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    with open(configuration_path, "r", encoding="utf-8") as file:
        configuration = json.load(file)

    function_name = configuration["function_name"]
    function = getattr(candidate, function_name, None)

    if not callable(function):
        raise AttributeError(
            f"Required function '{function_name}' was not found or is not callable."
        )

    # Execute candidate function for each test case
    for case in test_cases:

        start_time = time.perf_counter()

        try:
            if "args" in case:
                args = case["args"]
            else:
                args = [case["values"], case["target"]]
            returned_result = function(
                *args,
                **case.get("kwargs", {})
            )

            elapsed_time = time.perf_counter() - start_time

            results.append({
                "returned_result": returned_result,
                "execution_time": elapsed_time,
                "error": None
            })

        except Exception as error:

            elapsed_time = time.perf_counter() - start_time

            results.append({
                "returned_result": None,
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

                returned_result = execution_result.get(
                    "returned_result",
                    execution_result.get("returned_indices")
                )

                execution_error = execution_result.get("error")

                if execution_error:
                    validation = {
                        "passed": False,
                        "feedback": f"Execution error: {execution_error}"
                    }

                else:
                    validation = validate_problem_result(
                        problem,
                        case,
                        returned_result
                    )

                case_passed = validation["passed"]

                if case_passed:
                    passed_cases += 1

                validated_results.append({
                    "test_case": index,
                    "case_id": case.get(
                        "case_id",
                        case.get("test_id", f"case_{index:03d}")
                    ),
                    "passed": case_passed,
                    "returned_result": returned_result,
                    "returned_indices": (
                        returned_result
                        if validator == "two_sum"
                        else None
                    ),
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