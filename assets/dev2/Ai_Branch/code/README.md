# Nudge naar Dienst

Een starter voor een AI-gestuurde nudgebot. De bot stelt eerst vier intakevragen, daarna twee korte vervolgvragen en geeft vervolgens een persoonlijke, concrete nudge richting een passende dienst.

## Starten

De demo gebruikt een lokale Python-server en Ollama. Installeer Ollama en haal het gekozen model op:

```powershell
ollama pull qwen3:4b
```

Start daarna de demo vanuit de map `JS Provocatype`:

```powershell
python server.py
```

Open `http://127.0.0.1:8000`. De server bindt alleen aan je eigen computer. Zorg dat Ollama actief is.

## Projectstructuur

```text
src/
  data/          Vragen en dienstencatalogus
  AI/            Regelgebaseerde dienstkeuze en Ollama-client
  app.js         Schermflow en invoerverwerking
  index.html     Startpagina
  styles.css     Vormgeving
docs/            Architectuur en vervolgstappen
tests/           Tests voor de Ollama-server
server.py        Lokale webserver en Ollama-proxy
```

## Hoe de AI werkt

De vaste regels in `src/AI/nudgeEngine.js` kiezen drie diensten uit de O&P Rijk-catalogus (2026) en vinken de eerste vooraf aan. Als een open antwoord onduidelijk is, maakt het ingestelde Ollama-model via `/api/follow-up` een contextuele vervolgvraag én een toelichting die als vraagbeschrijving in het formulier verschijnt; er verschijnen maximaal twee extra vragen per formulier, ook als de melding na twee onbruikbare antwoorden al wordt getoond. Dan waarschuwt de demo dat de uiteindelijke aanbeveling algemener of minder zeker kan zijn. Een leeg antwoord op een vaste vraag blijft verplicht; een extra vraag mag worden overgeslagen. Qwen3 4B schrijft de nudgetekst en een korte reden als gestructureerde JSON (`format`-schema in `server.py`). Na de keuze toont het eindformulier per AI-stap de gebruikte model-ID, diens korte reden, vraagbeschrijving en uitvoer. De dienstkeuze zelf komt van vaste regels, niet van een LLM. De browser stuurt antwoorden naar `server.py`, die lokaal doorstuurt naar Ollama; er is geen API-sleutel nodig. Rechtsboven staat een gezicht dat blij, neutraal, verward of teleurgesteld kijkt (`src/AI/answerJudge.js`). Klik erop voor het logboek met de echte stappen van de app, niet de verborgen redeneertekst van een model. De demo is alleen bedoeld als gesimuleerd experiment, nooit voor echte gebruikers.

Dit is geen fine-tuning: Qwen3 is niet opnieuw getraind. De demo geeft het bestaande model een beperkte opdracht en JSON-schema. Om de kwaliteit te verbeteren, test je verschillende voorbeeldantwoorden en pas je de opdracht aan. Fine-tuning is pas te overwegen als je een grotere, gecontroleerde verzameling goede vraag/antwoord-voorbeelden hebt.

Als Ollama niet bereikbaar is of het model ontbreekt, toont de demo een fout en kun je zelf kiezen voor de standaardnudge zonder AI.

Zie `docs/architecture.md` voor de voorgestelde volgende stappen.

## Tests

```powershell
python -m unittest discover -s tests
```
