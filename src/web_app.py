import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from src.evaluator import evaluate_response
from src.reporting import build_evaluation_report, render_pdf_report


ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIRECTORY = ROOT / "data" / "problems"
STATIC_DIRECTORY = Path(__file__).resolve().parent / "static"
MAX_REQUEST_SIZE = 1_000_000
MAX_SOURCE_SIZE = 80_000


def load_problems():
    problems = []
    seen_ids = set()

    for path in sorted(PROBLEMS_DIRECTORY.glob("*.json")):
        with path.open(encoding="utf-8") as file:
            problem = json.load(file)
        validate_problem_spec(problem)
        problem_id = problem.get("id")
        if problem_id in seen_ids:
            raise ValueError(f"Duplicate problem id: {problem_id}")
        seen_ids.add(problem_id)
        problems.append(problem)

    return problems


def validate_problem_spec(problem):
    if not isinstance(problem, dict):
        raise ValueError("A problem specification must be a JSON object.")

    function_name = problem.get("function_name", "two_sum")
    if not isinstance(function_name, str) or not function_name.isidentifier():
        raise ValueError("The required function_name must be a valid identifier.")

    validator = problem.get("validator", "two_sum")
    if validator not in {"two_sum", "exact"}:
        raise ValueError("validator must be either 'two_sum' or 'exact'.")

    cases = problem.get("validation_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one validation case is required.")

    ids = set()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Test case {index} must be a JSON object.")

        case_id = case.get("case_id", case.get("test_id", f"case_{index:03d}"))
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"Test case {index} requires a non-empty id.")
        if case_id in ids:
            raise ValueError(f"Duplicate test case id: {case_id}")
        ids.add(case_id)

        if "args" in case:
            if (
                not isinstance(case["args"], list)
                or not isinstance(case.get("kwargs", {}), dict)
            ):
                raise ValueError(
                    f"Test case {case_id}: args must be an array and "
                    "kwargs must be an object."
                )
        elif validator == "two_sum" and not all(
            name in case for name in ("values", "target")
        ):
            raise ValueError(
                f"Test case {case_id}: Two Sum requires values and target."
            )

        if validator == "exact" and "expected" not in case:
            raise ValueError(
                f"Test case {case_id}: exact-match validation requires expected."
            )

    rubric = problem.get("reasoning_rubric", {})
    if rubric and (
        not isinstance(rubric, dict)
        or not isinstance(rubric.get("criteria"), list)
    ):
        raise ValueError("reasoning_rubric.criteria must be an array.")


def _public_problem(problem):
    public = {
        key: value
        for key, value in problem.items()
        if key != "validation_cases"
    }
    public["validation_cases"] = []

    for case in problem["validation_cases"]:
        public_case = {
            key: value
            for key, value in case.items()
            if key != "expected"
        }
        public["validation_cases"].append(public_case)

    return public


class EvaluationRequestHandler(BaseHTTPRequestHandler):
    server_version = "AIReasoningValidator/1.0"

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self._send_file(STATIC_DIRECTORY / "index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            self._send_file(
                STATIC_DIRECTORY / "styles.css",
                "text/css; charset=utf-8"
            )
        elif path == "/app.js":
            self._send_file(
                STATIC_DIRECTORY / "app.js",
                "text/javascript; charset=utf-8"
            )
        elif path == "/api/problems":
            self._send_json([
                _public_problem(problem)
                for problem in load_problems()
            ])
        else:
            self._send_json({"error": "Not found."}, status=404)

    def do_POST(self):
        path = urlsplit(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/evaluate":
                self._evaluate(payload)
            elif path == "/api/report.pdf":
                self._download_pdf(payload)
            else:
                self._send_json({"error": "Not found."}, status=404)
        except ValueError as error:
            self._send_json({"error": str(error)}, status=400)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid Content-Length header.") from error

        if length < 1 or length > MAX_REQUEST_SIZE:
            raise ValueError(
                f"Request body must be between 1 and {MAX_REQUEST_SIZE} bytes."
            )

        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("Request body must contain valid JSON.") from error

    def _evaluate(self, payload):
        if not isinstance(payload, dict):
            raise ValueError("Evaluation request must be a JSON object.")

        if "problem" in payload:
            problem = payload["problem"]
        else:
            problem_id = payload.get("problem_id")
            problem = next(
                (
                    item
                    for item in load_problems()
                    if item.get("id") == problem_id
                ),
                None
            )
            if problem is None:
                raise ValueError("Select a supported problem.")

        validate_problem_spec(problem)

        source_code = payload.get("source_code", "")
        if not isinstance(source_code, str):
            raise ValueError("source_code must be a string.")
        if len(source_code) > MAX_SOURCE_SIZE:
            raise ValueError(
                f"source_code must not exceed {MAX_SOURCE_SIZE} characters."
            )

        answer = payload.get("answer", "")
        if not isinstance(answer, (str, dict, list)):
            raise ValueError("answer must be text, an object, or an array.")
        candidate_results = payload.get("candidate_results", [])
        if not isinstance(candidate_results, (dict, list)):
            raise ValueError("candidate_results must be an array or object.")

        response = {
            "answer": answer,
            "candidate_results": candidate_results
        }
        evaluation = evaluate_response(
            response,
            problem,
            source_code=source_code
        )
        report = build_evaluation_report(
            problem,
            evaluation,
            {
                "answer": answer,
                "candidate_results": candidate_results,
                "source_code": source_code
            }
        )
        self._send_json(report)

    def _download_pdf(self, payload):
        if not isinstance(payload, dict) or not isinstance(
            payload.get("report"), dict
        ):
            raise ValueError("A report object is required.")

        report = payload["report"]
        if not isinstance(report.get("evaluation"), dict):
            raise ValueError("The report must include evaluation results.")

        filename_part = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "-",
            report.get("problem", {}).get("id", "evaluation")
        ).strip("-") or "evaluation"
        content = render_pdf_report(report)
        self._send_bytes(
            content,
            "application/pdf",
            f'attachment; filename="{filename_part}-report.pdf"'
        )

    def _send_file(self, path, content_type):
        try:
            content = path.read_bytes()
        except OSError:
            self._send_json({"error": "The application interface is missing."}, 500)
            return
        self._send_bytes(content, content_type)

    def _send_json(self, value, status=200):
        content = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self._send_bytes(content, "application/json; charset=utf-8", status=status)

    def _send_bytes(
        self,
        content,
        content_type,
        content_disposition=None,
        status=200
    ):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'"
        )
        self.send_header("Cache-Control", "no-store")
        if content_disposition:
            self.send_header("Content-Disposition", content_disposition)
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string, *args):
        print(
            "%s - %s"
            % (self.address_string(), format_string % args)
        )


def create_server(host="127.0.0.1", port=8000):
    return ThreadingHTTPServer((host, port), EvaluationRequestHandler)
