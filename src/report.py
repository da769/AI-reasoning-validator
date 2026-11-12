def generate_report(problem_id, evaluation):

    print("\n")
    print("=" * 55)
    print("              EVALUATION REPORT")
    print("=" * 55)

    print(f"\nProblem ID: {problem_id}")

    # Overall evaluation
    print("\nOVERALL EVALUATION")
    print("-" * 55)

    print(
        f"Overall Score: "
        f"{evaluation.get('score', 0)}/100"
    )

    print(
        f"Final Verdict: "
        f"{evaluation.get('verdict', 'NOT AVAILABLE')}"
    )

    # Reasoning evaluation
    print("\n1. WRITTEN REASONING")
    print("-" * 55)

    print(
        f"Raw Score: "
        f"{evaluation.get('reasoning_score', 0)}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation.get('weighted_reasoning_score', 0)}/50"
    )

    # Claimed answer validation
    print("\n2. INDEPENDENT ANSWER VALIDATION")
    print("-" * 55)

    print(
        f"Raw Score: "
        f"{evaluation.get('validation_score', 0)}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation.get('weighted_validation_score', 0)}/25"
    )

    print(
        f"Passed Cases: "
        f"{evaluation.get('passed_test_cases', 0)}/"
        f"{evaluation.get('total_test_cases', 0)}"
    )

    validation_details = evaluation.get(
        "validation_details", {}
    )

    for result in validation_details.get("results", []):

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"  {result['case_id']}: {status} - "
            f"{result['feedback']}"
        )

    # Actual Python execution
    print("\n3. PYTHON CODE EXECUTION")
    print("-" * 55)

    print(
        f"Execution Status: "
        f"{evaluation.get('execution_status', 'UNKNOWN')}"
    )

    print(
        f"Raw Score: "
        f"{evaluation.get('execution_score', 0)}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation.get('weighted_execution_score', 0)}/25"
    )

    print(
        f"Passed Cases: "
        f"{evaluation.get('execution_passed_cases', 0)}/"
        f"{evaluation.get('execution_total_cases', 0)}"
    )

    execution_details = evaluation.get(
        "execution_details", {}
    )

    print(
        f"Feedback: "
        f"{execution_details.get('feedback', 'Not available')}"
    )

    for result in execution_details.get("results", []):

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"  Test Case {result['test_case']}: {status} - "
            f"{result['feedback']}"
        )

    # Final feedback
    print("\n4. EVALUATION FEEDBACK")
    print("-" * 55)

    feedback = evaluation.get("feedback", {})

    for category, message in feedback.items():

        print(f"{category.title()}: {message}")

    print("\n" + "=" * 55)
    print("              END OF REPORT")
    print("=" * 55)