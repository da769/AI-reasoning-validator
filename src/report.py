def generate_report(problem_id, evaluation):

    print("\n")
    print("=" * 70)
    print("AI COMPUTER SCIENCE REASONING VALIDATOR")
    print("=" * 70)

    print(f"Problem ID: {problem_id}")

    print("\nFINAL EVALUATION")
    print("-" * 70)

    print(
        f"Overall Score: "
        f"{evaluation['score']}/{evaluation['maximum']}"
    )

    print(f"Verdict: {evaluation['verdict']}")

    print(
        f"Reasoning Score: "
        f"{evaluation['reasoning_score']}/70"
    )

    print(
        f"Validation Score: "
        f"{evaluation['validation_score']}/30"
    )

    print("\nDETAILED EVALUATION CRITERIA")
    print("-" * 70)

    print(
        f"{'CRITERION':<35}"
        f"{'SCORE':<12}"
        f"{'MAX':<10}"
        f"{'STATUS':<10}"
    )

    print("-" * 70)

    for criterion in evaluation["criteria"]:

        status = "PASS" if criterion["passed"] else "FAIL"

        print(
            f"{criterion['name']:<35}"
            f"{criterion['score']:<12}"
            f"{criterion['maximum']:<10}"
            f"{status:<10}"
        )

    print("\nINDEPENDENT VALIDATION RESULTS")
    print("-" * 70)

    for item in evaluation["validation_feedback"]:

        status = "PASS" if item["passed"] else "FAIL"

        print(f"{item['test_id']:<15} {status}")

        print(f"Feedback: {item['feedback']}")

    print("-" * 70)

    print(
        f"Validated test cases: "
        f"{evaluation['passed_test_cases']}/"
        f"{evaluation['total_test_cases']}"
    )

    print("=" * 70)