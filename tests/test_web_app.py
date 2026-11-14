import http.client
import json
import threading

import pytest

from src.reporting import build_evaluation_report, render_pdf_report
from src.web_app import create_server, validate_problem_spec


@pytest.fixture
def application_server():
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def request_json(address, method, path, payload=None):
    connection = http.client.HTTPConnection(*address, timeout=15)
    body = None if payload is None else json.dumps(payload)
    headers = {"Content-Type": "application/json"} if body else {}
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    content = response.read()
    content_type = response.getheader("Content-Type", "")
    connection.close()
    return response.status, content_type, content


def test_problem_library_hides_expected_outputs(application_server):
    status, _, content = request_json(
        application_server,
        "GET",
        "/api/problems"
    )
    problems = json.loads(content)

    assert status == 200
    assert {problem["id"] for problem in problems} >= {
        "problem_001",
        "problem_002",
        "problem_003"
    }
    for problem in problems:
        assert all(
            "expected" not in case
            for case in problem["validation_cases"]
        )


def test_problem_spec_rejects_duplicate_case_ids():
    problem = {
        "function_name": "solve",
        "validator": "exact",
        "validation_cases": [
            {"case_id": "same", "args": [], "expected": 1},
            {"case_id": "same", "args": [], "expected": 2}
        ]
    }

    with pytest.raises(ValueError, match="Duplicate test case id"):
        validate_problem_spec(problem)


def test_local_api_evaluates_custom_problem(application_server):
    problem = {
        "id": "test_palindrome",
        "title": "Palindrome",
        "question": "Check if the text is a palindrome.",
        "function_name": "is_palindrome",
        "validator": "exact",
        "reasoning_rubric": {
            "criteria": [{
                "name": "Palindrome property",
                "concepts": ["palindrome"],
                "maximum": 100
            }]
        },
        "validation_cases": [
            {"case_id": "yes", "args": ["level"], "expected": True},
            {"case_id": "no", "args": ["python"], "expected": False}
        ]
    }
    payload = {
        "problem": problem,
        "answer": "A palindrome reads the same forwards and backwards.",
        "candidate_results": [
            {"case_id": "yes", "result": True},
            {"case_id": "no", "result": False}
        ],
        "source_code": """
def is_palindrome(value):
    return value == value[::-1]
"""
    }

    status, content_type, content = request_json(
        application_server,
        "POST",
        "/api/evaluate",
        payload
    )
    report = json.loads(content)

    assert status == 200
    assert content_type.startswith("application/json")
    assert report["evaluation"]["verdict"] == "PASS"
    assert report["evaluation"]["execution_score"] == 100
    assert "expected" not in report["problem"]


def test_pdf_report_has_valid_header_and_cross_reference():
    problem = {"id": "p1", "title": "Example"}
    evaluation = {
        "score": 100,
        "verdict": "PASS",
        "reasoning_score": 100,
        "validation_score": 100,
        "execution_score": 100,
        "consistency_score": 100,
        "validation_details": {"results": []},
        "execution_details": {"results": []},
        "reasoning_details": {"criteria": []},
        "consistency_details": {"findings": []}
    }
    report = build_evaluation_report(
        problem,
        evaluation,
        {"answer": "All good."}
    )

    pdf = render_pdf_report(report)

    assert pdf.startswith(b"%PDF-1.4")
    assert b"startxref" in pdf
    assert b"Evaluation report" in pdf


def test_pdf_download_endpoint_returns_attachment(application_server):
    payload = {
        "report": {
            "problem": {"id": "sample", "title": "Sample problem"},
            "submission": {"answer": "A concise explanation."},
            "evaluation": {
                "score": 75,
                "verdict": "PARTIAL",
                "reasoning_score": 80,
                "validation_score": 60,
                "execution_score": 90,
                "consistency_score": 70,
                "validation_details": {"results": []},
                "execution_details": {"results": []},
                "reasoning_details": {"criteria": []},
                "consistency_details": {"findings": []}
            }
        }
    }

    status, content_type, content = request_json(
        application_server,
        "POST",
        "/api/report.pdf",
        payload
    )

    assert status == 200
    assert content_type == "application/pdf"
    assert content.startswith(b"%PDF-1.4")
