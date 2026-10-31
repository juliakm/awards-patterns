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
| Repository | Public code repository, with source data, secrets, and model binaries excluded; publish to GitHub Pages |
| Public technical evidence | Pipeline code, tests, data model, selected notebooks, methodology, evaluation results, and model documentation |
| Prediction target | Winners among announced Oscar nominees, not nomination prediction |
| Forecast products | Primary forecast immediately before final voting opens; early read at nominations + 24 hours |
| Priority | A credible richer model takes precedence over publishing all three initial articles |
| Capacity | Approximately 10 hours/week; free data preferred, paid APIs considered only if necessary |

**Launch contract:** an all-category historical dataset, a working public site, one substantive article, reproducible chronological model evaluation at both forecast cutoffs, and an inference pipeline that can accept the 2027 nominees. Every category gets a coverage/status entry; not every category needs a defensible learned model.

**Not required before launch:** three finished articles, a custom domain, live Python queries, visitor accounts, exhaustive precursor coverage, automated scraping of every prediction archive, or separately tuned models for every category.

Quarto is the publishing layer, not the main portfolio skill claim. It supports Python/Jupyter and article-style websites; there is no verified usage ranking in this plan. Emphasize the mainstream analytical and engineering tools in the site's methodology and project summary.

## 2. Release scope and editorial roadmap

### First three stories

1. **Who predicts which categories well?** Compare individual pundits and consensus entries from Awards Daily, showing accuracy, denominators, shared-year comparisons, and uncertainty.
2. **Which precursor awards actually help?** Compare category-specific precursor agreement and test whether those signals improve out-of-time predictions.
3. **Does box office matter?** Explore revenue versus winning among nominees, clearly distinguishing descriptive lifetime revenue from information available before an Oscar forecast.

Keep repeat-nominee questions, including Meryl Streep's nomination-to-win conversion, in the backlog. For career-history features, retain earlier Oscar records even though the main analytical window starts in 2010.

For January, publish whichever of stories 1–2 has the strongest verified data. Awards Daily accuracy may need to follow the precursor article if historical timestamps or reuse permissions are unresolved. A documented negative or inconclusive result is a valid finding; do not require a surprising pattern. Any article drafted before the frozen test run must exclude 2024–2026 from precursor-signal analysis.

### Public pages

- **Home:** project premise, featured article, current data coverage, and last update.
- **Articles:** accessible narratives with Plotly hover, zoom, legend toggles, and limited precomputed dropdowns.
- **Predictions:** model-readiness and historical backtest page before nominations; actual 2027 probabilities only after the nominee list is verified.
- **Methods and data:** schemas, sources, missingness, temporal cutoffs, reproducibility instructions, and model card.
- **About:** purpose, analytical skills demonstrated, selected notebook/code examples, and a link to the public repository.

Static interactivity means JavaScript operating on published data. Python runs during analysis/build, not in a visitor's browser. Do not use Python-backed notebook widgets as if they will work on GitHub Pages.

### Where Streamlit fits

Consider Streamlit as a later companion application, not a second launch requirement. It provides useful Python app-building experience and suits a category explorer or a prediction sandbox where visitors change inputs and rerun inference.

Keep Quarto for the article-first site, published notebooks, and stable forecast record. Plotly already provides interactivity without a running Python service. Streamlit becomes worthwhile when visitors need arbitrary queries or computations that precomputed charts cannot provide.

Streamlit requires a Python server and separate hosting; it cannot run on GitHub Pages. Link to a separately hosted app, reuse the same `oscar_patterns` package and approved data/model artifacts, and verify the hosting provider's current pricing and resource limits before deployment. Clearly separate hypothetical sandbox results from frozen official forecasts.

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
| Wikipedia award and ceremony pages | Added after the October 31 research; not yet checked. Candidate source for precursor nominees, winners, and event dates, and for an automated cross-check of Oscar records | Check table consistency, dates, and attribution/share-alike terms; treat as a candidate to verify against primary references |
| Kaggle precursor datasets | Added after the October 31 research; availability and contents not yet checked. Possible bulk starting point for Golden Globe, SAG, or other precursor records | Confirm the datasets exist, then check coverage, version pinning, license, and whether result dates are included |
| [Steve Hedden's knowledge-graph article](https://pub.towardsai.net/using-a-knowledge-graph-to-build-a-predictive-model-for-the-oscars-8203bc11d906) and [fckg repository](https://github.com/SteveHedden/fckg) | Article dated March 3, 2026 links an ontology, instance data, pipelines, and models; useful candidate for identifiers, nomination/recipient relationships, and cross-award category concepts. GitHub metadata reports CC0-1.0; no graph data has been acquired | Pin and inspect the repository's actual data coverage and license/provenance chain. Its core Oscar data comes from DLu/oscar_data, so existing upstream questions remain; dynamic TMDB/OMDb enrichment is not evidence of historical as-of availability |
| [Additional archived source supplied during implementation](https://archive.is/OxvZf#selection-4491.0-4494.0) | Uninspected candidate: the first request returned HTTP 429. Original publisher, article identity, selected passage, and archive capture time remain unknown | Inspect only when access is available; establish original source, capture/publication dates, relevance, and reuse terms. An archived page is not itself permission to extract or republish data |

**Primary recommendation:** begin with a licensed, versioned Oscar CSV, validate against Academy records, and store it locally. Use APIs to enrich that snapshot rather than making the project depend on a live third-party awards API.

**Box-office recommendation:** start with TMDB for descriptive analysis. Historical pre-cutoff grosses need a separate permitted source with dated observations. Defer paid data until a small sample demonstrates that it would materially improve the project. Do not assume Box Office Mojo permits scraping or bulk republication.

**Knowledge-graph candidate:** investigate whether permitted `fckg` records can feed the existing relational tables and identity crosswalks. Borrow its explicit nomination grain, award-concept mappings, and forecast provenance without requiring an RDF database or expanding the launch architecture. Preserve this project's multi-winner exceptions and temporal safeguards; do not import current revenue, ratings, or popularity into historical forecasts without as-of evidence.

### First source-audit deliverable

Create `data/source_registry.csv` and `data/coverage.csv`, plus a short source-audit notebook.

- [ ] For each source, record URL, publisher, version/commit where applicable, retrieval date, fields, year convention, license/terms link, attribution, and publication restrictions.
- [ ] Assess all 2010–2026 ceremony/category combinations against an independent expected-category registry.
- [ ] Spot-check 2010, 2011, 2021, and 2026 to expose year labels, category transitions, and recent additions.
- [ ] Inspect Awards Daily pages from at least an early, middle, and recent season, including a crafts/shorts page.
- [ ] Classify prediction records as timestamp-verified, uncertain, missing, protest/nonstandard, or unusable.
- [ ] Select the primary Oscar source and document a fallback by the end of week 2.

Avoid copying articles, images, biographies, or full third-party prediction charts into the public site without appropriate rights. Use permitted factual extracts, attribution, and derived summaries. Keep raw snapshots only where permitted and outside the public repository; private storage is not a waiver of source terms.

## 4. Data model and quality rules

Use immutable source snapshots where permitted, curated Parquet tables, and DuckDB SQL queries over those files. Keep one curated truth rather than maintaining unrelated CSV, notebook, and website versions. Record a checksum for every snapshot in `data/source_registry.csv` and back up permitted snapshots to private storage, because `data/raw/` and `data/curated/` are not committed and a source version can disappear.

| Table | Grain and essential fields |
|---|---|
| `ceremonies` | One Oscar ceremony: ID, ceremony year/date, eligibility label/window, nomination announcement date, final voting start date |
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

Defer `predictions` and `film_observations` until the pundit or dated-revenue data survives the source audit. Neither table is needed for the launch model without those sources.

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
- Build earlier-career Oscar counts using records before the analytical window when available, always ending before the forecast cutoff. For launch, limit person-level career history to acting and directing; parsing every historical credit string can wait.

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
  _freeze/                 # committed Quarto execution results
  index.qmd
  about.qmd
  methods.qmd
  predictions.qmd
  articles/
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
    raw/                   # permitted snapshots; ignored, backed up privately
    curated/               # Parquet tables; ignored, rebuilt from snapshots
    public/                # committed; explicitly approved publication extracts
  notebooks/
    00_source_audit.ipynb
    01_category_history.ipynb
    02_pundit_accuracy.ipynb
    03_precursor_signals.ipynb
    04_box_office.ipynb
    05_model_backtest.ipynb
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

Configure the root Quarto project with explicit render targets: the root-level public pages, `articles/`, and only selected notebooks. Keep the home page at the project root so it renders to `_site/index.html`; confirm this with the first minimal deployment. Publish artifacts to `_site/`; do not make the whole repository a website resource directory.

Set `execute: freeze: auto` and commit `_freeze/`. Published pages read only from `data/public/`, never `data/curated/`, so CI can render them without ignored data. `.ipynb` notebooks keep their saved outputs unless explicitly re-executed: run `quarto render <notebook> --execute` locally before committing a refreshed result.

Use DuckDB for joins, coverage checks, and analytical aggregations; use pandas for transformation and plotting. Add dependencies only when a concrete task needs them. Avoid a backend, cloud database, orchestration framework, and deep learning for this release.

### Environment/bootstrap checklist

The following commands are for the later implementation phase; this plan does not create or initialize the application.

```bash
cd /Users/juliakm/Code/OscarData
uv init --package --name oscar-patterns --python 3.12
uv add pandas pyarrow duckdb scikit-learn plotly jupyter httpx
uv add --dev pytest ruff
uv sync
quarto check
```

Install `uv` and the separate Quarto CLI through their official installers if absent. Keep Python and Quarto versions pinned to a tested combination in local setup and CI.

- [ ] Check for existing files before scaffolding; preserve this plan and other work.
- [ ] Adjust the generated Python package to `oscar_patterns` and add an `oscar-data` console entry point in `pyproject.toml`.
- [ ] Confirm `.gitignore` still covers environments, secrets, raw/curated datasets, model binaries, caches, and `_site/` before each new data source is added.
- [ ] Create README with setup, pipeline commands, source requirements, and public-site URL.
- [ ] Rename the existing private `juliakm/oscar-patterns` repository to `awards-patterns` before enabling Pages, then update the local remote. As of October 31, 2026, Pages was not enabled and the new name was available.
- [ ] Review the full commit history and staged files for source data, secrets, and restricted content, then change the repository's visibility to public.
- [ ] Add a code license and a README note that data has separate source terms and is not covered by that license.
- [ ] Confirm Pages deploys from the public repository through GitHub Actions.

### Pipeline interface to implement

These are proposed commands, not existing tools:

```bash
uv run oscar-data ingest --source oscar-csv
uv run oscar-data validate
uv run oscar-data build-features --cutoff-policy nominations-plus-24h
uv run oscar-data build-features --cutoff-policy pre-final-voting
uv run oscar-data backtest --config configs/backtest.toml
uv run oscar-data export-public
uv run pytest
uv run ruff check .
uv run ruff format --check .
quarto render
```

Add the referenced backtest configuration when the modeling phase begins. Provide equivalent Python imports for notebook use. Commands should fail clearly on unavailable sources or invalid data, rather than quietly publishing stale output.

## 6. Prediction research design

### Target and information policy

Produce probabilities for each nominee in each ceremony/category contest. Train only on completed historical contests. Predicting an announced nominee's win is different from predicting a film's nomination.

Define two forecast products and keep their evaluation separate:

| Product | Cutoff | Allowed information |
|---|---|---|
| Primary forecast | Immediately before final Oscar voting opens | Confirmed nominees and results/predictions available by that cutoff |
| Early read | Nomination announcement + 24 hours | Confirmed nominees and only information known by that cutoff |

Backtest both cutoffs before launch and use the same cutoff policies for historical evaluation and deployment. Any other interim update is labeled unvalidated unless its cutoff has its own backtest. For 2027, label the early read as a January 22 forecast, not a prediction made before nominations, and verify the final voting date from the Academy schedule.

Precursor timing changes across the historical window. In recent seasons, DGA, PGA, SAG, and BAFTA winners have generally been announced after Oscar nominations, while some were announced earlier in the first seasons of the window. Verify each date in the data. At the early-read cutoff, a precursor-win coefficient may therefore rest on a few older seasons; check this explicitly and do not present the early read as the model's strongest forecast.

If accurate historical announcement timestamps cannot be established for a feature, exclude it from strict backtests or label the experiment retrospective and non-deployable. A final pundit chart cannot be used as a nomination-day feature simply because it is archived.

### Candidate features

Start with features that can be reconstructed reliably:

- Category/family and nominee field size; ceremony-specific category rules.
- Same-season total Oscar nominations for the film, available after nominations.
- Prior Oscar nominations/wins for credited actors and directors, plus the film's studio/distributor where reliable.
- Category-mapped precursor nominations and wins known by the cutoff.
- Time-verified pundit consensus share and disagreement, only if the source audit supports them.
- Stable film metadata such as genre and runtime; carefully dated release information.

Revenue, budgets, critic scores, and popularity measures are optional. Current lifetime revenue, current review aggregates, TMDB popularity, retrospective biographies, and post-Oscar honors must not leak into historical forecasts. Static attributes that were known then still need verified definitions and coverage.

For each precursor, distinguish **not nominated**, **event not yet held**, **category not applicable**, and **source missing**. Map DGA to directing, PGA to picture, and acting guild awards to their corresponding acting contests. Pool these through shared `nominated_mapped_precursor` and `won_mapped_precursor` features, with limited interactions by category family; separate award-by-category effects would each rest on about 17 contests. A precursor counts only for its mapped contest, so do not create a signal for winning any guild award.

### Models and evaluation

1. Establish a uniform `1 / nominee_count` probability baseline, plus a documented precursor-rule baseline and time-valid pundit baseline where coverage permits.
2. Fit a pooled regularized logistic model with category/family features. Compare a conditional logit challenger on the same folds, because it models nominees competing within a contest. Use statsmodels if its regularization options are sufficient, or a small tested SciPy implementation. Histogram gradient boosting is optional and only follows if time remains; about 400 contest outcomes give it little to work with.
3. For the logistic model, convert positive entry scores into within-contest probabilities summing to one; apply exactly the same transformation during evaluation and inference. This is a practical contest-probability approximation, not proof of calibration. The conditional logit produces within-contest probabilities directly.
4. Add category-specific models only when enough historical contests and stable signals support them. Compare against the pooled model rather than assuming specialization is better.
5. Select the final approach using chronological validation, calibration, simplicity, and deployment-time feature availability—not just total winner accuracy.

Suggested split:

- Initial training window: ceremonies 2010–2016.
- Development: expanding-window one-season-ahead validation for 2017–2023.
- Untouched final test: 2024–2026, predicted one season at a time using only earlier seasons; do not revise choices in response to these results.
- After reporting the frozen test result, refit the selected approach on eligible 2010–2026 data for 2027 inference.

All preprocessing, imputation, feature selection, tuning, and any calibration happen inside the appropriate training window. Keep every contest and ceremony together; never randomly split nominee rows. If adding calibration, use earlier-year out-of-fold predictions, not the final test or in-sample fitted scores.

Quarantine the test years. Data-quality and coverage checks may include 2024–2026, but exploratory charts, feature analysis, and articles must not examine how features relate to outcomes in those years until the test is run. Before opening the test, pass a dry run on a development season. If a bug appears afterward, log the bug, the fix, and the before-and-after results publicly; do not change features or model choices in response to test performance.

Report:

- Top-choice winner accuracy, with per-category race counts.
- Contest-level log loss and multiclass Brier score on normalized probabilities.
- Calibration plots where sample size permits, plus year-to-year variation.
- Macro category summaries and coverage, so a pooled aggregate does not hide weak categories.
- Matched-contest comparisons against each applicable baseline.
- Feature-group ablations: precursors, career history, pundits, and optional revenue.

Bootstrap development-period uncertainty (2017–2023) by ceremony, not independently by nominee. The final test has about 70 contests across three ceremonies, which gives only 10 distinct ceremony resamples, so report it per year with paired contest-level differences against each baseline and no ceremony-bootstrap interval. Explain that 17 completed seasons and about 400 contests provide limited evidence even though there are many nominee rows. Individual-category estimates are especially noisy.

For true tied historical winners, declare the metric policy before evaluation: top-choice accuracy accepts any official winner; probability metrics can use an equal target distribution across official winners. Show a sensitivity result excluding those contests. Do not quietly assign a single winner.

**Model selection rule:** prefer the regularized model unless the challenger offers a consistent development-period improvement in probability quality without meaningful calibration or coverage regressions. Publish an honest baseline-only result if neither model adds value. Select on the primary forecast cutoff. Record the numeric selection criteria before opening the final test.

**Sparse-category policy:** publish status, coverage, and a transparent baseline or explicitly experimental forecast for categories with insufficient history, especially Casting. An all-category website is not a claim of validated ML in all categories. With DGA, PGA, and SAG, only about 6 of 24 categories have a mapped precursor at launch; state this on the Predictions and Methods pages, and show other categories as relying mainly on nomination counts and history.

### Model artifacts

- [ ] Versioned feature specification and timestamp rules.
- [ ] Backtest predictions with entry IDs, cutoffs, model version, and data snapshot ID.
- [ ] Metrics by year/category, baseline comparisons, and calibration figures.
- [ ] Model card documenting intended use, limitations, source gaps, and probabilistic interpretation.
- [ ] A dry-run inference command against a historical nominee list.
- [ ] Frozen 2027 early read and primary forecast, each committed publicly with a published SHA-256 hash and a third-party archive copy of its page.

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
| Nov 2–8 | 10 h | Initialize package and public code repository; deploy a minimal Quarto page with basic checks through CI. Home page works at the public URL |
| Nov 9–15 | 10 h | Complete source audit and pick primary/fallback sources. Acquire a pinned, checksummed Oscar snapshot; licensing blockers are explicit |
| Nov 16–22 | 10 h | Normalize all-category 2010–2026 data, category rules, aliases, and bridges. Independent coverage checks and core data tests pass; complete the precursor go/no-go |
| Nov 23–29 | 10 h | Thanksgiving week: collect DGA, PGA, and SAG nominees, winners, and result dates, and link them to Oscar entries |
| Nov 30–Dec 6 | 10 h | Build dated feature snapshots at both cutoffs; implement uniform and rule baselines. Prove no future features in a historical dry run |
| Dec 7–13 | 10 h | Run pooled regularized model and conditional logit challenger with chronological folds; produce initial evaluation notebook and coverage report. Audit Awards Daily sample further only if acquisition is on track |
| Dec 14–20 | 10 h | Run feature ablations and complete development comparisons; pass the development-season dry run; freeze feature/model/metric decisions |
| Dec 21–27 | 10 h | Run untouched test at both cutoffs, write model card, and refit deployment model. Use holiday slack explicitly if actual capacity drops |
| Dec 28–Jan 3 | 10 h | Draft and publish one article from validated findings, with methods, selected notebook, and historical prediction results |
| Jan 4–10 | 10 h | End-to-end historical season rehearsal, publication audit, mobile/chart checks, and inference/runbook fixes |
| Jan 11–14 | 10 h | Release freeze and launch. Collect 2027 precursor data known so far; confirm nominee import workflow and source-monitoring checklist |
| Jan 15–20 | Buffer | Repair only; verify Academy schedule, including final voting dates, and incoming nomination-day sources |

### Scope-cut checkpoints

- **Nov 15:** if the primary source is blocked, use a permitted historical fallback plus curated recent records; disclose incompleteness rather than claiming full coverage.
- **Nov 22:** go/no-go on precursor access and collection rate before modeling depends on the data. Launch precursors are DGA, PGA, and SAG; Globes and BAFTA wait until after launch unless work is ahead of schedule. If those three cannot be collected with dates in the available time, reduce to the sources that can and disclose the narrower coverage.
- **Nov 29:** if timestamped pundit or box-office data is unavailable, remove it from the launch model. Continue with stable metadata, career history, and dated precursors.
- **Dec 13:** if the challenger or precursor work is consuming the schedule, stop expanding models, award sources, and articles. Finish evaluation on the verified feature set.
- **Jan 3:** freeze features. Cut additional stories, advanced filters, and custom branding before cutting temporal validation, source disclosure, or deployment rehearsal.

Full competitive-category coverage is a launch goal, not something to claim if the source audit reveals unresolved gaps. Publish actual coverage and explicitly mark any reduced release.

## 9. Hosting, automation, and publication controls

Use the project Pages URL `https://juliakm.github.io/awards-patterns/`. A project Pages path comes from the repository name, so rename the existing `oscar-patterns` GitHub repository to `awards-patterns` before Pages is enabled.

No part of the live site's path may contain "oscar" or "oscars" in any letter case. This covers the repository name, page and article slugs, notebook paths, downloads, and other published assets. It does not restrict the internal Python package name, local folder name, or Oscar references in page text.

The source repository is public, so the project does not depend on GitHub Pro for Pages. Publishing the code lets readers inspect the pipeline, tests, and data model, and gives forecasts a public commit history. Run expensive modeling locally and keep deployment small.

Configure Pages to use GitHub Actions. Have the workflow:

1. Check out the source repository and install pinned Python/Quarto versions.
2. Restore the locked Python environment and run tests, Ruff, and public-data validation.
3. Render only approved publication targets from committed `data/public/` extracts, `_freeze/` results, and saved notebook outputs.
4. Fail the deployment if any path in `_site/` contains "oscar" in any letter case.
5. Upload only `_site/` through the Pages artifact/deploy actions.
6. Verify the deployed home page and an article URL return successfully.

Keep acquisition/training separate from deployment. Do not automatically retrain a model on each push. Execute notebooks locally and publish approved saved outputs; CI does not need ignored data or a live API. Record the data/artifact version so cached results do not silently become stale.

- [ ] Store API keys in local environment variables or GitHub secrets, never notebook cells or commits.
- [ ] Ensure copied resources, HTML, notebook downloads, logs, and Plotly payloads contain only material intended for public release.
- [ ] Omit raw source data, model binaries, environment files, and unselected notebooks from the site artifact.
- [ ] Show selected code through collapsible cells and link only approved notebook downloads.
- [ ] Include source attribution and, if using TMDB, its approved logo and required non-endorsement notice.
- [ ] Test project-subpath links, chart assets, phone-sized layouts, keyboard access, readable legends, and textual chart summaries.
- [ ] Set visible data/model update timestamps and a “known limitations” section.

## 10. Nomination-day and Oscar-season runbook

The Academy's linked calendar lists nominations for January 21, 2027 and the ceremony for March 14, 2027. Direct Academy calendar/press fetches returned HTTP 403 during research; independently recheck the official schedule before executing this runbook because dates can change.

- **Before Jan 21:** load 2027 precursor data known so far; confirm the import format, category registry, model artifact, cutoff policies, and baseline fallback. Rehearse with a completed historical season.
- **Jan 21:** import the official nominee list; verify every category, recipient bridge, work/song identity, and field size. Manually review new films and people into the crosswalk within the 24-hour window. Do not infer nominees from pundit picks.
- **Jan 22, after the defined 24-hour cutoff:** build the early-read feature snapshot, validate availability dates, run inference, and check per-contest probabilities and coverage.
- **Publication:** save an immutable forecast file with model/data versions, publication timestamp, and category reliability status. Commit it publicly, publish its SHA-256 hash, and archive the forecast page with a third party. Publish probabilities, not guaranteed outcomes.
- **Immediately before final voting opens:** load precursor results known by the cutoff, then build, validate, and publish the primary forecast the same way. Keep the early read visible and evaluate each forecast under its own information policy. Any other interim update is separately versioned and labeled unvalidated.
- **After March 14:** ingest verified results, score both frozen forecasts, compare baselines, and publish a postmortem including surprises and failures.

Never overwrite an earlier forecast and later report the updated version as if it were the original.

## 11. Definition of done

- [ ] A clean environment can recreate curated data and results from documented, permitted inputs or checksummed snapshots restored from private storage.
- [ ] Coverage is measured against expected competitive categories; all gaps and category transitions are visible.
- [ ] Tests cover ballot-entry deduplication, ambiguous year/title mapping, temporal leakage, normalization, and historical inference.
- [ ] Model comparison uses chronological validation and an untouched final test at both forecast cutoffs; probabilities, baseline comparisons, and uncertainty are published.
- [ ] At least one article has an explicit question, auditable denominator, interactive chart, defensible interpretation, and caveats.
- [ ] The public repository exposes the pipeline, tests, and selected notebooks without restricted data or secrets.
- [ ] The deployed site works at its actual public URL and does not depend on a visitor-side Python service.
- [ ] The publication artifact is audited for unintended data/code exposure.
- [ ] A historical end-to-end rehearsal passes before 2027 nominee ingestion.

## 12. References and unresolved decisions

Implementation references:

- [Quarto overview](https://quarto.org/) and [GitHub Pages publishing](https://quarto.org/docs/publishing/github-pages.html).
- [GitHub: creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
- [TMDB API FAQ and attribution](https://developer.themoviedb.org/docs/faq).
- [Knowledge-graph Oscar modeling article](https://pub.towardsai.net/using-a-knowledge-graph-to-build-a-predictive-model-for-the-oscars-8203bc11d906) and [linked ontology/data repository](https://github.com/SteveHedden/fckg).
- [Academy 99th Oscars key dates](https://www.oscars.org/99th-oscars-and-academy-key-dates).
- [Academy announcement: Casting begins at the 98th Oscars](https://www.oscars.org/news/academy-establishes-award-casting-beginning-98th-oscarsr).

Decide during execution, not before starting: final project title, exact dataset version, confirmed source licenses, historical prediction timestamp availability, minimum evidence for category-specific models, and whether a paid historical revenue source is worth its cost.

**First executable milestone:** establish the public code repository, publish a minimal Quarto page, and complete a small source-audit notebook before attempting full-scale scraping or model development.

## 13. Executable todo backlog

This is the repository copy of the 24 implementation todos created in the session task database. All started as **pending** on October 31, 2026; the checkboxes below record verified completion. The three completed fleet-decomposition tasks are planning work, not completed implementation, and are omitted here.

Each ID matches its session todo. Check off tasks here and update their session status as work completes. Dependencies are actual prerequisites, not ordering implied by this list. Independent tasks can run in parallel; coordinate shared files such as README, package configuration, and workflows.

**Initially ready to start independently:** `foundation-bootstrap`, `data-source-audit`, `model-cutoff-policy`, `repo-auditing-public-history`, and `site-minimal-root-quarto`.

Repository renaming, public visibility, and Pages setup are authorized future work, subject to the public-history audit. Adding this backlog does not perform those changes.

**Execution checkpoint, October 31:** Python 3.12.16, uv 0.13.6, and Quarto 1.10.20 are installed and tested locally. The initial Python suite passes 16 tests; the minimal homepage renders. The source audit is complete but has not cleared a primary/fallback bulk-data permission path. Acquisition and the independently verified category registry are blocked on source permissions/access; no actual Oscar dataset, fitted model, or empirical results are claimed. See `data/source_audit.json` for evidence and next steps. Code/site infrastructure can proceed without publishing source records.

### Python foundation and data

- [x] **`foundation-bootstrap` — Bootstrapping the reproducible Python foundation**

  Create the importable `src/oscar_patterns/` package, `oscar-data` console interface, `pyproject.toml`, `uv.lock`, tested Python/Quarto pins, README, and appropriate ignore rules. Preserve existing work; keep raw/curated data, secrets, models, and generated site output excluded. Code-license selection belongs to `repo-renaming-public-licensing`.

  **Acceptance:** locked environment restores; imports, console help, focused tests, Ruff, and `quarto check` pass; representative private paths are ignored. **Depends on:** none.

- [x] **`data-source-audit` — Auditing source permissions and acquisition viability**

  Create `data/source_registry.csv` and `notebooks/00_source_audit.ipynb` with inspected source evidence, versions, coverage, year conventions, timestamp certainty, acquisition/publication permissions, attribution, and restrictions. Recheck the Oscar candidates, Academy verification workflow, Awards Daily year-label/protest-pick issues, and feasible DGA/PGA/SAG sources. Treat Wikipedia and Kaggle precursor candidates as unverified until inspected.

  **Acceptance:** select a permitted primary/fallback Oscar source or explicitly record gaps/blockers; do not present old plan observations as new research. Optional pundit/revenue/other-award sources do not block the core pipeline. **Depends on:** none.

- [ ] **`data-category-rule-registry` — Defining independent ceremony and category rules**

  Create independently verified ceremony/category/rule registries for competitive 2010–2026 contests, including eligibility windows, nomination and final-voting dates or explicit unknowns, original labels, category transitions, field-size rules, and documented ties. Suggested outputs are `data/reference/` tables and `notebooks/01_category_history.ipynb`, subject to publication permissions.

  **Acceptance:** unique expected contests and provenance; checked 2010/2011/2021/2026 examples; correct Sound, Best Picture, Casting, and exceptional-window handling without guessed dates. **Depends on:** `data-source-audit`.

- [ ] **`data-pinned-acquisition` — Acquiring permitted immutable Oscar snapshots**

  Implement reusable ingestion and `oscar-data ingest --source oscar-csv`. Store permitted immutable snapshots privately, record source/version/retrieval time/SHA-256 in the registry, and document permission-compatible backup and restore. Retain earlier acting/directing records when available for career history.

  **Acceptance:** checksummed restores reproduce inputs; snapshots cannot be silently overwritten; unavailable/unlicensed inputs fail clearly; actual 2010–2026 completeness is inspected and gaps disclosed. No restricted data or credentials are staged. **Depends on:** `data-source-audit`, `foundation-bootstrap`.

- [ ] **`data-normalized-ballots` — Normalizing ballot entities and reviewed identity crosswalks**

  Implement `normalize.py`, curated Parquet entity/bridge tables, reviewed aliases/external-ID crosswalks, and an unresolved-match queue. Preserve ballot-entry grain, distinct songs from one film, multiple recipients, year conventions, original category labels, and genuine ties. Limit earlier person-level history parsing to acting/directing for launch.

  **Acceptance:** deterministic reruns, valid foreign keys, correct song/recipient examples, explicit ambiguity and coverage gaps; fuzzy candidates never silently become verified identities. **Depends on:** `data-category-rule-registry`, `data-pinned-acquisition`.

- [ ] **`data-coverage-validation` — Validating all-category coverage and temporal data integrity**

  Implement `oscar-data validate`, DuckDB coverage checks, focused normalization/data-validation tests, and `data/coverage.csv` against the independent registry. Check ballot duplication, bridges, identity matches, nominee expectations, exceptions, category transitions, and temporal fields.

  **Acceptance:** invalid fixtures fail and legitimate songs, multi-recipient entries, variable fields, and ties pass; real discrepancies fail clearly or remain explicitly disclosed. Final-test years may be inspected for data quality only, not feature/outcome relationships. **Depends on:** `data-category-rule-registry`, `data-normalized-ballots`.

- [ ] **`data-dated-precursors` — Collecting dated mapped launch precursor records**

  Complete the access/collection-rate go/no-go and collect feasible permitted DGA/PGA/SAG nominees, winners, result/availability dates, snapshots, mappings, and linked Oscar entities. Provide a documented 2027 update interface. Preserve non-Oscar-nominated winners and distinct missing/not-yet-held/not-applicable states.

  **Acceptance:** reviewed contest/entity mappings and date evidence support both cutoffs; unknown timestamps cannot enter strict forecasts. An evidence-backed no-go with explicit unavailable statuses is acceptable if no sources are feasible; baseline research must not depend on acquiring unpermitted data. **Depends on:** `data-normalized-ballots`, `data-source-audit`.

- [ ] **`data-approved-public-contract` — Exporting permission-approved public data contracts**

  Define the approved `data/public/` schema/manifest and implement `oscar-data export-public` for only permitted fields and aggregates needed by articles/notebooks/site pages. Record source terms, attribution, versions, input checksums, generation time, and coverage limits. Keep public output paths free of case-insensitive "oscar".

  **Acceptance:** allowlist, schema, provenance, and path tests pass; invalid/unapproved inputs fail rather than appear fresh; committed publication inputs work without private data or APIs. Optional fields require separate approval and do not block core exports. **Depends on:** `data-coverage-validation`, `data-source-audit`.

### Forecast research and analysis

- [x] **`model-cutoff-policy` — Defining dual-cutoff forecast and evaluation policy**

  Write the versioned early-read and pre-final-voting primary forecast specification, including exact timezone-aware boundaries, availability evidence, contest/tie policies, model/snapshot identifiers, sparse-category treatment, and final-test quarantine. Verify the official 2027 schedule before season execution.

  **Acceptance:** boundary fixtures demonstrate no future information; unverifiable features and unvalidated interim cutoffs are explicitly classified; model selection is based on the primary cutoff with the early read reported separately. **Depends on:** none.

- [ ] **`model-dated-features` — Building leakage-safe feature snapshots**

  Implement both-cutoff feature construction for contest rules, distinct same-film nomination counts, pre-cutoff actor/director history, and feasible mapped precursor signals. Distinguish absent/not-yet-held/not-applicable/missing sources; exclude current revenue/review/popularity and post-award information from historical forecasts.

  **Acceptance:** cutoff, count, history, and missing-state tests pass; feature coverage and early-read precursor sparsity are reported. Fixture-based implementation can proceed before acquisition; real-source validation gates development evaluation. **Depends on:** `foundation-bootstrap`, `model-cutoff-policy`.

- [ ] **`model-baseline-inference` — Implementing transparent baselines and shared inference contracts**

  Implement uniform and documented mapped-precursor baselines, plus a pundit baseline only where time-valid coverage permits. Create a shared historical nominee-list inference interface with deterministic fallbacks, entry IDs, cutoff/model/data versions, and reliability status.

  **Acceptance:** finite nonnegative probabilities sum to one per contest; evaluation and inference agree; missing signals, tied top picks, non-Oscar precursor winners, and sparse categories are handled explicitly. **Depends on:** `model-dated-features`.

- [ ] **`model-pooled-challengers` — Implementing pooled logistic and conditional-logit candidates**

  Implement pooled regularized logistic regression and a conditional-logit challenger, with documented contest-probability transformations, identifiability/convergence checks, and a defensible tied-winner training policy. Boosting remains optional after core work.

  **Acceptance:** tested fits are reproducible and numerically stable; probabilities normalize and match inference; sparse/convergence failures use explicit fallback. Do not imply separately validated models for every category. **Depends on:** `model-dated-features`.

- [ ] **`model-development-evaluation` — Running expanding-window development evaluation**

  Implement 2010–2016 initial training followed by one-season-ahead development folds for 2017–2023 at both cutoffs. Keep all transforms, tuning, and optional calibration inside training windows. Produce versioned predictions, coverage, accuracy, probability metrics, matched baselines, calibration diagnostics, and ceremony-level development uncertainty.

  **Acceptance:** split/train-transform tests prevent nominee-row or future leakage; ties and sparse categories follow policy; 2024–2026 feature/outcome relationships remain quarantined. Real data passes coverage checks, and precursor feasibility or explicit no-go is recorded. **Depends on:** `data-coverage-validation`, `data-dated-precursors`, `model-baseline-inference`, `model-pooled-challengers`.

- [ ] **`model-preregister-selection` — Freezing ablations selection and development dry run**

  Run development-only feature-group ablations and record numeric primary-cutoff model-selection criteria, frozen feature/transform/calibration/tie/fallback policies, and a successful dual-cutoff development-season inference rehearsal. Prefer the simpler model unless the challenger consistently earns its complexity; baseline-only selection is valid.

  **Acceptance:** preregistration and dry-run evidence exist before opening the test; excluded optional features are disclosed and no choices are made from test performance. **Depends on:** `model-development-evaluation`.

- [ ] **`model-final-test-refit` — Evaluating frozen final tests and refitting deployment artifacts**

  Evaluate 2024–2026 sequentially using only earlier completed seasons, at both cutoffs, with decisions frozen. Publish per-year/category metrics, matched baseline differences, tie sensitivity, and limitations without a three-ceremony bootstrap interval. Transparently log post-opening bugs and before/after fixes.

  **Acceptance:** reproducible historical artifacts and inference checks pass; selected approach is refit on eligible 2010–2026 data only after test reporting; model card explains both cutoffs, coverage, normalization, and sparse categories. **Depends on:** `model-preregister-selection`.

- [ ] **`analysis-verified-flagship` — Writing the verified flagship analysis and bounded follow-up stories**

  After final-test completion, write one article and selected reproducible notebook from verified findings with an explicit question, auditable denominators, interactive-chart inputs, matched comparisons, coverage, uncertainty, and noncausal caveats. Negative/inconclusive results are valid.

  **Acceptance:** claims trace to permitted inputs and frozen evaluation; content is ready for site integration. Optional later pundit and box-office stories follow section 7 and do not gate completion of this task or launch. **Depends on:** `model-final-test-refit`.

### Repository, website, and release

- [x] **`repo-auditing-public-history` — Auditing tracked history for public release**

  Review every branch/tag and reachable history intended for exposure, current/staged files, notebook outputs, and downloads for secrets, restricted data, models, and unreviewed assets. Record public-release acceptance and any needed remediation; ignore rules alone do not remove already tracked content.

  **Acceptance:** all refs to be exposed are clean; unresolved assets remain excluded/private. Unused source-license questions do not block a clean minimal site. This audit does not itself change visibility or hosting. **Depends on:** none.

- [ ] **`repo-renaming-public-licensing` — Renaming and licensing the public repository**

  Following audit acceptance, rename to `juliakm/awards-patterns`, update the local remote and documentation, add the selected code license and separate-data-terms notice, and change visibility to public. Review newly introduced files again before exposure.

  **Acceptance:** canonical repo/remote links and public visibility are verified; only reviewed material is exposed; license boundaries are explicit. **Depends on:** `foundation-bootstrap`, `repo-auditing-public-history`.

- [x] **`site-minimal-root-quarto` — Creating the minimal root Quarto site**

  Create `_quarto.yml` and root `index.qmd` with honest readiness content, explicit render/resource allowlists, reviewed saved outputs, and freeze configuration. No data/model acquisition is needed for the minimal page.

  **Acceptance:** root Home renders offline to `_site/index.html`; only intended material is included; every published path, including assets/downloads/notebooks, excludes case-insensitive "oscar". **Depends on:** none.

- [ ] **`release-offline-pages-workflows` — Building offline checks and Pages artifact workflows**

  Implement locked/pinned checks and Pages workflows with focused tests, Ruff, public-data validation, offline rendering, reviewed output freshness, and least-needed deployment permissions. Upload only `_site/`, never the checkout; keep acquisition/training out of CI publishing.

  **Acceptance:** clean render/checks work without private inputs/APIs; an injected forbidden path fails the guard; artifacts exclude secrets, raw data, models, and unselected notebooks. Live Pages remains gated by approved repository publication. **Depends on:** `foundation-bootstrap`, `site-minimal-root-quarto`.

- [ ] **`release-proving-public-deployment` — Proving safe public Pages deployment**

  Enable Actions-based Pages after publication approval and deploy the reviewed minimal artifact to `https://juliakm.github.io/awards-patterns/`. Verify actual HTTP responses, root entry, project-subpath assets, artifact inventory, and public settings.

  **Acceptance:** public Home and static navigation work with no Python server, private inputs, or unintended exposure; the early proof does not wait for full articles/models. **Depends on:** `release-offline-pages-workflows`, `repo-renaming-public-licensing`, `site-minimal-root-quarto`.

- [ ] **`site-integrating-public-navigation` — Integrating accessible pages charts and notebooks**

  Integrate Home/About/Methods/Predictions, the approved flagship article, Plotly charts, model/data documentation, and selected notebook/code links. Show coverage, source terms, update timestamps, both forecast policies, limitations, and required attributions.

  **Acceptance:** navigation and charts work under `/awards-patterns/` without Python services; mobile/keyboard checks and public-path rules pass; no real 2027 forecast appears before verified nominees. **Depends on:** `analysis-verified-flagship`, `data-approved-public-contract`, `model-final-test-refit`, `site-minimal-root-quarto`.

- [ ] **`release-rehearsing-launch` — Rehearsing historical inference and freezing launch**

  Rehearse a completed historical season end to end: permitted-input restore, nominees/identities/bridges, both cutoff snapshots, inference/fallback, forecast publication, and scoring. Apply the January 14 launch checklist with the January 15–20 repair buffer and official schedule/source monitoring.

  **Acceptance:** dual-cutoff evaluation/rehearsal evidence, public Home and actual article URL, accessible charts/notebook, honest coverage, and artifact/history audits pass. Label reduced scope; fix integration defects without changing frozen model choices. **Depends on:** `data-coverage-validation`, `model-final-test-refit`, `release-proving-public-deployment`, `site-integrating-public-navigation`.

- [ ] **`season-freezing-2027-forecasts` — Freezing season forecasts and publishing postmortem**

  Execute the verified-calendar season runbook: import official nominees, validate identities and both cutoffs, publish separate early-read and primary forecasts with immutable files, versions, timestamps, SHA-256 hashes, public commits, and third-party archive evidence. Preserve earlier forecasts; mark other interim updates unvalidated.

  **Acceptance:** after verified ceremony results, score the original hashed forecasts against baselines and publish a linked postmortem. Unsupported/fallback categories remain explicit; forecast files are never overwritten. This task extends through the 2027 season rather than blocking January website launch. **Depends on:** `release-rehearsing-launch`.
