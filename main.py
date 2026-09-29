import sys

sys.path.insert(0, ".")

from app.core.case_analyzer import analyze_case
from app.core.research import create_research_plan


def main():
    print("PLDA started")
    print("Core modules loaded successfully")
    print("Available:")
    print("- CASE analysis")
    print("- Research planning")


if __name__ == "__main__":
    main()
