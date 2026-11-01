# Awards Patterns

An article-first film awards analysis project with reusable Python tools and a
static Quarto website. This repository currently provides the project foundation,
not an ingestion pipeline or a trained forecasting model.

The configured public website is <https://juliakm.com/awards-patterns/>.
GitHub Pages inherits the account's existing `juliakm.com` domain; the
`juliakm.github.io/awards-patterns/` address redirects there. This project's HTTPS
setting is enabled, without changing the account's other sites.
The homepage, redirect, CSS, and JavaScript were verified over HTTPS on
November 1, 2026. GitHub Actions passed all 53 committed tests, lint/format
checks, artifact validation, and deployment. See
[publication evidence](artifacts/public-release-audit.json).

## Local setup

Use Python **3.12.16** (`.python-version`), uv **0.13.6**, locked dependency
versions in `uv.lock`, and Quarto **1.10.20** (`.quarto-version`).
Install uv from its
[official releases](https://github.com/astral-sh/uv/releases) and Quarto from its
[official releases](https://github.com/quarto-dev/quarto-cli/releases).
Workspace-local tools under `.tools/` are ignored.

This combination was validated on macOS ARM64 with `uv sync --locked`,
package/dependency imports, six CLI tests, Ruff checks/formatting, and
`quarto check` including its Jupyter engine render. TinyTeX and R are not needed
for the current HTML site.

This workspace uses `.tools/uv/uv`, `.tools/quarto/bin/quarto`, and uv-managed
Python under `.tools/python/`. After installing the pinned official tools there,
configure the paths below from the repository root. On other platforms, use the
matching official release archives or installed binaries on `PATH`.

```bash
export PATH="$PWD/.tools/uv:$PWD/.tools/quarto/bin:$PATH"
export UV_PYTHON_INSTALL_DIR="$PWD/.tools/python"
export UV_CACHE_DIR="$PWD/.tools/uv/cache"
export QUARTO_PYTHON="$PWD/.venv/bin/python"
uv python install
uv sync --locked
uv run --locked oscar-data --help
uv run --locked oscar-data --version
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
quarto check
quarto render
```

The package is available to notebooks as `import oscar_patterns`. Use
`uv run --locked jupyter lab` for notebook authoring. pandas and PyArrow support
tabular/Parquet validation; DuckDB supports SQL analysis; scikit-learn supports
the planned modeling experiments; Plotly supports static-site interactive
charts; httpx supports permission-aware source inspection. Jupyter provides the
notebook runtime. These dependencies do not imply a finished analysis pipeline.

## Available interface and proposed pipeline

`oscar-data` currently shows help with no arguments and supports `--help` and
`--version`. Unknown commands fail rather than pretending to process data.
Ingestion, validation, feature building, backtesting, training, and public export
are **proposed future work**, not runnable subcommands.

## Data and publication boundaries

Consult `data/source_registry.csv` for source-specific permissions and unresolved
acquisition requirements. Obtain any necessary access or permission before
downloading private or restricted inputs. Keep credentials in ignored local
environment files, never in notebooks or committed configuration.

`data/raw/`, `data/curated/`, models, and secrets are local/private and ignored;
ignore rules are a safeguard, not a substitute for reviewing staged files.
Only explicitly approved, attributed extracts belong in `data/public/`.
Published pages must use approved public data, not private inputs. Commit
reviewed Quarto `_freeze/` execution results; `_site/` is generated and ignored.
Check notebook outputs and frozen results for restricted data before committing.

Public code and source data have separate permissions. Any repository code
license does **not** grant rights to third-party datasets, source text, images,
or restricted notebook outputs. Public repository availability alone grants no
additional data redistribution rights.

Project code is licensed under the [MIT License](LICENSE). Third-party source
material is not covered by this license; follow the source registry's separate
permission decisions before acquisition or publication.

## Offline checks and deployment

The Actions workflows restore the locked environment, run tests and Ruff, and
render only the approved, nonexecuting homepage. Only the guarded `_site/`
artifact is uploaded to GitHub Pages; acquisition and training are never part
of publishing.

```bash
uv run --locked python scripts/validate_publication.py --check-inputs
quarto render index.qmd --no-execute
uv run --locked python scripts/validate_publication.py
```

The publication guard rejects unapproved pages, downloads, symlinks, private
files, and case-insensitive `oscar` paths. Adding an article or changing Quarto
assets requires reviewing and updating the publication allowlist.

The source audit is complete, but primary dataset acquisition remains blocked
on provenance/permission review. Its notebook reads committed metadata offline;
no actual source dataset or trained model is included.
