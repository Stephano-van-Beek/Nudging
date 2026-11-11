# Onderzoek AI-modellen voor het hond-hologram van O&P Rijk

## 1. Aanleiding

Binnen Studio Dark Tech ontwikkelen we een hond-hologram met een website die ambtenaren helpt om de juiste diensten van O&P Rijk te vinden. De hond moet gebruikers op een vriendelijke manier nudgen om bepaalde diensten te bekijken.

Een gebruiker kan bijvoorbeeld vragen waar die terechtkan met vragen over salaris of verlof. Het systeem moet herkennen waar de vraag over gaat en de gebruiker naar de juiste dienst begeleiden.

Voor dit project willen we onderzoeken welke AI-modellen het beste passen. Hierbij kijken we naar drie soorten modellen:

- Large Language Models (LLM's)
- Embeddingmodellen
- Classificatiemodellen

Van iedere soort vergelijken we drie kandidaten. Daarnaast testen we hoe goed de modellen werken voor onze toepassing.

De belangrijkste eisen zijn privacy, Nederlandse taalvaardigheid, nauwkeurigheid, snelheid, kosten en de mogelijkheid om het model op onze eigen hardware te draaien.

## 2. Welke soorten modellen hebben we nodig?

### 2.1 Large Language Model (LLM)

Een LLM begrijpt vragen die in natuurlijke taal worden gesteld en kan zelf een antwoord formuleren.

Voor ons project kan een LLM herkennen dat iemand een vraag over salaris stelt en een korte reactie geven, zoals: "Ik help je de juiste dienst te vinden!"

Het voordeel is dat gebruikers hun vraag op verschillende manieren kunnen stellen. Het nadeel is dat een LLM soms een verkeerde dienst kan noemen of informatie kan verzinnen.

### 2.2 Embeddingmodel

Een embeddingmodel zet tekst om in een numerieke representatie. Daardoor kunnen we teksten vergelijken op basis van hun betekenis.

Stel dat de website informatie bevat over de dienst salaris. Een gebruiker kan vragen: "Mijn loon klopt niet, waar moet ik zijn?" Ook als de woorden niet letterlijk overeenkomen met de beschrijving van de dienst, kan het embeddingmodel helpen om de juiste informatie te vinden.

Het embeddingmodel genereert zelf geen antwoord. Het zoekt naar de meest vergelijkbare dienstbeschrijvingen.

### 2.3 Classificatiemodel

Een classificatiemodel deelt een vraag in een vooraf bepaalde categorie in.

Voor ons project kunnen de categorieën bijvoorbeeld zijn:

- Salaris
- Verlof
- Geldzaken
- Loopbaan
- Overige vragen

Het model bepaalt welke categorie het beste bij de vraag past. De applicatie koppelt die categorie vervolgens aan de juiste dienst.

Dit kan efficiënter zijn dan een LLM, vooral als het aantal categorieën beperkt is. De modellen moeten meestal wel worden getraind met voorbeelden van vragen en de bijbehorende categorieën.

## 3. Vergelijking van de modellen

We vergelijken drie kandidaten per modelsoort. De kandidaten zijn geselecteerd op basis van hun mogelijke geschiktheid voor Nederlandse vragen, een prototype en lokale verwerking.

De tabellen geven een eerste inschatting. Welke kandidaat daadwerkelijk het beste presteert, moet uit onze eigen tests blijken.

## 4. LLM-modellen

| Model | Waarom past het bij ons? | Aandachtspunten / nadelen |
|---|---|---|
| **Qwen3 4B** | Relatief compact en ondersteunt Nederlands. Kan vragen begrijpen en korte reacties formuleren. | Heeft voldoende geheugen nodig. Kan verkeerde antwoorden geven of de verkeerde dienst kiezen. De kwaliteit moet getest worden. |
| **Gemma 3 4B** | Compact model dat meerdere talen ondersteunt. Interessant voor het beantwoorden van Nederlandse vragen. | De Nederlandse taalvaardigheid voor onze toepassing moet worden getest. Kan informatie verzinnen en heeft eigen gebruiksvoorwaarden. |
| **Ministral 3 3B** | Compact model dat interessant is voor lokale uitvoering en korte reacties. | De nauwkeurigheid voor Nederlandse vragen over O&P Rijk is nog onbekend. Hardware-eisen en licentie moeten worden gecontroleerd. |

### 4.1 Qwen3 4B

Qwen3 4B is mijn eerste kandidaat voor het prototype. Het model is relatief compact en kan vragen begrijpen en antwoorden formuleren.

Voordelen:
- Kan lokaal worden uitgevoerd met geschikte software en hardware.
- Geen kosten per API-aanroep bij lokale uitvoering.
- Interessant voor het herkennen van verschillende formuleringen van Nederlandse vragen.

Nadelen:
- Heeft voldoende geheugen nodig.
- Kan verkeerde antwoorden geven.
- De nauwkeurigheid voor onze specifieke diensten moet nog worden getest.

Bron: [Qwen3 4B - Hugging Face](https://huggingface.co/Qwen/Qwen3-4B).

### 4.2 Gemma 3 4B

Gemma 3 4B is een compacte kandidaat die meerdere talen ondersteunt. Het model kan worden gebruikt om vragen te begrijpen en korte antwoorden te formuleren.

Voordelen:
- Relatief compact.
- Ondersteunt meerdere talen.
- Geschikt om te onderzoeken of een kleiner model voldoende is voor ons prototype.

Nadelen:
- De kwaliteit van de Nederlandse antwoorden moet worden getest.
- Kan onjuiste informatie genereren.
- De gebruiksvoorwaarden moeten worden gecontroleerd.

Bron: [Gemma 3 - Google](https://ai.google.dev/gemma/docs/core/model_card_3).

### 4.3 Ministral 3 3B

Ministral 3 3B is een compacte kandidaat van Mistral die interessant is voor lokale toepassingen.

Voordelen:
- Een relatief kleine modelvariant.
- Interessant voor korte reacties.
- Maakt het mogelijk om modellen van verschillende aanbieders te vergelijken.

Nadelen:
- De nauwkeurigheid voor onze Nederlandse testvragen is nog onbekend.
- De benodigde hardware hangt af van de modelversie en quantisatie.
- De licentievoorwaarden moeten worden gecontroleerd.

Bron: [Ministral 3 3B - Mistral](https://docs.mistral.ai/models/ministral-3b-25-12).

## 5. Embeddingmodellen

| Model | Waarom past het bij ons? | Aandachtspunten / nadelen |
|---|---|---|
| **BGE-M3** | Ondersteunt veel talen en kan verschillende vormen van tekstuele zoekopdrachten uitvoeren. | Relatief groot voor een eenvoudige zoektaak. De prestaties moeten worden getest op onze dienstbeschrijvingen. |
| **multilingual-e5-base** | Ondersteunt honderd talen en is interessant voor semantisch zoeken. | Kan minder goed presteren dan grotere varianten bij bepaalde zoekopdrachten. Vereist een goede vergelijking van de resultaten. |
| **paraphrase-multilingual-MiniLM-L12-v2** | Compact model dat gericht is op het vergelijken van de betekenis van zinnen in meerdere talen. | De zoekkwaliteit moet worden getest op onze Nederlandse dienstbeschrijvingen. Kan minder nauwkeurig zijn bij ingewikkelde vragen. |

### 5.1 BGE-M3

BGE-M3 is een embeddingmodel dat teksten in meerdere talen kan verwerken. Het kan helpen om een gebruikersvraag te vergelijken met beschrijvingen van diensten.

Voordelen:
- Ondersteunt veel talen.
- Kan helpen om vergelijkbare informatie te vinden.
- Interessant wanneer gebruikers andere woorden gebruiken dan in de dienstbeschrijving staan.

Nadelen:
- Relatief groot voor een eenvoudige zoektaak.
- Vereist een goede verzameling dienstbeschrijvingen.
- De kwaliteit moet met Nederlandse testvragen worden gemeten.

Bron: [BGE-M3](https://bge-model.com/bge/bge_m3.html).

### 5.2 multilingual-e5-base

Multilingual-e5-base zet teksten om in embeddings waarmee we de overeenkomst tussen vragen en diensten kunnen berekenen.

Voordelen:
- Ondersteunt honderd talen.
- Geschikt voor semantisch zoeken.
- Kan lokaal worden uitgevoerd met geschikte hardware.

Nadelen:
- De resultaten zijn afhankelijk van de kwaliteit van de dienstbeschrijvingen.
- Kan de verkeerde dienst bovenaan zetten.
- De juiste instellingen en vergelijkingsmethode moeten worden getest.

Bron: [multilingual-e5-base - Hugging Face](https://huggingface.co/intfloat/multilingual-e5-base).

### 5.3 paraphrase-multilingual-MiniLM-L12-v2

Dit model is een compacte kandidaat om de betekenis van Nederlandse vragen en dienstbeschrijvingen te vergelijken.

Voordelen:
- Relatief compact.
- Interessant voor een eenvoudige zoekfunctie.
- Kan lokaal worden uitgevoerd.

Nadelen:
- Kan minder goed presteren bij ingewikkelde of dubbelzinnige vragen.
- De nauwkeurigheid voor onze specifieke diensten is nog onbekend.
- Moet worden vergeleken met de andere embeddingmodellen.

Bron: [Sentence Transformers - modellenoverzicht](https://github.com/UKPLab/sentence-transformers/blob/master/docs/sentence_transformer/pretrained_models.md).

## 6. Classificatiemodellen

| Model | Waarom past het bij ons? | Aandachtspunten / nadelen |
|---|---|---|
| **BERTje** | Gericht op de Nederlandse taal. Kan worden getraind om vragen in categorieën zoals salaris, verlof en geldzaken in te delen. | Moet worden getraind met gelabelde voorbeelden. Kan moeite hebben met onbekende of dubbelzinnige vragen. |
| **RobBERT** | Nederlandstalig model dat geschikt is om te onderzoeken voor het herkennen van onderwerpen in Nederlandse teksten. | Heeft trainingsdata nodig en kan verkeerde categorieën voorspellen. De nauwkeurigheid hangt af van de kwaliteit en hoeveelheid voorbeelden. |
| **XLM-RoBERTa-base** | Ondersteunt meerdere talen en kan worden aangepast voor het classificeren van Nederlandse vragen. | Kan meer geheugen en rekenkracht gebruiken dan een kleinere gespecialiseerde oplossing. Moet worden getraind en getest met onze eigen categorieën. |

### 6.1 BERTje

BERTje is een Nederlandstalig taalmodel dat we kunnen aanpassen voor tekstclassificatie.

Voordelen:
- Gericht op de Nederlandse taal.
- Kan worden getraind voor onze eigen dienstcategorieën.
- Interessant voor een systeem met een beperkt aantal categorieën.

Nadelen:
- Moet worden getraind met voorbeelden van onze categorieën.
- Begrijpt onze specifieke dienstindeling niet automatisch.
- Kan moeite hebben met onbekende vragen.

### 6.2 RobBERT

RobBERT is een Nederlandstalig model dat we kunnen onderzoeken voor het classificeren van gebruikersvragen.

Voordelen:
- Gericht op Nederlandse tekst.
- Kan worden aangepast voor onze eigen categorieën.
- Geschikt om te vergelijken met BERTje.

Nadelen:
- Heeft gelabelde trainingsdata nodig.
- Kan verkeerde categorieën voorspellen.
- De resultaten hangen af van de kwaliteit en hoeveelheid trainingsvoorbeelden.

### 6.3 XLM-RoBERTa-base

XLM-RoBERTa-base is een meertalig model dat kan worden aangepast om Nederlandse vragen te classificeren.

Voordelen:
- Ondersteunt meerdere talen.
- Kan worden aangepast voor onze categorieën.
- Interessant als het project later ook andere talen moet ondersteunen.

Nadelen:
- Kan meer geheugen en rekenkracht gebruiken dan een kleinere gespecialiseerde oplossing.
- Moet worden getraind en getest met onze eigen categorieën.
- Meertalige ondersteuning betekent niet automatisch dat het model voor onze toepassing nauwkeuriger is.

Bronnen voor de classificatiemodellen zijn te vinden via [Hugging Face](https://huggingface.co/). Controleer per kandidaat de exacte modelpagina, licentie en beschikbaarheid voordat we de modellen installeren.

## 7. Praktijktests voor ons project

Om te bepalen welk model het beste werkt, voeren we tests uit met dezelfde Nederlandse vragen. Zo kunnen we de modellen eerlijk vergelijken.

### Test 1: De juiste dienst herkennen

**Doel:** onderzoeken of het model de gebruiker naar de juiste dienst verwijst.

We maken een lijst van ongeveer dertig fictieve vragen. Bij iedere vraag leggen we vooraf vast welke dienst het juiste antwoord is.

| Vraag | Verwachte categorie |
|---|---|
| Mijn loon klopt niet. | Salaris |
| Hoe vraag ik verlof aan? | Verlof |
| Ik heb een vraag over mijn loopbaan. | Loopbaan |
| Waar vind ik informatie over geldzaken? | Geldzaken |
| Ik weet niet waar ik moet beginnen. | Onbekend / verduidelijking nodig |

We voeren dezelfde vragen in bij alle kandidaten.

**Meten:** het percentage vragen waarbij het model de juiste dienst kiest. Bij embeddingmodellen meten we ook of de juiste dienst in de eerste drie zoekresultaten staat.

### Test 2: Verschillende formuleringen

**Doel:** testen of het model de betekenis begrijpt in plaats van alleen op dezelfde woorden te zoeken.

We stellen dezelfde vraag op verschillende manieren, bijvoorbeeld:

- "Waar kan ik mijn salaris bekijken?"
- "Ik heb een vraag over mijn loon."
- "Mijn betaling lijkt niet te kloppen."
- "Waar vind ik mijn loonstrook?"

**Meten:** hoeveel formuleringen naar dezelfde juiste dienst leiden.

Dit is vooral belangrijk voor het embeddingmodel en het classificatiemodel.

### Test 3: Onbekende of onduidelijke vragen

**Doel:** voorkomen dat de hond een verkeerde dienst aanbeveelt.

We gebruiken vragen zoals:

- "Kun je mij helpen?"
- "Ik heb een probleem."
- "Waar moet ik zijn?"
- Een vraag die niet over de diensten van O&P Rijk gaat.

Het systeem moet bij onvoldoende informatie om verduidelijking vragen of aangeven dat het geen geschikte dienst kan vinden.

**Meten:** hoe vaak het systeem ten onrechte een dienst kiest in plaats van een verduidelijking te vragen.

### Test 4: Nederlandse taalvaardigheid

**Doel:** controleren of het model Nederlandse vragen begrijpt, inclusief informele taal en spelfouten.

We gebruiken bijvoorbeeld:

- "Me salaris klopt niet."
- "Hoe zit dat met me verlof?"
- "Waar moet ik wezen voor geldzaken?"

**Meten:** het aantal vragen dat correct wordt gekoppeld aan de juiste dienst.

### Test 5: Snelheid en hardware

**Doel:** bepalen of het model snel genoeg werkt voor een interactieve ervaring met het hologram.

We voeren twintig dezelfde vragen achter elkaar uit op dezelfde computer.

We meten:
- De gemiddelde responstijd.
- Hoe lang het duurt voordat het eerste antwoord beschikbaar is.
- Het geheugengebruik.
- Of het model zonder fouten blijft draaien.

Bij voorkeur voeren we de test meerdere keren uit en noteren we ook de 95e percentiel-responstijd. Dit laat zien hoe lang de langzaamste reacties ongeveer duren, zonder dat een enkele uitschieter het gemiddelde bepaalt.

### Test 6: Privacy

**Doel:** controleren of het model voldoet aan de uitgangspunten van O&P Rijk.

We gebruiken alleen fictieve testgegevens en controleren:

- Of vragen naar een externe server worden gestuurd.
- Of vragen of antwoorden worden opgeslagen in logs.
- Of de applicatie onnodige persoonsgegevens verwerkt.
- Of een eventuele API de afgesproken verwerkingslocatie gebruikt.

**Meten:** vastleggen welke gegevensstromen aanwezig zijn en welke opslag- en verwerkingsinstellingen zijn gecontroleerd.

Een lokaal model heeft hierbij voordelen, maar de applicatie moet nog steeds veilig worden ingericht.

### Test 7: De nudge van de hond

**Doel:** onderzoeken of de reactie van de hond duidelijk en behulpzaam is.

We maken bijvoorbeeld drie soorten reacties:

1. Een korte tekst met een link naar de dienst.
2. Een korte gesproken boodschap.
3. Een reactie met een kleine animatie en een link naar de dienst.

We laten een kleine groep testers dezelfde taken uitvoeren en vragen of zij de juiste dienst kunnen vinden.

**Meten:**
- Of de gebruiker de juiste dienst vindt.
- Hoe lang het duurt om de dienst te vinden.
- Of de boodschap duidelijk is.
- Of de nudge behulpzaam of juist storend voelt.

De hond moet de gebruiker helpen, niet onder druk zetten of onnodig afleiden.

### Test 8: De e-mailmelding

**Doel:** controleren of de hond een blafgeluid kan afspelen wanneer er een nieuwe e-mail binnenkomt.

Deze functie hoeft geen AI te gebruiken. We kunnen de melding als aparte applicatiefunctie implementeren.

We testen of:
- Het geluid wordt afgespeeld wanneer een nieuwe e-mail wordt ontvangen.
- Het geluid niet onnodig meerdere keren wordt afgespeeld.
- De gebruiker de melding kan uitschakelen.
- De inhoud van e-mails niet naar het AI-model wordt gestuurd.

## 8. Hoe leggen we de resultaten vast?

We maken één benchmarktabel voor alle negen modellen. De waarden vullen we pas in nadat de tests zijn uitgevoerd.

| Model | Juiste resultaten (%) | Responstijd (ms) | Geheugengebruik | Opmerking |
|---|---:|---:|---|---|
| Qwen3 4B | Nog te meten | Nog te meten | Nog te meten | LLM |
| Gemma 3 4B | Nog te meten | Nog te meten | Nog te meten | LLM |
| Ministral 3 3B | Nog te meten | Nog te meten | Nog te meten | LLM |
| BGE-M3 | Nog te meten | Nog te meten | Nog te meten | Embedding |
| multilingual-e5-base | Nog te meten | Nog te meten | Nog te meten | Embedding |
| MiniLM-L12-v2 | Nog te meten | Nog te meten | Nog te meten | Embedding |
| BERTje | Nog te meten | Nog te meten | Nog te meten | Classificatie |
| RobBERT | Nog te meten | Nog te meten | Nog te meten | Classificatie |
| XLM-RoBERTa-base | Nog te meten | Nog te meten | Nog te meten | Classificatie |

De score voor juiste resultaten berekenen we op basis van de verwachte dienstcategorie. Voor de classificatiemodellen gebruiken we dezelfde trainings- en testverdeling. De testvragen mogen niet worden gebruikt om het model te trainen.

De embeddingmodellen beoordelen we op de rangschikking van de juiste dienst. De LLM's beoordelen we op de gekozen dienst en op de betrouwbaarheid van de reactie.

We noteren daarnaast de hardware, modelversie, instellingen en eventuele quantisatie. Hierdoor kan Ian de resultaten gebruiken voor US-17 (#24).

## 9. Privacy, kosten en hardware

Voor elk model moeten we controleren of het lokaal kan draaien op de hardware die beschikbaar is voor het project. We mogen niet aannemen dat ieder model zonder problemen op een gewone laptop werkt.

Lokale modellen hebben geen kosten per API-aanroep, maar gebruiken wel geheugen, rekenkracht en stroom. Daarnaast moeten we rekening houden met installatie, onderhoud en beveiliging.

Een externe API kan eenvoudiger zijn, maar brengt mogelijk kosten per gebruik met zich mee. We moeten dan ook onderzoeken waar gegevens worden verwerkt en opgeslagen.

De AVG vereist dat persoonsgegevens zorgvuldig worden verwerkt. Daarom gebruiken we in de tests fictieve gegevens en sturen we geen vertrouwelijke informatie naar een externe aanbieder zonder goedkeuring.

## 10. Voorlopige keuze

Ik adviseer om de drie soorten modellen afzonderlijk te testen.

- **LLM:** begin met Qwen3 4B. Het kan vragen begrijpen en natuurlijke reacties formuleren.
- **Embeddingmodel:** begin met multilingual-e5-base. Het kan helpen om de juiste dienst te vinden zonder dat het zelf een antwoord hoeft te genereren.
- **Classificatiemodel:** begin met BERTje. Het is een kandidaat om Nederlandse vragen in vaste categorieën in te delen.

Deze drie modellen zijn de eerste kandidaten, geen definitieve winnaars. De benchmark bepaalt welke optie het beste werkt.

Het is ook mogelijk dat een embeddingmodel of classificatiemodel voldoende is voor de eerste versie. Als de hond alleen een vraag hoeft te koppelen aan een bestaande dienst, hebben we mogelijk geen LLM nodig. Dat kan het systeem eenvoudiger, sneller en goedkoper maken.

## 11. Conclusie

Voor het hond-hologram willen we vooral Nederlandse vragen correct koppelen aan de diensten van O&P Rijk. Daarom vergelijken we drie LLM's, drie embeddingmodellen en drie classificatiemodellen.

Met de praktijktests meten we nauwkeurigheid, snelheid, geheugengebruik, privacy en de bruikbaarheid van de nudges. Daarnaast testen we of de hond op een duidelijke en niet-storende manier reageert.

De e-mailmelding met een blafgeluid behandelen we als een aparte functie waarvoor geen AI nodig is.

De definitieve modelkeuze maken we op basis van de benchmarkresultaten en de beschikbare hardware. Zo kiezen we niet automatisch het grootste model, maar de eenvoudigste oplossing die goed genoeg werkt voor onze toepassing.

## Bronnen

- [Qwen3 4B - Hugging Face](https://huggingface.co/Qwen/Qwen3-4B)
- [Gemma 3 - Google](https://ai.google.dev/gemma/docs/core/model_card_3)
- [Ministral 3 3B - Mistral](https://docs.mistral.ai/models/ministral-3b-25-12)
- [BGE-M3 - modelinformatie](https://bge-model.com/bge/bge_m3.html)
- [multilingual-e5-base - Hugging Face](https://huggingface.co/intfloat/multilingual-e5-base)
- [Sentence Transformers - modellenoverzicht](https://github.com/UKPLab/sentence-transformers/blob/master/docs/sentence_transformer/pretrained_models.md)
- [Hugging Face - modelbibliotheek](https://huggingface.co/)

**Let op:** de negen modellen zijn kandidaten voor onderzoek. De prestaties, benodigde hardware en licentievoorwaarden moeten nog worden gecontroleerd. De testresultaten zijn nog niet ingevuld, zodat er geen niet-uitgevoerde benchmarks als feiten worden gepresenteerd.