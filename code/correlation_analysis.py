import pandas as pd
import sys
from scipy.stats import spearmanr, pointbiserialr, kruskal, ks_2samp
import matplotlib.pyplot as plt
import seaborn as sns

# Get the year from the command line argument
if len(sys.argv) < 2:
    print("Please provide the year as a command-line argument.")
    sys.exit(1)

year = sys.argv[1]

# Load the data
citations_df = pd.read_csv(f'dataset/sc{year}_citations.csv', names=['DOI', 'Citations'], skiprows=1)
reproducibility_df = pd.read_csv(f'dataset/sc{year}_reproducibility.csv', names=['DOI', 'Available', 'Functional', 'Replicable'], skiprows=1)

# Merge the two dataframes on DOI
merged_df = pd.merge(citations_df, reproducibility_df, on='DOI')

# Convert 'Citations' and 'Replicable' columns to numeric
merged_df['Citations'] = pd.to_numeric(merged_df['Citations'], errors='coerce')
merged_df['Available'] = pd.to_numeric(merged_df['Available'], errors='coerce')
merged_df['Functional'] = pd.to_numeric(merged_df['Functional'], errors='coerce')
merged_df['Replicable'] = pd.to_numeric(merged_df['Replicable'], errors='coerce')

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
        
# Kruskal-Wallis test
statistic, p_value = kruskal(
    merged_df['Citations'][merged_df['Replicable'] == 1],
    merged_df['Citations'][merged_df['Available'] == 0]
)
print(f"Kruskal-Wallis Test for Replicable vs No Badge: Statistic={statistic}, P-value={p_value}")

# Point-biserial correlation
correlation, p_value = pointbiserialr(merged_df['Available'], merged_df['Citations'])
print(f"Point-biserial correlation: Correlation={correlation}, P-value={p_value}")

# Spearman correlation
correlation, p_value = spearmanr(merged_df['Available'], merged_df['Citations'])
print(f"Spearman correlation: Correlation={correlation}, P-value={p_value}")

# Plot
sns.boxplot(x='Available', y='Citations', data=merged_df)
plt.title(f'Boxplot of Citations by Available Badge ({year})')
plt.xlabel('Available Badge')
plt.ylabel('Citations')
plt.show()

