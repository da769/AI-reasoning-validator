def evaluate_reasoning(answer):
    """
    Evaluate a Two Sum algorithm explanation
    using a weighted 100-point rubric.
    """

    if isinstance(answer, str):
        answer = {"explanation": answer}

    if not isinstance(answer, dict) or not any(
        value not in (None, "", [], {})
        for value in answer.values()
    ):
        return {
            "score": 0,
            "maximum": 100,
            "verdict": "FAIL",
            "feedback": "No answer or explanation was provided.",
            "criteria": [{
                "name": "Answer availability",
                "score": 0,
                "maximum": 100,
                "passed": False
            }]
        }

    def text(*fields):
        return " ".join(
            str(answer.get(field, ""))
            for field in fields
            if answer.get(field) is not None
        ).lower()

    algorithm = text("algorithm")
    implementation = text("implementation", "explanation")
    complexity = text("complexity", "time_complexity")
    assumptions = answer.get("assumptions", [])
    edge_cases = answer.get("edge_cases", [])
    conclusion = text("conclusion")

    criteria = []

    # 1. Algorithm correctness: 20 points
    algorithm_correct = (
        ("dictionary" in algorithm or "hash map" in algorithm)
        and (
            "single pass" in implementation
            or "previously" in implementation
            or "previous" in implementation
        )
    )

    criteria.append({
        "name": "Algorithm correctness",
        "score": 20 if algorithm_correct else 0,
        "maximum": 20,
        "passed": algorithm_correct
    })

    # 2. Complexity accuracy: 20 points
    complexity_correct = (
        "o(n)" in complexity.replace(" ", "")
        and (
            "average" in complexity
            or "time_complexity" in answer
        )
    )

    criteria.append({
        "name": "Complexity accuracy",
        "score": 20 if complexity_correct else 0,
        "maximum": 20,
        "passed": complexity_correct
    })

    # 3. Constraint compliance: 20 points
    constraint_correct = (
        "distinct" in implementation
        or "different indices" in implementation
        or "same element cannot be used twice" in implementation
        or "previously" in implementation
        or "previous" in implementation
    )

    criteria.append({
        "name": "Constraint compliance",
        "score": 20 if constraint_correct else 0,
        "maximum": 20,
        "passed": constraint_correct
    })

    # 4. Assumptions: 10 points
    assumptions_correct = (
        isinstance(assumptions, list)
        and len(assumptions) > 0
    )

    # 5. Edge-case consideration: 10 points
    edge_cases_correct = (
        isinstance(edge_cases, list)
        and len(edge_cases) >= 2
    )

    # 6. Conclusion validity: 20 points
    conclusion_correct = (
        "o(n)" in conclusion
        and (
            "hash map" in conclusion
            or "dictionary" in conclusion
        )
    )

    detailed_answer = any(
        field in answer
        for field in (
            "implementation",
            "complexity",
            "assumptions",
            "edge_cases",
            "conclusion"
        )
    )

    if detailed_answer:
        criteria.extend([
            {
                "name": "Assumptions",
                "score": 10 if assumptions_correct else 0,
                "maximum": 10,
                "passed": assumptions_correct
            },
            {
                "name": "Edge-case consideration",
                "score": 10 if edge_cases_correct else 0,
                "maximum": 10,
                "passed": edge_cases_correct
            },
            {
                "name": "Conclusion validity",
                "score": 20 if conclusion_correct else 0,
                "maximum": 20,
                "passed": conclusion_correct
            }
        ])

    # Calculate final score
    total_score = sum(item["score"] for item in criteria)
    maximum_score = sum(item["maximum"] for item in criteria)
    score = round(total_score / maximum_score * 100)

    if score >= 80:
        verdict = "PASS"
    elif score >= 50:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    return {
        "score": score,
        "maximum": maximum_score,
        "verdict": verdict,
        "criteria": criteria
    }