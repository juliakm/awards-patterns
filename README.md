# Awards Patterns

Experiments on Oscar history for movie fans. Read them at
<https://juliakm.com/awards-patterns/>.

From 1981 to 2009, the film with the most nominations won Best Picture 16 times out
of 23, not counting ties. Since 2010, it has won 4 out of 13.
[Read the experiment](https://juliakm.com/awards-patterns/experiments/most-nominated.html).

Ideas for what's next are in [plans/experiments.md](plans/experiments.md).

## Run it

You need [uv](https://github.com/astral-sh/uv) and
[Quarto](https://quarto.org/docs/get-started/) (versions are pinned in
`.python-version` and `.quarto-version`).

```bash
uv sync --locked
export QUARTO_PYTHON="$PWD/.venv/bin/python"
quarto preview
```

The site renders from the small tables in `data/public/`, so you don't need the raw
data to preview it or run the tests.

## Add an experiment

1. Add a function that builds its table to `src/oscar_patterns/data.py`, and write
   the table in `scripts/build_tables.py`.
2. Download [The Oscar Award v13](https://www.kaggle.com/datasets/unanimad/the-oscar-award)
   into `data/raw/kaggle-the-oscar-award-v13/`, then run
   `uv run python scripts/build_tables.py`.
3. Copy `experiments/most-nominated.qmd` and rewrite it. Each page has a guess, an
   answer, one chart, and a note on how I counted.
4. Link it from `index.qmd`.

## Checks

```bash
uv run pytest
uv run ruff check .
quarto render
uv run python scripts/check_site.py
```

Tests that need the raw file are skipped without it, including in CI. Run them
locally before publishing a new table. `check_site.py` fails if the built site
contains data files, secrets, symlinks, or "oscar" in a URL path. Pushing to `main`
runs all of this and publishes to GitHub Pages.

## Data and license

Raw and working data in `data/raw/` and `data/curated/` is private and ignored by
git. Only attributed summaries and small factual tables belong in `data/public/`.
Checksums for the raw download are in `data/snapshot_manifest.csv`.

`full_data.csv` is tab-separated, and it files the merged Sound award from 2021 on
under `SOUND MIXING`.

Project code is under the [MIT License](LICENSE), which doesn't cover third-party
data. The forecast model work is preserved at the `forecast-era` git tag.
