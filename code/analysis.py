from get_citations import get_citations  # Assuming get_citations.py has this function
from correlation_analysis import analyze_correlations  # Assuming correlation_analysis.py has this function

def main():
  get_citations()
  correlations_analysis(2022)
  correlations_analysis(2023)

if __name__ == "__main__":
  main()
