# Outputs Manifest

This manifest lists the expected generated outputs for the frozen SC 2022
citation-impact analysis. The files are produced by:

```bash
python correlation_analysis.py
```

The Docker equivalent is:

```bash
docker run --rm repro-impact python correlation_analysis.py
```

## Expected Output Directories

- `outputs/sc2022_nov2023/`
- `outputs/sc2022_oct2024/`
- `outputs/sc2022_jul2026/`

## Expected CSV Files

Each output directory should contain:

- `merge_diagnostics.csv`
- `unmatched_rows.csv`
- `badge_hierarchy_errors.csv`
- `analysis_dataset.csv`
- `descriptive_statistics.csv`
- `statistical_tests.csv`

## Expected JSON Files

Each output directory should contain:

- `summary.json`

## Expected PNG Files

Each output directory should contain:

- `citations_by_badge_category.png`
- `log_citations_by_badge_category.png`
- `badge_category_counts.png`

For appendix builds that expect top-level figure paths, these generated plots
are also mirrored as:

- `figures/citations_by_badge_category_nov2023.png`
- `figures/log_citations_by_badge_category_nov2023.png`
- `figures/citations_by_badge_category_oct2024.png`
- `figures/log_citations_by_badge_category_oct2024.png`
- `figures/citations_by_badge_category_jul2026.png`
- `figures/log_citations_by_badge_category_jul2026.png`

## Merge Diagnostics

All three citation windows have:

- citation rows: 88
- badge rows: 87
- present in both: 87
- only in citations: 1
- only in badge file: 0

The unmatched citation-only DOI is `10.1109/sc41404.2022`, represented in the
source citation files as `https://doi.org/10.1109/SC41404.2022`.

## Badge Category Counts

All three citation windows have:

- No badge: 26
- Available only: 13
- Functional only: 13
- Replicable: 36

## Key Numerical Results

### November 2023 Citation Snapshot

- Spearman rho: `0.04393962059085545`
- Spearman p-value: `0.6843804014842562`
- Kruskal-Wallis H: `2.2230909853949306`
- Kruskal-Wallis p-value: `0.5274144997145862`
- Mann-Whitney U, Replicable vs No badge: `490.5`
- Mann-Whitney p-value: `0.743144062736561`
- Cliff's delta, Replicable vs No badge: `0.04807692307692308`
- Kolmogorov-Smirnov statistic, Replicable vs No badge: `0.11752136752136752`
- Kolmogorov-Smirnov p-value: `0.9634413284575102`
- Post-hoc pairwise tests: skipped because the Kruskal-Wallis omnibus test was
  not significant at alpha `0.05`.

### October 2024 Citation Snapshot

- Spearman rho: `-0.01202887318916739`
- Spearman p-value: `0.9114328445347747`
- Kruskal-Wallis H: `3.426865068703888`
- Kruskal-Wallis p-value: `0.33037208295496573`
- Mann-Whitney U, Replicable vs No badge: `442.0`
- Mann-Whitney p-value: `0.7128641770547733`
- Cliff's delta, Replicable vs No badge: `-0.05555555555555555`
- Kolmogorov-Smirnov statistic, Replicable vs No badge: `0.11538461538461539`
- Kolmogorov-Smirnov p-value: `0.9683510842397156`
- Post-hoc pairwise tests: skipped because the Kruskal-Wallis omnibus test was
  not significant at alpha `0.05`.

### July 2026 Citation Snapshot

- Spearman rho: `0.010054532958606697`
- Spearman p-value: `0.9259245324699451`
- Kruskal-Wallis H: `2.0344647646326885`
- Kruskal-Wallis p-value: `0.5652843164905148`
- Mann-Whitney U, Replicable vs No badge: `458.5`
- Mann-Whitney p-value: `0.8976146329933391`
- Cliff's delta, Replicable vs No badge: `-0.0202991452991453`
- Kolmogorov-Smirnov statistic, Replicable vs No badge: `0.1517094017094017`
- Kolmogorov-Smirnov p-value: `0.8177888783320975`
- Post-hoc pairwise tests: skipped because the Kruskal-Wallis omnibus test was
  not significant at alpha `0.05`.

## Interpretation

These values support only the conservative statement that no statistically
detectable association was observed between SC 2022 badge level and citation
count in these citation windows at alpha `0.05`. They do not establish
equivalence and do not estimate a causal effect.
