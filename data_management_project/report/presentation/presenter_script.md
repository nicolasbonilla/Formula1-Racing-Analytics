# Presenter script - group presentation (10 minutes + 5 minutes Q&A)

Speaking pace assumed: 130 words per minute. Time budget per slide below; rehearse once with a timer.

| # | Slide | Presenter | Budget | Words | Est. at pace |
|---|---|---|---|---|---|
| 1 | Title | All (opened by Student A) | 18 s | 52 | 24 s |
| 2 | Dataset and motivation | Chirag Adhikari | 45 s | 103 | 48 s |
| 3 | Pipeline overview | Nicolas Bonilla | 40 s | 97 | 45 s |
| 4 | Data engineering architecture | Chirag Adhikari | 36 s | 72 | 33 s |
| 5 | FAIR assessment | Chirag Adhikari | 45 s | 85 | 39 s |
| 6 | FAIR gaps, licence and identifiers | Chirag Adhikari | 45 s | 102 | 47 s |
| 7 | Hidden missingness | Manohar Zalki | 40 s | 84 | 39 s |
| 8 | Duplicates vs shared drives | Manohar Zalki | 40 s | 94 | 43 s |
| 9 | Eras, outliers and impact | Manohar Zalki | 45 s | 94 | 43 s |
| 10 | Order of operations | Nicolas Bonilla | 45 s | 96 | 44 s |
| 11 | Validation and resolution | Nicolas Bonilla | 45 s | 92 | 42 s |
| 12 | Property graph and small world | Manohar Zalki | 42 s | 90 | 42 s |
| 13 | Communities by era | Chirag Adhikari | 33 s | 87 | 40 s |
| 14 | Interactive dashboard | Nicolas Bonilla | 29 s | 80 | 37 s |
| 15 | Dashboard gallery | Manohar Zalki | 27 s | 56 | 26 s |
| 16 | Conclusion | Nicolas Bonilla | 22 s | 89 | 41 s |
| 17 | Questions | All | 3 s | 18 | 8 s |

**Total budget:** 10 min 00 s.

| Presenter | Time budget |
|---|---|
| All | 0 min 21 s |
| Chirag Adhikari | 3 min 24 s |
| Nicolas Bonilla | 3 min 01 s |
| Manohar Zalki | 3 min 14 s |

## Script per slide

### Slide 1 - Title (All (opened by Student A), 18 s)

Good morning, we are Chirag Adhikari, Manohar Zalki and Nicolas Bonilla. We take 75 years of Formula 1 results from raw files to a FAIR, quality-assured dataset and a knowledge graph. I start with the dataset and FAIR, Manohar Zalki covers quality, Nicolas Bonilla the cleaning, and we close with the graph.

### Slide 2 - Dataset and motivation (Chirag Adhikari, 45 s)

Our dataset is the Ergast Formula 1 database, which the group downloaded from its successor, the Jolpica API. The core table has 25,907 race results: one row for every car in every championship Grand Prix since 1950, 1,149 races in total, linked to tables of races, circuits, drivers and constructors. We chose it for three reasons. It is relational, so joins and keys matter. Its quality problems are real: they come from 76 seasons of changing rules and from how the files were exported, not from planted errors. And drivers, teams and circuits form a natural network, which is ideal for graph modelling.

### Slide 3 - Pipeline overview (Nicolas Bonilla, 40 s)

Everything you will see comes from one pipeline. Step zero only flattens the raw archive into CSV files and records checksums; it never changes a value. Component B profiles those files and writes an issue register with 29 entries. Component C resolves every issue and only publishes data that passes all 55 validation gates. Component A describes the clean package with standard metadata, and the graph is built from validated output only. A single command rebuilds every file in about a minute, and two independent runs give byte-identical results, so every number in our report is reproducible.

### Slide 4 - Data engineering architecture (Chirag Adhikari, 36 s)

Here is the architecture behind it. Data move through zones: an immutable raw zone that keeps the source values and their lineage, a clean zone that is only written when every validation gate passes, and served products: the FAIR record, the graph, the dashboard and the report. Underneath are four engineering controls: one schema contract shared by cleaning and metadata, one orchestrated command, automated tests, and lineage down to the source line.

### Slide 5 - FAIR assessment (Chirag Adhikari, 45 s)

We measured FAIRness twice. First automatically with F-UJI, run on a local server against the three places where the data lives. The Jolpica API we downloaded from scores only 8 percent, our own GitHub repository 31 percent, and the Kaggle mirror 65 percent. Because F-UJI only sees what is online, we also scored all 41 indicators of the RDA maturity model with written evidence. Our curated package lifts maturity from 54 to 93 percent. Findable honestly stays at level zero until the DOI is minted.

### Slide 6 - FAIR gaps, licence and identifiers (Chirag Adhikari, 45 s)

We documented 7 concrete FAIR gaps, each with indicator, evidence and remedy. Two stand out. First, there is no persistent identifier: the data is only reachable through URLs that can change. Second, the licences contradict each other. Ergast allowed only non-commercial use and Jolpica licenses the data CC BY-NC-SA, yet the Kaggle mirror claims public domain and our own repository says MIT for everything. We fixed what we can: a clear licence split, a DataCite record that validates against the official schema, ISO country codes, provenance, and Wikidata identifiers for 98.7 percent of drivers. The DOI is reserved and minted on deposit.

### Slide 7 - Hidden missingness (Manohar Zalki, 40 s)

I profiled every column of all five tables and ran 29 quality rules. The first lesson: completeness is deceptive. Only 18 cells are empty, so the table looks almost perfect. But 9,913 values only pretend to be data. The position column is filled for 9,646 drivers who retired, withdrew or were disqualified, and 267 cars start from grid slot zero, which does not exist. A model that predicts results from grid positions would learn from a retirement ranked eighteenth and from a fictitious pole-better-than-pole.

### Slide 8 - Duplicates vs shared drives (Manohar Zalki, 40 s)

Uniqueness needs domain knowledge. 23 rows of the 1960 United States Grand Prix were appended twice, and 11 rows of the 1960 Italian Grand Prix are copies whose season and round were blanked, so they only look like duplicates after the keys are restored. The red bar is the real problem. The blue bars are not: 172 rows share season, round and driver because in the 1950s a driver could take over a team-mate's car and be classified twice. A naive duplicate check would delete that history. The correct key includes the car number.

### Slide 9 - Eras, outliers and impact (Manohar Zalki, 45 s)

Some issues are not errors at all, but they still break analyses. A race win was worth 8, 9, 10, 25 or even 50 points depending on the era, so raw points are not comparable over time. All 270 statistical outliers in laps are valid Indianapolis 500 results, so we flag them instead of deleting them. The root causes are export artefacts, undocumented source semantics and genuine historical change. For data science the impact is concrete: inflated win counts, biased prediction targets, sparse features from 136 free-text statuses, and train-test leakage through duplicated rows.

### Slide 10 - Order of operations (Nicolas Bonilla, 45 s)

The most important design decision was the order of operations. If you remove duplicates first and repair keys afterwards, 11 duplicates survive, because their season and round were blanked. So step C02 restores the missing season from the file name and the missing round by an exact lookup in the races table, and only then does step C03 remove all 34 copies. A unit test documents both orders. We also never invent values: no statistical imputation is used. Grid zero becomes missing with a flag, and withdrawn cars keep a missing number because none ever existed.

### Slide 11 - Validation and resolution (Nicolas Bonilla, 45 s)

Every one of the 29 issues is now closed: 18 are fixed, 3 are mitigated or flagged, 5 are kept and documented, and 3 were verified as non-errors. Our rule is flag, don't delete: Indianapolis 500 rows and shared drives stay in the data with flags. Status went from 136 free-text values to 8 groups. Every step writes an audit record, and 55 validation gates check schema, keys, foreign keys and vocabularies. If a single gate fails, nothing is published as clean. The final table has 25,873 rows and 35 documented columns.

### Slide 12 - Property graph and small world (Manohar Zalki, 42 s)

For the graph we modelled the cleaned data as a property graph: drivers, races, constructors, circuits and countries, with results stored as properties on RACED_IN edges, and a derived TEAMMATE_OF relationship. Indianapolis 500 rounds are excluded from the team-mate projection, a direct consequence of the quality analysis. The result is a small world: clustering is 0.41 against 0.014 for a random graph, yet two drivers are on average only 4.8 links apart. Juan Manuel Fangio reaches Max Verstappen in 8 steps, through long careers such as de Cesaris and Barrichello.

### Slide 13 - Communities by era (Chirag Adhikari, 33 s)

Louvain community detection finds 11 communities with a modularity of 0.70. The algorithm never sees a date, yet the large communities line up with eras, from the fifties around Stirling Moss and the sixties around Jack Brabham to the present grid around Sergio Pérez. Betweenness highlights bridges between eras such as Jo Bonnier and Andrea de Cesaris. One caveat links back to data quality: before the seventies the constructor field records the chassis make shared by private entrants, so early drivers look more connected than they were.

### Slide 14 - Interactive dashboard (Nicolas Bonilla, 29 s)

Everything we showed ends here, in an interactive dashboard that the group can open with one command. It reads only validated outputs: the clean tables, the graph metrics, the issue register and the FAIR scores, and run_all rebuilds it as its last step. It also paid back: the reliability view showed mechanical failures vanishing after 2022, which turned out to be the source no longer recording why cars retired. That became issue B29. If time allows, we open it live.

### Slide 15 - Dashboard gallery (Manohar Zalki, 27 s)

Four more views. The timing tower ranks drivers by wins or by our era-adjusted score. The grid view shows where cars finish from each starting slot, using classified positions only, which is exactly the fix for issue B11. The reliability view marks the 2023 break that became issue B29, and the globe places all seventy-seven circuits.

### Slide 16 - Conclusion (Nicolas Bonilla, 22 s)

Four lessons. First, quality is contextual: outliers, duplicates and short grids were often valid history, so every automatic rule needed domain checking before deleting anything. Second, the order of operations matters, as the 11 hidden duplicates show. Third, the largest FAIR gaps were around the values: no identifier, conflicting licences and no provenance. Fourth, automating the evidence, with an audit log, validation gates, tests and generated metadata, turns cleaning into something an examiner can verify. Next steps are a Zenodo DOI and reporting the source defects upstream to Jolpica.

### Slide 17 - Questions (All, 3 s)

Thank you. We are happy to take your questions; each of us will answer on our own component.

## Hand-over cues

- Slide 2 -> 3: Student A hands over to Student C for the pipeline overview.
- Slide 3 -> 4: Student C hands back to Student A for the FAIR assessment.
- Slide 5 -> 6: Student A hands over to Student B for data quality.
- Slide 8 -> 9: Student B hands over to Student C for the cleaning pipeline.
- Slide 10 -> 11: Student C hands over to Student B for the graph model.
- Slide 11 -> 12: Student B hands over to Student A for communities.
- Slide 12 -> 13: Student A hands over to Student C for the conclusion.
