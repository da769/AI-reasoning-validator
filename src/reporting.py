import json
import textwrap
from datetime import datetime, timezone


def build_evaluation_report(problem, evaluation, submission):
    return {
        "report_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "problem": {
            "id": problem.get("id", "custom"),
            "title": problem.get("title", "Custom problem"),
            "question": problem.get("question", "")
        },
        "submission": submission,
        "evaluation": evaluation
    }


def _display(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def _report_lines(report):
    evaluation = report["evaluation"]
    problem = report["problem"]
    lines = [
        "AI Computer Science Reasoning Validator",
        "Evaluation report",
        "",
        f"Problem: {problem.get('title', 'Custom problem')}",
        f"Problem ID: {problem.get('id', 'custom')}",
        f"Generated: {report.get('generated_at', '')}",
        f"Overall score: {evaluation.get('score', 0)}/100",
        f"Verdict: {evaluation.get('verdict', 'UNKNOWN')}",
        "",
        "Score breakdown"
    ]

    for label, key, weight in (
        ("Reasoning", "reasoning_score", 40),
        ("Claimed results", "validation_score", 20),
        ("Code execution", "execution_score", 25),
        ("Reasoning/code consistency", "consistency_score", 15)
    ):
        lines.append(
            f"{label}: {evaluation.get(key, 0)}/100 "
            f"(weighted {evaluation.get('weighted_' + key.replace('_score', '_score'), 0)}/{weight})"
        )

    lines.extend(["", "Claimed-result validation"])
    for result in evaluation.get("validation_details", {}).get("results", []):
        status = "PASS" if result.get("passed") else "FAIL"
        lines.append(
            f"{result.get('case_id', 'case')}: {status} - "
            f"{result.get('feedback', '')}"
        )

    lines.extend(["", "Code execution"])
    lines.append(
        f"Status: {evaluation.get('execution_status', 'UNKNOWN')}; "
        f"{evaluation.get('execution_passed_cases', 0)}/"
        f"{evaluation.get('execution_total_cases', 0)} cases passed"
    )
    for result in evaluation.get("execution_details", {}).get("results", []):
        status = "PASS" if result.get("passed") else "FAIL"
        lines.append(
            f"{result.get('case_id', result.get('test_case', 'case'))}: "
            f"{status} - {result.get('feedback', '')}"
        )

    lines.extend(["", "Reasoning rubric"])
    for criterion in evaluation.get("reasoning_details", {}).get(
        "criteria", []
    ):
        status = "PASS" if criterion.get("passed") else "NEEDS REVIEW"
        lines.append(
            f"{criterion.get('name', 'Criterion')}: {status} "
            f"({criterion.get('score', 0)}/{criterion.get('maximum', 0)})"
        )

    lines.extend(["", "Consistency findings"])
    consistency = evaluation.get("consistency_details", {})
    lines.append(
        f"Verdict: {consistency.get('verdict', 'UNKNOWN')} - "
        f"{consistency.get('feedback', '')}"
    )
    for finding in consistency.get("findings", []):
        status = "PASS" if finding.get("passed") else "CHECK"
        lines.append(
            f"{status}: {finding.get('criterion', 'Finding')} - "
            f"{finding.get('feedback', '')}"
        )

    submission = report.get("submission", {})
    lines.extend(["", "Submitted reasoning"])
    reasoning = _display(submission.get("answer", ""))
    lines.extend(reasoning.splitlines() or ["(not provided)"])

    code = submission.get("source_code", "")
    if code:
        lines.extend(["", "Submitted Python implementation"])
        lines.extend(code.splitlines())

    return [
        wrapped
        for line in lines
        for wrapped in (
            textwrap.wrap(
                line,
                width=92,
                replace_whitespace=False,
                drop_whitespace=False
            ) or [""]
        )
    ]


def render_pdf_report(report):
    lines = _report_lines(report)
    page_size = 48
    page_lines = [
        lines[index:index + page_size]
        for index in range(0, len(lines), page_size)
    ] or [[]]

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        None,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>"
    ]
    page_ids = []

    for page in page_lines:
        page_id = len(objects) + 1
        content_id = page_id + 1
        page_ids.append(page_id)
        objects.extend([None, None])

        commands = ["BT", "/F1 10 Tf", "50 790 Td"]
        for index, line in enumerate(page):
            if index:
                commands.append("0 -14 Td")
            safe_line = "".join(
                character
                for character in line
                if character >= " " and character != "\x7f"
            )
            encoded_line = safe_line.encode("cp1252", errors="replace")
            escaped_line = (
                encoded_line
                .replace(b"\\", b"\\\\")
                .replace(b"(", b"\\(")
                .replace(b")", b"\\)")
            )
            commands.append(b"(" + escaped_line + b") Tj")
        commands.append("ET")
        stream = b"\n".join(
            item if isinstance(item, bytes) else item.encode("ascii")
            for item in commands
        )

        objects[page_id - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id - 1] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"\nendstream"
        )

    objects[1] = (
        f"<< /Type /Pages /Kids "
        f"[{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
        f"/Count {len(page_ids)} >>"
    ).encode("ascii")

    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(
            f"{object_id} 0 obj\n".encode("ascii")
            + body
            + b"\nendobj\n"
        )

    xref_offset = len(document)
    document.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    document.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(document)
