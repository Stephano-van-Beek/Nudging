// Haalt de vragen en lokale AI-logica op die de pagina nodig heeft.
import { followUpQuestions, intakeQuestions } from "./data/questions.js";
import { createAiFollowUp, createAiNudge, classifyService, findAnsweredQuestions } from "./AI/aiProvider.js";
import { createLocalNudge } from "./AI/nudgeEngine.js";
import { judgeAnswer } from "./AI/answerJudge.js";
import { createFace } from "./face.js";

const face = createFace();
face.log("stap", "Formulier gestart. Ik wacht op het eerste antwoord.");

// Voegt de vier intakevragen en twee vervolgvragen samen tot één vragenlijst.
const questions = [...intakeQuestions, ...followUpQuestions];
// Bewaart de antwoorden tijdelijk totdat de nudge wordt gemaakt.
const answers = {};
const clarificationAnswers = {};
const aiSteps = [];
let followUpCount = 0;
let unhelpfulAnswerCount = 0;
let limitedInformation = false;
let currentQuestion = 0;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

// Verwijzingen naar onderdelen van de pagina die tijdens de vragen worden bijgewerkt.
const form = document.querySelector("#nudge-form");
const container = document.querySelector("#question-container");
const backButton = document.querySelector("#back-button");
const nextButton = document.querySelector("#next-button");
const errorMessage = document.querySelector("#error-message");
const progressBar = document.querySelector("#progress-bar");
const progressText = document.querySelector("#progress-text");
const result = document.querySelector("#result");
const report = document.querySelector("#report");
const qualityWarning = document.querySelector("#quality-warning");
let currentNudge = null;
const fallbackButton = document.querySelector("#fallback-button");

// Toont de huidige vraag, inclusief invoerveld of antwoordkeuzes.
function renderQuestion() {
  const question = questions[currentQuestion];
  const isChoiceQuestion = Boolean(question.choices);
  face.setQuestion(question.id);

  const visibleQuestions = questions.filter((item) => !item.skippedBy);
  const visibleIndex = visibleQuestions.indexOf(question);
  progressBar.style.width = `${(visibleIndex / visibleQuestions.length) * 100}%`;
  progressText.textContent = `Vraag ${visibleIndex + 1} van ${visibleQuestions.length}`;
  backButton.hidden = currentQuestion === 0;
  nextButton.textContent = limitedInformation
    ? currentQuestion === questions.length - 1
      ? "Bekijk nudge (beperkte informatie)"
      : "Verder met beperkte informatie"
    : currentQuestion === questions.length - 1
      ? "Bekijk mijn nudge"
      : "Verder";
  errorMessage.textContent = "";

  container.innerHTML = `
    <legend>${escapeHtml(question.title)}</legend>
    <p class="hint">${escapeHtml(question.hint ?? "")}</p>
    ${
      isChoiceQuestion
        ? question.choices
            .map(
              (choice) => `
                <label class="choice">
                  <input type="radio" name="${question.id}" value="${choice}"
                    ${answers[question.id] === choice ? "checked" : ""} />
                  <span>${choice}</span>
                </label>`,
            )
            .join("")
        : `<label class="sr-only" for="${question.id}">${question.title}</label>
           <textarea id="${escapeHtml(question.id)}" name="${escapeHtml(question.id)}" rows="5"
             maxlength="${question.isClarification ? 500 : 1000}"
             placeholder="${escapeHtml(question.placeholder)}">${escapeHtml(question.isClarification ? clarificationAnswers[question.id] ?? "" : answers[question.id] ?? "")}</textarea>`
    }
  `;
}

// Verwijdert denkstappen van deze vraag en latere vragen als de gebruiker teruggaat of corrigeert.
function clearQuestionHistoryFrom(questionIndex) {
  const questionIds = questions.slice(questionIndex).map((question) => question.id);
  const ids = new Set(questionIds);
  face.removeQuestionLogs(questionIds);
  for (let index = aiSteps.length - 1; index >= 0; index -= 1) {
    if (ids.has(aiSteps[index].questionId)) aiSteps.splice(index, 1);
  }
}

// Zet hoofdvragen weer open die door een extra vraag waren overgeslagen.
function unskipQuestions(clarificationId) {
  questions.forEach((item) => {
    if (item.skippedBy !== clarificationId) return;
    delete item.skippedBy;
    delete answers[item.id];
  });
}

// Controleert het antwoord van de huidige vraag en bewaart het als het is ingevuld.
function storeAnswer() {
  clearQuestionHistoryFrom(currentQuestion);
  const question = questions[currentQuestion];
  if (question.isClarification) unskipQuestions(question.id);
  const selected = form.elements[question.id];
  const value =
    selected instanceof RadioNodeList
      ? selected.value
      : selected.value.trim();

  if (!value) {
    if (question.isClarification) {
      face.log("stap", "Je hebt de extra vraag overgeslagen; we gaan verder.");
      recordAnswerQuality(false);
      return { question, value: "", mood: "neutral", why: "Vervolgvraag overgeslagen." };
    }
    errorMessage.textContent = `Ik mis je antwoord. ${question.hint ?? "Kun je iets invullen?"}`;
    face.setMood("confused");
    face.log("resultaat", "Er is geen antwoord ingevuld; de vraag blijft open.");
    return false;
  }

  if (question.isClarification) {
    clarificationAnswers[question.id] = value;
    face.log("zoek", `Extra uitleg lezen: "${value}"`);
    const assessment = judgeAnswer({ title: question.title }, value);
    recordAnswerQuality(assessment.mood === "happy");
    face.setMood(assessment.mood);
    face.log("resultaat", assessment.mood === "happy"
      ? "De extra uitleg bevat een herkenbaar onderwerp en wordt meegenomen."
      : "De extra uitleg geeft nog geen duidelijke richting.");
    return { question, value, ...assessment };
  }

  for (let index = questions.length - 1; index > currentQuestion; index -= 1) {
    if (questions[index].isClarification && questions[index].parentId === question.id) {
      unskipQuestions(questions[index].id);
      delete clarificationAnswers[questions[index].id];
      questions.splice(index, 1);
      followUpCount -= 1;
    }
  }
  for (let index = aiSteps.length - 1; index >= 0; index -= 1) {
    if (aiSteps[index].questionId === question.id) aiSteps.splice(index, 1);
  }
  answers[question.id] = value;
  const { mood, why } = judgeAnswer(question, value);
  if (!question.choices) recordAnswerQuality(mood === "happy");
  face.setMood(mood);
  face.log("zoek", `Antwoord op vraag ${currentQuestion + 1} lezen: "${value}"`);
  face.log("resultaat", why);
  return { question, value, mood, why };
}

function recordAnswerQuality(isHelpful) {
  if (isHelpful) return;
  unhelpfulAnswerCount = Math.min(unhelpfulAnswerCount + 1, 2);
  face.log(
    "resultaat",
    `Antwoord helpt onvoldoende (${unhelpfulAnswerCount} van 2).`,
  );
  if (unhelpfulAnswerCount >= 2) {
    limitedInformation = true;
    qualityWarning.hidden = false;
    nextButton.textContent = "Verder met beperkte informatie";
    face.log(
      "resultaat",
      "Na twee antwoorden is er nog onvoldoende informatie; de aanbeveling kan algemeen of minder zeker zijn.",
    );
  }
}

function getAnswersWithClarifications() {
  const completeAnswers = { ...answers };
  questions
    .filter((question) => question.isClarification && clarificationAnswers[question.id])
    .forEach((question) => {
      const base = completeAnswers[question.parentId];
      const addition =
        `\nAanvulling: ${clarificationAnswers[question.id]}`.slice(
          0,
          Math.max(0, 1000 - base.length),
        );
      completeAnswers[question.parentId] = `${base}${addition}`;
    });
  return completeAnswers;
}

// Laat Qwen3 nagaan of een extra antwoord open hoofdvragen al beantwoordt en slaat die over.
async function maybeSkipAnsweredQuestions({ question, value, mood }) {
  if (!question.isClarification || !value || mood !== "happy") return;
  const openQuestions = questions
    .slice(currentQuestion + 1)
    .filter((item) => !item.choices && !item.isClarification && !item.skippedBy && !answers[item.id])
    .map((item) => ({ id: item.id, title: item.title }));
  if (!openQuestions.length) return;

  const previousLabel = nextButton.textContent;
  nextButton.disabled = true;
  nextButton.textContent = "Wacht op AI...";
  errorMessage.textContent = "Qwen3 kijkt of je al antwoord gaf op een volgende vraag...";
  face.log("zoek", "Het lokale Ollama-model vragen of dit antwoord een volgende vraag al beantwoordt.");
  try {
    const check = await findAnsweredQuestions(question.title, value, openQuestions);
    const skipped = [];
    check.covered.forEach((id) => {
      const target = questions.find((item) => item.id === id);
      if (!target) return;
      target.skippedBy = question.id;
      answers[id] = value;
      skipped.push(target.title);
    });
    aiSteps.push({
      task: "Beantwoorde vragen overslaan",
      model: check.model,
      output: skipped.length ? `Overgeslagen: ${skipped.join("; ")}` : "Geen vragen overgeslagen.",
      reason: check.reason,
      questionId: question.id,
    });
    face.log(
      "resultaat",
      skipped.length
        ? `${check.model || "AI-model"} sloeg over: ${skipped.join("; ")}. ${check.reason}`
        : `${check.model || "AI-model"} sloeg geen vragen over. ${check.reason}`,
    );
  } catch (error) {
    face.log("resultaat", `Overslaan niet mogelijk, alle vragen blijven staan: ${error.message}`);
  } finally {
    nextButton.disabled = false;
    nextButton.textContent = previousLabel;
    errorMessage.textContent = "";
  }
}

// Zoekt de dichtstbijzijnde vraag in een richting die niet is overgeslagen.
function stepIndex(direction) {
  let index = currentQuestion + direction;
  while (questions[index]?.skippedBy) index += direction;
  return index;
}

async function maybeAddFollowUp({ question, value, mood }) {
  if (
    question.choices ||
    question.isClarification ||
    mood === "happy" ||
    followUpCount >= 2
  ) {
    return;
  }

  const previousLabel = nextButton.textContent;
  nextButton.disabled = true;
  nextButton.textContent = "Wacht op AI...";
  errorMessage.textContent = "Qwen3 kijkt of een extra vraag helpt...";
  face.log("zoek", "Het lokale Ollama-model vragen om een verduidelijkingsvraag te formuleren.");
  try {
    const previousAnswers = { ...answers };
    delete previousAnswers[question.id];
    const result = await createAiFollowUp(question.title, value, previousAnswers);
    followUpCount += 1;
    aiSteps.push({
      task: "Vervolgvraag maken",
      model: result.model,
      output: result.question,
      description: result.description,
      reason: result.reason,
      questionId: question.id,
    });
    const followUp = {
      id: `clarification-${followUpCount}`,
      title: result.question,
      hint: result.description,
      placeholder: "Bijvoorbeeld: ...",
      isClarification: true,
      parentId: question.id,
    };
    questions.splice(currentQuestion + 1, 0, followUp);
    face.setMood("neutral");
    face.log(
      "resultaat",
      result.adjusted
        ? `${result.model || "AI-model"} stelde een vraag, veilig aangepast zodat je antwoord niet wordt herhaald: ${result.question}`
        : `${result.model || "AI-model"} stelt een vervolgvraag: ${result.question}`,
    );
    if (result.description) {
      face.log("resultaat", `Toelichting bij de vervolgvraag: ${result.description}`);
    }
  } catch (error) {
    errorMessage.textContent = `Ik kon geen vervolgvraag maken: ${error.message}`;
    face.log("resultaat", `Vervolgvraag niet beschikbaar: ${error.message}`);
  } finally {
    nextButton.disabled = false;
    nextButton.textContent = previousLabel;
    if (errorMessage.textContent.startsWith("Qwen3 kijkt")) errorMessage.textContent = "";
  }
}

// Toont de nudge met de drie opties; de eerste optie staat vooraf aangevinkt.
function showResult(nudge, source) {
  progressBar.style.width = "100%";
  progressText.textContent = "Bijna klaar";
  form.hidden = true;
  result.hidden = false;
  currentNudge = nudge;
  document.querySelector("#service-name").textContent = nudge.serviceName;
  document.querySelector("#nudge-message").textContent = nudge.message;
  document.querySelector("#result-source").textContent = source;

  const optionsContainer = document.querySelector("#options-container");
  optionsContainer.replaceChildren();
  const legend = document.createElement("legend");
  legend.textContent = "Kies een dienst";
  optionsContainer.append(legend);

  nudge.options.forEach((option, index) => {
    const label = document.createElement("label");
    label.className = "choice";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "service";
    input.value = option.name;
    input.checked = index === 0;
    const text = document.createElement("span");
    text.textContent = `${option.name} (${option.category})`;
    if (index === 0) text.textContent += " - de meeste collega's kiezen dit";
    label.append(input, text);
    optionsContainer.append(label);
  });
}

// Toont het eindformulier met antwoorden, AI-redenering, technieken en de gemaakte keuze.
function showReport(chosenName) {
  result.hidden = true;
  report.hidden = false;
  progressText.textContent = "Klaar";

  const list = document.querySelector("#report-answers");
  list.replaceChildren();
  questions.forEach((question) => {
    const term = document.createElement("dt");
    term.textContent = question.title;
    const definition = document.createElement("dd");
    definition.textContent = question.isClarification
      ? clarificationAnswers[question.id] || "Vervolgvraag overgeslagen"
      : answers[question.id];
    list.append(term, definition);
  });

  const usedAi = Boolean(currentNudge.model);
  document.querySelector("#report-reason").textContent = usedAi
    ? `Redenering van de AI: ${currentNudge.reason || "geen redenering teruggegeven."}`
    : "Er is geen AI gebruikt om de nudgetekst te schrijven; de dienst is gekozen met vaste trefwoordregels" +
      (currentNudge.matchedKeywords.length
        ? ` (gevonden: ${currentNudge.matchedKeywords.join(", ")}).`
        : " (geen trefwoorden gevonden, standaarddienst).");
  document.querySelector("#report-message").textContent = `Getoonde nudge: ${currentNudge.message}`;
  const modelSteps = document.querySelector("#report-ai-steps");
  modelSteps.replaceChildren();
  aiSteps.forEach((step) => {
    const item = document.createElement("li");
    const details = [
      `${step.task} — model: ${step.model || "onbekend"}`,
      step.reason ? `Waarom: ${step.reason}` : "",
      step.description ? `Toelichting: ${step.description}` : "",
      step.output ? `Uitvoer: ${step.output}` : "",
    ].filter(Boolean);
    item.textContent = details.join(" ");
    modelSteps.append(item);
  });
  if (!aiSteps.length) {
    const item = document.createElement("li");
    item.textContent = "Er is geen AI-model gebruikt.";
    modelSteps.append(item);
  }
  document.querySelector("#report-quality").textContent = limitedInformation
    ? `Na ${unhelpfulAnswerCount} antwoorden was er nog onvoldoende informatie. De aanbeveling kan daardoor algemeen of minder zeker zijn.`
    : "Er is geen waarschuwing wegens onvoldoende informatie.";

  const techniques = document.querySelector("#report-techniques");
  techniques.replaceChildren(
    ...currentNudge.techniques.map((technique) => {
      const item = document.createElement("li");
      item.textContent = technique;
      return item;
    }),
  );

  const followed = chosenName === currentNudge.options[0].name;
  face.setMood(followed ? "happy" : "sad");
  face.log(
    "antwoord",
    followed
      ? `Gekozen: ${chosenName}. De voorgeselecteerde dienst, mijn nudge werkte.`
      : `Gekozen: ${chosenName}. Niet de voorgeselecteerde dienst; jammer.`,
  );
  document.querySelector("#report-choice").textContent =
    `Je koos "${chosenName}". ` +
    (followed
      ? "Dat is de voorgeselecteerde dienst: de nudge werkte."
      : "Je koos een andere dienst dan de voorgeselecteerde: je liet je niet sturen.");
  document.querySelector("#report-source").textContent = usedAi
    ? `Tekst en redenering gemaakt door ${currentNudge.model} via Ollama op deze computer.`
    : aiSteps.length
      ? "Nudgetekst met vaste regels; geen AI gebruikt voor de nudge. Eerdere AI-stappen staan hierboven."
      : "Standaardnudge met vaste regels; geen AI gebruikt.";
}

async function createAndShowAiNudge() {
  const completedAnswers = getAnswersWithClarifications();
  const localRecommendation = createLocalNudge(completedAnswers);
  face.log("zoek", "Alle antwoorden doorzoeken op trefwoorden uit de O&P-catalogus 2026.");
  if (localRecommendation.scores.length === 0) {
    face.log("resultaat", "Geen trefwoorden gevonden; ik val terug op Organisatieonderzoek.");
  }
  localRecommendation.scores.forEach((score) =>
    face.log("resultaat", `${score.name}: ${score.matches.join(", ")}`),
  );
  face.log(
    "stap",
    `Drie opties gekozen: ${localRecommendation.options.map((option) => option.name).join(", ")}. "${localRecommendation.serviceName}" staat voorgeselecteerd.`,
  );

  // Laat de AI (Ollama) zelf een dienst kiezen uit de vaste catalogus.
  let recommendation = localRecommendation;
  face.log("zoek", "Het lokale Ollama-model vragen om de passende dienst te bepalen.");
  try {
    const classification = await classifyService(completedAnswers);
    recommendation = {
      ...localRecommendation,
      serviceName: classification.serviceName,
      category: classification.category || localRecommendation.category,
      action: classification.action || localRecommendation.action,
      matchedKeywords: classification.matchedKeywords.length
        ? classification.matchedKeywords
        : localRecommendation.matchedKeywords,
    };
    aiSteps.push({
      task: "Dienst classificeren",
      model: classification.model,
      input: `Antwoorden: ${Object.values(completedAnswers).join(" | ")}`.slice(0, 240),
      output: `${classification.serviceName} (${classification.category})`,
      reason: `${classification.reason} (zekerheid ${Math.round(classification.confidence * 100)}%, bron: ${classification.source}).`,
    });
    face.log(
      "resultaat",
      `AI koos "${classification.serviceName}" (${classification.source}, zekerheid ${Math.round(classification.confidence * 100)}%): ${classification.reason}`,
    );
    if (classification.candidates.length) {
      face.log(
        "resultaat",
        `Kandidaten: ${classification.candidates.map((item) => `${item.name} (${item.score})`).join(", ")}`,
      );
    }
  } catch (error) {
    face.log("resultaat", `AI-classificatie niet beschikbaar, trefwoordregels gebruikt: ${error.message}`);
    aiSteps.push({
      task: "Dienst classificeren",
      model: "",
      input: "Trefwoordregels",
      output: localRecommendation.serviceName,
      reason: "AI-classificatie mislukt; teruggevallen op trefwoordregels.",
    });
  }

  face.log("zoek", "Het lokale Ollama-model vragen om nudgetekst en een korte uitleg.");
  nextButton.disabled = true;
  nextButton.textContent = "Nudge maken...";
  fallbackButton.hidden = true;
  errorMessage.textContent = "Het lokale Ollama-model maakt een nudge...";

  try {
    const nudge = await createAiNudge(completedAnswers, recommendation);
    aiSteps.push({
      task: "Nudgetekst maken",
      model: nudge.model,
      input: `Aanbevolen dienst: ${nudge.serviceName}.`,
      output: nudge.message,
      reason: nudge.reason,
    });
    errorMessage.textContent = "";
    face.setMood("happy");
    face.log("resultaat", `Redenering van het model: ${nudge.reason || "geen"}`);
    face.log("antwoord", nudge.message);
    showResult(nudge, `Geformuleerd door ${nudge.model} via Ollama op deze computer.`);
  } catch (error) {
    errorMessage.textContent = `De AI-nudge is niet gemaakt: ${error.message}`;
    face.setMood("sad");
    face.log("resultaat", `Fout: ${error.message}`);
    fallbackButton.hidden = false;
  } finally {
    nextButton.disabled = false;
    nextButton.textContent = limitedInformation
      ? "Bekijk nudge (beperkte informatie)"
      : "Bekijk mijn nudge";
  }
}

// Gaat na een geldig antwoord naar de volgende vraag of toont het eindresultaat.
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const storedAnswer = storeAnswer();
  if (!storedAnswer) return;

  await maybeAddFollowUp(storedAnswer);
  await maybeSkipAnsweredQuestions(storedAnswer);

  if (stepIndex(1) >= questions.length) {
    await createAndShowAiNudge();
    return;
  }

  currentQuestion = stepIndex(1);
  renderQuestion();
});

document.querySelector("#choice-form").addEventListener("submit", (event) => {
  event.preventDefault();
  showReport(new FormData(event.currentTarget).get("service"));
});

fallbackButton.addEventListener("click", () => {
  errorMessage.textContent = "";
  face.log("stap", "Standaardnudge met vaste regels getoond; er is geen AI gebruikt.");
  showResult(
    { ...createLocalNudge(getAnswersWithClarifications()), model: "" },
    "Standaardnudge met vaste regels; er is geen AI gebruikt.",
  );
});

// Gaat terug naar de vorige vraag om een antwoord te kunnen aanpassen.
backButton.addEventListener("click", () => {
  const previous = stepIndex(-1);
  clearQuestionHistoryFrom(previous);
  face.setMood("neutral");
  currentQuestion = previous;
  renderQuestion();
});

// Leegt alle antwoorden en start de vragenlijst opnieuw.
document.querySelector("#restart-button").addEventListener("click", () => {
  currentQuestion = 0;
  Object.keys(answers).forEach((key) => delete answers[key]);
  Object.keys(clarificationAnswers).forEach((key) => delete clarificationAnswers[key]);
  for (let index = questions.length - 1; index >= 0; index -= 1) {
    delete questions[index].skippedBy;
    if (questions[index].isClarification) questions.splice(index, 1);
  }
  followUpCount = 0;
  unhelpfulAnswerCount = 0;
  limitedInformation = false;
  aiSteps.length = 0;
  qualityWarning.hidden = true;
  nextButton.textContent = "Verder";
  currentNudge = null;
  face.reset();
  face.log("stap", "Opnieuw begonnen.");
  result.hidden = true;
  report.hidden = true;
  form.hidden = false;
  fallbackButton.hidden = true;
  errorMessage.textContent = "";
  renderQuestion();
});

renderQuestion();
