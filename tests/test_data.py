"""Checks for the loader, the private Kaggle file and the published tables."""

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from oscar_patterns.data import (
    RAW_FILE,
    ceremony_year,
    film_totals,
    load_nominations,
    most_nominated_table,
)

COLUMNS = "Ceremony Year Class CanonicalCategory Category Film FilmId Name Winner"
PUBLIC_TABLE = Path("data/public/most-nominated.csv")
needs_raw = pytest.mark.skipif(not RAW_FILE.exists(), reason="raw data is private")


@pytest.fixture
def sample(tmp_path):
    rows = [
        "1\t2000\tTitle\tBEST PICTURE\tBEST PICTURE\tA\ttt1\tP\tTrue",
        "1\t2000\tTitle\tBEST PICTURE\tBEST PICTURE\tB\ttt2\tP\t",
        "1\t2000\tActing\tACTOR\tACTOR\tB|C\ttt2|tt3\tN\t",
        "1\t2000\tWriting\tWRITING\tWRITING\tB\ttt2\tW\tTrue",
        "1\t2000\tSpecial\tHONORARY AWARD\tHONORARY AWARD\tA\ttt1\tH\tTrue",
    ]
    path = tmp_path / "sample.tsv"
    path.write_text("\n".join(["\t".join(COLUMNS.split()), *rows]), encoding="utf-8")
    return load_nominations(path)


def test_honorary_awards_are_excluded(sample):
    assert "Special" not in set(sample["Class"])


def test_a_row_naming_two_films_counts_for_both(sample):
    totals = film_totals(sample).set_index("film")
    assert totals.loc["B", "nominations"] == 3
    assert totals.loc["C", "nominations"] == 1


def test_table_compares_leader_with_picture_winner(sample):
    row = most_nominated_table(sample).iloc[0]
    assert row["picture_winner"] == "A"
    assert row["most_nominated"] == "B"
    assert not row["most_nominated_won"]


def test_ceremony_years_handle_the_early_calendar():
    assert [ceremony_year(c) for c in (1, 3, 5, 6, 82, 98)] == [
        1929,
        1930,
        1932,
        1934,
        2010,
        2026,
    ]


@needs_raw
def test_raw_file_matches_its_recorded_checksum():
    manifest = pd.read_csv("data/snapshot_manifest.csv")
    recorded = manifest.loc[manifest["file"] == RAW_FILE.name, "sha256"].iloc[0]
    assert hashlib.sha256(RAW_FILE.read_bytes()).hexdigest() == recorded


@needs_raw
def test_raw_file_has_expected_contests_and_ties():
    recent = load_nominations()
    recent = recent[recent["ceremony_year"].between(2010, 2026)]
    assert recent.groupby(["Ceremony", "CanonicalCategory"]).ngroups == 403
    winners = recent[recent["won"]].groupby(["ceremony_year", "CanonicalCategory"])
    ties = winners.size()
    assert set(ties[ties > 1].index) == {
        (2013, "SOUND EDITING"),
        (2026, "SHORT FILM (Live Action)"),
    }


@needs_raw
@pytest.mark.parametrize(
    ("film", "ceremony", "nominations", "wins"),
    [
        ("Titanic", 70, 14, 11),
        ("La La Land", 89, 14, 6),
        ("Ben-Hur", 32, 12, 11),
        ("The Color Purple", 58, 11, 0),
    ],
)
def test_film_totals_match_well_known_records(film, ceremony, nominations, wins):
    totals = film_totals(load_nominations())
    row = totals[(totals["film"] == film) & (totals["Ceremony"] == ceremony)].iloc[0]
    assert (row["nominations"], row["wins"]) == (nominations, wins)


@needs_raw
def test_public_table_is_current():
    built = most_nominated_table(load_nominations())
    published = pd.read_csv(PUBLIC_TABLE)
    assert built["picture_winner"].tolist() == published["picture_winner"].tolist()
    assert built["most_nominated"].tolist() == published["most_nominated"].tolist()


def test_public_table_has_one_row_per_ceremony():
    table = pd.read_csv(PUBLIC_TABLE)
    assert table["ceremony"].tolist() == list(range(1, 99))


def test_published_finding_matches_the_table():
    """index.qmd and the experiment page quote these counts in their prose."""
    table = pd.read_csv(PUBLIC_TABLE)
    clear = table[~table["tied_for_most"]]
    before = clear[clear["year"].between(1981, 2009)]["most_nominated_won"]
    since = clear[clear["year"].between(2010, 2026)]["most_nominated_won"]
    assert (before.sum(), len(before)) == (16, 23)
    assert (since.sum(), len(since)) == (4, 13)
