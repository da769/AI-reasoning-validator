def generate_report(problem_id, evaluation):

    print("\n" + "=" * 60)
    print("AI COMPUTER SCIENCE REASONING VALIDATION REPORT")
    print("=" * 60)

    print(f"Problem: {problem_id}")

    print(
        f"Score: {evaluation['score']}/"
        f"{evaluation['maximum']}"
    )

    print(f"Verdict: {evaluation['verdict']}")

    print("\nCriteria:")

    for criterion in evaluation["criteria"]:
        status = "PASS" if criterion["passed"] else "FAIL"

        print(
            f"- {criterion['criterion']}: {status}"
        )
        