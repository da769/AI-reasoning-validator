CONCEPT_ALIASES = {
    "hash_map": (
        "hash map",
        "hash-map",
        "dictionary",
        "lookup table",
        "map from values to indices",
        "map each value to its index",
        "values mapped to positions",
        "mapping from values to their positions",
        "position associated with each value"
    ),
    "single_pass": (
        "single pass",
        "one pass",
        "examine each value once",
        "visit each item once",
        "once through",
        "iterate through the array"
    ),
    "complement_lookup": (
        "complement",
        "wanted partner",
        "value needed to reach the target",
        "partner that reaches the target",
        "target minus the current",
        "target minus",
        "difference between the target",
        "remaining value"
    ),
    "distinct_indices": (
        "distinct indices",
        "different indices",
        "cannot use the same element",
        "different from the earlier position",
        "two separate positions",
        "different array positions",
        "previously seen",
        "previously visited",
        "previous element"
    ),
    "linear_average_time": (
        "o(n)",
        "linear time",
        "linear average",
        "proportional to the input size",
        "scales with the input size",
        "grows linearly",
        "expected linear time",
        "average-case linear time",
        "each item is processed once with constant-time lookup"
    ),
    "binary_search": (
        "binary search",
        "middle element",
        "midpoint",
        "halve the",
        "halve the remaining",
        "divide the search range",
        "repeatedly discard half",
        "cut the candidate range in half",
        "narrow the search interval by half",
        "halve the remaining candidates"
    ),
    "sorted_input": (
        "sorted",
        "in order",
        "ordered input",
        "ascending order",
        "smallest to largest"
    ),
    "logarithmic_time": (
        "o(log n)",
        "logarithmic time",
        "log n",
        "halves the remaining"
    ),
    "palindrome": (
        "palindrome",
        "reads the same forwards and backwards",
        "same in reverse",
        "equal to its reverse",
        "matches its reversed sequence",
        "symmetric around the center"
    )
}


def _answer_text(value):
    if isinstance(value, dict):
        return " ".join(_answer_text(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return " ".join(_answer_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _has_concept_evidence(text, concept, custom_aliases):
    aliases = custom_aliases.get(
        concept,
        CONCEPT_ALIASES.get(concept, (concept.replace("_", " "),))
    )

    for alias in aliases:
        alias = str(alias).strip().lower()
        if not alias:
            continue

        start = 0
        while True:
            position = text.find(alias, start)
            if position < 0:
                break

            preceding_text = text[max(0, position - 24):position]
            if not any(
                marker in preceding_text
                for marker in ("not ", "never ", "avoid ", "without ")
            ):
                return True

            start = position + len(alias)

    return False


def evaluate_reasoning(answer, problem=None):
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

    rubric = (problem or {}).get("reasoning_rubric", {})
    rubric_criteria = rubric.get("criteria", [])
    if rubric_criteria:
        answer_text = _answer_text(answer).lower()
        custom_aliases = (problem or {}).get("concept_aliases", {})
        criteria = []

        for rubric_criterion in rubric_criteria:
            concepts = rubric_criterion.get("concepts", [])
            evidence = {
                concept: _has_concept_evidence(
                    answer_text,
                    concept,
                    custom_aliases
                )
                for concept in concepts
            }
            passed = bool(concepts) and all(evidence.values())
            criteria.append({
                "name": rubric_criterion.get("name", "Reasoning criterion"),
                "score": (
                    rubric_criterion.get("maximum", 1)
                    if passed else 0
                ),
                "maximum": rubric_criterion.get("maximum", 1),
                "passed": passed,
                "evidence": evidence
            })

        maximum_score = sum(item["maximum"] for item in criteria)
        total_score = sum(item["score"] for item in criteria)
        score = round(total_score / maximum_score * 100)
        verdict = (
            "PASS" if score >= 80
            else "PARTIAL" if score >= 50
            else "FAIL"
        )
        return {
            "score": score,
            "maximum": maximum_score,
            "verdict": verdict,
            "criteria": criteria
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