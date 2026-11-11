// Diensten uit de O&P Rijk Producten- en Dienstencatalogus 2026 (categorie + voorbeelddienst).
const services = [
  {
    category: "Loopbaan- en Talentontwikkeling",
    name: "Loopbaanbegeleiding",
    keywords: ["loopbaan", "carrière", "carriere", "ontwikkel", "talent", "opleiding", "training", "groei", "doorgroeien", "baan"],
    action: "Plan een vrijblijvend gesprek over loopbaanbegeleiding.",
  },
  {
    category: "Teamontwikkeling",
    name: "Dag(deel) teamcoaching",
    keywords: ["team", "samenwerk", "collega", "sfeer", "teamgeest", "communicatie"],
    action: "Vraag een intake aan voor teamcoaching.",
  },
  {
    category: "Bedrijfszorg",
    name: "Advies en begeleiding bij verzuim",
    keywords: ["ziek", "verzuim", "stress", "burn", "gezond", "werkdruk", "werkplezier", "belast"],
    action: "Neem contact op met bedrijfszorg voor advies en begeleiding.",
  },
  {
    category: "Advocaten en Adviseurs Arbeidsrecht",
    name: "Arbeidsjuridische dienstverlening",
    keywords: ["ontslag", "contract", "juridisch", "recht", "geschil", "arbeidsrecht", "rechtspositie"],
    action: "Vraag een arbeidsjuridisch adviesgesprek aan.",
  },
  {
    category: "Organisatieadvies",
    name: "Organisatieonderzoek",
    keywords: ["organisatie", "reorganis", "structuur", "proces", "beleid", "inrichting", "werkwijze"],
    action: "Bespreek een organisatieonderzoek met een organisatieadviseur.",
  },
  {
    category: "Dienstverlening P-Direkt",
    name: "Dienstverlening P-Direkt",
    keywords: ["salaris", "verlof", "declar", "belon", "mobiliteit", "uit dienst", "autorisatie", "hr-administratie", "loon", "loonsverhoging", "salarisverhoging", "beloning", "functiewaardering"],
    action: "Neem contact op met P-Direkt voor je HR-vraag.",
  },
  {
    category: "Arbeidsmarkt",
    name: "Wervingsadvies",
    keywords: ["werving", "vacature", "personeel zoeken", "krapte", "stagiair", "trainee", "tijdelijk", "werven"],
    action: "Vraag wervingsadvies aan voor je vacature.",
  },
  {
    category: "Diversiteit, Gelijkwaardigheid en Inclusie",
    name: "Advies en expertise DGI",
    keywords: ["divers", "inclus", "gelijkwaardig", "discrimin", "banenafspraak", "beperking"],
    action: "Vraag advies en expertise aan over diversiteit en inclusie.",
  },
  {
    category: "Datagedreven hr",
    name: "Gesprek, workshop en advies",
    keywords: ["data", "dashboard", "cijfers", "analyse", "inzicht", "rapportage"],
    action: "Plan een gesprek over datagedreven hr.",
  },
  {
    category: "Binnenwerk",
    name: "Werksoorten",
    keywords: ["werksoort", "functiebouw", "functie-indeling", "functiewaardering"],
    action: "Vraag informatie aan over werksoorten.",
  },
];

const defaultService = services[4];

// Telt per dienst hoeveel trefwoorden in de antwoorden voorkomen.
function scoreServices(answers) {
  const text = Object.values(answers).join(" ").toLocaleLowerCase("nl-NL");

  return services
    .map((service, index) => ({
      service,
      index,
      matches: service.keywords.filter((keyword) => text.includes(keyword)),
    }))
    .sort((a, b) => b.matches.length - a.matches.length || a.index - b.index);
}

// Kiest drie opties: de best passende dienst eerst (voorgeselecteerd), daarna de rest.
function selectOptions(answers) {
  const scored = scoreServices(answers);
  const matched = scored.filter((entry) => entry.matches.length > 0);
  const ordered = matched.length > 0 ? matched : [{ service: defaultService, matches: [] }];
  const options = ordered.slice(0, 3).map((entry) => entry.service);

  for (const entry of scored) {
    if (options.length === 3) break;
    if (!options.includes(entry.service)) options.push(entry.service);
  }

  return { options, matches: ordered[0].matches };
}

export // Geeft de namen van diensten waarvan een trefwoord in de tekst voorkomt.
function findMatches(text) {
  const lowered = text.toLocaleLowerCase("nl-NL");
  return services
    .map((service) => ({
      name: service.name,
      matches: service.keywords.filter((keyword) => lowered.includes(keyword)),
    }))
    .filter((entry) => entry.matches.length > 0);
}

export // Maakt de regelgebaseerde dienstkeuze met drie opties en de gebruikte nudgetechnieken.
function createLocalNudge(answers) {
  const { options, matches } = selectOptions(answers);
  const primary = options[0];
  const timing = answers.timing.toLocaleLowerCase("nl-NL");

  return {
    serviceName: primary.name,
    category: primary.category,
    action: primary.action,
    message: `Je wilt werken aan "${answers.goal}". Een kleine stap ${timing}: ${primary.action}`,
    contactPreference: answers.contact,
    options: options.map(({ name, category, action }) => ({ name, category, action })),
    matchedKeywords: matches,
    scores: scoreServices(answers)
      .filter((entry) => entry.matches.length > 0)
      .slice(0, 5)
      .map((entry) => ({ name: entry.service.name, matches: entry.matches })),
    techniques: [
      "Beperkte keuze: slechts drie van de tien dienstcategorieën getoond",
      "Standaardkeuze: de eerste optie staat al aangevinkt",
      "Sociale bewijskracht (gesimuleerd): 'de meeste collega's kiezen dit'; er zijn geen echte cijfers",
    ],
  };
}
