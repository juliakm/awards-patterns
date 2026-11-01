"""Rebuild data/public/ from the private Kaggle file.

Run this locally after changing an experiment's table, then commit the CSVs.
The site renders from those CSVs, so CI never needs the raw data.
"""

from pathlib import Path

from oscar_patterns.data import load_nominations, most_nominated_table

OUTPUT = Path("data/public")


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    nominations = load_nominations()
    most_nominated_table(nominations).to_csv(OUTPUT / "most-nominated.csv", index=False)


if __name__ == "__main__":
    main()
