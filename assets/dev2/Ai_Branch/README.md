# Ai_Branch - Compleet Project

Dit is het eindresultaat van de Ai_branch. Een werkende AI-gestuurde nudge applicatie voor O&P Rijk diensten.

## Structuur

```
Ai_Branch/
├── code/              -> Alle werkende code
│   ├── server.py      -> Python webserver
│   ├── src/           -> Frontend (HTML/JS/CSS)
│   ├── tests/         -> Tests
│   └── [Python files] -> Models, validators, etc
│
└── commits/           -> Beschrijving wat je hebt gemaakt
    ├── 001-omgeving-gemaakt.md
    ├── 002-core-ai-engine.md
    ├── 003-antwoord-beoordeling.md
    ├── 004-kwaliteit-vervolgvragen.md
    ├── 005-vervolgvragen-beschrijving.md
    ├── 006-ai-nudging-profiel.md
    └── README.md      -> Overzicht van alle commits
```

## Hoe te starten

### Vereisten

1. **Python 3.9+**
2. **Ollama** (download van https://ollama.ai)
3. **Qwen model** voor Ollama:
   ```bash
   ollama pull qwen3:4b
   ```

### Stap 1: Ollama starten

```bash
ollama serve
```

Dit start Ollama op `http://127.0.0.1:11434`

### Stap 2: De app starten

Ga naar de `code/` folder:

```bash
cd code
python server.py
```

De server start op: `http://127.0.0.1:8000`

### Stap 3: Browser openen

Ga naar: http://127.0.0.1:8000

Je ziet nu:
- Formulier met 6 vragen
- Gezicht dat reageert
- Mogelijke vervolgvragen
- Finale nudge aanbeveling

## Wat je kunt doen

1. **Vragen beantwoorden** -> App stuurt naar Ollama
2. **AI genereert vervolgvragen** -> Als antwoord niet goed genoeg
3. **AI geeft nudge** -> Persoonlijk advies naar dienst
4. **Fallback** -> Als Ollama crash: regelgebaseerde aanbeveling
5. **Logs zien** -> Klik op gezicht rechtsboven

## Hoe het werkt

### Stap-voor-stap

1. **Frontend verzamelt antwoorden** (6 vragen)
2. **Backend checkt kwaliteit** via answerJudge
3. **Slecht antwoord?** -> Ollama genereert vervolgvraag
4. **Antwoord goed?** -> Naar AI-nudge
5. **AI-nudge** -> Ollama genereert persoonlijke bericht
6. **Fallback** -> Regelgebaseerde matching als AI faalt

### Code flow

```python
# 1. Inkomend antwoord
POST /api/nudge
{
  "answers": {
    "situation": "Ik ben gestrest",
    "goal": "Beter werkplezier",
    ...
  }
}

# 2. Server stuurt naar Ollama
# 3. Ollama genereert nudge
# 4. Response terug naar frontend
{
  "message": "Bedrijfszorg kan helpen met stress...",
  "reason": "Je noemde 'stress' en 'werkdruk'",
  ...
}
```

## De commits (lees dit voor details!)

Lees `commits/README.md` voor:
- Wat in ELKE commit gedaan is
- Welke folders/files gemaakt
- Waarom keuzes gemaakt
- Hoe features werken

## Foutmeldingen?

### "Ollama is niet bereikbaar"
- Zorg dat `ollama serve` draait
- Check: http://127.0.0.1:11434

### "Model niet gevonden"
- Voer uit: `ollama pull qwen3:4b`

### "Python errors"
- Check requirements: `pip install flask urllib3`

## Volgende stappen

Wat je nog kunt doen:
1. **Meer diensten toevoegen** -> service_catalogue.py
2. **AI-prompts verbeteren** -> server.py (PROMPT_* variabelen)
3. **More tests** -> tests/test_server.py
4. **Deployment** -> Docker container
5. **Fine-tuning** -> Ollama model tunen met betere prompts

## Vragen?

Lees:
- `code/README.md` -> Technische details
- `commits/README.md` -> Wat je hebt gemaakt
- `commits/006-ai-nudging-profiel.md` -> Meeste advanced features
