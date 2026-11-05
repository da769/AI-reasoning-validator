def generate_report(problem_id, evaluation):

    print("\n")
    print("=" * 65)
    print("DETAILED EVALUATION")
    print("=" * 65)

    print(f"Problem ID: {problem_id}")
    print(f"Final Score: {evaluation['score']}/{evaluation['maximum']}")
    print(f"Verdict: {evaluation['verdict']}")

    print("\nEvaluation Criteria")
    print("-" * 65)

    print(
        f"{'CRITERION':<30}"
        f"{'SCORE':<12}"
        f"{'MAXIMUM':<12}"
        f"{'STATUS':<10}"
    )

    print("-" * 65)

    for criterion in evaluation["criteria"]:

        name = criterion["name"]
        score = criterion["score"]
        maximum = criterion["maximum"]

        status = "PASS" if criterion["passed"] else "FAIL"

        print(
            f"{name:<30}"
            f"{score:<12}"
            f"{maximum:<12}"
            f"{status:<10}"
        )

    print("-" * 65)
    print("=" * 65)