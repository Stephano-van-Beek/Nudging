"""
DATA KLASSEN VOOR NUDGE-APP

Dit bestand bevat alle "model"-klassen. Models zijn objecten die data opslaan.

Denk eraan als voorgemaakte formulieren die je invult met informatie.
Elk model weet hoe het zichzelf kan controleren en omzetten naar JSON.

VOORBEELD:
    Je hebt een klasse "UserAnswers" die 6 vragen beantwoord opslaat.
    In plaats van losse variabelen, hebben we 1 object met alles erin.
    
    answers = UserAnswers(
        situation="Ik ben gestrest",
        goal="Beter slapen",
        barrier="Werk",
        support="Coaching",
        timing="Snel",
        contact="Email"
    )

WAAROM KLASSEN?
    - Alles bij elkaar
    - Gemakkelijk controleren
    - Gemakkelijk naar JSON omzetten
    - Makkelijker in tests
    - Python weet wat type data het is (type-safe)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


# @dataclass = Laat Python automatisch __init__, __repr__, __eq__ schrijven

@dataclass
class UserAnswers:
    """
    Verzamelt alle 6 antwoorden die een gebruiker geeft.
    
    Dit is als een voorgemaakt formulier met 6 velden:
    1. situation: Wat is je situatie?
    2. goal: Wat wil je bereiken?
    3. barrier: Wat staat je in de weg?
    4. support: Hulp bij wat?
    5. timing: Wanneer wil je starten?
    6. contact: Hoe bereiken we je?
    
    GEBRUIK:
        answers = UserAnswers(
            situation="Ik ben gestrest",
            goal="Beter werkplezier",
            barrier="Te veel werkdruk",
            support="Coaching",
            timing="Snel",
            contact="Email"
        )
    
    TYPE HINTS:
        : str = Dit moet TEKST zijn, niet een getal of iets anders
    """
    
    # VELD 1: Huidige situatie (wat speelt er?)
    situation: str
    
    # VELD 2: Doel (wat wil je bereiken?)
    goal: str
    
    # VELD 3: Barriere (wat staat je in de weg?)
    barrier: str
    
    # VELD 4: Ondersteuning (wat voor hulp wil je?)
    support: str
    
    # VELD 5: Timing (wanneer wil je beginnen?)
    timing: str
    
    # VELD 6: Contactvoorkeur (hoe bereiken we je?)
    contact: str

    def as_dict(self) -> Dict[str, str]:
        """Zet UserAnswers om naar dict (voor JSON-serialisatie)."""
        return {
            'situation': self.situation,
            'goal': self.goal,
            'barrier': self.barrier,
            'support': self.support,
            'timing': self.timing,
            'contact': self.contact
        }

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'UserAnswers':
        """Maak UserAnswers object uit dict, valideer alle 6 velden."""
        # Controleer dat alle 6 velden aanwezig zijn
        required_fields = {'situation', 'goal', 'barrier', 'support', 'timing', 'contact'}
        
        if not isinstance(data, dict) or set(data.keys()) != required_fields:
            raise ValueError(f"Alle velden moeten aanwezig zijn: {required_fields}")
        
        # Valideer elk veld: moet tekst zijn, niet leeg, niet langer dan 1000
        for key, value in data.items():
            if not isinstance(value, str):
                raise ValueError(f"Veld '{key}' moet tekst zijn, niet getal of iets anders.")
            
            if not value.strip():
                raise ValueError(f"Veld '{key}' mag niet leeg zijn.")
            
            if len(value) > 1000:
                raise ValueError(f"Veld '{key}' is te lang (max 1000 tekens).")
        # Alles OK! Maak het object
        # **data = Zet alle sleutels/waarden in als parameters
        return UserAnswers(**data)


# Service uit O&P Rijk-catalogus (diagnostiek, matching, aanbeveling)
@dataclass
class Service:
    """
    Dit is een DIENST uit de O&P Rijk-catalogus (2026).
    
    Een dienst is een soort hulp die we kunnen aanbieden.
    Bijvoorbeeld: "Bedrijfszorg" helpt bij stress en burn-out.
    
    VOORBEELD DIENST:
        ┌─────────────────────────────────────────────┐
        │ ID:       "bedrijfszorg"                     │
        │ Naam:     "Advies en begeleiding bij verzuim"│
        │ Categorie:"Bedrijfszorg"                     │
        │ Beschr.:  "Hulp bij ziekte, verzuim, stress" │
        │ Keywords: ["ziek", "verzuim", "stress", ...] │
        │ Actie:    "Neem contact op met bedrijfszorg" │
        └─────────────────────────────────────────────┘
    
    HOEWERK HET MATCHEN:
        Gebruiker zegt: "Ik ben gestrest en heb burn-out"
        
        We zoeken naar TREFWOORDEN in wat ze zeggen:
        - Trefwoord "stress" gevonden? JA! +1 punt
        - Trefwoord "burn" gevonden? JA! +1 punt
        
        Bedrijfszorg krijgt 2 punten = hoog match!
        Dit is de beste dienst voor deze persoon.
    
    GEBRUIK:
        service = Service(
            id="bedrijfszorg",
            name="Advies en begeleiding bij verzuim",
            category="Bedrijfszorg",
            description="Hulp bij ziekte, verzuim, stress, burn-out...",
            keywords=["ziek", "verzuim", "stress", "burn", "gezond", ...],
            action="Neem contact op met bedrijfszorg"
        )
    """
    
    # Unieke ID (bijv. "bedrijfszorg" of "teamcoaching")
    # Net als een product-code in een supermarkt
    id: str
    
    # Prachtige naam van de dienst (wat de gebruiker ziet)
    name: str
    
    # Categorie (soort)
    # Bijv. "Bedrijfszorg" of "Loopbaan- en Talentontwikkeling"
    category: str
    
    # Langere beschrijving (wat doet deze dienst?)
    description: str
    
    # TREFWOORDEN = Woorden waarnaar we zoeken in antwoorden
    # Als gebruiker zegt: "Ik heb stress" → trefwoord "stress" gevonden!
    keywords: List[str]
    
    # De actie die we voorstellen
    # Bijv. "Neem contact op met bedrijfszorg"
    action: str

    def as_dict(self) -> Dict:
        """Zet Service om naar dict (voor JSON)."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'keywords': self.keywords,
            'action': self.action
        }


# Aanbeveling van dienst (regelgebaseerd of AI-gegenereerd)
@dataclass
class ServiceRecommendation:
    """
    Dit is de aanbeveling die we geven: "Jij zou deze dienst kunnen proberen!"
    
    De aanbeveling kan op 2 manieren ontstaan:
    1. REGELGEBASEERD (trefwoorden tellen)
    2. AI-GEGENEREERD (Ollama model beslist)
    
    VOORBEELD:
        Gebruiker zegt: "Ik ben gestrest"
        We matchen op trefwoorden → Bedrijfszorg match!
        
        recommendation = ServiceRecommendation(
            service_id="bedrijfszorg",
            service_name="Advies en begeleiding bij verzuim",
            category="Bedrijfszorg",
            action="Neem contact op met bedrijfszorg",
            confidence=0.95,  # 95% zeker dat dit goed is
            reason="Gebruiker noemde 'stress' en 'burn-out'",
            source="fallback"  # (Niet van AI, maar van trefwoorden)
        )
    
    CONFIDENCE (ZEKERHEID):
        - 0.0 = Niet zeker
        - 0.5 = Redelijk zeker
        - 1.0 = Heel zeker
    
    SOURCE (BRON):
        - "ai" = Van het AI-model
        - "fallback" = Van trefwoord-matching (als AI faalt)
    """
    
    # ID van de aanbevolen dienst
    service_id: str
    
    # Naam van de dienst
    service_name: str
    
    # Categorie
    category: str
    
    # Wat moeten ze doen? (bijv. "Bel bedrijfszorg")
    action: str
    
    # Hoe zeker zijn we? (0.0 = niet zeker, 1.0 = heel zeker)
    confidence: float = 0.5
    
    # Waarom deze dienst? (uitleg)
    reason: str = ""
    
    # Welke trefwoorden pasten?
    matched_keywords: List[str] = None
    
    # Is dit van AI ("ai") of fallback ("fallback")?
    source: str = "fallback"

    def __post_init__(self):
        """Initialiseer matched_keywords als None."""
        if self.matched_keywords is None:
            self.matched_keywords = []

    def as_dict(self) -> Dict:
        """Omzet ServiceRecommendation naar dict."""
        return {
            'serviceId': self.service_id,
            'serviceName': self.service_name,
            'category': self.category,
            'action': self.action,
            'confidence': round(self.confidence, 2),  # Rond af op 2 decimalen
            'reason': self.reason,
            'matchedKeywords': self.matched_keywords,
            'source': self.source
        }


# AI-gegenereerd nudgebericht naar gebruiker
@dataclass
class NudgeMessage:
    """
    Dit is het BERICHTJE dat het AI-model genereert.
    
    Een "nudge" (duwtje) is een zachte aanmoediging.
    
    VOORBEELD:
        message = NudgeMessage(
            message="Je bent gestrest en heb burn-out gevoel. Een goed eerste "
                    "stap is contact opnemen met bedrijfszorg. Velen doen dat!",
            reason="Gebruiker noemde stress en veel werkdruk",
            model="qwen3:4b",  # Welk AI-model dit maakte
            confidence=0.95  # 95% vertrouwen in dit bericht
        )
    
    HET BERICHTJE ZIET ER ZO UIT:
        ┌────────────────────────────────────────────────┐
        │ "Jij bent gestrest en heb burn-out gevoel.     │
        │  Een goed eerste stap is contact opnemen met   │
        │  bedrijfszorg. Velen doen dat!"                │
        └────────────────────────────────────────────────┘
    
    WAAR KOMT DEZE TEKST VANDAAN?
        1. We geven het AI-model (Ollama) alle antwoorden
        2. Ollama genereert een persoonlijk, vriendelijk bericht
        3. Het bericht voldoet aan strikte regels (max 2 zinnen, etc.)
    """
    
    # De daadwerkelijke nudge-tekst (wat we naar gebruiker sturen)
    message: str
    
    # Waarom deze nudge? (voor debug/logging)
    reason: str = ""
    
    # Welk AI-model maakte dit? (bijv. "qwen3:4b")
    model: str = ""
    
    # Hoe zeker zijn we van dit bericht? (0.0 tot 1.0)
    confidence: float = 1.0

    def as_dict(self) -> Dict:
        """Converteer NudgeMessage naar dict (voor JSON-response)."""
        return {
            'message': self.message,
            'reason': self.reason,
            'model': self.model,
            'confidence': round(self.confidence, 2)
        }



# Vervolgvraag voor verduidelijking van onduidelijk antwoord
@dataclass
class FollowUpQuestion:
    """
    Dit is een vervolgvraag die we stellen om meer te begrijpen.
    
    WAAROM VERVOLGVRAGEN?
        Gebruiker zegt alleen: "Ik ben gestrest"
        Dat is niet genoeg om goed te helpen!
        
        We stellen een vervolgvraag:
        "Wat is de OORZAAK van je stress?"
        → Nu begrijpen we het probleem beter
    
    VOORBEELD:
        question = FollowUpQuestion(
            question="Wat is de oorzaak van je stress?",
            description="Help ons meer over je situatie begrijpen",
            reason="Gebruiker noemde werkstress",
            model="qwen3:4b",
            adjusted=False
        )
    
    BESCHRIJVING vs REASON:
        - description: Wat zeggen we tegen de GEBRUIKER?
                      "Help ons meer over je situatie begrijpen"
        - reason: Wat is de INTERNE REDEN?
                 "Gebruiker noemde werkstress, need details"
    
    VOORBEELD DIALOOG:
        User:   "Ik ben gestrest"
        AI:     "Wat is de oorzaak van je stress?" ← FollowUpQuestion
        User:   "Te veel werkdruk"
        AI:     "Ah! Dan kan bedrijfszorg helpen" ← Betere aanbeveling!
    
    ADJUSTED (AANGEPAST):
        - False = Dit is een GELDIG AI-gegenereerd vraag
        - True = Dit is een STANDAARD fallback vraag
                 (AI kon niks bedenken, dus default vraag)
    """
    
    # De daadwerkelijke vervolgvraag
    question: str
    
    # Wat zeggen we tegen de gebruiker? (vriendelijk)
    description: str
    
    # Interne reden waarom we dit vragen
    reason: str
    
    # Welk AI-model maakte deze vraag?
    model: str = ""
    
    # Is dit een standaard fallback vraag?
    # False = AI genereert dit, True = Default vraag
    adjusted: bool = False

    def as_dict(self) -> Dict:
        """Converteer naar dict voor JSON-serialisatie."""
        return {
            'question': self.question,
            'description': self.description,
            'reason': self.reason,
            'model': self.model,
            'adjusted': self.adjusted
        }


# Resultaat van check welke vragen al beantwoord zijn
@dataclass
class QuestionCoverageResult:
    """
    Dit vertelt ons: "Welke vragen heeft de gebruiker al beantwoord?"
    
    VOORBEELD:
        De 6 vragen zijn:
        1. Wat is je situatie?          ✓ BEANTWOORD
        2. Wat is je doel?              ✓ BEANTWOORD
        3. Wat is je barrière?          ✓ BEANTWOORD
        4. Wat helpt?                   ✗ NIET BEANTWOORD
        5. Timing?                      ✗ NIET BEANTWOORD
        6. Contactgegevens?             ✓ BEANTWOORD
        
        result = QuestionCoverageResult(
            covered=['situation', 'goal', 'barrier', 'contact'],
            reason="Gebruiker antwoordde volledig op vragen 1,2,3,6",
            model="qwen3:4b"
        )
    
    WAAROM NODIG?
        We willen weten: "Hebben we genoeg info?"
        - Alle 6 vragen beantwoord? → Kan aanbeveling geven!
        - Nog 2 vragen open? → Stel vervolgvragen
    
    COVERED (BEANTWOORD):
        Lijst van vragen die al beantwoord zijn:
        ['situation', 'goal', 'barrier', 'support', 'timing', 'contact']
    """
    
    # Welke vragen zijn al beantwoord?
    # Bijv: ['situation', 'goal', 'barrier']
    covered: List[str]
    
    # Waarom deze controle? (korte uitleg)
    reason: str
    
    # Welk AI-model voerde deze controle uit?
    model: str = ""

    def as_dict(self) -> Dict:
        """Omzet naar dict (voor JSON-response)."""
        return {
            'covered': self.covered,
            'reason': self.reason,
            'model': self.model
        }


# Aangepaste exception voor AI-provider fouten
class AIProviderError(Exception):
    """Fout van Ollama-server (timeout, invalid JSON, etc)."""
    pass
