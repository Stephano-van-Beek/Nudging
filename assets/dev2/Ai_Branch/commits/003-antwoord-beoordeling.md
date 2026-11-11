# Commit 3: AI Antwoord Beoordeling & Gezicht Interactie

**Datum:** 27 oktober 2026

## Wat is gedaan

Gebruiker feedback systeem toegevoegd. De app reageert nu op antwoorden en geeft visuele feedback.

## Files gemaakt/gewijzigd

### JS Provocatype/
- `src/AI/answerJudge.js` - NIEUW: Beoordeelt antwoorden (blij, verward, verdrietig, neutraal)
- `src/face.js` - NIEUW: Gezicht dat reageert met emoties
- `src/data/questions.js` - Verbeterd met meer vraag details
- `server.py` - Verbeterd met validatie
- `src/app.js` - Aangepast voor gezicht integratie
- `src/index.html` - Nieuw gezicht element
- `src/styles.css` - Styling voor gezicht
- `README.md` - Documentatie updated
- `docs/architecture.md` - Updated
- `tests/test_server.py` - Tests toegevoegd

### Documentatie
- `PROJECT_MAP.md` - NIEUW: Volledige file overview
- `Verslag_model.md` - NIEUW: Uitleg over model keuzes

## Waarom

De app voelde statisch. Door een gezicht toe te voegen dat reageert op input maakt het:
- Meer interactief
- User-friendly
- Duidelijk wat de app aan het doen is

Antwoord beoordeling helpt om:
- Slechte antwoorden op te sporen (te kort, irrelevant)
- Gebruiker stimuleren beter antwoord te geven
- Kwaliteit van data verbeteren

## Functie van antwordJudge.js

```javascript
judgeAnswer(question, value)
- Input: vraag ID en antwoord tekst
- Output: { mood: "happy"/"sad"/"confused"/"neutral", why: "reden" }
- Controleert: lengte, woorden, unieke letters
- Checkt tegen trefwoorden
```

## Volgende stap

Vervolgvragen toevoegen als gebruiker antwoord niet goed genoeg is.
