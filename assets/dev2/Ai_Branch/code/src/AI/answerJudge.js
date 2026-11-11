import { findMatches } from "./nudgeEngine.js";

// Beoordeelt één antwoord met vaste regels en geeft een stemming en uitleg terug.
export function judgeAnswer(question, value) {
  if (question.choices) {
    if (value === "Later deze maand") {
      return { mood: "sad", why: "Je stelt het uit: dat maakt het voor mij moeilijker." };
    }
    if (value === "Vandaag" || value === "Een gesprek") {
      return { mood: "happy", why: `"${value}" past goed bij een snelle stap.` };
    }
    return { mood: "neutral", why: `"${value}" is prima, maar minder concreet.` };
  }

  const letters = value.replace(/[^a-zA-ZÀ-ÿ]/g, "");
  const words = value.split(/\s+/).filter(Boolean);
  const unique = new Set(letters.toLowerCase()).size;
  if (letters.length < 8 || words.length < 2 || unique < 4) {
    return {
      mood: "confused",
      why: "Ik mis nog wat context; ik vraag je om dit iets duidelijker te maken.",
    };
  }

  const matches = findMatches(value);
  if (matches.length > 0) {
    return {
      mood: "happy",
      why: `Ik herken woorden die bij ${matches[0].name} passen.`,
    };
  }
  return { mood: "neutral", why: "Ik vind geen duidelijke dienst in dit antwoord." };
}
