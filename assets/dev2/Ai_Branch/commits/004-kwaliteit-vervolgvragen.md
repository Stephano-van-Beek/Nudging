# Commit 4: AI Interactie Verbeterd - Kwaliteit & Vervolgvragen

**Datum:** 27 oktober 2026

## Wat is gedaan

Kwaliteitsbepaling toegevoegd. App vraagt nu automatisch vervolgvragen als antwoord niet goed genoeg is.

## Files gewijzigd

### JS Provocatype/
- `server.py` - Verbeterd validatie voor vervolgvragen
- `src/AI/aiProvider.js` - Nieuwe endpoint voor /api/follow-up
- `src/app.js` - Integratie vervolgvragen in flow
- `src/index.html` - Dynamische vraag rendering
- `src/styles.css` - Styling voor vervolgvragen
- `README.md` - Updated docs
- `docs/architecture.md` - Updated flow
- `tests/test_server.py` - Nieuwe tests

## Waarom

Met alleen hoofdvragen krijgen we soms:
- Te korte antwoorden ("Ja" / "Nee")
- Irrelevante antwoorden
- Niet genoeg informatie om goed advies te geven

Vervolgvragen zorgen voor:
- Diepere, betere antwoorden
- Meer context
- Beter AI-advies

## Hoe het werkt

1. Gebruiker geeft antwoord
2. `judgeAnswer()` beoordeelt of het goed genoeg is
3. Als slecht: roep `/api/follow-up` aan
4. Ollama genereert automatisch vervolgvraag
5. Gebruiker beantwoordt vervolgvraag
6. Antwoorden gecombineerd voor aanbeveling

## Limiet

Maximaal 2 vervolgvragen per formulier (anders duurt het te lang).

## Volgende stap

AI-aanbeveling voor diensten (niet alleen regelgebaseerd matching).
