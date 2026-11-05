import ast


UNSAFE_FUNCTIONS = {
    "eval",
    "exec",
    "compile",
}

UNSAFE_MODULES = {
    "pickle",
    "marshal",
}

UNSAFE_SUBPROCESS_FUNCTIONS = {
    "run",
    "Popen",
    "call",
    "check_call",
    "check_output",
}


def check_code_security(source_code):
    """
    Perform basic static security checks on Python source code.

    This function does not execute the submitted code.
    """

    findings = []

    # Step 1: Parse the Python source code
    try:
        tree = ast.parse(source_code)

    except SyntaxError as error:
        return {
            "passed": False,
            "findings": [f"Syntax error: {error}"]
        }

    # Step 2: Inspect the code structure
    for node in ast.walk(tree):

        # Check function calls
        if isinstance(node, ast.Call):

            # Detect eval(), exec(), and compile()
            if (
                isinstance(node.func, ast.Name)
                and node.func.id in UNSAFE_FUNCTIONS
            ):
                findings.append(
                    f"Potentially unsafe function: {node.func.id}()"
                )

            # Detect os.system()
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr == "system"
            ):
                findings.append(
                    "Potentially unsafe command execution: os.system()"
                )

            # Detect subprocess calls using shell=True
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in UNSAFE_SUBPROCESS_FUNCTIONS
            ):
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        findings.append(
                            "Potentially unsafe subprocess call: shell=True"
                        )

        # Check imported modules
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]

                if module_name in UNSAFE_MODULES:
                    findings.append(
                        f"Potentially unsafe module import: {module_name}"
                    )

        # Check from-import statements
        if isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split(".")[0]

                if module_name in UNSAFE_MODULES:
                    findings.append(
                        f"Potentially unsafe module import: {module_name}"
                    )

    # Step 3: Return the security assessment
    return {
        "passed": len(findings) == 0,
        "findings": findings
    }