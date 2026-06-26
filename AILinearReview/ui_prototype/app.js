const tabs = document.querySelectorAll(".tab");
const views = {
  practice: document.querySelector("#practiceView"),
  dialogue: document.querySelector("#dialogueView")
};

const segments = document.querySelectorAll(".segment");
const difficultyRange = document.querySelector("#difficultyRange");
const difficultyValue = document.querySelector("#difficultyValue");
const gradeButton = document.querySelector("#gradeButton");
const hintButton = document.querySelector("#hintButton");
const nextButton = document.querySelector("#nextButton");
const feedbackBox = document.querySelector("#feedbackBox");
const readinessScore = document.querySelector("#readinessScore");
const readinessBar = document.querySelector("#readinessBar");
const conceptList = document.querySelector("#conceptList");
const workflowSteps = document.querySelectorAll(".workflow-step");
const selectionNote = document.querySelector("#selectionNote");
const thetaValue = document.querySelector("#thetaValue");
const confidenceValue = document.querySelector("#confidenceValue");
const nextAction = document.querySelector("#nextAction");
const chunkValue = document.querySelector("#chunkValue");
const chatInput = document.querySelector("#chatInput");
const sendButton = document.querySelector("#sendButton");
const chatLog = document.querySelector("#chatLog");
const itemTitle = document.querySelector("#itemTitle");
const itemSource = document.querySelector("#itemSource");
const itemDifficulty = document.querySelector("#itemDifficulty");
const questionBox = document.querySelector("#questionBox");
const answerBox = document.querySelector("#answerBox");
const conceptChips = document.querySelector("#conceptChips");
const pathList = document.querySelector("#pathList");
const evidenceList = document.querySelector("#evidenceList");
const agentStatus = document.querySelector("#agentStatus");

let itemIndex = 0;
let theta = 0.31;
let lastAction = "Diagnose";
let reviewMode = "diagnostic";
const learnerStats = {
  gradedAttempts: 0,
  hintRequests: 0,
  lastScore: null,
  lastConfidence: 0.52
};

const conceptLabels = {
  eigenspace: "Eigenspace basis",
  nullspace: "Nullspace computation",
  diagonalization: "Diagonalization criterion",
  rank: "Rank",
  basis_dimension: "Basis and dimension",
  projection: "Orthogonal projection",
  orthogonality: "Orthogonality",
  least_squares: "Least squares",
  determinants: "Determinants",
  eigenvalues: "Eigenvalues",
  characteristic_polynomial: "Characteristic polynomial"
};

const mastery = {
  eigenspace: 42,
  nullspace: 55,
  diagonalization: 48,
  projection: 71,
  rank: 63,
  basis_dimension: 58,
  orthogonality: 67,
  least_squares: 52,
  determinants: 61,
  eigenvalues: 57,
  characteristic_polynomial: 50
};

let items = [];
let recentItemIds = [];

const fallbackItems = [
  {
    id: "eigenspace-diagonalization",
    source: "Recommended Item",
    title: "Eigenspace Basis and Diagonalization",
    difficulty: 0.58,
    concepts: ["eigenspace", "nullspace", "diagonalization"],
    questionHtml: `
      <p>Suppose that \\(2\\) is an eigenvalue of a matrix \\(A\\), and the reduced row echelon form of \\(A - 2I\\) is</p>
      <pre><code>[ 1  0 -1 ]
[ 0  1  2 ]
[ 0  0  0 ]</code></pre>
      <p>Find a basis for the corresponding eigenspace and explain how this step contributes to deciding whether \\(A\\) is diagonalizable.</p>
    `,
    starterAnswer: "x = z and y = -2z, so an eigenvector has the form z(1, -2, 1). A basis for the eigenspace is {(1, -2, 1)}. To test diagonalizability, we compare the total number of independent eigenvectors from all eigenspaces with the size of the matrix.",
    path: ["Nullspace computation", "Eigenspace basis", "Geometric multiplicity", "Diagonalization criterion"],
    activePathIndex: 1,
    evidence: [
      ["slides_md/five", "Diagonalization requires enough linearly independent eigenvectors to form a basis."],
      ["mit_linear_algebra_md/spring2014", "Final-exam problems often connect nullspace computation with diagonalizability."]
    ]
  },
  {
    id: "rank-nullity",
    source: "Adaptive Follow-up",
    title: "Rank-Nullity and Free Variables",
    difficulty: 0.46,
    concepts: ["rank", "nullspace", "basis_dimension"],
    questionHtml: `
      <p>A \\(4\\times 6\\) matrix has rank \\(3\\). Determine the dimension of its nullspace and explain which part of the row-reduction result gives this number.</p>
    `,
    starterAnswer: "The nullity is 6 - 3 = 3 by the rank-nullity theorem. In row reduction, the number of free variables is the number of non-pivot columns, which is also 3.",
    path: ["Pivot columns", "Free variables", "Nullspace dimension", "Rank-nullity theorem"],
    activePathIndex: 2,
    evidence: [
      ["slides_md/two", "Basis and dimension are used to describe solution spaces and nullspaces."],
      ["flipped_md/inclass/linear-systems", "Row-reduction activities repeatedly identify pivots and free variables."]
    ]
  },
  {
    id: "projection-least-squares",
    source: "Exam-Style Item",
    title: "Projection and Least Squares",
    difficulty: 0.67,
    concepts: ["projection", "orthogonality", "least_squares"],
    questionHtml: `
      <p>Let \\(W\\) be the column space of a matrix \\(A\\). Explain why the least-squares solution to \\(Ax=b\\) is characterized by \\(b-Ax\\) being orthogonal to \\(W\\).</p>
    `,
    starterAnswer: "The least-squares approximation Ax is the projection of b onto the column space W. The error vector b - Ax is perpendicular to W, so it is orthogonal to every column of A. This gives the normal equations A^T(Ax - b) = 0.",
    path: ["Inner product", "Orthogonal projection", "Column space", "Normal equations"],
    activePathIndex: 1,
    evidence: [
      ["slides_md/five", "Projection links orthogonality with approximation in a subspace."],
      ["mit_linear_algebra_md/fall2018", "Least-squares questions often ask for geometric interpretation and normal equations."]
    ]
  },
  {
    id: "determinant-eigenvalues",
    source: "Prerequisite Check",
    title: "Determinants and Eigenvalues",
    difficulty: 0.61,
    concepts: ["determinants", "eigenvalues", "characteristic_polynomial"],
    questionHtml: `
      <p>Explain why eigenvalues of \\(A\\) are found by solving \\(\\det(A-\\lambda I)=0\\). What does a nonzero determinant of \\(A-\\lambda I\\) tell us?</p>
    `,
    starterAnswer: "lambda is an eigenvalue when there is a nonzero vector x with (A - lambda I)x = 0. That means A - lambda I has a nontrivial nullspace, so it is singular, which is equivalent to determinant zero. A nonzero determinant means only the zero solution exists.",
    path: ["Determinant criterion", "Singular matrix", "Nontrivial nullspace", "Characteristic equation"],
    activePathIndex: 2,
    evidence: [
      ["slides_md/four", "Determinants provide an invertibility criterion for square matrices."],
      ["slides_md/five", "Eigenvalues arise from the characteristic polynomial det(A - lambda I)."]
    ]
  }
];

items = fallbackItems.slice();

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((button) => button.classList.remove("active"));
    tab.classList.add("active");
    Object.values(views).forEach((view) => view.classList.remove("active"));
    views[tab.dataset.tab].classList.add("active");
    setWorkflowStage(tab.dataset.tab === "dialogue" ? "feedback" : "graph");
  });
});

segments.forEach((segment) => {
  segment.addEventListener("click", () => {
    segments.forEach((button) => button.classList.remove("active"));
    segment.classList.add("active");
    reviewMode = segment.dataset.mode;
    nextAction.textContent = titleCase(reviewMode);
    lastAction = titleCase(reviewMode);
    if (reviewMode === "diagnostic") {
      selectionNote.textContent = "Diagnostic mode prioritizes weak-concept coverage before difficulty fit.";
      setWorkflowStage("graph");
    }
    if (reviewMode === "practice") {
      selectionNote.textContent = "Practice mode prioritizes items near the selected IRT difficulty.";
      setWorkflowStage("irt");
    }
    if (reviewMode === "explain") {
      selectionNote.textContent = "Explain mode opens the grounded dialogue agent for concept clarification.";
      document.querySelector('[data-tab="dialogue"]')?.click();
    }
  });
});

difficultyRange.addEventListener("input", () => {
  difficultyValue.textContent = Number(difficultyRange.value).toFixed(2);
  selectionNote.textContent = `Next item will favor difficulty near ${Number(difficultyRange.value).toFixed(2)} and weak active concepts.`;
  setWorkflowStage("irt");
});

gradeButton.addEventListener("click", async () => {
  const item = currentItem();
  setWorkflowStage("feedback");
  setBusy(gradeButton, "Grading...");
  feedbackBox.innerHTML = '<div class="feedback-placeholder">The agent is grading the response and mapping errors to concepts.</div>';
  try {
    const result = await callAgent("grade", answerBox.value, item);
    renderFeedback(result.reply || "The agent returned an empty grading response.", result);
    applyLearnerUpdate(item, result);
  } catch (error) {
    renderAgentError("Grading was not completed because the agent call failed. The learner model was not updated from this attempt.");
    agentStatus.textContent = "Agent: offline";
    agentStatus.classList.add("offline");
    lastAction = "Retry agent";
    refreshLearnerState(item);
  } finally {
    restoreButton(gradeButton, "Submit and Grade");
  }
});

hintButton.addEventListener("click", async () => {
  const item = currentItem();
  setWorkflowStage("feedback");
  setBusy(hintButton, "Asking...");
  feedbackBox.innerHTML = '<div class="feedback-placeholder">The agent is generating a targeted hint.</div>';
  try {
    learnerStats.hintRequests += 1;
    const result = await callAgent("hint", answerBox.value, item);
    renderFeedback(result.reply || "The agent returned an empty hint response.", result);
    lastAction = "Practice";
    refreshLearnerState(item);
  } catch (error) {
    renderAgentError("Hint generation was not completed because the agent call failed. No synthetic hint was inserted.");
    agentStatus.textContent = "Agent: offline";
    agentStatus.classList.add("offline");
    lastAction = "Retry agent";
    refreshLearnerState(item);
  } finally {
    restoreButton(hintButton, "Ask for Hint");
  }
});

nextButton.addEventListener("click", () => {
  setWorkflowStage("irt");
  itemIndex = selectNextItemIndex();
  renderItem(currentItem());
  feedbackBox.innerHTML = '<div class="feedback-placeholder">The next item has been selected from the local adaptive item pool. Submit an answer to update the learner model.</div>';
  nextAction.textContent = "Diagnose";
  lastAction = "Diagnose";
});

sendButton.addEventListener("click", async () => {
  const text = chatInput.value.trim();
  if (!text) return;
  appendMessage("learner", "Student", text);
  setWorkflowStage("feedback");
  chatInput.value = "";
  setBusy(sendButton, "Sending...");
  try {
    const result = await callAgent("chat", text, currentItem());
    appendMessage("agent", "Agent", result.reply || "The agent returned an empty dialogue response.");
    markAgentOnline();
  } catch (error) {
    appendMessage("agent error", "Agent unavailable", "The dialogue request failed. No local template response was used.");
    agentStatus.textContent = "Agent: offline";
    agentStatus.classList.add("offline");
  } finally {
    restoreButton(sendButton, "Send");
    chatLog.scrollTop = chatLog.scrollHeight;
  }
});

window.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    if (views.practice.classList.contains("active")) {
      gradeButton.click();
    } else {
      sendButton.click();
    }
  }
});

async function checkAgent() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("health check failed");
    markAgentOnline();
  } catch {
    agentStatus.textContent = "Agent: local UI only";
    agentStatus.classList.add("offline");
  }
}

async function loadItemBank() {
  try {
    const response = await fetch("/api/items");
    if (!response.ok) throw new Error("item bank request failed");
    const data = await response.json();
    if (Array.isArray(data.items) && data.items.length > 0) {
      items = data.items;
      itemIndex = 0;
      recentItemIds = [items[0].id];
      selectionNote.textContent = `${items.length} flipped/MIT items loaded from the benchmark item bank.`;
    }
  } catch {
    items = fallbackItems.slice();
    recentItemIds = [items[0].id];
    selectionNote.textContent = "Using local fallback items because the benchmark item bank could not be loaded.";
  }
}

async function callAgent(action, input, item) {
  const response = await fetch("/api/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action,
      input,
      item,
      learner_state: {
        readiness: calculateReadiness(item).percent,
        theta,
        target_difficulty: Number(difficultyRange.value)
      }
    })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "agent request failed");
  }
  const data = await response.json();
  markAgentOnline();
  return data;
}

function renderItem(item) {
  itemTitle.textContent = item.title;
  itemSource.textContent = item.source;
  itemDifficulty.textContent = `IRT b = ${item.difficulty.toFixed(2)}`;
  questionBox.innerHTML = item.questionHtml;
  answerBox.value = item.starterAnswer;
  answerBox.placeholder = item.starterAnswer ? "" : "Enter a student solution or reasoning steps here.";
  difficultyRange.value = item.difficulty.toFixed(2);
  difficultyValue.textContent = item.difficulty.toFixed(2);
  renderConceptChips(item);
  renderConceptList(item);
  renderPath(item);
  renderEvidence(item);
  updateSystemState(item);
  setWorkflowStage("retrieval");
  typesetMath(questionBox);
  typesetMath(evidenceList);
}

function renderConceptChips(item) {
  conceptChips.innerHTML = [
    "<span>Active concepts</span>",
    ...item.concepts.map((concept) => `<em>${escapeHtml(conceptLabels[concept] || titleCase(concept.replaceAll("_", " ")))}</em>`)
  ].join("");
}

function renderConceptList(item = currentItem()) {
  const active = new Set(item.concepts);
  const rows = Object.entries(mastery)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 5);
  conceptList.innerHTML = rows.map(([concept, value]) => `
    <li data-concept="${escapeHtml(concept)}" class="${active.has(concept) ? "active" : ""}">
      <span>${escapeHtml(conceptLabels[concept] || titleCase(concept.replaceAll("_", " ")))}</span>
      <meter min="0" max="100" value="${value}"></meter>
    </li>
  `).join("");
}

function renderPath(item) {
  pathList.innerHTML = item.path
    .map((step, index) => {
      const className = index < item.activePathIndex ? "done" : index === item.activePathIndex ? "active" : "";
      return `<li class="${className}">${escapeHtml(step)}</li>`;
    })
    .join("");
}

function renderEvidence(item) {
  evidenceList.innerHTML = item.evidence
    .map(([source, text]) => `
      <article class="evidence-card">
        <span class="source-label">${escapeHtml(source)}</span>
        <p>${formatMathText(text)}</p>
      </article>
    `)
    .join("");
  chunkValue.textContent = String(item.evidence.length);
  setWorkflowStage("retrieval");
  typesetMath(evidenceList);
}

function renderFeedback(markdownLike, meta = {}) {
  const lines = markdownLike.split("\n").filter(Boolean);
  const body = lines.map((line) => {
    if (/^\s*[-*]\s+/.test(line)) {
      return `<li>${formatMathText(line.replace(/^\s*[-*]\s+/, ""))}</li>`;
    }
    return `<p>${formatMathText(line)}</p>`;
  }).join("");
  feedbackBox.innerHTML = `
    <div class="score-row">
      <span class="metric-label">${meta.warning ? "Fallback feedback" : "Agent feedback"}</span>
      <strong>${meta.score || "Review"}</strong>
    </div>
    <div class="agent-feedback">${body}</div>
  `;
  typesetMath(feedbackBox);
}

function renderAgentError(message) {
  feedbackBox.innerHTML = `
    <div class="feedback-placeholder error">
      <strong>Agent unavailable</strong>
      <p>${escapeHtml(message)}</p>
    </div>
  `;
}

function applyLearnerUpdate(item, result) {
  const parsedScore = parseGradeScore(result.reply);
  if (parsedScore === null) {
    lastAction = "Needs review";
    refreshLearnerState(item);
    return;
  }

  learnerStats.gradedAttempts += 1;
  learnerStats.lastScore = parsedScore;
  learnerStats.lastConfidence = estimateGradeConfidence(item, parsedScore, result.reply);

  const normalizedScore = parsedScore / 100;
  theta = Number((theta + (normalizedScore - 0.68) * 0.32).toFixed(2));
  item.concepts.forEach((concept) => {
    const current = mastery[concept] ?? 50;
    const delta = Math.round((normalizedScore - 0.5) * 18);
    mastery[concept] = clamp(current + delta, 15, 98);
  });
  const pathConcept = item.path[item.activePathIndex]?.toLowerCase() || "";
  Object.keys(mastery).forEach((concept) => {
    const label = conceptLabels[concept]?.toLowerCase() || concept;
    if (pathConcept.includes(label.split(" ")[0])) {
      mastery[concept] = clamp(mastery[concept] + Math.round((normalizedScore - 0.6) * 8), 15, 98);
    }
  });
  lastAction = chooseNextAction(item, parsedScore);
  refreshLearnerState(item);
  renderConceptList(item);
  setWorkflowStage("irt");
}

function currentItem() {
  return items[itemIndex];
}

function selectNextItemIndex() {
  const target = Number(difficultyRange.value);
  const weakConcepts = Object.entries(mastery)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 4)
    .map(([concept]) => concept);

  const candidates = items
    .map((item, index) => ({ item, index }))
    .filter(({ index }) => index !== itemIndex || items.length === 1);
  const nonRecentCandidates = candidates.filter(({ item }) => !recentItemIds.includes(item.id));
  const scoringPool = nonRecentCandidates.length >= Math.min(8, candidates.length)
    ? nonRecentCandidates
    : candidates;

  let bestIndex = itemIndex;
  let bestScore = -Infinity;
  scoringPool.forEach(({ item, index }) => {
    const weakOverlap = item.concepts.filter((concept) => weakConcepts.includes(concept)).length;
    const difficultyFit = 1 - Math.abs(item.difficulty - target);
    const rotationBonus = index > itemIndex ? 0.02 : 0;
    const recencyPenalty = recentItemIds.includes(item.id) ? 0.8 : 0;
    const conceptWeight = reviewMode === "practice" ? 0.38 : 0.7;
    const difficultyWeight = reviewMode === "practice" ? 0.58 : 0.3;
    const explanationBonus = reviewMode === "explain" && item.evidence.length > 1 ? 0.18 : 0;
    const score = weakOverlap * conceptWeight + difficultyFit * difficultyWeight + explanationBonus + rotationBonus - recencyPenalty;
    if (score > bestScore) {
      bestScore = score;
      bestIndex = index;
    }
  });
  const selected = items[bestIndex];
  recentItemIds = [...recentItemIds, selected.id].slice(-10);
  selectionNote.textContent = `Selected "${selected.title}" by weak-concept overlap and difficulty fit (${selected.difficulty.toFixed(2)}).`;
  return bestIndex;
}

function updateSystemState(item) {
  refreshLearnerState(item);
}

function refreshLearnerState(item = currentItem()) {
  const state = calculateReadiness(item);
  readinessScore.textContent = `${state.percent}%`;
  readinessBar.style.width = `${state.percent}%`;
  thetaValue.textContent = theta.toFixed(2);
  confidenceValue.textContent = state.confidence.toFixed(2);
  chunkValue.textContent = String(item.evidence.length);
  nextAction.textContent = lastAction;
}

function calculateReadiness(item = currentItem()) {
  const allMastery = Object.values(mastery);
  const conceptCoverage = average(allMastery) / 100;
  const activeCoverage = average(item.concepts.map((concept) => mastery[concept] ?? 50)) / 100;
  const performance = learnerStats.lastScore === null ? activeCoverage : learnerStats.lastScore / 100;
  const ability = sigmoid(theta);
  const difficultyFit = clamp(1 - Math.abs(item.difficulty - ability), 0, 1);
  const evidenceSupport = clamp(item.evidence.length / 4, 0, 1);
  const confidence = estimateStateConfidence(item);
  const readinessValue =
    0.34 * performance +
    0.28 * conceptCoverage +
    0.22 * difficultyFit +
    0.16 * evidenceSupport;
  return {
    percent: Math.round(clamp(readinessValue, 0, 1) * 100),
    confidence
  };
}

function estimateStateConfidence(item = currentItem()) {
  const evidenceSupport = clamp(item.evidence.length / 4, 0, 1);
  const interactionSupport = clamp((learnerStats.gradedAttempts * 0.45) + (learnerStats.hintRequests * 0.12), 0, 1);
  const scoreSupport = learnerStats.lastScore === null ? 0.45 : learnerStats.lastConfidence;
  return clamp(0.42 * evidenceSupport + 0.33 * scoreSupport + 0.25 * interactionSupport, 0.2, 0.98);
}

function estimateGradeConfidence(item, score, reply = "") {
  const evidenceSupport = clamp(item.evidence.length / 4, 0, 1);
  const answerSupport = clamp(answerBox.value.trim().length / 260, 0.2, 1);
  const feedbackSupport = clamp(String(reply).split(/\n+/).filter(Boolean).length / 5, 0.4, 1);
  const scoreStability = score >= 55 && score <= 95 ? 0.9 : 0.72;
  return clamp(
    0.34 * evidenceSupport +
    0.26 * answerSupport +
    0.22 * feedbackSupport +
    0.18 * scoreStability,
    0.25,
    0.97
  );
}

function chooseNextAction(item, score) {
  const activeCoverage = average(item.concepts.map((concept) => mastery[concept] ?? 50));
  if (score < 60) return "Remediate";
  if (score < 78) return "Practice";
  if (activeCoverage < 70) return "Review graph";
  if (Math.abs(item.difficulty - sigmoid(theta)) > 0.25) return "Recalibrate";
  return "Advance";
}

function parseGradeScore(text = "") {
  const match = String(text).match(/score\s*:\s*(\d{1,3})(?:\s*\/\s*100)?/i);
  if (!match) return null;
  return clamp(Number(match[1]), 0, 100);
}

function average(values) {
  const filtered = values.filter((value) => Number.isFinite(value));
  if (!filtered.length) return 0;
  return filtered.reduce((sum, value) => sum + value, 0) / filtered.length;
}

function sigmoid(value) {
  return 1 / (1 + Math.exp(-value));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function setWorkflowStage(stage) {
  const order = ["graph", "retrieval", "feedback", "irt"];
  const activeIndex = Math.max(0, order.indexOf(stage));
  workflowSteps.forEach((step, index) => {
    step.classList.toggle("active", index === activeIndex);
    step.classList.toggle("done", index < activeIndex);
  });
}

function setBusy(button, label) {
  button.disabled = true;
  button.dataset.oldText = button.textContent;
  button.textContent = label;
}

function restoreButton(button, fallbackLabel) {
  button.disabled = false;
  button.textContent = button.dataset.oldText || fallbackLabel;
}

function appendMessage(kind, speaker, text) {
  const message = document.createElement("div");
  message.className = `message ${kind}`;
  message.innerHTML = `<strong>${speaker}</strong><p>${formatMathText(text)}</p>`;
  chatLog.appendChild(message);
  typesetMath(message);
}

function titleCase(text) {
  return text.slice(0, 1).toUpperCase() + text.slice(1);
}

function markAgentOnline() {
  agentStatus.textContent = "Agent: online";
  agentStatus.classList.remove("offline");
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatMathText(text) {
  let html = escapeHtml(text);
  html = html
    .replace(/\\\\\(/g, "\\(")
    .replace(/\\\\\)/g, "\\)")
    .replace(/\\\\\[/g, "\\[")
    .replace(/\\\\\]/g, "\\]")
    .replace(/\\\((.*?)\\\)/g, "\\($1\\)")
    .replace(/\\\[(.*?)\\\]/gs, "\\[$1\\]")
    .replace(/\bA\^T\s*\(\s*Ax\s*-\s*b\s*\)\s*=\s*0\b/g, "\\(A^T(Ax-b)=0\\)")
    .replace(/\bA\^T\b/g, "\\(A^T\\)")
    .replace(/\bA\^\{T\}\b/g, "\\(A^{T}\\)")
    .replace(/\bA\s*-\s*2I\b/g, "\\(A-2I\\)")
    .replace(/\bA\s*-\s*lambda\s*I\b/gi, "\\(A-\\lambda I\\)")
    .replace(/\bdet\s*\(\s*A\s*-\s*lambda\s*I\s*\)\s*=\s*0\b/gi, "\\(\\det(A-\\lambda I)=0\\)")
    .replace(/\blambda\s*=\s*([0-9.-]+)/gi, "\\(\\lambda=$1\\)")
    .replace(/\blambda\b/gi, "\\(\\lambda\\)")
    .replace(/\bAx\s*=\s*b\b/g, "\\(Ax=b\\)")
    .replace(/\bb\s*-\s*Ax\b/g, "\\(b-Ax\\)")
    .replace(/\bA\^T\s*b\b/g, "\\(A^Tb\\)")
    .replace(/\bA\^T\s*A\b/g, "\\(A^TA\\)")
    .replace(/\bz\(([-0-9,\s]+)\)/g, "\\(z($1)\\)")
    .replace(/\{\(([-0-9,\s]+)\)\}/g, "\\(\\{($1)\\}\\)");
  return html;
}

function typesetMath(root = document.body) {
  if (window.MathJax?.typesetPromise) {
    window.MathJax.typesetPromise([root]).catch(() => {});
  }
}

initialize();

async function initialize() {
  await loadItemBank();
  renderItem(currentItem());
  applyUrlSnapshotMode();
  checkAgent();
}

function applyUrlSnapshotMode() {
  const params = new URLSearchParams(window.location.search);
  const view = params.get("view");
  if (view === "dialogue") {
    document.querySelector('[data-tab="dialogue"]')?.click();
  }
}
