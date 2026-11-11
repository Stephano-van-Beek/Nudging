# Commit 5: Vervolgvragen Beschrijving Veld

**Datum:** 27 oktober 2026

## Wat is gedaan

Vervolgvragen hebben nu een beschrijving/toelichting. Dit helpt gebruiker beter antwoorden.

## Files gewijzigd

### JS Provocatype/
- `server.py` - Description field toegevoegd aan /api/follow-up response
- `src/AI/aiProvider.js` - Description nu uit API gehaald
- `src/app.js` - Description tonen in UI
- `src/face.js` - Integratie met face logging
- `README.md` - Updated
- `docs/architecture.md` - Updated
- `tests/test_server.py` - Nieuwe tests

## Waarom

Soms is een vervolgvraag onduidelijk. Voorbeeld:

**SLECHT:**
```
Vervolgvraag: Kunt u gespecificeerd de barriere aangeven?
(gebruiker is verward)
```

**GOED:**
```
Vervolgvraag: Kunt u gespecificeerd de barriere aangeven?
Beschrijving: We willen weten WELKE dingen je werkdruk veroorzaken.
             Is het veel werk? Te lastige taken? Slecht team?
(gebruiker begrijpt en geeft beter antwoord)
```

## Response format

```json
{
  "question": "Kun je concreter zijn?",
  "description": "We willen weten wat je precies bedoelt",
  "reason": "Antwoord was te algemeen",
  "model": "qwen3:4b",
  "adjusted": false
}
```

## Volgende stap

AI-genereerde dienstkeuze (fallback op regelgebaseerd).
