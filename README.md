# Reasoning Lab

Reasoning Lab is a local web application for evaluating computer-science
submissions. It assesses written reasoning against a configurable rubric,
checks claimed outputs against reference cases, runs the required Python
function against those cases, and compares selected algorithm claims with
the implementation structure.

The application works offline and does not call an AI service. Reasoning
assessment is rubric-based and deterministic; it is not a general-purpose
proof checker.

## Features

- Responsive browser interface for built-in or custom problem specifications.
- Separate reasoning, claimed-output, execution, and consistency scores.
- Independent output validation: expected values are not sent to the browser
  when it loads the built-in problem library.
- JSON and PDF evaluation report downloads.
- Problem-specific required function names and exact-output or Two Sum
  validators.
- Built-in Two Sum, Binary Search, and Palindrome Check examples.

## Requirements and setup

Python 3.10 or later is recommended. The application uses the Python standard
library; `pytest` is only needed to run tests.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If dependencies are already installed in your environment, no install step is
needed. Run the application from the repository root:

```powershell
python run_app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server binds to
loopback by default. Stop it with `Ctrl+C`.

To select another local interface or port:

```powershell
python run_app.py --host 127.0.0.1 --port 8080
```

Do not bind to a public interface when evaluating untrusted submissions.

## Using the evaluator

1. Select a built-in task or choose **Custom problem** and edit its JSON
   specification.
2. Explain the approach in plain language. Structured answer text is accepted
   too.
3. Optionally enter claimed outputs as a JSON array, or insert a case template.
   Use `case_id` (or `test_id`) and `indices` for Two Sum; use `case_id` and
   `result` for exact-output problems.
4. Implement the configured function in Python.
5. Run the evaluation, inspect each score and case result, and download a JSON
   or PDF report.

Claimed outputs and executed outputs are scored separately. A correct written
explanation does not excuse failing code, and passing code does not establish
that the submitted explanation is correct.

## Adding a problem

Add a JSON file under `data/problems/`. Each problem needs a unique `id`, a
`function_name`, a supported `validator`, and non-empty `validation_cases`.
Problems can also be supplied directly in the custom-problem editor.

### Two Sum problem

Use `"validator": "two_sum"`. Cases have `values` and `target`; the required
function accepts those as two positional arguments and returns a pair of
distinct indices. The independent validator checks index types, bounds,
distinctness, and the sum.

### Exact-output problem

Use `"validator": "exact"`. Cases have positional `args` (and optional
`kwargs`) and an `expected` value. The function's return value is compared
recursively and with strict JSON type equality. For example, `true` is not
accepted in place of `1`.

### Reasoning rubric

An optional `reasoning_rubric` lets each problem define weighted criteria:

```json
{
  "reasoning_rubric": {
    "criteria": [
      {
        "name": "Binary-search strategy",
        "concepts": ["binary_search", "sorted_input"],
        "maximum": 60
      },
      {
        "name": "Logarithmic complexity",
        "concepts": ["logarithmic_time"],
        "maximum": 40
      }
    ]
  }
}
```

Each criterion passes only when evidence for each listed concept is found in
the response. Built-in concept aliases and optional `concept_aliases` in the
problem JSON support common paraphrases. This is a transparent lexical
heuristic: negated phrases are filtered, but nuanced claims, proofs, and
mathematical equivalence are not understood. Without a rubric, the legacy
Two Sum-specific rubric is used.

The consistency checker uses Python AST structure and known algorithm signals;
it can flag obvious contradictions (for example, a hash-map claim with no
dictionary, or a binary-search claim with no recognizable bounds/midpoint
pattern). It does not prove program semantics or infer the true asymptotic
complexity of arbitrary Python.

## Architecture

```text
run_app.py
  └── src/web_app.py             Local HTTP interface and input validation
       ├── src/evaluator.py      Weighted evaluation orchestration
       ├── src/validators/
       │    ├── reasoning.py     Problem rubric and built-in concept matching
       │    ├── algorithm.py     Independent output validators
       │    ├── code_execution.py
       │    └── consistency.py   AST and explanation-claim checks
       ├── src/reporting.py      JSON report model and PDF generation
       └── src/static/           Browser interface

data/problems/                   Built-in problem specifications
tests/                           Evaluator, API, and report regression tests
```

## Reports

The downloadable JSON includes the problem metadata, submission, timestamp,
all score details, case outcomes, and feedback. The PDF presents the same
evaluation in a printable summary. Reports are generated locally by the
application; the JSON report includes the submitted reasoning and source
code, so treat downloaded reports as private.

## Running tests

```powershell
python -m pytest -q
```

## Important safety limitation

Submitted Python code is executed in a child Python process with a timeout and
preliminary static checks. **This is not a secure sandbox.** It does not
prevent filesystem or network access, resource abuse, or all forms of harmful
code behavior. Only evaluate code you trust, keep the server bound to
`127.0.0.1`, and do not expose this service to the internet or use it for
multi-user evaluation of untrusted submissions. A production deployment needs
a separately isolated execution service with operating-system-enforced
resource and network restrictions.
