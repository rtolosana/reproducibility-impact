import pandas as pd
from scipy.stats import spearmanr, pointbiserialr, kruskal, ks_2samp
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(citations_file, reproducibility_file):
    # Load the data
    citations_df = pd.read_csv(citations_file, names=['DOI', 'Citations'], skiprows=1)
    reproducibility_df = pd.read_csv(reproducibility_file, names=['DOI', 'Available', 'Functional', 'Replicable'], skiprows=1)

    # Merge the two dataframes on DOI
    merged_df = pd.merge(citations_df, reproducibility_df, on='DOI')

    # Convert columns to numeric
    merged_df['Citations'] = pd.to_numeric(merged_df['Citations'], errors='coerce')
    merged_df['Available'] = pd.to_numeric(merged_df['Available'], errors='coerce')
    merged_df['Functional'] = pd.to_numeric(merged_df['Functional'], errors='coerce')
    merged_df['Replicable'] = pd.to_numeric(merged_df['Replicable'], errors='coerce')

    return merged_df

def ks_test(merged_df):
    # Define groups
    group_names = ['Badge Artifact Available', 'Badge Artifact Functional', 'Badge Results Replicated', 'No Badge']
    groups = {
        'Badge Artifact Available': merged_df['Citations'][merged_df['Available'] == 1],
        'Badge Artifact Functional': merged_df['Citations'][merged_df['Functional'] == 1],
        'Badge Results Replicated': merged_df['Citations'][merged_df['Replicable'] == 1],
        'No Badge': merged_df['Citations'][merged_df['Available'] == 0] 
    }

    # Perform KS test between pairs of groups
    for i in range(len(group_names)):
        for j in range(i+1, len(group_names)):
            group1_name = group_names[i]
            group2_name = group_names[j]
            group1 = groups[group1_name]
            group2 = groups[group2_name]
            statistic, p_value = ks_2samp(group1, group2)
            print(f"KS Test between {group1_name} and {group2_name}:")
            print(f"Test Statistic: {statistic}")
            print(f"P-value: {p_value}")
            if p_value < 0.05:
                print("Reject the null hypothesis. The distributions are different.")
            else:
                print("Fail to reject the null hypothesis. The distributions are similar.")
            print()

def kruskal_wallis_test(merged_df):
    # Kruskal-Wallis test
    statistic, p_value = kruskal(
        merged_df['Citations'][merged_df['Replicable'] == 1],
        merged_df['Citations'][merged_df['Available'] == 0]
    )
    print(f"Kruskal-Wallis Test for Replicable vs No Badge: Statistic={statistic}, P-value={p_value}")

def point_biserial_correlation(merged_df):
    # Point-biserial correlation
    correlation, p_value = pointbiserialr(merged_df['Replicable'], merged_df['Citations'])
    print(f"Point-biserial correlation: Correlation={correlation}, P-value={p_value}")

def plot_boxplot(merged_df, year):
    # Plot boxplot
    sns.boxplot(x='Replicable', y='Citations', data=merged_df)
    plt.title(f'Boxplot of Citations by Replicable Badge ({year})')
    plt.xlabel('Replicable Badge')
    plt.ylabel('Citations')
    # Save the plot as an image file
    plt.savefig(f'boxplot_citations_by_replicable_badge_{year}.png', dpi=300, bbox_inches='tight')
    #plt.show()

# Call the functions for the hardcoded datasets
def analyze_data(year, citations_file, reproducibility_file):
    print(f"Analyzing data for the year {year}...")
    merged_df = load_data(citations_file, reproducibility_file)
    
    # Perform statistical tests
    ks_test(merged_df)
    kruskal_wallis_test(merged_df)
    point_biserial_correlation(merged_df)
    
    # Plot
    plot_boxplot(merged_df, year)

# Hardcoded files for different years
analyze_data('2022-citations-nov2023', 'dataset/data-nov-2023/sc2022_citations.csv', 'dataset/sc2022_reproducibility.csv')
analyze_data('2022-citations-oct2024', 'dataset/data-oct-2024/sc2022_citations.csv', 'dataset/sc2022_reproducibility.csv')

