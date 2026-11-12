def generate_report(problem_id, evaluation):

    print("\n")
    print("=" * 65)
    print("          AI COMPUTER SCIENCE REASONING VALIDATOR")
    print("=" * 65)

    print(f"\nProblem ID: {problem_id}")

    print("\n" + "-" * 65)
    print("OVERALL EVALUATION")
    print("-" * 65)

    print(
        f"Overall Score: {evaluation['score']}/100"
    )

    print(
        f"Final Verdict: {evaluation['verdict']}"
    )

    # -----------------------------------------
    # REASONING QUALITY
    # -----------------------------------------

    print("\n" + "-" * 65)
    print("1. REASONING QUALITY (40%)")
    print("-" * 65)

    print(
        f"Raw Score: {evaluation['reasoning_score']}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation['weighted_reasoning_score']}/40"
    )

    # -----------------------------------------
    # CLAIMED ANSWER VALIDATION
    # -----------------------------------------

    print("\n" + "-" * 65)
    print("2. CLAIMED ANSWER VALIDATION (20%)")
    print("-" * 65)

    print(
        f"Raw Score: {evaluation['validation_score']}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation['weighted_validation_score']}/20"
    )

    print(
        f"Passed Cases: "
        f"{evaluation['passed_test_cases']}/"
        f"{evaluation['total_test_cases']}"
    )

    for result in evaluation["validation_details"]["results"]:

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"  {result['case_id']}: {status}"
            f" - {result['feedback']}"
        )

    # -----------------------------------------
    # CODE EXECUTION
    # -----------------------------------------

    print("\n" + "-" * 65)
    print("3. PYTHON CODE EXECUTION (25%)")
    print("-" * 65)

    print(
        f"Execution Status: "
        f"{evaluation['execution_status']}"
    )

    print(
        f"Raw Score: {evaluation['execution_score']}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation['weighted_execution_score']}/25"
    )

    print(
        f"Passed Cases: "
        f"{evaluation['execution_passed_cases']}/"
        f"{evaluation['execution_total_cases']}"
    )

    for result in evaluation["execution_details"]["results"]:

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"  {result['case_id']}: {status}"
            f" - {result['feedback']}"
        )

    # -----------------------------------------
    # REASONING-TO-CODE CONSISTENCY
    # -----------------------------------------

    print("\n" + "-" * 65)
    print("4. REASONING-TO-CODE CONSISTENCY (15%)")
    print("-" * 65)

    print(
        f"Raw Score: {evaluation['consistency_score']}/100"
    )

    print(
        f"Weighted Score: "
        f"{evaluation['weighted_consistency_score']}/15"
    )

    consistency = evaluation["consistency_details"]

    print(
        f"Consistency Verdict: {consistency['verdict']}"
    )

    print(
        f"Feedback: {consistency['feedback']}"
    )

    for finding in consistency.get("findings", []):

        status = "PASS" if finding["passed"] else "FAIL"

        print(
            f"  [{status}] {finding['criterion']}"
        )

        print(
            f"       {finding['feedback']}"
        )

    # -----------------------------------------
    # FINAL FEEDBACK
    # -----------------------------------------

    print("\n" + "-" * 65)
    print("FINAL FEEDBACK")
    print("-" * 65)

    for category, feedback in evaluation["feedback"].items():

        print(f"{category.capitalize()}: {feedback}")

    print("\n" + "=" * 65)
    print("                 END OF EVALUATION")
    print("=" * 65)