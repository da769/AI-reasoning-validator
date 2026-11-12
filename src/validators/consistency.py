import ast
import re


def analyze_code_structure(source_code):
    """
    Analyze Python code using AST.

    Identifies:
    - Dictionary usage
    - Nested loops
    - Function definitions
    - Loop structures
    """

    try:
        tree = ast.parse(source_code)

    except SyntaxError as error:
        return {
            "passed": False,
            "feedback": f"Unable to analyze code: {error}",
            "features": {}
        }

    features = {
        "uses_dictionary": False,
        "uses_nested_loops": False,
        "has_two_sum_function": False,
        "uses_loops": False
    }

    class CodeAnalyzer(ast.NodeVisitor):

        def __init__(self):
            self.loop_depth = 0

        def visit_FunctionDef(self, node):

            if node.name == "two_sum":
                features["has_two_sum_function"] = True

            self.generic_visit(node)

        def visit_Dict(self, node):
            features["uses_dictionary"] = True
            self.generic_visit(node)

        def visit_For(self, node):

            features["uses_loops"] = True

            self.loop_depth += 1

            if self.loop_depth >= 2:
                features["uses_nested_loops"] = True

            self.generic_visit(node)

            self.loop_depth -= 1

        def visit_While(self, node):

            features["uses_loops"] = True

            self.loop_depth += 1

            if self.loop_depth >= 2:
                features["uses_nested_loops"] = True

            self.generic_visit(node)

            self.loop_depth -= 1

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    return {
        "passed": True,
        "feedback": "Code structure analyzed successfully.",
        "features": features
    }


def analyze_reasoning_claims(answer):
    """
    Identify algorithm and complexity claims
    in the written explanation.
    """

    answer = answer.lower()

    claims = {
        "claims_hash_map": False,
        "claims_nested_loops": False,
        "claims_linear_time": False,
        "claims_quadratic_time": False
    }

    # Hash map claims
    hash_map_patterns = [
        r"hash\s*map",
        r"dictionary",
        r"dict\b"
    ]

    if any(
        re.search(pattern, answer)
        for pattern in hash_map_patterns
    ):
        claims["claims_hash_map"] = True

    # Nested-loop claims
    if (
        "nested loop" in answer
        or "two loops" in answer
        or "double loop" in answer
    ):
        claims["claims_nested_loops"] = True

    # Complexity claims
    if re.search(r"o\s*\(\s*n\s*\)", answer):
        claims["claims_linear_time"] = True

    if re.search(r"o\s*\(\s*n\s*(?:\*\s*n|²|\^2)\s*\)", answer):
        claims["claims_quadratic_time"] = True

    return claims


def evaluate_consistency(answer, source_code):
    """
    Compare written algorithm claims against
    the actual Python implementation.

    This is a heuristic consistency checker,
    not a complete semantic code analyzer.
    """

    code_analysis = analyze_code_structure(source_code)

    if not code_analysis["passed"]:
        return {
            "passed": False,
            "score": 0,
            "verdict": "FAIL",
            "feedback": code_analysis["feedback"],
            "findings": []
        }

    code_features = code_analysis["features"]

    reasoning_claims = analyze_reasoning_claims(answer)

    findings = []

    # Check whether a hash map is claimed and implemented
    if reasoning_claims["claims_hash_map"]:

        if code_features["uses_dictionary"]:

            findings.append({
                "criterion": "Hash map consistency",
                "passed": True,
                "feedback": (
                    "The explanation claims dictionary/hash map usage, "
                    "and the implementation contains a dictionary."
                )
            })

        else:

            findings.append({
                "criterion": "Hash map consistency",
                "passed": False,
                "feedback": (
                    "The explanation claims dictionary/hash map usage, "
                    "but no dictionary literal was detected."
                )
            })

    # Check nested-loop claims
    if reasoning_claims["claims_nested_loops"]:

        if code_features["uses_nested_loops"]:

            findings.append({
                "criterion": "Nested-loop consistency",
                "passed": True,
                "feedback": (
                    "The explanation describes nested loops, "
                    "and nested loops were detected."
                )
            })

        else:

            findings.append({
                "criterion": "Nested-loop consistency",
                "passed": False,
                "feedback": (
                    "The explanation describes nested loops, "
                    "but nested loops were not detected."
                )
            })

    # Check linear time claims
    if reasoning_claims["claims_linear_time"]:

        if code_features["uses_nested_loops"]:

            findings.append({
                "criterion": "Time complexity consistency",
                "passed": False,
                "feedback": (
                    "The explanation claims O(n) time, "
                    "but nested loops were detected. "
                    "This requires further complexity analysis."
                )
            })

        else:

            findings.append({
                "criterion": "Time complexity consistency",
                "passed": True,
                "feedback": (
                    "No nested loops were detected. "
                    "The O(n) claim is not contradicted by this "
                    "basic structural check."
                )
            })

    # Check quadratic time claims
    if reasoning_claims["claims_quadratic_time"]:

        if code_features["uses_nested_loops"]:

            findings.append({
                "criterion": "Time complexity consistency",
                "passed": True,
                "feedback": (
                    "The explanation claims O(n²), "
                    "and nested loops were detected."
                )
            })

        else:

            findings.append({
                "criterion": "Time complexity consistency",
                "passed": False,
                "feedback": (
                    "The explanation claims O(n²), "
                    "but nested loops were not detected."
                )
            })

    # Check required function
    if not code_features["has_two_sum_function"]:

        findings.append({
            "criterion": "Function availability",
            "passed": False,
            "feedback": (
                "The required two_sum function was not detected."
            )
        })

    # Calculate score
    if not findings:

        score = 100

        findings.append({
            "criterion": "General consistency",
            "passed": True,
            "feedback": (
                "No contradictory algorithm or complexity claims "
                "were detected."
            )
        })

    else:

        passed_findings = sum(
            1 for finding in findings
            if finding["passed"]
        )

        score = round(
            (passed_findings / len(findings)) * 100,
            2
        )

    # Determine verdict
    if score >= 80:
        verdict = "PASS"

    elif score >= 50:
        verdict = "PARTIAL"

    else:
        verdict = "FAIL"

    return {
        "passed": score >= 80,
        "score": score,
        "verdict": verdict,
        "feedback": (
            "Reasoning and implementation are broadly consistent."
            if score >= 80
            else "Potential inconsistencies were detected."
        ),
        "code_features": code_features,
        "reasoning_claims": reasoning_claims,
        "findings": findings
    }