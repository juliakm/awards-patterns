# Oscar analytics and winner prediction: execution plan

Created October 31, 2026. Target public launch: January 14, 2027, with a one-week buffer before the January 21 nominations announcement.

## 1. Project brief and decisions

Build an article-first website for film and data enthusiasts, backed by reproducible Python analysis and an honestly evaluated Oscar winner model. The project should be fun while demonstrating analyst/data-science skills through data modeling, SQL, statistical reasoning, machine learning, testing, and clear communication.

| Decision | Agreed direction |
|---|---|
| Historical scope | Film eligibility years beginning in 2009; Oscar ceremonies beginning in 2010 |
| Categories | All competitive categories, including shorts and documentaries; exclude honorary and special awards |
| Website | Mostly articles with interactive charts, rather than a full dashboard |
| Authoring | Jupyter notebooks, published through Quarto |
| Core tools | Python, pandas, SQL/DuckDB, scikit-learn, Plotly, pytest, Ruff, GitHub Actions |
| Repository | Private; publish directly to public GitHub Pages using GitHub Pro |
| Public technical evidence | Selected notebook code, methodology, evaluation results, and model documentation |
| Prediction target | Winners among announced Oscar nominees, not nomination prediction |
| Priority | A credible richer model takes precedence over publishing all three initial articles |
| Capacity | Approximately 10 hours/week; free data preferred, paid APIs considered only if necessary |

**Launch contract:** an all-category historical dataset, a working public site, one substantive article, reproducible chronological model evaluation, and an inference pipeline that can accept the 2027 nominees. Every category gets a coverage/status entry; not every category needs a defensible learned model.

**Not required before launch:** three finished articles, a custom domain, live Python queries, visitor accounts, exhaustive precursor coverage, automated scraping of every prediction archive, or separately tuned models for every category.

Quarto is the publishing layer, not the main portfolio skill claim. It supports Python/Jupyter and article-style websites; there is no verified usage ranking in this plan. Emphasize the mainstream analytical and engineering tools in the site's methodology and project summary.

## 2. Release scope and editorial roadmap

### First three stories

1. **Who predicts which categories well?** Compare individual pundits and consensus entries from Awards Daily, showing accuracy, denominators, shared-year comparisons, and uncertainty.
2. **Which precursor awards actually help?** Compare category-specific precursor agreement and test whether those signals improve out-of-time predictions.
3. **Does box office matter?** Explore revenue versus winning among nominees, clearly distinguishing descriptive lifetime revenue from information available before an Oscar forecast.

Keep repeat-nominee questions, including Meryl Streep's nomination-to-win conversion, in the backlog. For career-history features, retain earlier Oscar records even though the main analytical window starts in 2010.

For January, publish whichever of stories 1–2 has the strongest verified data. Awards Daily accuracy may need to follow the precursor article if historical timestamps or reuse permissions are unresolved. A documented negative or inconclusive result is a valid finding; do not require a surprising pattern.

### Public pages

- **Home:** project premise, featured article, current data coverage, and last update.
- **Articles:** accessible narratives with Plotly hover, zoom, legend toggles, and limited precomputed dropdowns.
- **Predictions:** model-readiness and historical backtest page before nominations; actual 2027 probabilities only after the nominee list is verified.
- **Methods and data:** schemas, sources, missingness, temporal cutoffs, reproducibility instructions, and model card.
- **About:** purpose, analytical skills demonstrated, and selected public notebook/code examples.

Static interactivity means JavaScript operating on published data. Python runs during analysis/build, not in a visitor's browser. Do not use Python-backed notebook widgets as if they will work on GitHub Pages.

### Where Streamlit fits

Consider Streamlit as a later companion application, not a second launch requirement. It provides useful Python app-building experience and suits a category explorer or a prediction sandbox where visitors change inputs and rerun inference.

Keep Quarto for the article-first site, published notebooks, and stable forecast record. Plotly already provides interactivity without a running Python service. Streamlit becomes worthwhile when visitors need arbitrary queries or computations that precomputed charts cannot provide.

Streamlit requires a Python server and separate hosting; it cannot run on GitHub Pages. Link to a separately hosted app, reuse the same `oscar_patterns` package and approved data/model artifacts, and verify the hosting provider's current private-repository support, pricing, and resource limits before deployment. Clearly separate hypothetical sandbox results from frozen official forecasts.

## 3. Source research and acquisition decisions

The following reflects checks made October 31, 2026. A documentation page being reachable does not establish that an API works, a dataset is complete, or redistribution is permitted.

| Source | Findings and proposed use | Required next check |
|---|---|---|
| [Academy Awards database](https://awardsdatabase.oscars.org/) | Authoritative reference for nominees, winners, category names, and disputed records | Establish a permitted verification workflow; do not assume a public bulk API or open-data license |
| [Kaggle: unanimad/the-oscar-award](https://www.kaggle.com/datasets/unanimad/the-oscar-award) | Page advertises 1927–2026 coverage; preferred first bulk-data candidate | Download a pinned version; verify actual columns, all competitive categories, 2026 completeness, and dataset license |
| [Oscarbase](https://oscarbase.com/) and [API docs](https://api.oscarbase.com) | Docs describe nomination, ceremony, film, and person IDs, with IMDb/TMDB links; useful enrichment/cross-check candidate | Both `year=2026&limit=2` and `year=2010&limit=1` nomination requests returned HTTP 500 during research. Recheck health, completeness, limits, licensing, and persistence of IDs before depending on it |
| [leandcesar/theawards](https://github.com/leandcesar/theawards) | README advertises 1927–2023; repository includes `app/data.json`; declared repository license is Apache-2.0; last push was May 2023 | Inspect actual JSON coverage and provenance. Treat as a historical fallback, not the current-season source; repository licensing does not automatically clear upstream content |
| [Awards Daily main chart supplied in interview](https://www.awardsdaily.com/main/main-predictions-2026/) | Page links to earlier main-category and separate crafts/shorts charts; fetched text did not expose a current prediction table | Locate the actual chart, verify year and publication timing, inspect format, and establish permission/terms for extraction and publication |
| [Awards Daily `/main-predictions-2010/`](https://www.awardsdaily.com/main/main-predictions-2010/) | Accessible table contains *The King's Speech* and *The Social Network*: it corresponds to the 2011 ceremony, despite the URL label. Includes explicitly described protest picks | Audit every page by film/ceremony, not URL year; classify protest picks separately and document transcription corrections |
| [DGA history](https://www.dga.org/Awards/History), [PGA awards](https://producersguild.org/awards/), [SAG archive](https://www.sagawards.org/awards/nominations-and-recipients), [BAFTA database](https://awards.bafta.org/), [Golden Globes](https://goldenglobes.com/winners-nominees/) | Primary precursor references; start with DGA, PGA, and acting guild awards, then Globes and BAFTA where feasible | Audit ceremony dates, nominee/winner coverage, category mappings, and access/reuse terms. Historical URLs and organizational naming can change |
| [TMDB API](https://developer.themoviedb.org/docs/faq) | Official FAQ permits free noncommercial use with required attribution; suitable for film metadata and exploratory revenue | Register a key; check revenue coverage and current terms. API lifetime revenue is not a historical as-of revenue series |
| [Wikidata](https://www.wikidata.org/wiki/Wikidata:Licensing) | Candidate for CC0 structured identifiers and supplementary facts | Verify actual award completeness and temporal meaning; do not substitute incomplete community records for Academy verification |

**Primary recommendation:** begin with a licensed, versioned Oscar CSV, validate against Academy records, and store it locally. Use APIs to enrich that snapshot rather than making the project depend on a live third-party awards API.

**Box-office recommendation:** start with TMDB for descriptive analysis. Historical pre-cutoff grosses need a separate permitted source with dated observations. Defer paid data until a small sample demonstrates that it would materially improve the project. Do not assume Box Office Mojo permits scraping or bulk republication.

### First source-audit deliverable

Create `data/source_registry.csv` and `data/coverage.csv`, plus a short source-audit notebook.

- [ ] For each source, record URL, publisher, version/commit where applicable, retrieval date, fields, year convention, license/terms link, attribution, and publication restrictions.
- [ ] Assess all 2010–2026 ceremony/category combinations against an independent expected-category registry.
- [ ] Spot-check 2010, 2011, 2021, and 2026 to expose year labels, category transitions, and recent additions.
- [ ] Inspect Awards Daily pages from at least an early, middle, and recent season, including a crafts/shorts page.
- [ ] Classify prediction records as timestamp-verified, uncertain, missing, protest/nonstandard, or unusable.
- [ ] Select the primary Oscar source and document a fallback by the end of week 2.

Avoid copying articles, images, biographies, or full third-party prediction charts into the public site without appropriate rights. Use permitted factual extracts, attribution, and derived summaries. Keep raw snapshots only where permitted; a private repository is not a waiver of source terms.

## 4. Data model and quality rules

Use immutable source snapshots where permitted, curated Parquet tables, and DuckDB SQL queries over those files. Keep one curated truth rather than maintaining unrelated CSV, notebook, and website versions.

| Table | Grain and essential fields |
|---|---|
| `ceremonies` | One Oscar ceremony: ID, ceremony year/date, eligibility label/window, nomination announcement date |
| `categories` | Stable category ID, source labels, category family, competitive flag, active ceremony range |
| `category_rules` | Ceremony/category-specific nominee expectations, voting/rule regime, transition notes |
| `films` | Internal film ID, title, release date, IMDb/TMDB IDs where verified |
| `people` | Internal person ID, credited name, external IDs where verified |
| `entries` | One Oscar ballot entry: entry ID, ceremony, category, film if applicable, song/work title if applicable, winner flag |
| `entry_people` | Entry/person bridge with credit role; multiple recipients must not multiply the number of ballot entries |
| `precursor_entries` | Award event/category/entry, nominee and winner status, linked Oscar entity, result announcement date, source |
| `predictions` | Predictor/ceremony/category/snapshot, selected entry, publication time, time-verification status, record type, source |
| `film_observations` | Film/field/as-of observation: revenue or other mutable measure, currency, scope, effective date, retrieval date, source |
| `feature_snapshots` | One Oscar entry at one forecast cutoff: feature values, availability indicators, provenance, outcome stored separately |

Track `retrieved_at` separately from `published_at` or `available_at`: downloading a fact today does not prove it was known at an old forecast date.

### Non-negotiable invariants

- Distinguish ceremony year from film eligibility year and precursor event year. Do not derive eligibility solely as ceremony year minus one; exceptional windows exist.
- Represent a nomination as a ballot entry, not simply a film or credited person. Two nominated songs from one film are different entries.
- Join acting/directing awards using person plus film and category context where needed; join film-level awards using verified film IDs.
- Resolve ambiguous titles and people through a reviewed alias/crosswalk table. Fuzzy matches propose candidates; they do not silently become truth.
- Preserve original category labels. Map renamed categories while keeping genuinely different categories distinct.
- Account for the 2021 ceremony's Sound consolidation; do not pretend earlier Sound Mixing and Sound Editing are identical to the merged award.
- Track Best Picture field-size/rule changes instead of assuming ten nominees throughout the period.
- Include Casting, introduced at the 2026 ceremony, but label its learned forecasts as unsupported/experimental given the very short history.
- Validate expected nominee counts from the rule registry, not a universal five-nominee assumption.
- Support genuine ties and exceptional outcomes. Standard races normally have one winner; explicitly documented multi-winner races must not fail an unconditional one-winner assertion.
- Treat missing budget/revenue and source sentinel zeroes as unknown where appropriate, not evidence of no revenue.
- Build earlier-career Oscar counts using records before the analytical window when available, always ending before the forecast cutoff.

Tests should catch duplicate ballot entries, broken bridges, unresolved joins, incorrect year mappings, unexplained category gaps, and future-dated features.

## 5. Python/notebook/static-site architecture

Recommended structure to create during implementation:

```text
OscarData/
  plans/oscar-analytics-project-plan.md
  pyproject.toml
  uv.lock
  README.md
  _quarto.yml
  src/oscar_patterns/
    cli.py
    ingest.py
    normalize.py
    features.py
    evaluate.py
    predict.py
  data/
    source_registry.csv
    coverage.csv
    raw/                   # permitted snapshots; usually ignored
    curated/               # Parquet tables; usually ignored
    public/                # explicitly approved publication extracts
  notebooks/
    00_source_audit.ipynb
    01_category_history.ipynb
    02_pundit_accuracy.ipynb
    03_precursor_signals.ipynb
    04_box_office.ipynb
    05_model_backtest.ipynb
  site/
    index.qmd
    about.qmd
    methods.qmd
    predictions.qmd
    articles/
  tests/
  artifacts/
    metrics/
    models/                # ignored; local/private artifacts
    forecasts/
  .github/workflows/
    checks.yml
    publish.yml
```

Notebooks explore and explain; package functions perform reusable ingestion, matching, feature construction, fitting, and evaluation. Test those functions rather than burying essential logic in notebook cells.

Render selected `.ipynb` files directly through Quarto when publishing technical notebooks. Use `.qmd` articles for tighter storytelling and call the same package functions or consume the same approved result tables. Do not duplicate the core analysis in two independent implementations.

Configure the root Quarto project with explicit render targets: public `site/` pages and only selected notebooks. Publish artifacts to `_site/`; do not make the whole repository a website resource directory.

Use DuckDB for joins, coverage checks, and analytical aggregations; use pandas for transformation and plotting. Add dependencies only when a concrete task needs them. Avoid a backend, cloud database, orchestration framework, and deep learning for this release.

### Environment/bootstrap checklist

The following commands are for the later implementation phase; this plan does not create or initialize the application.

```bash
cd /Users/juliakm/Code/OscarData
git init -b main
uv init --package --name oscar-patterns --python 3.12
uv add pandas pyarrow duckdb scikit-learn plotly jupyter httpx
uv add --dev pytest ruff
uv sync
quarto check
```

Install `uv` and the separate Quarto CLI through their official installers if absent. Keep Python and Quarto versions pinned to a tested combination in local setup and CI.

- [ ] Check for existing files before scaffolding; preserve this plan and other work.
- [ ] Adjust the generated Python package to `oscar_patterns` and add an `oscar-data` console entry point in `pyproject.toml`.
- [ ] Set `.gitignore` before the first commit: environments, secrets, raw/curated datasets, model binaries, caches, and `_site/`.
- [ ] Create README with setup, pipeline commands, source requirements, and public-site URL.
- [ ] After reviewing staged files, create the private GitHub repository and connect the local repository.
- [ ] Confirm GitHub Pro enables Pages for the private repository.

### Pipeline interface to implement

These are proposed commands, not existing tools:

```bash
uv run oscar-data ingest --source oscar-csv
uv run oscar-data validate
uv run oscar-data build-features --cutoff-policy nominations-plus-24h
uv run oscar-data backtest --config configs/backtest.toml
uv run oscar-data export-public
uv run pytest
uv run ruff check .
uv run ruff format --check .
quarto render --execute
```

Add the referenced backtest configuration when the modeling phase begins. Provide equivalent Python imports for notebook use. Commands should fail clearly on unavailable sources or invalid data, rather than quietly publishing stale output.

## 6. Prediction research design

### Target and information policy

Produce probabilities for each nominee in each ceremony/category contest. Train only on completed historical contests. Predicting an announced nominee's win is different from predicting a film's nomination.

Define two forecast products and keep their evaluation separate:

| Product | Cutoff | Allowed information |
|---|---|---|
| Initial forecast | Nomination announcement + 24 hours | Confirmed nominees and only information known by that cutoff |
| Updated forecast | Explicit later timestamp, such as after a precursor event | Additional results/predictions available by that timestamp |

Use the same cutoff policy for historical evaluation and deployment. For 2027, label the initial release as a January 22 forecast, not a prediction made before nominations.

If accurate historical announcement timestamps cannot be established for a feature, exclude it from strict backtests or label the experiment retrospective and non-deployable. A final pundit chart cannot be used as a nomination-day feature simply because it is archived.

### Candidate features

Start with features that can be reconstructed reliably:

- Category/family and nominee field size; ceremony-specific category rules.
- Same-season total Oscar nominations for the film, available after nominations.
- Prior Oscar nominations/wins for the credited people and film's studio/distributor where reliable.
- Category-mapped precursor nominations and wins known by the cutoff.
- Time-verified pundit consensus share and disagreement, only if the source audit supports them.
- Stable film metadata such as genre and runtime; carefully dated release information.

Revenue, budgets, critic scores, and popularity measures are optional. Current lifetime revenue, current review aggregates, TMDB popularity, retrospective biographies, and post-Oscar honors must not leak into historical forecasts. Static attributes that were known then still need verified definitions and coverage.

For each precursor, distinguish **not nominated**, **event not yet held**, **category not applicable**, and **source missing**. Map DGA to directing, PGA to picture, and acting guild awards to their corresponding acting contests; do not create a universal “won a guild award” signal.

### Models and evaluation

1. Establish a uniform `1 / nominee_count` probability baseline, plus a documented precursor-rule baseline and time-valid pundit baseline where coverage permits.
2. Fit a pooled regularized logistic model with category/family features. Compare a scikit-learn histogram gradient-boosting challenger on the same folds.
3. Convert positive entry scores into within-contest probabilities summing to one; apply exactly the same transformation during evaluation and inference. This is a practical contest-probability approximation, not proof of calibration.
4. Add category-specific models only when enough historical contests and stable signals support them. Compare against the pooled model rather than assuming specialization is better.
5. Select the final approach using chronological validation, calibration, simplicity, and deployment-time feature availability—not just total winner accuracy.

Suggested split:

- Initial training window: ceremonies 2010–2016.
- Development: expanding-window one-season-ahead validation for 2017–2023.
- Untouched final test: 2024–2026, predicted one season at a time using only earlier seasons; do not revise choices in response to these results.
- After reporting the frozen test result, refit the selected approach on eligible 2010–2026 data for 2027 inference.

All preprocessing, imputation, feature selection, tuning, and any calibration happen inside the appropriate training window. Keep every contest and ceremony together; never randomly split nominee rows. If adding calibration, use earlier-year out-of-fold predictions, not the final test or in-sample fitted scores.

Report:

- Top-choice winner accuracy, with per-category race counts.
- Contest-level log loss and multiclass Brier score on normalized probabilities.
- Calibration plots where sample size permits, plus year-to-year variation.
- Macro category summaries and coverage, so a pooled aggregate does not hide weak categories.
- Matched-contest comparisons against each applicable baseline.
- Feature-group ablations: precursors, career history, pundits, and optional revenue.

Bootstrap uncertainty by ceremony, not independently by nominee. Explain that 17 completed seasons provide limited evidence even though there are many nominee rows. Individual-category estimates are especially noisy.

For true tied historical winners, declare the metric policy before evaluation: top-choice accuracy accepts any official winner; probability metrics can use an equal target distribution across official winners. Show a sensitivity result excluding those contests. Do not quietly assign a single winner.

**Model selection rule:** prefer the regularized model unless the challenger offers a consistent development-period improvement in probability quality without meaningful calibration or coverage regressions. Publish an honest baseline-only result if neither model adds value. Record the numeric selection criteria before opening the final test.

**Sparse-category policy:** publish status, coverage, and a transparent baseline or explicitly experimental forecast for categories with insufficient history, especially Casting. An all-category website is not a claim of validated ML in all categories.

### Model artifacts

- [ ] Versioned feature specification and timestamp rules.
- [ ] Backtest predictions with entry IDs, cutoffs, model version, and data snapshot ID.
- [ ] Metrics by year/category, baseline comparisons, and calibration figures.
- [ ] Model card documenting intended use, limitations, source gaps, and probabilistic interpretation.
- [ ] A dry-run inference command against a historical nominee list.
- [ ] Frozen initial 2027 forecast and separate timestamped later updates.

## 7. Analysis standards

For Awards Daily accuracy, preserve predictor identity and organization changes without combining different people. Separate the site's published consensus from a consensus calculated from available contributors. Exclude consensus rows from contributor vote counts.

Show correct picks divided by observed picks, category coverage, shared-season comparisons, and missingness. Do not rank a pundit with two picks above one with a long history without warning. Compare the same contests when claiming one predictor outperforms another. Treat protest picks as a separate analysis/sensitivity case.

For precursors, show the denominator explicitly: agreement across seasons where the precursor result was available and relevant. Account for a precursor winner who is not an Oscar nominee. The two Golden Globe film/acting divisions are not interchangeable with one Oscar contest. Distinguish descriptive agreement from incremental predictive value.

For box office, describe domestic versus worldwide gross, currency, missingness, and release timing. Use log scaling where helpful and consider inflation for comparisons over time. Lifetime gross can partly reflect an Oscar win; it cannot establish that gross caused the win. Among-nominee analysis does not answer which films get nominated.

Avoid causal claims from correlations, overconfident category rankings, and cherry-picking dozens of exploratory questions without labeling them exploratory.

## 8. Delivery schedule: approximately 110 planned hours

The calendar provides roughly 11 working weeks before the January 14 target. Reserve January 15–20 for fixes and preparation, not new features.

| Window | Budget | Deliverable and completion gate |
|---|---:|---|
| Nov 2–8 | 10 h | Initialize package and private repository; deploy a minimal Quarto page. Public URL works while source remains private |
| Nov 9–15 | 10 h | Complete source audit and pick primary/fallback sources. Acquire a pinned Oscar snapshot; licensing blockers are explicit |
| Nov 16–22 | 10 h | Normalize all-category 2010–2026 data, category rules, aliases, and bridges. Independent coverage checks and core data tests pass |
| Nov 23–29 | 10 h | Build first precursor dataset and dated feature snapshots; implement uniform and rule baselines. Prove no future features in a historical dry run |
| Nov 30–Dec 6 | 10 h | Run pooled regularized model with chronological folds; produce initial evaluation notebook and coverage report |
| Dec 7–13 | 10 h | Run boosted-tree challenger and feature ablations. Audit Awards Daily sample further only if acquisition is on track |
| Dec 14–20 | 10 h | Complete development comparisons; freeze feature/model/metric decisions. Draft one strong article from validated findings |
| Dec 21–27 | 10 h | Run untouched test, write model card, and refit deployment model. Use holiday slack explicitly if actual capacity drops |
| Dec 28–Jan 3 | 10 h | Publish article, methods, selected notebook, and historical prediction results. Automate checks and deployment |
| Jan 4–10 | 10 h | End-to-end historical season rehearsal, publication audit, mobile/chart checks, and inference/runbook fixes |
| Jan 11–14 | 10 h | Release freeze and launch. Confirm nominee import workflow and source-monitoring checklist |
| Jan 15–20 | Buffer | Repair only; verify Academy schedule and incoming nomination-day sources |

### Scope-cut checkpoints

- **Nov 15:** if the primary source is blocked, use a permitted historical fallback plus curated recent records; disclose incompleteness rather than claiming full coverage.
- **Nov 29:** if timestamped pundit or box-office data is unavailable, remove it from the launch model. Continue with stable metadata, career history, and dated precursors.
- **Dec 13:** if precursor collection is consuming the schedule, stop expanding award sources and articles. Finish evaluation on the verified feature set.
- **Jan 3:** freeze features. Cut additional stories, advanced filters, and custom branding before cutting temporal validation, source disclosure, or deployment rehearsal.

Full competitive-category coverage is a launch goal, not something to claim if the source audit reveals unresolved gaps. Publish actual coverage and explicitly mark any reduced release.

## 9. Hosting, automation, and publication controls

Use a project Pages URL such as `https://juliakm.github.io/oscar-patterns/`; the final path depends on the repository name.

GitHub documents that Free accounts require a public repository for Pages. The agreed setup uses GitHub Pro with a private source repository and a public site. Private-repository Actions usage can incur charges beyond included allowances; run expensive modeling locally and keep deployment small.

Configure Pages to use GitHub Actions. Have the workflow:

1. Check out the private source repository and install pinned Python/Quarto versions.
2. Restore the locked Python environment and run tests, Ruff, and public-data validation.
3. Render only approved publication targets using deterministic, already prepared inputs.
4. Upload only `_site/` through the Pages artifact/deploy actions.
5. Verify the deployed home page and an article URL return successfully.

Keep acquisition/training separate from deployment. Do not automatically retrain a model on each push. If notebooks execute in CI, they must use fixed inputs and need no live API. Otherwise execute locally and publish approved saved outputs; record the data/artifact version so cached results do not silently become stale.

- [ ] Store API keys in local environment variables or GitHub secrets, never notebook cells or commits.
- [ ] Ensure copied resources, HTML, notebook downloads, logs, and Plotly payloads contain only material intended for public release.
- [ ] Omit raw source data, model binaries, environment files, and unselected notebooks from the site artifact.
- [ ] Show selected code through collapsible cells and link only approved notebook downloads.
- [ ] Include source attribution and, if using TMDB, its approved logo and required non-endorsement notice.
- [ ] Test project-subpath links, chart assets, phone-sized layouts, keyboard access, readable legends, and textual chart summaries.
- [ ] Set visible data/model update timestamps and a “known limitations” section.

## 10. Nomination-day and Oscar-season runbook

The Academy's linked calendar lists nominations for January 21, 2027 and the ceremony for March 14, 2027. Direct Academy calendar/press fetches returned HTTP 403 during research; independently recheck the official schedule before executing this runbook because dates can change.

- **Before Jan 21:** confirm the import format, category registry, model artifact, cutoff policy, and baseline fallback. Rehearse with a completed historical season.
- **Jan 21:** import the official nominee list; verify every category, recipient bridge, work/song identity, and field size. Do not infer nominees from pundit picks.
- **Jan 22, after the defined 24-hour cutoff:** build the initial feature snapshot, validate availability dates, run inference, and check per-contest probabilities and coverage.
- **Publication:** save an immutable forecast file with model/data versions, publication timestamp, and category reliability status. Publish probabilities, not guaranteed outcomes.
- **Later precursor events:** issue separately versioned updates. Keep the initial forecast visible and evaluate each snapshot under its own information policy.
- **After March 14:** ingest verified results, score frozen forecasts, compare baselines, and publish a postmortem including surprises and failures.

Never overwrite an earlier forecast and later report the updated version as if it were the original.

## 11. Definition of done

- [ ] A clean environment can recreate curated data and results from documented, permitted inputs or approved snapshots.
- [ ] Coverage is measured against expected competitive categories; all gaps and category transitions are visible.
- [ ] Tests cover ballot-entry deduplication, ambiguous year/title mapping, temporal leakage, normalization, and historical inference.
- [ ] Model comparison uses chronological validation and an untouched final test; probabilities, baseline comparisons, and uncertainty are published.
- [ ] At least one article has an explicit question, auditable denominator, interactive chart, defensible interpretation, and caveats.
- [ ] Selected notebooks expose useful technical work while the full repository remains private.
- [ ] The deployed site works at its actual public URL and does not depend on a visitor-side Python service.
- [ ] The publication artifact is audited for unintended data/code exposure.
- [ ] A historical end-to-end rehearsal passes before 2027 nominee ingestion.

## 12. References and unresolved decisions

Implementation references:

- [Quarto overview](https://quarto.org/) and [GitHub Pages publishing](https://quarto.org/docs/publishing/github-pages.html).
- [GitHub: creating a Pages site, private-repository constraints, and public visibility](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
- [TMDB API FAQ and attribution](https://developer.themoviedb.org/docs/faq).
- [Academy 99th Oscars key dates](https://www.oscars.org/99th-oscars-and-academy-key-dates).
- [Academy announcement: Casting begins at the 98th Oscars](https://www.oscars.org/news/academy-establishes-award-casting-beginning-98th-oscarsr).

Decide during execution, not before starting: final project title, exact dataset version, confirmed source licenses, historical prediction timestamp availability, minimum evidence for category-specific models, and whether a paid historical revenue source is worth its cost.

**First executable milestone:** establish the private repository, publish a minimal Quarto page, and complete a small source-audit notebook before attempting full-scale scraping or model development.
