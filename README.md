# reproducibility-impact

This repository contains a reproducibility artifact for analyzing whether SC 2022
reproducibility badge level is associated with citation count in the available
citation snapshots.

The analysis is conservative. It does not estimate or claim a causal effect of
badges on citations. The supported claim is only whether a statistically
detectable association is observed between SC 2022 badge level and citation
count in the frozen citation windows included in this repository.

## Data

The artifact analysis uses three frozen citation snapshots:

- `dataset/data-nov-2023/sc2022_citations.csv`
- `dataset/data-oct-2024/sc2022_citations.csv`
- `dataset/data-jul-2026/sc2022_citations.csv`

The badge data are stored in:

- `dataset/sc2022_reproducibility.csv`

The badge file records the SC badge hierarchy:

- `aa`: ACM Artifacts Available
- `af`: ACM Artifacts Evaluated-Functional
- `ar`: ACM Results Replicated

The analysis renames these internally to `Available`, `Functional`, and
`Replicable`. SC badge levels are hierarchical: `Replicable` implies
`Functional` and `Available`, and `Functional` implies `Available`.

The DBLP API URL used for live citation retrieval is stored in:

- `dataset/dblp-urls-sc.txt`

## Installation

### Local Python

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Docker

```bash
docker build . -t repro-impact
docker run --rm repro-impact python correlation_analysis.py
```

The command above runs the frozen-snapshot analysis inside the container. To
persist regenerated outputs back to the host filesystem, mount the output
directory:

```bash
docker run --rm -v "$PWD/outputs:/usr/src/app/outputs" repro-impact python correlation_analysis.py
```

## Reproduce The Paper Analysis

Run the analysis from the frozen citation snapshots:

```bash
python correlation_analysis.py
```

The script analyzes all three citation windows and writes outputs under:

- `outputs/sc2022_nov2023/`
- `outputs/sc2022_oct2024/`
- `outputs/sc2022_jul2026/`

Each output directory contains:

- `merge_diagnostics.csv`
- `unmatched_rows.csv`
- `badge_hierarchy_errors.csv`
- `analysis_dataset.csv`
- `descriptive_statistics.csv`
- `statistical_tests.csv`
- `summary.json`
- `citations_by_badge_category.png`
- `log_citations_by_badge_category.png`
- `badge_category_counts.png`

The analysis also refreshes appendix-facing plot copies under `figures/`:

- `figures/citations_by_badge_category_nov2023.png`
- `figures/log_citations_by_badge_category_nov2023.png`
- `figures/citations_by_badge_category_oct2024.png`
- `figures/log_citations_by_badge_category_oct2024.png`
- `figures/citations_by_badge_category_jul2026.png`
- `figures/log_citations_by_badge_category_jul2026.png`

The repository may include generated example outputs for release review. These
files are reproducible by rerunning `python correlation_analysis.py`. See
`outputs_manifest.md` for the complete output inventory and key numerical
results.

## Live Citation Fetching

Live citation retrieval is separate from reproducing the paper analysis. It uses
current OpenAlex results and can therefore change over time.

To fetch live citation counts from DBLP/OpenAlex:

```bash
python get-citations.py
```

This writes `dataset/sc2022_citations.csv`. That live output is not used by
`correlation_analysis.py`, which intentionally uses the frozen November 2023,
October 2024, and July 2026 snapshots listed above. To preserve a future live
fetch as a reproducible snapshot, save it under a dated `dataset/data-*/`
directory and add that path explicitly to `correlation_analysis.py`.

## Analysis Method

The pipeline performs the following steps for each citation snapshot:

1. Normalize DOI values by stripping whitespace, lowercasing, removing DOI URL
   prefixes, and removing trailing slashes.
2. Outer-join citations and badges to produce merge diagnostics before analysis.
3. Build the analysis dataset from papers with citation data. Citation rows
   absent from the manually curated badge file are treated as having no recorded
   badge.
4. Validate duplicate DOI values, numeric citation counts, binary badge columns,
   and badge hierarchy consistency.
5. Convert badges into mutually exclusive categories:
   `No badge`, `Available only`, `Functional only`, and `Replicable`.
6. Encode an ordinal badge level:
   `No badge = 0`, `Available only = 1`, `Functional only = 2`,
   `Replicable = 3`.
7. Compute descriptive citation statistics by badge category.
8. Run conservative statistical tests:
   Spearman correlation between ordinal badge level and citations,
   Kruskal-Wallis across mutually exclusive badge categories,
   Mann-Whitney U for `Replicable` vs `No badge`,
   Cliff's delta for `Replicable` vs `No badge`, and a secondary exploratory
   KS test for `Replicable` vs `No badge`.

The analysis does not compare overlapping badge groups as independent
categories. Post-hoc pairwise tests across all badge categories are skipped
unless the Kruskal-Wallis omnibus test is significant.

## Interpretation

A non-significant test result is reported as no statistically detectable
association or difference at the specified alpha level. It is not interpreted as
proof that the groups are equivalent, proof that badge status has no effect, or
evidence that citation distributions are the same.

Citation counts are observational and are affected by many factors outside this
artifact. The analysis should therefore be read as an association check for the
available SC 2022 data and citation windows only.

## Known Limitations

- The analysis is observational and cannot establish causality.
- It covers one venue, SC, and one publication year, 2022.
- The citation windows are snapshots from November 2023, October 2024, and July
  2026.
- Citation counts depend on the frozen OpenAlex snapshots included here.
- ACM badge data were manually extracted and curated.
- One citation-only DOI absent from the badge file is treated as having no
  recorded badge.
- The analysis does not control for citation confounders such as topic,
  author/team visibility, institution, paper type, funding, or prior work.
