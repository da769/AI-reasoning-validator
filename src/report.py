def generate_report(problem_id, evaluation):

    print("\n" + "=" * 65)

    print("AI COMPUTER SCIENCE REASONING VALIDATION REPORT")

    print("=" * 65)

    print(f"\nProblem ID: {problem_id}")

    print(
        f"Final Score: {evaluation['score']}/"
        f"{evaluation['maximum']}"
    )

    print(f"Overall Verdict: {evaluation['verdict']}")

    print("\nDETAILED EVALUATION")

    print("-" * 65)

    for criterion in evaluation["criteria"]:

        status = (
            "PASS" if criterion["passed"]
            else "FAIL"
        )

        print(
            f"{criterion['criterion']:<30}"
            f"{criterion['score']:>5}/"
            f"{criterion['maximum']:<5}"
            f"{status:>10}"
        )

    print("-" * 65)

    print("\nEND OF REPORT")