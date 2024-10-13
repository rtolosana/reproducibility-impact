# reproducibility-impact
Analysis of the impact of reproducibility
In this appendix, we study the impact of reproducibility on citation count and to guarantee the reproducibility of this experiment, we provide the reproducibility artifact.


## Artifact Identification

Given the SC conference's established expertise in reproducibility, our aim here is to assess whether an impact on SC papers could be quantified through the adoption of reproducibility practices. In particular, we want to examine whether the presence of a reproducibility badge is correlated with the number of citations of the paper.

We consider the three ACM reproducibility badges that SC grants, namely:

- **ACM Artifacts Available**
- **ACM Artifacts Evaluated-Functional** (i.e. "The artifacts associated with the research are found to be documented, consistent, complete, exercisable, and include appropriate evidence of verification and validation.")
- **ACM Results Replicated** (i.e. "The main results of the paper have been obtained in a subsequent study by a person or team other than the authors, using, in part, artifacts provided by the author.")

Although, in general, a paper can obtain any of these badges, in SC practice, a paper that has the ACM Results Replicated badge also has the other two badges. A paper that has the ACM Artifacts Evaluated-Functional badge also has the ACM Artifacts Available badge. This establishes three different levels of reproducibility, each building upon the other.

These variables are binary, indicating whether a paper had a badge granted or not. We also consider continuous variables, such as an SC paper's citation count.

The full reproducibility evaluation stage, where badges are granted, has become prevalent since 2022, so we are focusing on 2022 and beyond. For 2023, the number of citations is still not significant.

## Artifact Contributions

The artifact contributes to the reproducibility of experiments in the following ways:

- **Experimental Framework**: All components necessary to recreate the experiments are provided, allowing users to reproduce the computational results reported in this appendix.
- **Data Integrity**: The artifact ensures that input data is either provided or generated to match the original experimental conditions, ensuring results can be replicated.

## Artifact Dependencies and Requirements

This section outlines the resources and environments needed to run the artifact. Our experiments do not have any specific requirements and can be executed on any modern computer. However, to streamline installation and execution, we have packaged the artifact in a Docker container. If Docker is used, its system requirements must be met.

### Supported Operating Systems

- **Linux**: 
  - Ubuntu (18.04 or higher)
  - Debian (Buster or higher)
  - Fedora (32 or higher)
  - CentOS (7 or higher)
  - RHEL (7 or higher)
  - Other Linux distributions with kernel versions 3.10 or newer
- **Windows**: Windows 10 (Pro, Enterprise, or Education editions) or Windows Server 2016/2019/2022
- **macOS**: macOS 10.15 (Catalina) or higher

### Hardware Requirements

- **CPU**: 64-bit processor architecture
- **Memory**:
  - Linux: At least 2 GB RAM
  - Windows/macOS: Minimum 4 GB RAM recommended for Docker Desktop
- **Storage**: At least 10 GB of free disk space for Docker images and containers

### Software Dependencies

The artifact relies on the following libraries:

- Python 3.9 with libraries: `pandas`, `scipy`, `matplotlib`, `seaborn`
- A Dockerfile is provided to help reproduce these experiments
- A `requirements.txt` file in the Dockerfile is provided to install these libraries

### Input Dataset

| Type of data                     | Source     | Extraction       |
|-----------------------------------|------------|------------------|
| SC Accepted Paper List            | dblp       | Python           |
| SC Citation Count                 | Open Alex  | API & Python     |
| SC Reproducibility Badge Lists    | ACM website| Manual           |

For the reasons explained, we considered SC2022. The sources of our datasets and the extraction methods are summarized in the table above. The accepted list of papers was obtained from dblp with a Python script. We used Open Alex to retrieve the citation count of each accepted paper. The reproducibility badges were retrieved manually from the ACM Digital Library, and they can be found in the artifact DOI repository.

## Artifact Installation and Execution Process

### Installation, Compilation, and Execution Process

The artifact can be installed by following these steps:

```bash
git clone https://github.com/rtolosana/reproducibility-impact/
cd artifact-directory
docker build . -t repro-impact
docker run -it repro-impact bash
python get_citations.py
python correlation_analysis.py
```
Estimated installation and execution time: ~1 minute.

## Reproducibility of Experiments

The artifact facilitates the reproduction of the experiments as described in the paper:
### Experiment Workflow
The artifact facilitates the following experiment workflow. The first step involves retrieving the citation counts of papers published in SC. A file, dataset/dblp-urls-sc.txt, contains the list of accepted papers for a specific SC year, along with their DOIs. The script get_citations.py parses this file and generates a CSV file with each paper and its corresponding citation count, using data retrieved from Open Alex. 

Subsequently, as a second step to be executed, the script correlation_analysis.py performs a correlation analysis on the collected data and on the provided badges. We designed the experiments in Python, using pandas, scipy, matplotlib, and seaborn. We have undertaken various analyses to examine the correlation between the binary variable indicating the presence of a specific reproducibility badge and the citation counts. We considered 4 types of groups with the papers: papers with badge “artifact available”, papers with badge “artifact functional”, papers with badge “results replicated”, and papers with no badge. Given that having a badge is binary (i.e. either having it or not) and the citation count is continuous, we made use of the point-biserial correlation analysis. The point-biserial correlation coefficient quantifies the strength and direction of the linear relationship between two variable types. Additionally, we also conducted a Kruskal-Wallis test between each of four groups and the citation counts. We also conducted the two-sample Kolmogorov-Smirnov between each pair of the four groups.

## Expected Results

## Experiments for SC2022, citations as of November 2023

### Kolmogorov-Smirnov (KS) Tests

The following KS tests were conducted to compare the distributions of citation counts between different badge categories. The null hypothesis asserts that there is no significant difference between the distributions of the two groups being compared. In other words, any observed differences in their data are due to random chance rather than a true effect or relationship.

- **KS Test between Badge Artifact Available and Badge Artifact Functional:**  
  Test Statistic = 0.0411, P-value = 0.99999998  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Available and Badge Results Replicated:**  
  Test Statistic = 0.0493, P-value = 0.99999964  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Available and No Badge:**  
  Test Statistic = 0.1166, P-value = 0.93361  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Functional and Badge Results Replicated:**  
  Test Statistic = 0.0618, P-value = 0.99995  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Functional and No Badge:**  
  Test Statistic = 0.1578, P-value = 0.71739  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Results Replicated and No Badge:**  
  Test Statistic = 0.1175, P-value = 0.96344  
  _Fail to reject the null hypothesis. The distributions are similar._

### Kruskal-Wallis Test

This test was conducted to compare the citation counts between papers with a replicable badge and those with no badge. The null hypothesis is that the two groups have the same distribution.

- **Kruskal-Wallis Test for Replicable vs No Badge:**  
  Statistic = -0.06891, P-value = 0.5235  
  _Fail to reject the null hypothesis. There is no significant difference between the groups._

### The Point-biserial Correlation Tests

The point-biserial correlation measures the relationship between a binary variable (with two categories) and a continuous variable (numeric data like citation count). In this case, the binary variable is whether a paper has the Replicable badge (1 = Yes, 0 = No), and the continuous variable is the citation count of papers. The point-biserial correlation analysis how strongly having the replicable badge is associated with citation count.

- **Point-biserial correlation:**  
  Correlation = -0.0689, P-value = 0.5235  
  _The correlation is weak and not statistically significant._

## Experiments for SC2022, citations as of October 2024

Overall, we could not find significant evidence that reproducibility has an impact on the number of citations. A detailed description of the statistical analysis can be found in Appendix I. This result is similar to the one in [Winter et al. (2022)](winter2022retrospective). However, some work found some evidence that the reproducibility practices can have a positive impact on citation counts ([Raff et al. (2023)](raff2023does), [Heumüller et al. (2020)](heumuller2020publish)). Nevertheless, it is clear that, in addition to having a reproducibility badge or not, there are many other factors that lead a researcher to reference other publications. It is clear, though, that the impact of _irreproducibility_ of research is more significant, and it can be found in the productivity of third-party researchers and in the progress of the whole research community, as well as in terms of trustworthiness of science.

### Kolmogorov-Smirnov (KS) Tests

The following KS tests were conducted to compare the distributions of citation counts between different badge categories. The null hypothesis asserts that there is no significant difference between the distributions of the two groups being compared. In other words, any observed differences in their data are due to random chance rather than a true effect or relationship.

- **KS Test between Badge Artifact Available and Badge Artifact Functional:**  
  Test Statistic = 0.0517, P-value = 0.99998  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Available and Badge Results Replicated:**  
  Test Statistic = 0.0780, P-value = 0.99634  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Available and No Badge:**  
  Test Statistic = 0.1154, P-value = 0.93754  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Functional and Badge Results Replicated:**  
  Test Statistic = 0.0595, P-value = 0.99998  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Artifact Functional and No Badge:**  
  Test Statistic = 0.1311, P-value = 0.88180  
  _Fail to reject the null hypothesis. The distributions are similar._

- **KS Test between Badge Results Replicated and No Badge:**  
  Test Statistic = 0.1154, P-value = 0.96835  
  _Fail to reject the null hypothesis. The distributions are similar._

### Kruskal-Wallis Test

This test was conducted to compare the citation counts between papers with a replicable badge and those with no badge. The null hypothesis is that the two groups have the same distribution.

- **Kruskal-Wallis Test for Replicable vs No Badge:**  
  Statistic = 0.1408, P-value = 0.7075  
  _Fail to reject the null hypothesis. There is no significant difference between the groups._

### The Point-biserial Correlation Tests

The point-biserial correlation measures the relationship between a binary variable (with two categories) and a continuous variable (numeric data like citation count). In this case, the binary variable is whether a paper has the Replicable badge (1 = Yes, 0 = No), and the continuous variable is the citation count of papers. The point-biserial correlation analysis how strongly having the replicable badge is associated with citation count.

- **Point-biserial correlation:**  
  Correlation = -0.1212, P-value = 0.2606  
  _The correlation is weak and not statistically significant._

## Result Analysis

According to these tests, we fail to reject the null hypothesis; there is no statistically significant evidence to suggest that the citation counts differ between the badge categories (No Badge, Available, Functional, Replicable). In other words, the distribution of citations across the different badge groups and the group without a badge is likely similar.

## Other Notes

This appendix will be periodically updated as improvements are made to the artifact to ensure continued reproducibility of the experiments.
