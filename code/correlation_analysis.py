import pandas as pd
from scipy.stats import spearmanr
from scipy.stats import pointbiserialr
from scipy.stats import kruskal
from scipy.stats import shapiro, normaltest
from scipy.stats import ks_2samp


import matplotlib.pyplot as plt
import seaborn as sns



# Load the data
citations_df = pd.read_csv('sc2022_citations.csv', names=['DOI', 'Citations'], skiprows=1)
reproducibility_df = pd.read_csv('sc2022_reproducibility.csv', names=['DOI', 'Available', 'Functional', 'Replicable'], skiprows=1)

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
        

# Extract 'Citations' for each reproducibility badge group
citations_badge_replicable = merged_df['Citations'][merged_df['Replicable'] == 1]
citations_badge_functional = merged_df['Citations'][merged_df['Functional'] == 1]
citations_badge_available = merged_df['Citations'][merged_df['Available'] == 1]
citations_no_badge_available = merged_df['Citations'][merged_df['Available'] == 0] 

# Perform Kruskal-Wallis test
statistic, p_value = kruskal(citations_badge_replicable,citations_no_badge_available)

# Print Kruskal-Wallis test results
print("Kruskal-Wallis Test: citations_badge_replicable and no badge")
print(f"Test Statistic: {statistic}")
print(f"P-value: {p_value}")

statistic, p_value = kruskal(citations_badge_functional,citations_no_badge_available)

# Print Kruskal-Wallis test results
print("Kruskal-Wallis Test: citations_badge_functional and no badge")
print(f"Test Statistic: {statistic}")
print(f"P-value: {p_value}")

statistic, p_value = kruskal(citations_badge_available,citations_no_badge_available)

# Print Kruskal-Wallis test results
print("Kruskal-Wallis Test: citations_badge_available and no badge")
print(f"Test Statistic: {statistic}")
print(f"P-value: {p_value}")


# Interpret the results
alpha = 0.05
if p_value < alpha:
    print("Reject the null hypothesis. There are statistically significant differences among the groups.")
else:
    print("Fail to reject the null hypothesis. There are no statistically significant differences among the groups.")


# Conduct Pointbiserial correlation analysis
correlation, p_value = pointbiserialr(merged_df['Available'], merged_df['Citations'])

# Print the point-biserial correlation coefficient and p-value
print(f"Point-biserial correlation coefficient: {correlation}")
print(f"P-value: {p_value}")

# Check for statistical significance at a significance level of 0.05
if p_value < 0.05:
    print("Reject the null hypothesis. There is evidence of a statistically significant correlation.")
else:
    print("Fail to reject the null hypothesis. There is no statistically significant evidence of a correlation.")

# Conduct Spearman correlation analysis
correlation, p_value = spearmanr(merged_df['Available'], merged_df['Citations'])

# Print the correlation coefficient and p-value
print(f"Spearman correlation coefficient: {correlation}")
print(f"P-value: {p_value}")

if p_value < 0.05:
    print("Reject the null hypothesis. There is evidence of a statistically significant correlation.")
else:
    print("Fail to reject the null hypothesis. There is no statistically significant evidence of a correlation.")
    
# Create a scatter plot
#sns.scatterplot(x='Available', y='Citations', data=merged_df)

# Optionally, add a regression line
#sns.regplot(x='Available', y='Citations', data=merged_df, scatter=False)

#plt.title('Scatter Plot of Replicable vs. Citations')
#plt.xlabel('Available Badge')
#plt.ylabel('Citations')
#plt.show()

# Create a boxplot
sns.boxplot(x='Available', y='Citations', data=merged_df)

# Add labels and title
plt.title('Boxplot of Citations by Having an Available Badge')
plt.xlabel('Available Badge')
plt.ylabel('Citations')

# Show the plot
#plt.show()
