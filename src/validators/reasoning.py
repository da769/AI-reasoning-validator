def evaluate_reasoning(answer):

    algorithm = answer.get("algorithm", "").lower()

    implementation = answer.get(
        "implementation", ""
    ).lower()

    complexity = answer.get(
        "complexity", ""
    ).lower()

    assumptions = answer.get(
        "assumptions", []
    )

    edge_cases = answer.get(
        "edge_cases", []
    )

    conclusion = answer.get(
        "conclusion", ""
    ).lower()

    results = []

    # Algorithm correctness
    algorithm_passed = (
        ("dictionary" in algorithm or "hash map" in algorithm)
        and "single pass" in implementation
    )

    results.append({
        "criterion": "Algorithm correctness",
        "score": 20 if algorithm_passed else 0,
        "maximum": 20,
        "passed": algorithm_passed
    })

    # Complexity
    complexity_passed = (
        "o(n)" in complexity
        and "average" in complexity
    )

    results.append({
        "criterion": "Complexity accuracy",
        "score": 20 if complexity_passed else 0,
        "maximum": 20,
        "passed": complexity_passed
    })

    # Constraints
    constraints_passed = (
        "distinct" in implementation
        or "different indices" in implementation
        or "same element cannot be used twice" in implementation
    )

    results.append({
        "criterion": "Constraint compliance",
        "score": 20 if constraints_passed else 0,
        "maximum": 20,
        "passed": constraints_passed
    })

    # Assumptions
    assumptions_passed = len(assumptions) > 0

    results.append({
        "criterion": "Assumptions",
        "score": 10 if assumptions_passed else 0,
        "maximum": 10,
        "passed": assumptions_passed
    })

    # Edge cases
    edge_cases_passed = len(edge_cases) >= 2

    results.append({
        "criterion": "Edge-case consideration",
        "score": 10 if edge_cases_passed else 0,
        "maximum": 10,
        "passed": edge_cases_passed
    })

    # Conclusion
    conclusion_passed = (
        "o(n)" in conclusion
        and ("hash map" in conclusion or "dictionary" in conclusion)
    )

    results.append({
        "criterion": "Conclusion validity",
        "score": 20 if conclusion_passed else 0,
        "maximum": 20,
        "passed": conclusion_passed
    })

    total_score = sum(
        item["score"] for item in results
    )

    maximum_score = sum(
        item["maximum"] for item in results
    )

    return {
        "score": total_score,
        "maximum": maximum_score,
        "verdict": (
            "PASS" if total_score >= 80
            else "PARTIAL" if total_score >= 50
            else "FAIL"
        ),
        "criteria": results
    }