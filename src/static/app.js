const elements = {
  problem: document.querySelector("#problem-select"),
  summary: document.querySelector("#problem-summary"),
  cases: document.querySelector("#case-summary"),
  reasoning: document.querySelector("#reasoning"),
  claimed: document.querySelector("#claimed-results"),
  code: document.querySelector("#source-code"),
  evaluate: document.querySelector("#evaluate-button"),
  error: document.querySelector("#error-message"),
  empty: document.querySelector("#empty-state"),
  report: document.querySelector("#report-panel"),
  state: document.querySelector("#report-state")
};

let problems = [];
let currentReport = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
}

function selectedProblem() {
  if (elements.problem.value === "__custom__") {
    try {
      return JSON.parse(document.querySelector("#custom-problem").value);
    } catch {
      return null;
    }
  }
  return problems.find(problem => problem.id === elements.problem.value);
}

function makeCaseTemplate(problem) {
  if (!problem) throw new Error("Enter a valid custom problem JSON specification first.");
  return problem.validation_cases.map((testCase, index) => {
    const caseId = testCase.case_id || testCase.test_id || `case_${index + 1}`;
    if (problem.validator === "two_sum") {
      return { case_id: caseId, indices: null };
    }
    return { case_id: caseId, result: null };
  });
}

function updateProblem() {
  const problem = selectedProblem();
  const isCustom = elements.problem.value === "__custom__";
  document.querySelector("#custom-problem-wrap").hidden = !isCustom;
  document.querySelector("#problem-summary").hidden = isCustom;
  document.querySelector("#case-summary").hidden = isCustom;
  document.querySelector("#case-caption").hidden = isCustom;
  if (isCustom) {
    const specification = document.querySelector("#custom-problem");
    if (!specification.value) {
      specification.value = JSON.stringify({
        id: "custom_binary_search",
        title: "Custom binary search",
        question: "Search a sorted array and return the matching index, or -1.",
        function_name: "binary_search",
        validator: "exact",
        reasoning_rubric: {
          criteria: [{
            name: "Binary-search strategy",
            concepts: ["binary_search"],
            maximum: 100
          }]
        },
        validation_cases: [
          { case_id: "found", args: [[1, 3, 5, 7], 5], expected: 2 },
          { case_id: "missing", args: [[1, 3, 5, 7], 2], expected: -1 }
        ]
      }, null, 2);
    }
    let functionName = "solution";
    try {
      functionName = JSON.parse(specification.value).function_name || functionName;
    } catch {
      // The form reports invalid problem JSON when the user runs evaluation.
    }
    elements.code.value = `def ${functionName}(*args, **kwargs):\n    # Implement the required function\n    pass`;
    return;
  }
  if (!problem) return;
  elements.summary.textContent = problem.question || "No problem description provided.";
  elements.cases.replaceChildren();
  for (const [index, testCase] of problem.validation_cases.entries()) {
    const chip = document.createElement("div");
    chip.className = "case-chip";
    const id = document.createElement("strong");
    id.textContent = testCase.case_id || testCase.test_id || `case_${index + 1}`;
    const inputs = document.createElement("small");
    const args = testCase.args || (
      problem.validator === "two_sum"
        ? [testCase.values, testCase.target]
        : []
    );
    inputs.textContent = `input: ${JSON.stringify(args)}`;
    chip.append(id, inputs);
    elements.cases.append(chip);
  }
  elements.code.value = problem.starter_code || "";
}

function updateCounts() {
  document.querySelector("#reasoning-count").textContent =
    `${elements.reasoning.value.length} characters`;
  document.querySelector("#code-count").textContent =
    `${elements.code.value.split("\n").length} lines`;
}

function setChildren(selector, rows) {
  document.querySelector(selector).replaceChildren(...rows);
}

function createCaseRow(result) {
  const row = document.createElement("div");
  row.className = "case-row";
  const icon = document.createElement("span");
  icon.className = `case-icon${result.passed ? "" : " fail"}`;
  icon.textContent = result.passed ? "✓" : "×";
  const content = document.createElement("div");
  content.className = "case-content";
  const title = document.createElement("strong");
  title.textContent = result.case_id || `Case ${result.test_case}`;
  const detail = document.createElement("span");
  detail.textContent = result.feedback || "";
  content.append(title, detail);
  row.append(icon, content);
  return row;
}

function renderReport(report) {
  currentReport = report;
  const evaluation = report.evaluation;
  elements.empty.hidden = true;
  elements.report.hidden = false;
  const verdict = (evaluation.verdict || "FAIL").toLowerCase();
  elements.state.className = `status-pill ${verdict}`;
  elements.state.innerHTML = `<span></span>${escapeHtml(evaluation.verdict)} · COMPLETE`;

  document.querySelector("#overall-score").textContent = evaluation.score;
  const badge = document.querySelector("#verdict-badge");
  badge.textContent = evaluation.verdict;
  badge.className = `verdict-badge ${verdict}`;
  document.querySelector("#overall-track").style.width =
    `${Math.max(0, Math.min(100, evaluation.score))}%`;
  document.querySelector("#score-caption").textContent =
    evaluation.score >= 80 ? "Strong submission" :
      evaluation.score >= 50 ? "Review feedback" : "Needs improvement";

  const categories = [
    ["Reasoning quality", "reasoning_score", 40],
    ["Claimed results", "validation_score", 20],
    ["Code execution", "execution_score", 25],
    ["Reasoning / code", "consistency_score", 15]
  ];
  const breakdown = categories.map(([label, key, weight]) => {
    const score = Math.max(0, Math.min(100, evaluation[key] || 0));
    const row = document.createElement("div");
    row.className = "score-row";
    const title = document.createElement("span");
    title.className = "score-row-label";
    title.innerHTML = `${escapeHtml(label)} <small>${weight}%</small>`;
    const value = document.createElement("span");
    value.className = "score-row-score";
    value.textContent = `${score}`;
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("span");
    fill.style.width = `${score}%`;
    track.append(fill);
    row.append(title, value, track);
    return row;
  });
  setChildren("#score-breakdown", breakdown);

  const claimed = evaluation.validation_details?.results || [];
  document.querySelector("#claimed-count").textContent =
    `${claimed.filter(item => item.passed).length}/${claimed.length} passed`;
  setChildren("#claimed-list", claimed.map(createCaseRow));

  document.querySelector("#execution-status").textContent =
    evaluation.execution_status || "UNKNOWN";
  document.querySelector("#execution-summary").textContent =
    `${evaluation.execution_passed_cases || 0} of ${evaluation.execution_total_cases || 0} cases passed`;
  const execution = evaluation.execution_details?.results || [];
  setChildren("#execution-list", execution.map(createCaseRow));

  const reasoning = evaluation.reasoning_details || {};
  document.querySelector("#reasoning-verdict").textContent =
    reasoning.verdict || "NOT EVALUATED";
  const rubric = (reasoning.criteria || []).map(item =>
    createRubricRow(item.name, item.passed, `${item.score}/${item.maximum}`)
  );
  setChildren("#reasoning-list", rubric);

  const consistency = evaluation.consistency_details || {};
  document.querySelector("#consistency-verdict").textContent =
    consistency.verdict || "NOT EVALUATED";
  document.querySelector("#consistency-feedback").textContent =
    consistency.feedback || "";
  setChildren("#consistency-list", (consistency.findings || []).map(item =>
    createRubricRow(item.criterion, item.passed, item.passed ? "CONSISTENT" : "REVIEW")
  ));
  document.querySelector("#report-panel").scrollIntoView({
    behavior: "smooth",
    block: "nearest"
  });
}

function createRubricRow(name, passed, score) {
  const row = document.createElement("div");
  row.className = "rubric-row";
  const title = document.createElement("strong");
  title.textContent = name || "Criterion";
  const status = document.createElement("span");
  status.className = passed ? "" : "fail";
  status.textContent = score;
  row.append(title, status);
  return row;
}

async function submitEvaluation() {
  elements.error.hidden = true;
  elements.error.textContent = "";
  elements.evaluate.disabled = true;
  elements.evaluate.querySelector("span:first-child").textContent = "Evaluating…";
  try {
    let candidateResults = [];
    if (elements.claimed.value.trim()) {
      candidateResults = JSON.parse(elements.claimed.value);
      if (!Array.isArray(candidateResults) && (
        candidateResults === null || typeof candidateResults !== "object"
      )) {
        throw new Error("Claimed results must be a JSON array or object.");
      }
    }
    const response = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...(elements.problem.value === "__custom__"
          ? { problem: JSON.parse(document.querySelector("#custom-problem").value) }
          : { problem_id: elements.problem.value }),
        answer: elements.reasoning.value,
        candidate_results: candidateResults,
        source_code: elements.code.value
      })
    });
    const report = await response.json();
    if (!response.ok) throw new Error(report.error || "Evaluation failed.");
    renderReport(report);
  } catch (error) {
    elements.error.textContent = error.message || "Unable to evaluate submission.";
    elements.error.hidden = false;
  } finally {
    elements.evaluate.disabled = false;
    elements.evaluate.querySelector("span:first-child").textContent = "Run evaluation";
  }
}

function downloadJson() {
  if (!currentReport) return;
  const blob = new Blob(
    [JSON.stringify(currentReport, null, 2)],
    { type: "application/json" }
  );
  triggerDownload(blob, `${safeFilename(currentReport.problem.id)}-report.json`);
}

async function downloadPdf() {
  if (!currentReport) return;
  const button = document.querySelector("#download-pdf");
  button.disabled = true;
  try {
    const response = await fetch("/api/report.pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report: currentReport })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "PDF report generation failed.");
    }
    triggerDownload(
      await response.blob(),
      `${safeFilename(currentReport.problem.id)}-report.pdf`
    );
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    button.disabled = false;
  }
}

function safeFilename(value) {
  return String(value || "evaluation").replace(/[^a-z0-9_-]+/gi, "-");
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

async function initialize() {
  try {
    const response = await fetch("/api/problems");
    if (!response.ok) throw new Error("Unable to load problem library.");
    problems = await response.json();
    for (const problem of problems) {
      const option = document.createElement("option");
      option.value = problem.id;
      option.textContent = `${problem.title} · ${problem.difficulty || "custom"}`;
      elements.problem.append(option);
    }
    const customOption = document.createElement("option");
    customOption.value = "__custom__";
    customOption.textContent = "Custom problem · your specification";
    elements.problem.append(customOption);
    if (!problems.length) throw new Error("No problems are configured yet.");
    updateProblem();
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
    elements.evaluate.disabled = true;
  }
}

elements.problem.addEventListener("change", updateProblem);
elements.reasoning.addEventListener("input", updateCounts);
elements.code.addEventListener("input", updateCounts);
document.querySelector("#results-template").addEventListener("click", () => {
  try {
    elements.claimed.value = JSON.stringify(makeCaseTemplate(selectedProblem()), null, 2);
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  }
});
elements.evaluate.addEventListener("click", submitEvaluation);
document.querySelector("#download-json").addEventListener("click", downloadJson);
document.querySelector("#download-pdf").addEventListener("click", downloadPdf);
initialize();
