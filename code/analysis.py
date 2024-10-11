from get_citations import get_citations  # Assuming get_citations.py has this function
from correlation_analysis import analyze_correlations  # Assuming correlation_analysis.py has this function

def main():
  get_citations()
  analyze_correlations(2022)
  analyze_correlations(2023)

if __name__ == "__main__":
  main()