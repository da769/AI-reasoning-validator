import ast


UNSAFE_FUNCTIONS = {
    "eval",
    "exec",
    "compile"
}

UNSAFE_MODULES = {
    "pickle",
    "marshal"
}


def check_code_security(source_code):

    findings = []

    try:
        tree = ast.parse(source_code)

    except SyntaxError as error:
        return {
            "passed": False,
            "findings": [
                f"Syntax error: {error}"
            ]
        }

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id in UNSAFE_FUNCTIONS:
                    findings.append(
                        f"Potentially unsafe function: {node.func.id}"
                    )

            if isinstance(node.func, ast.Attribute):

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                    and node.func.attr == "system"
                ):
                    findings.append(
                        "Potentially unsafe command execution: os.system"
                    )

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "subprocess"
                    and node.func.attr in {"run", "Popen", "call"}
                ):
                    for keyword in node.keywords:
                        if (
                            keyword.arg == "shell"
                            and isinstance(keyword.value, ast.Constant)
                            and keyword.value.value is True
                        ):
                            findings.append(
                                "Potentially unsafe subprocess shell=True"
                            )

        if isinstance(node, ast.Import):

            for alias in node.names:

                if alias.name in UNSAFE_MODULES:
                    findings.append(
                        f"Review unsafe deserialization module: {alias.name}"
                    )

        if isinstance(node, ast.ImportFrom):

            if node.module in UNSAFE_MODULES:
                findings.append(
                    f"Review unsafe deserialization module: {node.module}"
                )

    return {
        "passed": len(findings) == 0,
        "findings": findings
    }