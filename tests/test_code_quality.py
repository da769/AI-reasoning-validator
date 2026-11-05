from src.validators.code_quality import check_code_security


def test_safe_code():
    code = """
def add(a, b):
    return a + b
"""

    result = check_code_security(code)

    assert result["passed"] is True
    assert result["findings"] == []


def test_detect_eval():
    code = """
result = eval("2 + 2")
"""

    result = check_code_security(code)

    assert result["passed"] is False
    assert any("eval" in finding for finding in result["findings"])


def test_detect_exec():
    code = """
exec("print('Hello')")
"""

    result = check_code_security(code)

    assert result["passed"] is False


def test_detect_unsafe_import():
    code = """
import pickle
"""

    result = check_code_security(code)

    assert result["passed"] is False
    assert any("pickle" in finding for finding in result["findings"])


def test_detect_os_system():
    code = """
import os
os.system("some-command")
"""

    result = check_code_security(code)

    assert result["passed"] is False


def test_detect_subprocess_shell():
    code = """
import subprocess
subprocess.run(["some-command"], shell=True)
"""

    result = check_code_security(code)

    assert result["passed"] is False


def test_detect_syntax_error():
    code = """
def broken_function(
"""

    result = check_code_security(code)

    assert result["passed"] is False
    assert any("Syntax error" in finding for finding in result["findings"])