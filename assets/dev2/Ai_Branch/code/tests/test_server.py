import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from unittest.mock import MagicMock, patch
from urllib.error import URLError
from urllib.request import Request, urlopen

from server import (
    AIProviderError,
    NudgeRequestHandler,
    classify_service,
    find_answered_questions,
    generate_follow_up,
    generate_message,
    validate_classify_payload,
    validate_follow_up_payload,
    validate_payload,
    validate_skip_payload,
)


def valid_payload():
    return {
        "answers": {
            "situation": "Ik wil mijn werk veranderen.",
            "goal": "Een opleiding vinden.",
            "barrier": "Ik weet niet waar ik moet beginnen.",
            "support": "Informatie over mogelijkheden.",
            "timing": "Deze week",
            "contact": "Online informatie",
        },
        "recommendation": {
            "serviceName": "Werk & ontwikkeling",
            "action": "Plan een vrijblijvend gesprek met een loopbaanadviseur.",
        },
    }


class ValidatePayloadTests(unittest.TestCase):
    def test_accepts_six_answers_and_rule_based_recommendation(self):
        answers, recommendation = validate_payload(valid_payload())
        self.assertEqual(answers["goal"], "Een opleiding vinden.")
        self.assertEqual(recommendation["serviceName"], "Werk & ontwikkeling")

    def test_rejects_missing_answers(self):
        payload = valid_payload()
        del payload["answers"]["goal"]
        with self.assertRaisesRegex(ValueError, "zes antwoorden"):
            validate_payload(payload)

    def test_rejects_oversized_answer(self):
        payload = valid_payload()
        payload["answers"]["goal"] = "x" * 1001
        with self.assertRaisesRegex(ValueError, "maximaal 1000"):
            validate_payload(payload)

    def test_validates_follow_up_input(self):
        question, answer, context = validate_follow_up_payload(
            {
                "question": "Wat speelt er?",
                "answer": "fuck you",
                "context": {"situation": "Ik weet het nog niet."},
            }
        )
        self.assertEqual(question, "Wat speelt er?")
        self.assertEqual(answer, "fuck you")
        self.assertEqual(context["situation"], "Ik weet het nog niet.")

    def test_rejects_empty_follow_up_answer(self):
        with self.assertRaisesRegex(ValueError, "antwoord moet tekst"):
            validate_follow_up_payload(
                {"question": "Wat bedoel je?", "answer": " ", "context": {}}
            )


class GenerateMessageTests(unittest.TestCase):
    @patch("server.urlopen")
    def test_sends_structured_qwen_request_and_returns_message_and_reason(self, open_url):
        chat_response = MagicMock()
        chat_response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "message": "  De meeste collega's kiezen loopbaanbegeleiding.  ",
                            "reason": "Je noemde een opleiding.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = chat_response

        result = generate_message(*validate_payload(valid_payload()))

        self.assertEqual(result["message"], "De meeste collega's kiezen loopbaanbegeleiding.")
        self.assertEqual(result["reason"], "Je noemde een opleiding.")
        body = json.loads(open_url.call_args.args[0].data)
        self.assertEqual(body["model"], "qwen3:4b")
        self.assertFalse(body["stream"])
        self.assertFalse(body["think"])
        self.assertEqual(body["format"]["required"], ["message", "reason"])

    @patch("server.urlopen")
    def test_rejects_unstructured_reply(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"message": {"content": "gewone tekst"}}
        ).encode("utf-8")
        open_url.return_value = response

        with self.assertRaisesRegex(AIProviderError, "gestructureerd"):
            generate_message(*validate_payload(valid_payload()))

    @patch("server.urlopen", side_effect=URLError("connection refused"))
    def test_reports_unavailable_ollama(self, _open_url):
        with self.assertRaisesRegex(AIProviderError, "Ollama is niet bereikbaar"):
            generate_message(*validate_payload(valid_payload()))

    @patch("server.urlopen")
    def test_generates_structured_follow_up_question(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "question": "Kun je vertellen wat er precies speelt?",
                            "description": "Vertel bijvoorbeeld waar je ondersteuning bij zoekt.",
                            "reason": "De eerste reactie maakt de hulpvraag nog niet duidelijk.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = response

        result = generate_follow_up(
            "Vertel kort wat er speelt", "fuck you", {"goal": "Ik wil hulp."}
        )

        self.assertEqual(
            result,
            {
                "question": "Kun je vertellen wat er precies speelt?",
                "description": "Vertel bijvoorbeeld waar je ondersteuning bij zoekt.",
                "reason": "De eerste reactie maakt de hulpvraag nog niet duidelijk.",
                "model": "qwen3:4b",
                "adjusted": False,
            },
        )
        body = json.loads(open_url.call_args.args[0].data)
        self.assertEqual(body["format"]["required"], ["question", "description", "reason"])
        self.assertIn("O&P Rijk-vragenformulier", body["messages"][0]["content"])

    @patch("server.urlopen")
    def test_rejects_follow_up_without_a_description(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "question": "Wat maakt dit lastig?",
                            "description": "",
                            "reason": "Meer context is nodig.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = response

        with self.assertRaisesRegex(AIProviderError, "toelichting"):
            generate_follow_up("Wat maakt dit lastig?", "tijd", {})

    @patch("server.urlopen")
    def test_skip_check_only_returns_known_open_questions(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {"covered": ["barrier", "unknown", "barrier"], "reason": "Obstakel genoemd."}
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = response
        open_questions = [{"id": "barrier", "title": "Wat maakt dit nu lastig?"}]

        result = find_answered_questions(
            "Wat maakt het lastig?", "Mijn moeder is al weken ziek", open_questions
        )

        self.assertEqual(result["covered"], ["barrier"])

    @patch("server.urlopen")
    def test_skip_check_ignores_very_short_answers(self, open_url):
        result = find_answered_questions(
            "Wat maakt het lastig?", "tijd", [{"id": "barrier", "title": "Wat?"}]
        )

        self.assertEqual(result["covered"], [])
        open_url.assert_not_called()

    def test_rejects_unknown_open_question_id(self):
        with self.assertRaisesRegex(ValueError, "open vraag"):
            validate_skip_payload(
                {"question": "Q?", "answer": "A", "openQuestions": [{"id": "x", "title": "T"}]}
            )

    @patch("server.urlopen")
    def test_does_not_repeat_an_insult_in_follow_up(self, open_url):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "question": "Kun je uitleggen wat je bedoelt met fuck you?",
                            "description": "Vertel wat er speelt.",
                            "reason": "De vraag is nog onduidelijk.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = response

        result = generate_follow_up("Wat speelt er?", "fuck you", {})

        self.assertEqual(
            result["question"],
            "Kun je iets concreter vertellen wat er speelt of waarbij je hulp zoekt?",
        )
        self.assertTrue(result["adjusted"])


class ClassifyServiceTests(unittest.TestCase):
    def test_validate_classify_payload_accepts_six_answers(self):
        answers = validate_classify_payload(
            {"answers": valid_payload()["answers"]}
        )
        self.assertEqual(answers["goal"], "Een opleiding vinden.")

    def test_validate_classify_payload_rejects_wrong_fields(self):
        with self.assertRaisesRegex(ValueError, "zes antwoorden"):
            validate_classify_payload({"answers": {"goal": "x"}})

    @patch("server.urlopen")
    def test_classify_service_uses_ollama_choice(self, open_url):
        chat_response = MagicMock()
        chat_response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "serviceId": "p-direkt",
                            "confidence": 0.9,
                            "reason": "Je noemde salaris, dus P-Direkt past.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = chat_response

        result = classify_service(valid_payload()["answers"])

        self.assertEqual(result["serviceName"], "Dienstverlening P-Direkt")
        self.assertEqual(result["source"], "ai")
        self.assertAlmostEqual(result["confidence"], 0.9)

    @patch("server.urlopen", side_effect=URLError("connection refused"))
    def test_classify_service_falls_back_to_keywords(self, _open_url):
        answers = {
            "situation": "Ik wil een loonsverhoging.",
            "goal": "Meer salaris.",
            "barrier": "Ik weet niet hoe.",
            "support": "Informatie.",
            "timing": "Deze week",
            "contact": "Online informatie",
        }
        result = classify_service(answers)
        self.assertEqual(result["serviceName"], "Dienstverlening P-Direkt")
        self.assertEqual(result["source"], "fallback")

    @patch("server.urlopen")
    def test_classify_service_rejects_unknown_service_id(self, open_url):
        chat_response = MagicMock()
        chat_response.__enter__.return_value.read.return_value = json.dumps(
            {
                "message": {
                    "content": json.dumps(
                        {
                            "serviceId": "niet-bestaand",
                            "confidence": 0.8,
                            "reason": "Onbekend.",
                        }
                    )
                }
            }
        ).encode("utf-8")
        open_url.return_value = chat_response

        answers = valid_payload()["answers"]
        result = classify_service(answers)
        self.assertEqual(result["source"], "fallback")


class OllamaStubHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        request_body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if "question" in request_body["format"]["required"]:
            content = {
                "question": "Kun je vertellen wat er precies speelt?",
                "description": "Vertel bijvoorbeeld waar je ondersteuning bij zoekt.",
                "reason": "De eerste reactie maakt de hulpvraag nog niet duidelijk.",
            }
        elif "serviceId" in request_body["format"]["required"]:
            content = {
                "serviceId": "p-direkt",
                "confidence": 0.85,
                "reason": "Je noemde salaris, dus P-Direkt past.",
            }
        else:
            content = {
                "message": "Je kunt rustig een passende opleiding verkennen.",
                "reason": "Je noemde een opleiding.",
            }
        payload = {"message": {"content": json.dumps(content)}}
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format, *_args):
        pass

class LocalApiTests(unittest.TestCase):
    def test_api_returns_nudge_from_local_ollama(self):
        ollama = HTTPServer(("127.0.0.1", 0), OllamaStubHandler)
        ollama_thread = threading.Thread(target=ollama.serve_forever, daemon=True)
        ollama_thread.start()
        app = ThreadingHTTPServer(("127.0.0.1", 0), NudgeRequestHandler)
        app_thread = threading.Thread(target=app.serve_forever, daemon=True)
        app_thread.start()

        try:
            ollama_url = f"http://127.0.0.1:{ollama.server_port}/api/chat"
            with patch("server.OLLAMA_URL", ollama_url):
                request = Request(
                    f"http://127.0.0.1:{app.server_port}/api/nudge",
                    data=json.dumps(valid_payload()).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=3) as response:
                    result = json.loads(response.read().decode("utf-8"))
                self.assertEqual(
                    result["message"],
                    "Je kunt rustig een passende opleiding verkennen.",
                )
                self.assertEqual(result["reason"], "Je noemde een opleiding.")
                self.assertEqual(result["model"], "qwen3:4b")
            request = Request(
                f"http://127.0.0.1:{app.server_port}/api/follow-up",
                data=json.dumps(
                    {
                        "question": "Wat speelt er?",
                        "answer": "fuck you",
                        "context": {"goal": "Ik wil hulp."},
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with patch("server.OLLAMA_URL", ollama_url):
                with urlopen(request, timeout=3) as response:
                    follow_up = json.loads(response.read().decode("utf-8"))
            self.assertEqual(
                follow_up["question"], "Kun je vertellen wat er precies speelt?"
            )
            classify_request = Request(
                f"http://127.0.0.1:{app.server_port}/api/classify",
                data=json.dumps({"answers": valid_payload()["answers"]}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with patch("server.OLLAMA_URL", ollama_url):
                with urlopen(classify_request, timeout=3) as response:
                    classified = json.loads(response.read().decode("utf-8"))
            self.assertEqual(classified["serviceName"], "Dienstverlening P-Direkt")
            self.assertEqual(classified["source"], "ai")
        finally:
            app.shutdown()
            app.server_close()
            ollama.shutdown()
            ollama.server_close()
            app_thread.join(timeout=3)
            ollama_thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
