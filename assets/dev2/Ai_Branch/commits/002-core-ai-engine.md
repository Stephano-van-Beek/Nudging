# Commit 2: Core AI Engine Geinitialiseerd

**Datum:** 21 oktober 2026

## Wat is gedaan

Volledige AI-gestuurde nudge engine gebouwd. Dit is het hart van het project.

## Mappen gemaakt

- `JS Provocatype/` (Folder voor JavaScript versie van de app)
- `Python Engine/` (Folder voor Python backend)
- `JS Provocatype/docs/` (Documentatie voor JS versie)
- `Python Engine/backend/` (Backend code)
- `Python Engine/frontend/` (Frontend assets)
- `Python Engine/tests/` (Tests)

## Folders/Files volledig gemaakt

### JS Provocatype/ (JavaScript versie)
- `README.md` - Uitleg hoe te gebruiken
- `server.py` - Python webserver voor demo
- `src/AI/nudgeEngine.js` - Regelgebaseerde dienst matching (10 O&P Rijk diensten)
- `src/AI/aiProvider.js` - Communicatie met Ollama AI
- `src/app.js` - Frontend logica
- `src/data/questions.js` - 6 intakevragen (situatie, doel, barriere, ondersteuning, timing, contact)
- `src/index.html` - Homepage met vragenformulier
- `src/styles.css` - Styling
- `tests/test_server.py` - Server tests

### Python Engine/ (Organisatie & workflows)
- `backend/app/engine/catalogue.py` - Dienstencatalogus
- `backend/app/engine/policy.py` - Bedrijfsregels
- `backend/app/engine/profiler.py` - Gebruiker profiel matching
- `backend/app/main.py` - Flask API server
- `backend/app/storage.py` - Data opslag
- `frontend/` - HTML/JS/CSS voor Python versie
- `tests/` - Test suite
- `requirements.txt` - Python dependencies
- `run_windows.bat` / `run_unix.sh` - Start scripts

### Documentatie
- `docs/architecture.md` - Architectuur uitleg
- `docs/DEVELOPMENT_PLAN.md` - Plan voor volgende stappen
- `PROJECT_MAP.md` - Overview van al files
- `Verslag_model.md` - Uitleg over het AI model

## Waarom

Het project spitstte zich op in 2 versies:
1. **JS Provocatype** - Simpele demo met regels + Ollama AI
2. **Python Engine** - Complexere backend met organisatie hierarchie

Dit is de eerste grote milestone waar alles werkend is.

## Volgende stap

Toevoegen van geavanceerde features zoals antwoord beoordeling en vervolgvragen.
