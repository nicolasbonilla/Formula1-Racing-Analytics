# Component A - FAIR assessment and metadata design: key findings

## Automated assessment (F-UJI 4.0.1, metrics v0.5)

| Resource | FAIR | F | A | I | R |
|---|---|---|---|---|---|
| github_repository (https://github.com/zalkimanohar/Formula1-Racing-Analytics) | 31.2% | 35.7% | 33.3% | 25.0% | 30.0% |
| jolpica_ergast_api (http://api.jolpi.ca/ergast/f1/) | 8.3% | 14.3% | 33.3% | 0.0% | 0.0% |
| kaggle_ergast_mirror (https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) | 64.6% | 50.0% | 100.0% | 75.0% | 60.0% |

## RDA FAIR Data Maturity Model (41 indicators, 0-4 maturity scale)

| Area | Progress as obtained | RDA level | Progress curated | RDA level | Essential passed (obtained -> curated) |
|---|---|---|---|---|---|
| Findable | 50.0% | 0 | 82.1% | 0 | 1/7 -> 2/7 |
| Accessible | 83.3% | 0 | 93.8% | 0 | 5/8 -> 5/8 |
| Interoperable | 37.5% | 1 | 93.8% | 2 | 0/0 -> 0/0 |
| Reusable | 40.0% | 0 | 100.0% | 5 | 0/5 -> 5/5 |
| Overall | 53.7% | - | 93.3% | - | 6/20 -> 12/20 |

## Gaps and improvements

- **G1 No persistent identifier for the data or metadata** (RDA-F1-01D; RDA-F1-01M; RDA-F3-01M; RDA-A1-03D): F-UJI FsF-F1-02D = 0 for the GitHub archive, the Jolpica API and even the Kaggle mirror; data are only reachable by mutable URLs. -> Publish each release of the curated package through the GitHub-Zenodo integration to mint a versioned DOI (prefix 10.5281) and a concept DOI; cite the DOI in README and CITATION.cff. *Status: Prepared (DataCite record with DOI placeholder); minting requires the group's Zenodo account.*
- **G2 Missing and conflicting licence information** (RDA-R1.1-01M; RDA-R1.1-02M; RDA-R1.1-03M): Jolpica TERMS.md (27 Aug 2025): data licensed CC BY-NC-SA 4.0. The group's README declares 'MIT License' for everything; the Kaggle mirror declares CC0 although Ergast allowed non-commercial use only. F-UJI FsF-R1.1-01M = 0 for GitHub and Jolpica. -> License the data CC BY-NC-SA 4.0 (ShareAlike obliges it), add LICENSE-DATA with the SPDX id CC-BY-NC-SA-4.0 and the legal-code URI, keep MIT for code only, and attribute Jolpica-F1 and Ergast. *Status: Implemented in DataCite rightsList, schema.org license and datapackage.json.*
- **G3 No machine-readable, standard dataset metadata** (RDA-F2-01M; RDA-F4-01M; RDA-I1-01M; RDA-R1-01M; RDA-R1.3-01M; RDA-R1.3-02M): Only a pipeline README; F-UJI FsF-F2-01M = 0.5/2 (GitHub) and 0/2 (Jolpica); FsF-R1-01MD = 1/4 and 0/4. -> Ship a DataCite 4.5 record (XML validated against the XSD), schema.org Dataset JSON-LD for search engines and a Frictionless Data Package with a full data dictionary. *Status: Implemented.*
- **G4 Non-standard vocabularies inside the data** (RDA-I2-01D; RDA-I1-02D): Country values 'UK', 'USA', 'UAE', 'Korea'; nationalities as lowercase demonyms including former states ('east german', 'rhodesian'); 136 free-text status values mixing laps-behind with failure causes. -> Add ISO 3166-1 alpha-3 codes (ISO 3166-3 for former states), Wikidata QIDs, and an 8-category status vocabulary; publish the status vocabulary as SKOS. *Status: ISO codes, QIDs and status groups implemented; SKOS publication proposed.*
- **G5 No provenance or integrity information** (RDA-R1.2-01M; RDA-R1.2-02M): The repository never names Ergast or Jolpica as the source; no checksums; no record of transformations; the original Ergast terms page now returns 404. -> Record derivation (DataCite IsDerivedFrom), SHA-256 checksums of every source and output file, the cleaning audit log, and a W3C PROV-O graph. *Status: Implemented.*
- **G6 Unqualified and partly broken links to external entities** (RDA-I3-01D; RDA-I3-02D): 861 of 864 driver URLs use http; 12 entities have no URL; 1 driver URL is a Wikipedia talk page (monarch); 2 constructor pages no longer exist (Hall, Turner). -> Normalise to https and add Wikidata QIDs as persistent entity identifiers; flag unresolved links for manual curation. *Status: Implemented (QID crosswalk in data/reference/).*
- **G7 No guarantee that metadata outlives the data** (RDA-A2-01M): The Ergast API was shut down and is only mirrored by a volunteer project (Jolpica) that 'does not guarantee uptime'; GitHub repositories can be deleted. -> Deposit in a certified repository (Zenodo/CERN) whose policy keeps metadata and a tombstone page after withdrawal. *Status: Proposed; requires deposit.*

## Persistent identifiers

- Dataset: DOI via Zenodo, placeholder `10.5281/zenodo.TO-BE-MINTED` (to be minted - never cite before minting).
- Creators: ORCID iDs to be added by each student.
- Institution: ROR to be confirmed; best candidate https://ror.org/00g07sz63 (SRH University of Applied Sciences Heidelberg) (see data/reference/ror_candidates.csv).
- Countries: ISO 3166-1 alpha-3 (ISO 3166-3 for former states); dates: ISO 8601; licence: SPDX.
- Entities: Wikidata QIDs from Wikipedia URLs (data/reference/wikidata_crosswalk.csv):
  - circuit: 82/82 (100.0%)
  - constructor: 210/214 (98.1%)
  - driver: 863/874 (98.7%)

## Licence findings

- Jolpica-F1 Terms of Use (TERMS.md, updated 27 Aug 2025, https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md): data licensed CC BY-NC-SA 4.0, non-commercial use; the code repository itself is Apache-2.0.
- Ergast Developer API terms (Wayback snapshot 18 May 2024 of https://ergast.com/mrd/terms/, live page now 404): "You may use this API for personal, non-commercial applications and services including educational and research purposes"; attribution appreciated, not required.
- Kaggle mirror (rohanrao/formula-1-world-championship-1950-2020, version 24, updated 29 Jan 2025): declared "CC0: Public Domain", although compiled from Ergast, whose terms were non-commercial - a licence inconsistency.
- Group repository README: "MIT License" for the whole project, no data licence - conflicts with CC BY-NC-SA 4.0.
- Decision: curated data released under CC-BY-NC-SA-4.0 (ShareAlike obligation); MIT kept for code only.

## Metadata record

- DataCite 4.5 XML: valid (valid against DataCite kernel-4.5 XSD).
- Files: datacite_metadata.xml, datacite_metadata.json, schema_org_dataset.jsonld, datapackage.json, provenance_prov.jsonld, data_dictionary.csv/.md, LICENSE-DATA.md.
- Coverage: 1950-05-13 to 2025-12-07, 25,873 rows in the results table; raw files collected 2026-10-15.
