# Commit 6: AI-Nudging & Profielpagina

**Datum:** 6 november 2026

## Wat is gedaan

Volledige AI-aanbeveling systeem + gebruikersprofielpagina.

## Mappen/Files gemaakt

### JS Provocatype/
- `server.py` - Uitgebreid met /api/nudge endpoint
- `src/AI/aiProvider.js` - Nieuwe functies voor AI communicatie
- `src/AI/nudgeEngine.js` - Regelgebaseerde fallback
- `src/app.js` - Flow met AI-nudge aanbeveling
- `tests/test_server.py` - Uitgebreide tests

### Python Engine/
- `backend/app/main.py` - Nieuwe profielpagina API
- `frontend/profile.html` - NIEUW: Profielpagina
- `frontend/profile.css` - NIEUW: Styling profielpagina
- `frontend/profile.js` - NIEUW: JavaScript logica

## Hoe AI-Nudging werkt

1. Gebruiker beantwoordt 6 vragen + mogelijk 2 vervolgvragen
2. Frontend stuurt naar `/api/nudge`
3. Server stuurt naar Ollama met:
   - Alle antwoorden
   - Regelgebaseerde aanbeveling (fallback)
   - Instructies (JSON format!)
4. Ollama genereert:
   - `message`: Persoonlijke nudge tekst
   - `reason`: Korte uitleg waarom deze dienst
5. Frontend toont nudge met opties

## Fallback mechanisme

ALS Ollama crash/niet reageerd:
- Gebruik regelgebaseerde aanbeveling
- Toon waarschuwing "beperkte informatie"
- Gebruiker kan nog kiezen

## Profielpagina

- Toon alle sessies
- Statistieken (hoeveel vragen gesteld, etc)
- Welke diensten aanbevolen
- Trend over tijd

## Volgende stap

Verbeteringen op basis van gebruikersfeedback.
