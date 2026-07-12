import itertools
import json
import os
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "reproducibility-impact-matplotlib")
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import kruskal, ks_2samp, mannwhitneyu, spearmanr


BADGE_FILE = REPO_ROOT / "dataset" / "sc2022_reproducibility.csv"
SNAPSHOTS = [
    {
        "label": "sc2022_nov2023",
        "citation_window": "November 2023",
        "citation_file": REPO_ROOT
        / "dataset"
        / "data-nov-2023"
        / "sc2022_citations.csv",
        "output_dir": REPO_ROOT / "outputs" / "sc2022_nov2023",
        "figure_suffix": "nov2023",
    },
    {
        "label": "sc2022_oct2024",
        "citation_window": "October 2024",
        "citation_file": REPO_ROOT
        / "dataset"
        / "data-oct-2024"
        / "sc2022_citations.csv",
        "output_dir": REPO_ROOT / "outputs" / "sc2022_oct2024",
        "figure_suffix": "oct2024",
    },
    {
        "label": "sc2022_jul2026",
        "citation_window": "July 2026",
        "citation_file": REPO_ROOT
        / "dataset"
        / "data-jul-2026"
        / "sc2022_citations.csv",
        "output_dir": REPO_ROOT / "outputs" / "sc2022_jul2026",
        "figure_suffix": "jul2026",
    },
]

BADGE_COLUMNS = ["Available", "Functional", "Replicable"]
CATEGORY_ORDER = ["No badge", "Available only", "Functional only", "Replicable"]
CATEGORY_LEVELS = {
    "No badge": 0,
    "Available only": 1,
    "Functional only": 2,
    "Replicable": 3,
}
ALPHA = 0.05


def normalize_doi(value):
    doi = "" if pd.isna(value) else str(value)
    doi = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://dx.doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
            break
    return doi.rstrip("/")


def load_citations(path):
    df = pd.read_csv(path)
    required = {"DOI", "Citations"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")

    df = df[["DOI", "Citations"]].copy()
    df["CitationDOI"] = df["DOI"]
    df["DOI"] = df["DOI"].map(normalize_doi)
    df["Citations"] = pd.to_numeric(df["Citations"], errors="coerce")
    validate_no_duplicate_dois(df, path)
    validate_numeric_citations(df, path)
    return df


def load_badges(path):
    df = pd.read_csv(path)
    df = df.rename(columns={"aa": "Available", "af": "Functional", "ar": "Replicable"})
    required = {"DOI", *BADGE_COLUMNS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")

    df = df[["DOI", *BADGE_COLUMNS]].copy()
    df["BadgeDOI"] = df["DOI"]
    df["DOI"] = df["DOI"].map(normalize_doi)
    for column in BADGE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    validate_no_duplicate_dois(df, path)
    validate_binary_badges(df, path)
    return df


def validate_no_duplicate_dois(df, label):
    duplicated = df[df["DOI"].duplicated(keep=False)].sort_values("DOI")
    if not duplicated.empty:
        duplicate_values = duplicated["DOI"].tolist()
        raise ValueError(f"Duplicate DOI values after normalization in {label}: {duplicate_values}")


def validate_numeric_citations(df, label):
    invalid = df[df["Citations"].isna()]
    if not invalid.empty:
        raise ValueError(
            f"Non-numeric citation counts in {label}: "
            f"{invalid[['DOI', 'CitationDOI', 'Citations']].to_dict(orient='records')}"
        )


def validate_binary_badges(df, label):
    for column in BADGE_COLUMNS:
        invalid = df[~df[column].isin([0, 1])]
        if not invalid.empty:
            raise ValueError(
                f"Badge column {column} in {label} contains values other than 0/1: "
                f"{invalid[['DOI', column]].to_dict(orient='records')}"
            )


def build_outer_merge(citations_df, badges_df):
    return citations_df.merge(
        badges_df,
        on="DOI",
        how="outer",
        indicator=True,
        suffixes=("_citation", "_badge"),
    )


def save_merge_diagnostics(merged_df, citations_df, badges_df, output_dir):
    diagnostics = pd.DataFrame(
        [
            {
                "citation_rows": len(citations_df),
                "badge_rows": len(badges_df),
                "present_in_both": int((merged_df["_merge"] == "both").sum()),
                "only_in_citations": int((merged_df["_merge"] == "left_only").sum()),
                "only_in_badge_file": int((merged_df["_merge"] == "right_only").sum()),
            }
        ]
    )
    diagnostics.to_csv(output_dir / "merge_diagnostics.csv", index=False)

    unmatched = merged_df.loc[merged_df["_merge"] != "both"].copy()
    unmatched = unmatched.rename(columns={"_merge": "merge_status"})
    unmatched_columns = [
        "DOI",
        "CitationDOI",
        "BadgeDOI",
        "Citations",
        "Available",
        "Functional",
        "Replicable",
        "merge_status",
    ]
    unmatched.reindex(columns=unmatched_columns).to_csv(
        output_dir / "unmatched_rows.csv", index=False
    )

    return diagnostics.iloc[0].to_dict()


def create_analysis_dataset(merged_df):
    analysis_df = merged_df[merged_df["Citations"].notna()].copy()

    # Absence from the manually curated badge file is interpreted as no recorded
    # badge for papers that have citation data but no badge record.
    missing_badges = analysis_df["BadgeDOI"].isna()
    analysis_df.loc[missing_badges, BADGE_COLUMNS] = 0

    for column in BADGE_COLUMNS:
        analysis_df[column] = analysis_df[column].astype(int)

    analysis_df["BadgeCategory"] = analysis_df.apply(assign_badge_category, axis=1)
    analysis_df["BadgeLevel"] = analysis_df["BadgeCategory"].map(CATEGORY_LEVELS)

    output_columns = [
        "DOI",
        "CitationDOI",
        "BadgeDOI",
        "Citations",
        "Available",
        "Functional",
        "Replicable",
        "BadgeCategory",
        "BadgeLevel",
    ]
    analysis_df = analysis_df[output_columns].sort_values("DOI").reset_index(drop=True)
    validate_no_duplicate_dois(analysis_df, "analysis dataset")
    validate_binary_badges(analysis_df, "analysis dataset")
    return analysis_df


def assign_badge_category(row):
    if row["Replicable"] == 1:
        return "Replicable"
    if row["Functional"] == 1:
        return "Functional only"
    if row["Available"] == 1:
        return "Available only"
    return "No badge"


def hierarchy_errors(df):
    rows = []
    replicable_errors = df[
        (df["Replicable"] == 1) & ((df["Functional"] != 1) | (df["Available"] != 1))
    ]
    functional_errors = df[(df["Functional"] == 1) & (df["Available"] != 1)]

    for _, row in replicable_errors.iterrows():
        rows.append(
            {
                "DOI": row["DOI"],
                "CitationDOI": row["CitationDOI"],
                "BadgeDOI": row["BadgeDOI"],
                "error": "Replicable does not imply Functional and Available",
            }
        )
    for _, row in functional_errors.iterrows():
        rows.append(
            {
                "DOI": row["DOI"],
                "CitationDOI": row["CitationDOI"],
                "BadgeDOI": row["BadgeDOI"],
                "error": "Functional does not imply Available",
            }
        )

    return pd.DataFrame(rows, columns=["DOI", "CitationDOI", "BadgeDOI", "error"])


def save_hierarchy_diagnostics(analysis_df, output_dir):
    errors = hierarchy_errors(analysis_df)
    errors.to_csv(output_dir / "badge_hierarchy_errors.csv", index=False)
    if not errors.empty:
        raise ValueError(
            "Badge hierarchy validation failed; see "
            f"{output_dir / 'badge_hierarchy_errors.csv'}"
        )
    return errors


def descriptive_statistics(analysis_df):
    rows = []
    for category in CATEGORY_ORDER:
        values = analysis_df.loc[analysis_df["BadgeCategory"] == category, "Citations"]
        if values.empty:
            rows.append({"BadgeCategory": category, "n": 0})
            continue
        q25 = values.quantile(0.25)
        q75 = values.quantile(0.75)
        rows.append(
            {
                "BadgeCategory": category,
                "n": int(values.count()),
                "mean": values.mean(),
                "median": values.median(),
                "std": values.std(),
                "min": values.min(),
                "q25": q25,
                "q75": q75,
                "IQR": q75 - q25,
                "max": values.max(),
            }
        )
    return pd.DataFrame(rows)


def cliffs_delta(x_values, y_values):
    greater = 0
    lesser = 0
    for x in x_values:
        for y in y_values:
            if x > y:
                greater += 1
            elif x < y:
                lesser += 1
    total = len(x_values) * len(y_values)
    if total == 0:
        return None
    return (greater - lesser) / total


def test_row(
    test,
    comparison,
    statistic=None,
    p_value=None,
    adjusted_p_value=None,
    effect_size=None,
    effect_size_name=None,
    n_1=None,
    n_2=None,
    n_total=None,
    status="computed",
    interpretation=None,
    notes=None,
):
    return {
        "test": test,
        "comparison": comparison,
        "statistic": statistic,
        "p_value": p_value,
        "adjusted_p_value": adjusted_p_value,
        "effect_size": effect_size,
        "effect_size_name": effect_size_name,
        "n_1": n_1,
        "n_2": n_2,
        "n_total": n_total,
        "status": status,
        "interpretation": interpretation,
        "notes": notes,
    }


def statistical_tests(analysis_df):
    rows = []
    n_total = len(analysis_df)

    spearman_result = spearmanr(analysis_df["BadgeLevel"], analysis_df["Citations"])
    rows.append(
        test_row(
            "Spearman rank correlation",
            "Ordinal badge level vs citations",
            statistic=spearman_result.statistic,
            p_value=spearman_result.pvalue,
            n_total=n_total,
            interpretation=association_interpretation(spearman_result.pvalue),
            notes="Badge level is encoded as No badge=0, Available only=1, Functional only=2, Replicable=3.",
        )
    )

    grouped = [
        analysis_df.loc[analysis_df["BadgeCategory"] == category, "Citations"]
        for category in CATEGORY_ORDER
    ]
    kruskal_result = kruskal(*grouped)
    rows.append(
        test_row(
            "Kruskal-Wallis H",
            "Citations across mutually exclusive badge categories",
            statistic=kruskal_result.statistic,
            p_value=kruskal_result.pvalue,
            n_total=n_total,
            interpretation=category_difference_interpretation(kruskal_result.pvalue),
            notes="Omnibus non-parametric test across the four mutually exclusive badge categories.",
        )
    )

    replicable = analysis_df.loc[
        analysis_df["BadgeCategory"] == "Replicable", "Citations"
    ].tolist()
    no_badge = analysis_df.loc[
        analysis_df["BadgeCategory"] == "No badge", "Citations"
    ].tolist()

    mann_whitney = mannwhitneyu(replicable, no_badge, alternative="two-sided")
    rows.append(
        test_row(
            "Mann-Whitney U",
            "Replicable vs No badge",
            statistic=mann_whitney.statistic,
            p_value=mann_whitney.pvalue,
            n_1=len(replicable),
            n_2=len(no_badge),
            interpretation=two_group_interpretation(mann_whitney.pvalue),
            notes="Pre-specified conservative comparison between the highest badge level and no recorded badge.",
        )
    )

    delta = cliffs_delta(replicable, no_badge)
    rows.append(
        test_row(
            "Cliff's delta",
            "Replicable vs No badge",
            effect_size=delta,
            effect_size_name="Cliff's delta",
            n_1=len(replicable),
            n_2=len(no_badge),
            interpretation="Effect size only; positive values mean Replicable citation counts tend to be larger than No badge.",
        )
    )

    ks_result = ks_2samp(replicable, no_badge)
    rows.append(
        test_row(
            "Kolmogorov-Smirnov",
            "Replicable vs No badge",
            statistic=ks_result.statistic,
            p_value=ks_result.pvalue,
            n_1=len(replicable),
            n_2=len(no_badge),
            interpretation=two_group_interpretation(ks_result.pvalue),
            notes="Secondary/exploratory distributional check.",
        )
    )

    if kruskal_result.pvalue < ALPHA:
        rows.extend(posthoc_pairwise_tests(analysis_df))
    else:
        rows.append(
            test_row(
                "Post-hoc pairwise tests",
                "All badge categories",
                status="skipped",
                interpretation="Skipped because the Kruskal-Wallis omnibus test was not significant at alpha=0.05.",
            )
        )

    return pd.DataFrame(rows)


def association_interpretation(p_value):
    if p_value < ALPHA:
        return "Statistically detectable monotonic association at alpha=0.05."
    return "No statistically detectable monotonic association at alpha=0.05."


def category_difference_interpretation(p_value):
    if p_value < ALPHA:
        return "Statistically detectable difference across badge categories at alpha=0.05."
    return "No statistically detectable difference across badge categories at alpha=0.05."


def two_group_interpretation(p_value):
    if p_value < ALPHA:
        return "Statistically detectable difference between the two groups at alpha=0.05."
    return "No statistically detectable difference between the two groups at alpha=0.05."


def posthoc_pairwise_tests(analysis_df):
    rows = []
    pairs = list(itertools.combinations(CATEGORY_ORDER, 2))
    raw_results = []
    for first, second in pairs:
        first_values = analysis_df.loc[
            analysis_df["BadgeCategory"] == first, "Citations"
        ].tolist()
        second_values = analysis_df.loc[
            analysis_df["BadgeCategory"] == second, "Citations"
        ].tolist()
        result = mannwhitneyu(first_values, second_values, alternative="two-sided")
        raw_results.append((first, second, first_values, second_values, result))

    correction_factor = len(raw_results)
    for first, second, first_values, second_values, result in raw_results:
        adjusted_p = min(result.pvalue * correction_factor, 1.0)
        rows.append(
            test_row(
                "Post-hoc Mann-Whitney U",
                f"{first} vs {second}",
                statistic=result.statistic,
                p_value=result.pvalue,
                adjusted_p_value=adjusted_p,
                n_1=len(first_values),
                n_2=len(second_values),
                interpretation=two_group_interpretation(adjusted_p),
                notes="Bonferroni-adjusted post-hoc test run because the Kruskal-Wallis omnibus test was significant.",
            )
        )
    return rows


def save_plots(analysis_df, output_dir, citation_window):
    sns.set_theme(style="whitegrid")
    plot_df = analysis_df.copy()
    plot_df["BadgeCategory"] = pd.Categorical(
        plot_df["BadgeCategory"], categories=CATEGORY_ORDER, ordered=True
    )
    plot_df["LogCitations"] = np.log1p(plot_df["Citations"])

    save_boxplot(
        plot_df,
        output_dir / "citations_by_badge_category.png",
        "Citations",
        f"SC 2022 citations by badge category ({citation_window})",
        "Citation count",
    )
    save_boxplot(
        plot_df,
        output_dir / "log_citations_by_badge_category.png",
        "LogCitations",
        f"SC 2022 log citations by badge category ({citation_window})",
        "log(1 + citation count)",
    )
    save_count_plot(plot_df, output_dir / "badge_category_counts.png", citation_window)


def save_appendix_figure_copies(output_dir, figure_suffix):
    figures_dir = REPO_ROOT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_map = {
        "citations_by_badge_category.png": f"citations_by_badge_category_{figure_suffix}.png",
        "log_citations_by_badge_category.png": f"log_citations_by_badge_category_{figure_suffix}.png",
    }
    for source_name, target_name in figure_map.items():
        shutil.copyfile(output_dir / source_name, figures_dir / target_name)


def save_boxplot(plot_df, path, y_column, title, y_label):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=plot_df,
        x="BadgeCategory",
        y=y_column,
        order=CATEGORY_ORDER,
        showfliers=False,
        color="#a8dadc",
        ax=ax,
    )
    sns.stripplot(
        data=plot_df,
        x="BadgeCategory",
        y=y_column,
        order=CATEGORY_ORDER,
        color="#1d3557",
        alpha=0.75,
        jitter=0.2,
        size=4,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel("Mutually exclusive badge category")
    ax.set_ylabel(y_label)
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def save_count_plot(plot_df, path, citation_window):
    counts = (
        plot_df["BadgeCategory"]
        .value_counts()
        .reindex(CATEGORY_ORDER)
        .reset_index()
    )
    counts.columns = ["BadgeCategory", "Papers"]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=counts,
        x="BadgeCategory",
        y="Papers",
        order=CATEGORY_ORDER,
        color="#457b9d",
        ax=ax,
    )
    ax.set_title(f"SC 2022 papers by badge category ({citation_window})")
    ax.set_xlabel("Mutually exclusive badge category")
    ax.set_ylabel("Paper count")
    ax.tick_params(axis="x", rotation=15)
    for container in ax.containers:
        ax.bar_label(container, fmt="%d", padding=3)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def write_summary(
    output_dir,
    snapshot,
    merge_diagnostics,
    analysis_df,
    stats_df,
    tests_df,
):
    group_counts = (
        analysis_df["BadgeCategory"].value_counts().reindex(CATEGORY_ORDER).fillna(0)
    )
    summary = {
        "snapshot": snapshot["label"],
        "citation_window": snapshot["citation_window"],
        "citation_file": str(snapshot["citation_file"].relative_to(REPO_ROOT)),
        "badge_file": str(BADGE_FILE.relative_to(REPO_ROOT)),
        "merge_diagnostics": merge_diagnostics,
        "group_counts": {category: int(group_counts[category]) for category in CATEGORY_ORDER},
        "statistical_tests": tests_df.to_dict(orient="records"),
        "descriptive_statistics": stats_df.to_dict(orient="records"),
        "supported_claim": (
            "The analysis evaluates whether a statistically detectable association "
            "is observed between SC 2022 badge level and citation count in this "
            "citation snapshot. It does not estimate a causal effect."
        ),
    }

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(clean_for_json(summary), handle, indent=2)


def clean_for_json(value):
    if isinstance(value, dict):
        return {key: clean_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_for_json(item) for item in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def analyze_snapshot(snapshot, badges_df):
    output_dir = snapshot["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    citations_df = load_citations(snapshot["citation_file"])
    merged_df = build_outer_merge(citations_df, badges_df)
    merge_diagnostics = save_merge_diagnostics(
        merged_df, citations_df, badges_df, output_dir
    )

    analysis_df = create_analysis_dataset(merged_df)
    save_hierarchy_diagnostics(analysis_df, output_dir)
    analysis_df.to_csv(output_dir / "analysis_dataset.csv", index=False)

    stats_df = descriptive_statistics(analysis_df)
    stats_df.to_csv(output_dir / "descriptive_statistics.csv", index=False)

    tests_df = statistical_tests(analysis_df)
    tests_df.to_csv(output_dir / "statistical_tests.csv", index=False)

    save_plots(analysis_df, output_dir, snapshot["citation_window"])
    save_appendix_figure_copies(output_dir, snapshot["figure_suffix"])
    write_summary(output_dir, snapshot, merge_diagnostics, analysis_df, stats_df, tests_df)

    return analysis_df, tests_df


def main():
    badges_df = load_badges(BADGE_FILE)
    for snapshot in SNAPSHOTS:
        analysis_df, tests_df = analyze_snapshot(snapshot, badges_df)
        counts = analysis_df["BadgeCategory"].value_counts().reindex(CATEGORY_ORDER)
        print(f"Analyzed {snapshot['label']} ({snapshot['citation_window']})")
        print(f"  Output: {snapshot['output_dir'].relative_to(REPO_ROOT)}")
        print(f"  Group counts: {counts.to_dict()}")
        key_tests = tests_df.loc[
            tests_df["test"].isin(
                ["Spearman rank correlation", "Kruskal-Wallis H", "Mann-Whitney U"]
            ),
            ["test", "statistic", "p_value", "interpretation"],
        ]
        print(key_tests.to_string(index=False))
        print()


if __name__ == "__main__":
    main()
