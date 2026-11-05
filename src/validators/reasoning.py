def evaluate_reasoning(answer):
    results = []

    algorithm = answer.get("algorithm", "")
    complexity = answer.get("complexity", "")
    assumptions = answer.get("assumptions", [])

    results.append({
        "criterion": "algorithm",
        "passed": "dictionary" in algorithm.lower()
    })

    results.append({
        "criterion": "complexity",
        "passed": "o(n)" in complexity.lower()
    })

    results.append({
        "criterion": "assumptions",
        "passed": len(assumptions) > 0
    })

    return results
