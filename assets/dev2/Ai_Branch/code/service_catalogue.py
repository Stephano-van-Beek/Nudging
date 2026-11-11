"""
DIENSTENCATALOGUS & REGELGEBASEERDE MATCHING

Dit bestand bevat:
1. ALLE 10 DIENSTEN van O&P Rijk (2026)
2. TREFWOORDEN voor elke dienst
3. REGELGEBASEERD MATCHING-ALGORITME (fallback als AI faalt)

SYNCHRONISATIE:
    BELANGRIJK: Dit bestand is GESYNCHRONISEERD met:
    -> src/AI/nudgeEngine.js (Frontend JavaScript)
    
    Als je hier diensten toevoegt/wijzigt:
    -> Voeg ze ook toe in nudgeEngine.js
    -> Anders matchen frontend en backend niet

TWEE MANIEREN OM DIENSTEN TE KIEZEN:

REGELGEBASEERD (Fallback, snel, betrouwbaar):
   - We tellen trefwoorden in wat gebruiker zegt
   - Gebruiker zegt: "Ik ben gestrest"
   - Trefwoord "stress" -> Bedrijfszorg +1 punt
   - Trefwoord "burn" -> Bedrijfszorg +1 punt
   - Bedrijfszorg wint = aanbeveling

AI-GEGENEREERD (Slim, flexibel, kan mislukken):
   - We geven alle antwoorden aan Ollama
   - Ollama genereert eigen aanbeveling
   - Als Ollama crashed -> fallback op regelgebaseerd

VOORDELEN REGELGEBASEERD:
   - Snel (geen AI nodig)
   - Betrouwbaar (geen hallucinations)
   - Transparant (we zien welke trefwoorden matchen)
   - Offline (geen API-call)

VOORDELEN AI:
   - Beter begrijpen context
   - Nuances detecteren
   - Gevallen opvangen die trefwoorden missen

VOORBEELD MATCHING:
    Gebruiker:
    - Situatie: "Ik heb veel stress"
    - Doel: "Beter slapen"
    - Barriere: "Werkdruk"
    
    Combined text: "ik heb veel stress beter slapen werkdruk"
    
    Scoring:
    - Bedrijfszorg: "stress" + "werkdruk" = 2 punten (WINT)
    - Loopbaanbeg: 0 punten
    - Teamcoaching: 0 punten
    
    AANBEVELING: Bedrijfszorg (met 2 trefwoorden)
"""

from typing import List, Dict
from models import Service


# ════════════════════════════════════════════════════════════════════════════
# COMPLETE SERVICE CATALOGUE - Alle 10 O&P Rijk Diensten
# ════════════════════════════════════════════════════════════════════════════

SERVICES: List[Service] = [
    Service(
        id="loopbaanbegeleiding",
        name="Loopbaanbegeleiding",
        category="Loopbaan- en Talentontwikkeling",
        description="Hulp bij loopbaan, carrière, ontwikkeling, opleiding, training, groei en doorstroming.",
        # TREFWOORDEN = Woorden waarop we zoeken in gebruikerantwoorden
        # Deze worden gematchd CASE-INSENSITIVE (geen verschil tussen STRESS en stress)
        keywords=["loopbaan", "carrière", "carriere", "ontwikkel", "talent", "opleiding", "training", "groei", "doorgroeien", "baan"],
        action="Plan een vrijblijvend gesprek over loopbaanbegeleiding."
    ),
    Service(
        id="teamcoaching",
        name="Dag(deel) teamcoaching",
        category="Teamontwikkeling",
        description="Ondersteuning bij samenwerking, teamgeest, sfeer en communicatie in teams.",
        keywords=["team", "samenwerk", "collega", "sfeer", "teamgeest", "communicatie"],
        action="Vraag een intake aan voor teamcoaching."
    ),
    Service(
        id="bedrijfszorg",
        name="Advies en begeleiding bij verzuim",
        category="Bedrijfszorg",
        description="Hulp bij ziekte, verzuim, stress, burn-out, werkdruk, gezondheid en belasting.",
        keywords=["ziek", "verzuim", "stress", "burn", "gezond", "werkdruk", "werkplezier", "belast"],
        action="Neem contact op met bedrijfszorg voor advies en begeleiding."
    ),
    Service(
        id="arbeidsjuridisch",
        name="Arbeidsjuridische dienstverlening",
        category="Advocaten en Adviseurs Arbeidsrecht",
        description="Juridisch advies bij ontslag, contracten, geschillen en rechtspositie.",
        keywords=["ontslag", "contract", "juridisch", "recht", "geschil", "arbeidsrecht", "rechtspositie"],
        action="Vraag een arbeidsjuridisch adviesgesprek aan."
    ),
    Service(
        id="organisatieonderzoek",
        name="Organisatieonderzoek",
        category="Organisatieadvies",
        description="Ondersteuning bij organisatie, reorganisatie, structuur, proces, beleid en werkwijze.",
        keywords=["organisatie", "reorganis", "structuur", "proces", "beleid", "inrichting", "werkwijze"],
        action="Bespreek een organisatieonderzoek met een organisatieadviseur."
    ),
    Service(
        id="p-direkt",
        name="Dienstverlening P-Direkt",
        category="Dienstverlening P-Direkt",
        description="HR-administratie: salaris, loon, beloning, verlof, declaraties, mobiliteit, uit dienst, autorisatie.",
        keywords=["salaris", "verlof", "declar", "belon", "mobiliteit", "uit dienst", "autorisatie", "hr-administratie", "loon", "loonsverhoging", "salarisverhoging", "beloning", "functiewaardering"],
        action="Neem contact op met P-Direkt voor je HR-vraag."
    ),
    Service(
        id="wervingsadvies",
        name="Wervingsadvies",
        category="Arbeidsmarkt",
        description="Advies bij werving, vacatures, personeel zoeken, krapte, stagiairs en trainees.",
        keywords=["werving", "vacature", "personeel zoeken", "krapte", "stagiair", "trainee", "tijdelijk", "werven"],
        action="Vraag wervingsadvies aan voor je vacature."
    ),
    Service(
        id="dgi",
        name="Advies en expertise DGI",
        category="Diversiteit, Gelijkwaardigheid en Inclusie",
        description="Advies over diversiteit, inclusie, gelijkwaardigheid en banenafspraak.",
        keywords=["divers", "inclus", "gelijkwaardig", "discrimin", "banenafspraak", "beperking"],
        action="Vraag advies en expertise aan over diversiteit en inclusie."
    ),
    Service(
        id="datagedreven-hr",
        name="Gesprek, workshop en advies",
        category="Datagedreven hr",
        description="Ondersteuning bij data, dashboards, cijfers, analyse, inzicht en rapportage.",
        keywords=["data", "dashboard", "cijfers", "analyse", "inzicht", "rapportage"],
        action="Plan een gesprek over datagedreven hr."
    ),
    Service(
        id="werksoorten",
        name="Werksoorten",
        category="Binnenwerk",
        description="Informatie over werksoorten, functiebouw, functie-indeling en functiewaardering.",
        keywords=["werksoort", "functiebouw", "functie-indeling", "functiewaardering", "functie", "waardering"],
        action="Vraag informatie aan over werksoorten."
    ),
]

# Standaard fallback-dienst als NIETS matcht
# Organisatieonderzoek is neutraal en kan voor veel situaties bruikbaar zijn
DEFAULT_SERVICE = SERVICES[4]


# ════════════════════════════════════════════════════════════════════════════
# GET_SERVICE_BY_ID - Dienst Opzoeken Op ID
# ════════════════════════════════════════════════════════════════════════════

def get_service_by_id(service_id: str) -> Service:
    """Zoek dienst op ID uit catalogus."""
    for service in SERVICES:
        if service.id == service_id:
            return service
    raise ValueError(f"Dienst '{service_id}' niet gevonden.")


# ════════════════════════════════════════════════════════════════════════════
# SCORE_SERVICES - Het Regelgebaseerde Matching-Algoritme
# ════════════════════════════════════════════════════════════════════════════

def score_services(answers: Dict[str, str]) -> List[Dict]:
    """Tel trefwoorden per dienst: regelgebaseerd matching-algoritme."""
    # Zet alle antwoorden samen in 1 string, maak lowercase
    combined_text = " ".join(answers.values()).lower()
    
    # Score elke dienst op trefwoord-matches
    scored = []
    for index, service in enumerate(SERVICES):
        # Zoek welke trefwoorden voorkomen in combined_text
        matches = [kw for kw in service.keywords if kw in combined_text]
        
        scored.append({
            "service": service,
            "index": index,
            "matches": matches,
            "score": len(matches)
        })
    
    # Sorteer op score (hoger eerst), dan op index (lagere eerst voor tiebreaker)
    scored.sort(key=lambda x: (-x["score"], x["index"]))
    
    return scored


def select_recommendation_options(answers: Dict[str, str]) -> Dict:
    """Selecteer top 3 dienstkeuzen met geselecteerde top-optie."""
    # Score alle diensten regelgebaseerd
    scored = score_services(answers)
    
    # Filter diensten MET trefwoord-matches
    matched = [s for s in scored if s["matches"]]
    
    # Fallback naar DEFAULT_SERVICE als niets matchte
    top_matches = matched if matched else [{"service": DEFAULT_SERVICE, "matches": []}]
    
    # Neem TOP 3 diensten
    options = [entry["service"] for entry in top_matches[:3]]
    
    # Vul aan tot 3 (voeg diensten zonder matches toe als nodig)
    for entry in scored:
        if len(options) >= 3:
            break
        if entry["service"] not in options:
            options.append(entry["service"])
