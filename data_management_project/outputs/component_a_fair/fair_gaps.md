# FAIR compliance gaps and improvement proposals

## G1 - No persistent identifier for the data or metadata

- **RDA indicators:** RDA-F1-01D; RDA-F1-01M; RDA-F3-01M; RDA-A1-03D
- **Evidence:** F-UJI FsF-F1-02D = 0 for the GitHub archive, the Jolpica API and even the Kaggle mirror; data are only reachable by mutable URLs.
- **Improvement:** Publish each release of the curated package through the GitHub-Zenodo integration to mint a versioned DOI (prefix 10.5281) and a concept DOI; cite the DOI in README and CITATION.cff.
- **Status in delivered package:** Prepared (DataCite record with DOI placeholder); minting requires the group's Zenodo account.

## G2 - Missing and conflicting licence information

- **RDA indicators:** RDA-R1.1-01M; RDA-R1.1-02M; RDA-R1.1-03M
- **Evidence:** Jolpica TERMS.md (27 Aug 2025): data licensed CC BY-NC-SA 4.0. The group's README declares 'MIT License' for everything; the Kaggle mirror declares CC0 although Ergast allowed non-commercial use only. F-UJI FsF-R1.1-01M = 0 for GitHub and Jolpica.
- **Improvement:** License the data CC BY-NC-SA 4.0 (ShareAlike obliges it), add LICENSE-DATA with the SPDX id CC-BY-NC-SA-4.0 and the legal-code URI, keep MIT for code only, and attribute Jolpica-F1 and Ergast.
- **Status in delivered package:** Implemented in DataCite rightsList, schema.org license and datapackage.json.

## G3 - No machine-readable, standard dataset metadata

- **RDA indicators:** RDA-F2-01M; RDA-F4-01M; RDA-I1-01M; RDA-R1-01M; RDA-R1.3-01M; RDA-R1.3-02M
- **Evidence:** Only a pipeline README; F-UJI FsF-F2-01M = 0.5/2 (GitHub) and 0/2 (Jolpica); FsF-R1-01MD = 1/4 and 0/4.
- **Improvement:** Ship a DataCite 4.5 record (XML validated against the XSD), schema.org Dataset JSON-LD for search engines and a Frictionless Data Package with a full data dictionary.
- **Status in delivered package:** Implemented.

## G4 - Non-standard vocabularies inside the data

- **RDA indicators:** RDA-I2-01D; RDA-I1-02D
- **Evidence:** Country values 'UK', 'USA', 'UAE', 'Korea'; nationalities as lowercase demonyms including former states ('east german', 'rhodesian'); 136 free-text status values mixing laps-behind with failure causes.
- **Improvement:** Add ISO 3166-1 alpha-3 codes (ISO 3166-3 for former states), Wikidata QIDs, and an 8-category status vocabulary; publish the status vocabulary as SKOS.
- **Status in delivered package:** ISO codes, QIDs and status groups implemented; SKOS publication proposed.

## G5 - No provenance or integrity information

- **RDA indicators:** RDA-R1.2-01M; RDA-R1.2-02M
- **Evidence:** The repository never names Ergast or Jolpica as the source; no checksums; no record of transformations; the original Ergast terms page now returns 404.
- **Improvement:** Record derivation (DataCite IsDerivedFrom), SHA-256 checksums of every source and output file, the cleaning audit log, and a W3C PROV-O graph.
- **Status in delivered package:** Implemented.

## G6 - Unqualified and partly broken links to external entities

- **RDA indicators:** RDA-I3-01D; RDA-I3-02D
- **Evidence:** 861 of 864 driver URLs use http; 12 entities have no URL; 1 driver URL is a Wikipedia talk page (monarch); 2 constructor pages no longer exist (Hall, Turner).
- **Improvement:** Normalise to https and add Wikidata QIDs as persistent entity identifiers; flag unresolved links for manual curation.
- **Status in delivered package:** Implemented (QID crosswalk in data/reference/).

## G7 - No guarantee that metadata outlives the data

- **RDA indicators:** RDA-A2-01M
- **Evidence:** The Ergast API was shut down and is only mirrored by a volunteer project (Jolpica) that 'does not guarantee uptime'; GitHub repositories can be deleted.
- **Improvement:** Deposit in a certified repository (Zenodo/CERN) whose policy keeps metadata and a tombstone page after withdrawal.
- **Status in delivered package:** Proposed; requires deposit.
