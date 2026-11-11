// De eerste vier open vragen waarmee de bot de situatie van de gebruiker begrijpt.
export const intakeQuestions = [
  {
    id: "situation",
    title: "Vertel kort wat er nu speelt",
    hint: "Bijvoorbeeld: mijn team werkt slecht samen, ik wil doorgroeien of ik heb een vraag over verlof.",
    placeholder: "Mijn situatie is...",
  },
  {
    id: "goal",
    title: "Wat wil je graag bereiken?",
    hint: "Een klein of groot doel is allebei goed.",
    placeholder: "Ik wil graag...",
  },
  {
    id: "barrier",
    title: "Wat maakt dit nu lastig?",
    hint: "Denk aan tijd, informatie, budget, motivatie of iets anders.",
    placeholder: "Ik loop vooral vast op...",
  },
  {
    id: "support",
    title: "Waar zou je hulp bij willen?",
    hint: "Je hoeft het nog niet precies te weten.",
    placeholder: "Hulp bij...",
  },
];

// Twee korte keuzevragen die de nudge persoonlijker maken.
export const followUpQuestions = [
  {
    id: "timing",
    title: "Wanneer wil je hiermee een eerste stap zetten?",
    choices: ["Vandaag", "Deze week", "Later deze maand"],
  },
  {
    id: "contact",
    title: "Welke vorm van hulp past het best bij jou?",
    choices: ["Een gesprek", "Online informatie", "Een korte herinnering"],
  },
];
