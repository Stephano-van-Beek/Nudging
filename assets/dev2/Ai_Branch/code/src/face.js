const MOODS = {
  happy: { label: "Blij", mouth: "M 30 62 Q 50 82 70 62", brows: "" },
  neutral: { label: "Neutraal", mouth: "M 32 70 L 68 70", brows: "" },
  confused: {
    label: "Ik vraag even door",
    mouth: "M 34 72 Q 48 62 66 70",
    brows: "M 26 38 Q 34 32 42 38 M 58 38 L 74 34",
  },
  sad: {
    label: "Teleurgesteld",
    mouth: "M 30 76 Q 50 56 70 76",
    brows: "M 26 34 L 42 40 M 74 34 L 58 40",
  },
};

const KIND_LABELS = {
  stap: "Stap",
  zoek: "Zoeken",
  resultaat: "Resultaat",
  antwoord: "Antwoord",
};

// Koppelt het gezicht en het logboek met denkstappen aan de pagina.
export function createFace() {
  const button = document.querySelector("#face-button");
  const panel = document.querySelector("#trace-panel");
  const list = document.querySelector("#trace-list");
  const label = document.querySelector("#face-label");
  const mouth = document.querySelector("#face-mouth");
  const brows = document.querySelector("#face-brows");
  let currentQuestionId = null;

  button.addEventListener("click", () => {
    const open = panel.hidden;
    panel.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
  });

  function setMood(mood) {
    const config = MOODS[mood] ?? MOODS.neutral;
    mouth.setAttribute("d", config.mouth);
    brows.setAttribute("d", config.brows);
    button.dataset.mood = mood;
    label.textContent = config.label;
  }

  function log(kind, text) {
    const item = document.createElement("li");
    item.className = `trace-${kind}`;
    if (currentQuestionId) item.dataset.questionId = currentQuestionId;
    const tag = document.createElement("strong");
    tag.textContent = `${KIND_LABELS[kind] ?? "Stap"}: `;
    item.append(tag, document.createTextNode(text));
    list.append(item);
    list.scrollTop = list.scrollHeight;
  }

  function setQuestion(questionId) {
    currentQuestionId = questionId;
  }

  function removeQuestionLogs(questionIds) {
    const ids = new Set(questionIds);
    list.querySelectorAll("li[data-question-id]").forEach((item) => {
      if (ids.has(item.dataset.questionId)) item.remove();
    });
    list.scrollTop = list.scrollHeight;
  }

  function reset() {
    list.replaceChildren();
    currentQuestionId = null;
    setMood("neutral");
  }

  reset();
  return { setMood, log, setQuestion, removeQuestionLogs, reset };
}
