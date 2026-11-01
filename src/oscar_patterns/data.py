"""Load the private Kaggle file and build the small tables the site publishes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_FILE = Path("data/raw/kaggle-the-oscar-award-v13/full_data.csv")

# Ceremonies 3-5 ran on a different calendar; the rest are ordinal + 1928.
EARLY_CEREMONY_YEARS = {3: 1930, 4: 1931, 5: 1932}


def ceremony_year(ceremony: int) -> int:
    """Return the calendar year a ceremony number was held."""
    return EARLY_CEREMONY_YEARS.get(ceremony, ceremony + 1928)


def load_nominations(path: Path = RAW_FILE) -> pd.DataFrame:
    """Return one row per competitive ballot entry."""
    rows = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    rows = rows[~rows["Class"].isin(["Special", "SciTech"])].copy()
    rows["Ceremony"] = rows["Ceremony"].astype(int)
    rows["ceremony_year"] = rows["Ceremony"].map(ceremony_year)
    rows["won"] = rows["Winner"] == "True"
    # The file also lists write-ins, withdrawn nominations and preliminary lists.
    # Write-ins can still win, and ceremony 2 never announced nominees, so its
    # flagged rows are the only field that year.
    unofficial = (
        rows["Note"].str.contains("NOT AN OFFICIAL NOMINATION", regex=False)
        & ~rows["won"]
        & (rows["Ceremony"] != 2)
    )
    return rows[~unofficial]


def film_totals(nominations: pd.DataFrame) -> pd.DataFrame:
    """Count each film's nominations and wins at each ceremony."""
    films = nominations[nominations["FilmId"] != ""].copy()
    # Early acting rows can credit one performance to several films.
    films["FilmId"] = films["FilmId"].str.split("|")
    films["Film"] = films["Film"].str.split("|")
    films = films[films["FilmId"].str.len() == films["Film"].str.len()]
    films = films.explode(["FilmId", "Film"])
    grouped = films.groupby(["Ceremony", "FilmId"], as_index=False)
    return grouped.agg(
        film=("Film", "first"), nominations=("won", "size"), wins=("won", "sum")
    )


def most_nominated_table(nominations: pd.DataFrame) -> pd.DataFrame:
    """Compare each ceremony's most-nominated film with its Best Picture winner."""
    totals = film_totals(nominations)
    picture = nominations[
        (nominations["CanonicalCategory"] == "BEST PICTURE") & nominations["won"]
    ]
    rows = []
    for row in picture.sort_values("Ceremony").itertuples():
        field = totals[totals["Ceremony"] == row.Ceremony]
        leaders = field[field["nominations"] == field["nominations"].max()]
        winner = field[field["FilmId"] == row.FilmId].iloc[0]
        rows.append(
            {
                "ceremony": row.Ceremony,
                "year": row.ceremony_year,
                "picture_winner": row.Film,
                "picture_winner_nominations": winner["nominations"],
                "most_nominated": " / ".join(sorted(leaders["film"])),
                "most_nominations": leaders["nominations"].iloc[0],
                "tied_for_most": len(leaders) > 1,
                "most_nominated_won": row.FilmId in set(leaders["FilmId"]),
            }
        )
    return pd.DataFrame(rows)
