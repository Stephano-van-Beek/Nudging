const SERVER_HINT =
  "Start de demo met 'python server.py' en open http://127.0.0.1:8000.";

export async function createAiNudge(answers, recommendation) {
  let response;
  try {
    response = await fetch("/api/nudge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        answers,
        recommendation: {
          serviceName: recommendation.serviceName,
          action: recommendation.action,
        },
      }),
    });
  } catch {
    throw new Error(`De lokale AI-server is niet bereikbaar. ${SERVER_HINT}`);
  }

  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`De lokale AI-server gaf geen geldig antwoord terug. ${SERVER_HINT}`);
  }

  if (!result || typeof result !== "object") {
    throw new Error("De lokale AI-server gaf een ongeldig antwoord terug.");
  }

  if (!response.ok) {
    throw new Error(result.error ?? `De AI-server gaf fout ${response.status}.`);
  }

  if (typeof result.message !== "string" || !result.message.trim()) {
    throw new Error("Het Ollama-model gaf geen bruikbare nudge-tekst terug.");
  }

  return {
    ...recommendation,
    message: result.message.trim(),
    reason: typeof result.reason === "string" ? result.reason.trim() : "",
    model: typeof result.model === "string" ? result.model : "",
  };
}

export async function findAnsweredQuestions(question, answer, openQuestions) {
  let response;
  try {
    response = await fetch("/api/skip-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, answer, openQuestions }),
    });
  } catch {
    throw new Error(`De lokale AI-server is niet bereikbaar. ${SERVER_HINT}`);
  }
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`De lokale AI-server gaf geen geldig antwoord terug. ${SERVER_HINT}`);
  }
  if (!response.ok) {
    throw new Error(result?.error ?? `De AI-server gaf fout ${response.status}.`);
  }
  if (!Array.isArray(result.covered) || !result.covered.every((id) => typeof id === "string")) {
    throw new Error("Het Ollama-model gaf geen geldige lijst met beantwoorde vragen terug.");
  }
  return {
    covered: result.covered,
    reason: typeof result.reason === "string" ? result.reason : "",
    model: typeof result.model === "string" ? result.model : "",
  };
}

export async function classifyService(answers) {
  let response;
  try {
    response = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
  } catch {
    throw new Error(`De lokale AI-server is niet bereikbaar. ${SERVER_HINT}`);
  }
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`De lokale AI-server gaf geen geldig antwoord terug. ${SERVER_HINT}`);
  }
  if (!response.ok) {
    throw new Error(result?.error ?? `De AI-server gaf fout ${response.status}.`);
  }
  if (typeof result.serviceName !== "string" || !result.serviceName.trim()) {
    throw new Error("Het Ollama-model gaf geen bruikbare dienst terug.");
  }
  return {
    serviceId: typeof result.serviceId === "string" ? result.serviceId : "",
    serviceName: result.serviceName.trim(),
    category: typeof result.category === "string" ? result.category : "",
    action: typeof result.action === "string" ? result.action : "",
    confidence: typeof result.confidence === "number" ? result.confidence : 0,
    reason: typeof result.reason === "string" ? result.reason.trim() : "",
    model: typeof result.model === "string" ? result.model : "",
    matchedKeywords: Array.isArray(result.matchedKeywords) ? result.matchedKeywords : [],
    source: result.source === "ai" ? "ai" : "fallback",
    candidates: Array.isArray(result.candidates) ? result.candidates : [],
  };
}

export async function createAiFollowUp(question, answer, context) {
  let response;
  try {
    response = await fetch("/api/follow-up", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, answer, context }),
    });
  } catch {
    throw new Error(`De lokale AI-server is niet bereikbaar. ${SERVER_HINT}`);
  }

  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`De lokale AI-server gaf geen geldig antwoord terug. ${SERVER_HINT}`);
  }

  if (!result || typeof result !== "object") {
    throw new Error("De lokale AI-server gaf een ongeldig antwoord terug.");
  }
  if (!response.ok) {
    throw new Error(result.error ?? `De AI-server gaf fout ${response.status}.`);
  }
  if (typeof result.question !== "string" || !result.question.trim()) {
    throw new Error("Het Ollama-model gaf geen bruikbare vervolgvraag terug.");
  }
  if (
    typeof result.description !== "string" ||
    !result.description.trim() ||
    result.description.length > 240
  ) {
    throw new Error("Het Ollama-model gaf geen toelichting bij de vervolgvraag terug.");
  }
  if (typeof result.reason !== "string") {
    throw new Error("De AI gaf geen korte uitleg bij de vervolgvraag terug.");
  }

  return {
    question: result.question.trim(),
    description: result.description.trim(),
    reason: result.reason.trim(),
    model: typeof result.model === "string" ? result.model : "",
    adjusted: result.adjusted === true,
  };
}
