"""
Ollama AI-client voor nudge-generatie en vervolgvragen.
Handelt HTTP-communicatie met lokale Ollama-server af.
"""

import json
import os
import re
from typing import Dict, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from models import (
    UserAnswers, NudgeMessage, FollowUpQuestion, 
    QuestionCoverageResult, AIProviderError
)


# Ollama API-URL (standaard localhost:11434)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_TIMEOUT = 120

# Modelnaam uit omgeving of standaard Qwen3 4B
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen3:4b")


def get_model_name() -> str:
    """Geef de huidige Ollama-modelnaam."""
    return MODEL_NAME


class OllamaClient:
    """Client voor HTTP-communicatie met lokale Ollama-server."""
    
    def __init__(self, url: str = OLLAMA_URL, model: str = MODEL_NAME):
        """Initialiseer Ollama-client met URL en modelnaam."""
        self.url = url
        self.model = model
    
    def _make_request(
        self,
        system_prompt: str,
        user_content: Dict,
        response_schema: Dict = None,
        temperature: float = 0.4,
        max_tokens: int = 400
    ) -> Dict:
        """Verstuur request naar Ollama en ontvang JSON-response."""
        # Zet user content om naar JSON
        user_json = json.dumps(user_content, ensure_ascii=False)
        
        # Bouw request-body op
        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_json},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Voeg schema toe als gegeven
        if response_schema:
            request_body["format"] = response_schema
        
        # Maak HTTP-request en verstuur
        request = Request(
            self.url,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        # Ontvang antwoord, vang fouten op
        try:
            with urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")[:300]
            raise AIProviderError(
                f"Ollama gaf HTTP-fout {exc.code}: {details or exc.reason}"
            ) from exc
        except (TimeoutError, URLError) as exc:
            raise AIProviderError(
                f"Ollama is niet bereikbaar. Start Ollama en controleer of "
                f"model '{self.model}' is geïnstalleerd."
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AIProviderError(
                "Ollama gaf geen geldig JSON-antwoord terug."
            ) from exc
        
        return result
    
    def _extract_content(self, result: Dict) -> str:
        """Extraheer inhoud uit Ollama-response (zonder denkstappen)."""
        try:
            assistant_message = result["message"]
            if not isinstance(assistant_message, dict):
                raise AIProviderError("Ollama gaf geen geldig bericht terug.")
            
            # Check: geen denkstappen aanwezig?
            if assistant_message.get("thinking"):
                raise AIProviderError(
                    "Ollama gaf redeneerstappen terug terwijl die "
                    "uitgeschakeld horen te zijn."
                )
            
            content = assistant_message.get("content")
            if not isinstance(content, str):
                raise AIProviderError("Ollama gaf geen tekstinhoud terug.")
            
            return content
        except (KeyError, TypeError) as exc:
            raise AIProviderError(
                "Ollama gaf geen verwachte response-structuur."
            ) from exc
    
    def generate_nudge(
        self,
        answers: UserAnswers,
        service_name: str,
        action: str,
        system_prompt: str,
        response_schema: Dict
    ) -> NudgeMessage:
        """Genereer AI-nudge-bericht (aanmoediging met aanbeveling)."""
        # Zet antwoorden en dienstaanbeveling in JSON
        user_content = {
            "antwoorden": answers.as_dict(),
            "vaste_dienstkeuze": {
                "serviceName": service_name,
                "action": action
            }
        }
        
        # Verstuur naar model met schema-eis
        result = self._make_request(
            system_prompt=system_prompt,
            user_content=user_content,
            response_schema=response_schema,
            temperature=0.4,
            max_tokens=400
        )
        
        # Extraheer inhoud, parse JSON (met fallback voor <think> tags)
        content = self._extract_content(result)
        
        try:
            parsed = json.loads(
                re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
            )
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                "Ollama gaf geen geldig gestructureerd antwoord terug."
            ) from exc
        
        # Valideer antwoord: moet object zijn met message en reason
        if not isinstance(parsed, dict):
            raise AIProviderError("Model antwoord is geen object.")
        
        message = parsed.get("message")
        reason = parsed.get("reason")
        
        if not isinstance(message, str) or not message.strip() or len(message) > 400:
            raise AIProviderError(
                "Ollama gaf geen bruikbare korte nudge terug."
            )
        
        if not isinstance(reason, str):
            reason = ""
        
        return NudgeMessage(
            message=message.strip(),
            reason=reason.strip()[:300],
            model=self.model,
            confidence=1.0
        )
    
    def generate_follow_up(
        self,
        question: str,
        answer: str,
        context: Dict[str, str],
        system_prompt: str,
        response_schema: Dict
    ) -> FollowUpQuestion:
        """Genereer vervolgvraag om onduidelijk antwoord te verduidelijken."""
        # Zeer kort antwoord? Gebruik standaard fallback-vraag
        if len(answer.split()) < 4:
            return FollowUpQuestion(
                question="Kun je iets concreter vertellen wat er speelt?",
                description="Geef wat meer details zodat we beter kunnen helpen.",
                reason="Antwoord was te kort.",
                model=self.model,
                adjusted=True
            )
        
        # Voeg vraag, antwoord en context in JSON samen
        user_content = {
            "formulier_vraag": question,
            "antwoord": answer,
            "eerdere_antwoorden": context
        }
        
        # Verstuur naar model
        result = self._make_request(
            system_prompt=system_prompt,
            user_content=user_content,
            response_schema=response_schema,
            temperature=0.4,
            max_tokens=300
        )
        
        # Extraheer en parse JSON
        content = self._extract_content(result)
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                "Ollama gaf geen geldige vervolgvraag terug."
            ) from exc
        
        if not isinstance(parsed, dict):
            raise AIProviderError("Model antwoord is geen object.")
        
        # Haal vraag, beschrijving en reden uit response
        follow_up = parsed.get("question", "").strip()
        description = parsed.get("description", "").strip()
        reason = parsed.get("reason", "")
        
        # Valideer vraag (8-160 tekens)
        if not follow_up or len(follow_up) < 8 or len(follow_up) > 160:
            raise AIProviderError(
                "Ollama gaf geen bruikbare vervolgvraag terug."
            )
        
        # Valideer beschrijving (max 240 tekens)
        if not description or len(description) > 240:
            raise AIProviderError(
                "Ollama gaf geen toelichting bij de vervolgvraag terug."
            )
        
        # Check: herhaalt model het antwoord van gebruiker? Dat mag niet
        adjusted = len(answer) >= 6 and answer.casefold() in follow_up.casefold()
        
        if adjusted:
            follow_up = "Kun je iets concreter vertellen wat er speelt of waarbij je hulp zoekt?"
        
        return FollowUpQuestion(
            question=follow_up,
            description=description,
            reason=reason.strip()[:160] if isinstance(reason, str) else "",
            model=self.model,
            adjusted=adjusted
        )
    
    def check_question_coverage(
        self,
        question: str,
        answer: str,
        open_questions: List[Dict[str, str]],
        system_prompt: str,
        response_schema: Dict
    ) -> QuestionCoverageResult:
        """Controleer welke open vragen dit antwoord al beantwoordt."""
        # Zet vraag, antwoord en open vragen in JSON
        user_content = {
            "extra_vraag": question,
            "antwoord": answer,
            "open_vragen": open_questions
        }
        
        # Verstuur naar model (deterministisch, temp=0.0)
        result = self._make_request(
            system_prompt=system_prompt,
            user_content=user_content,
            response_schema=response_schema,
            temperature=0.0,
            max_tokens=120
        )
        
        # Extraheer en parse JSON
        content = self._extract_content(result)
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIProviderError(
                "Ollama gaf geen geldige controle-response terug."
            ) from exc
        
        # Haal covered vragen en reden uit response
        covered = parsed.get("covered") if isinstance(parsed, dict) else None
        reason = parsed.get("reason") if isinstance(parsed, dict) else None
        
        # Valideer covered (moet list zijn)
        if not isinstance(covered, list):
            raise AIProviderError(
                "Ollama gaf geen geldige lijst met beantwoorde vragen."
            )
        
        if not isinstance(reason, str):
            reason = "Geen reden gegeven."
        
        # Filter: alleen geldige vraag-IDs (voorkomen hallucinations)
        allowed_ids = {q["id"] for q in open_questions}
        valid_covered = [
            item for item in dict.fromkeys(covered)  # Verwijder duplicaten
            if item in allowed_ids
        ]
        
        return QuestionCoverageResult(
            covered=valid_covered,
            reason=reason.strip()[:160],
            model=self.model
        )
