"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    VALIDATIELOGICA VOOR API-VERZOEKEN                      ║
╚════════════════════════════════════════════════════════════════════════════╝

Dit bestand zorgt ervoor dat ALLE inkomende data van de frontend CORRECT en
VEILIG is voordat we ermee werken.

WAAROM VALIDATIE?
    Stel je voor: een gebruiker stuurt slechte data!
    
    SLECHTE DATA:
        ✗ Lege antwoorden ("" is niet geldig)
        ✗ Te lange antwoorden (>1000 tekens)
        ✗ Verkeerde type data (getal in plaats van tekst)
        ✗ Ontbrekende velden (slechts 5 van 6 vragen)
        ✗ Verdachte data (hack-pogingen!)
    
    VALIDATIE CHECKT:
        ✓ Zijn alle velden aanwezig?
        ✓ Is elk veld het juiste TYPE?
        ✓ Is geen veld leeg?
        ✓ Zijn velden niet te lang?
        ✓ Zijn velden veilig (geen injecties)?

ANALOGIE:
    Een validatie-functie is zoals een RECEPTIONIST bij een ziekenhuis:
    
    Patiënt komt aan met een formulier
    Receptionist checkt:
        ✓ Alle hokjes ingevuld?
        ✓ Handschrift leesbaar?
        ✓ Geen verdachte vlek op papier?
    
    Als OK → Patiënt mag door
    Als fout → "Sorry, vul dit beter in"
    
    Net zo: Validatie checkt data voordat het in OUR SYSTEM gaat!

PROCESSEN DIE WE VALIDEREN:
    1. validate_nudge_request()
       → Frontend stuurt antwoorden + aanbeveling
       → We checken: Zijn alle 6 velden goed?
    
    2. validate_follow_up_request()
       → Frontend stuurt vervolgvraag + antwoord
       → We checken: Is vraag + antwoord valide?
    
    3. validate_skip_check_request()
       → Frontend vraagt: "Zijn er al beantwoorde vragen?"
       → We checken: Zijn die vragen echt?
    
    4. validate_classify_request()
       → Frontend vraagt aanbeveling
       → We checken: Zijn alle 6 antwoorden goed?
"""

from typing import Dict, List, Tuple
from models import UserAnswers, Service


# CONSTANTEN = Instellingen die overal gebruikt worden
# MAX = Maximale lengte

ANSWER_FIELDS = {"situation", "goal", "barrier", "support", "timing", "contact"}
MAX_ANSWER_LENGTH = 1000  # Max 1000 tekens per antwoord
MAX_QUESTION_LENGTH = 300  # Max 300 tekens voor vervolgvragen
MAX_BODY_BYTES = 8192     # Max 8 KB voor hele request


# ════════════════════════════════════════════════════════════════════════════
# VALIDATE_NUDGE_REQUEST - Controleer Nudge-Aanvraag
# ════════════════════════════════════════════════════════════════════════════

def validate_nudge_request(payload: object) -> Tuple[UserAnswers, Dict[str, str]]:
    """Valideer nudge-aanvraag: controleert antwoorden en dienstaanbeveling."""
    # Eerste check: is het wel een dict?
    if not isinstance(payload, dict):
        raise ValueError("De aanvraag moet een JSON-object zijn.")

    answers_data = payload.get("answers")
    recommendation = payload.get("recommendation")
    
    # Zet en valideer UserAnswers (UserAnswers.from_dict controleert alles)
    try:
        answers = UserAnswers.from_dict(answers_data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Antwoorden ongeldig: {e}")

    # Controleer aanbeveling (serviceName en action)
    if not isinstance(recommendation, dict):
        raise ValueError("De aanvraag mist de regelgebaseerde dienstkeuze.")

    service_name = recommendation.get("serviceName")
    action = recommendation.get("action")
    
    # Valideer serviceName (string, niet leeg, max 100 tekens)
    if not isinstance(service_name, str) or not service_name.strip() or len(service_name) > 100:
        raise ValueError("De aanbevolen dienst is ongeldig.")
    
    # Valideer action (string, niet leeg, max 300 tekens)
    if not isinstance(action, str) or not action.strip() or len(action) > 300:
        raise ValueError("De aanbevolen actie is ongeldig.")

    # Alles OK! Return gevalideerde data
    return answers, {
        "serviceName": service_name.strip(),
        "action": action.strip()
    }


# Valideer vervolgvraag-aanvraag van frontend
def validate_follow_up_request(payload: object) -> Tuple[str, str, Dict[str, str]]:
    """Valideer vervolgvraag: controleert vraag, antwoord en context."""
    if not isinstance(payload, dict):
        raise ValueError("De aanvraag moet een JSON-object zijn.")
    
    question = payload.get("question")
    answer = payload.get("answer")
    context = payload.get("context", {})
    
    # Valideer vraag (string, niet leeg, max 300)
    if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(f"De vraag moet tussen 1 en {MAX_QUESTION_LENGTH} tekens zijn.")
    
    # Valideer antwoord (string, niet leeg, max 1000)
    if not isinstance(answer, str) or not answer.strip() or len(answer) > MAX_ANSWER_LENGTH:
        raise ValueError(f"Het antwoord moet tussen 1 en {MAX_ANSWER_LENGTH} tekens zijn.")
    
    # Valideer context (eerdere antwoorden)
    if not isinstance(context, dict) or len(context) > len(ANSWER_FIELDS):
        raise ValueError("De context met eerdere antwoorden is ongeldig.")
    
    # Check elk context-veld
    for key, value in context.items():
        if key not in ANSWER_FIELDS:
            raise ValueError(f"Onbekend contextveld: {key}")
        if not isinstance(value, str) or len(value) > MAX_ANSWER_LENGTH:
            raise ValueError(f"Contextveld '{key}' moet een string zijn.")
    
    return question.strip(), answer.strip(), context


# Valideer aanvraag voor check al beantwoorde vragen
def validate_skip_check_request(payload: object) -> Tuple[str, str, List[Dict[str, str]]]:
    """Valideer skip-check-aanvraag: controleert vraag, antwoord, open vragen."""
    if not isinstance(payload, dict):
        raise ValueError("De aanvraag moet een JSON-object zijn.")
    
    question = payload.get("question")
    answer = payload.get("answer")
    open_questions = payload.get("openQuestions")
    
    # Valideer vraag (string, niet leeg, max 300)
    if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
        raise ValueError("De extra vraag is ongeldig.")
    
    # Valideer antwoord (string, niet leeg, max 1000)
    if not isinstance(answer, str) or not answer.strip() or len(answer) > MAX_ANSWER_LENGTH:
        raise ValueError("Het antwoord moet tekst van maximaal 1000 tekens zijn.")
    
    # Valideer open vragen (list, niet leeg, max 6 items)
    if not isinstance(open_questions, list) or not open_questions or len(open_questions) > len(ANSWER_FIELDS):
        raise ValueError("De open vragen zijn ongeldig.")
    
    # Controleer elke open vraag op ID en titel
    cleaned = []
    for item in open_questions:
        if not isinstance(item, dict):
            raise ValueError("Elke open vraag moet een object zijn.")
        
        q_id = item.get("id")
        q_title = item.get("title")
        
        # Is q_id een geldige vraag-ID?
        if q_id not in ANSWER_FIELDS:
            raise ValueError(f"Onbekende vraag-ID: {q_id}")
        
        # Is q_title een geldige string?
        if not isinstance(q_title, str) or not q_title.strip() or len(q_title) > MAX_QUESTION_LENGTH:
            raise ValueError("Elke vraag moet een titel hebben.")
        
        cleaned.append({"id": q_id, "title": q_title.strip()})
    
    return question.strip(), answer.strip(), cleaned


# Valideer classificatie-aanvraag (dienst kiezen)
def validate_classify_request(payload: object) -> UserAnswers:
    """Valideer classificatie-aanvraag: controleert alle 6 antwoorden."""
    if not isinstance(payload, dict):
        raise ValueError("De aanvraag moet een JSON-object zijn.")
    
    answers_data = payload.get("answers")
    
    # UserAnswers.from_dict doet alle validatie voor ons
    try:
        return UserAnswers.from_dict(answers_data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Antwoorden ongeldig: {e}")
