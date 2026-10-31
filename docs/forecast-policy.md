# Announced-nominee forecast policy — version 1.0.0

This normative specification accompanies `configs/forecast-policy.toml` and
`oscar_patterns.forecast_policy`. It defines eligibility, not a trained model or
a completed backtest. Changes to boundaries, identities, or evaluation rules
require a new policy version recorded in prediction artifacts.

## Products and timestamp evidence

Both products predict a **confirmed nominee's win**, never nomination itself.
Require independently verified nomination-announcement and final-voting-start
instants from the ceremony schedule, with source references preserved in the
schedule registry. No date-only, guessed-midnight, or naive datetime inputs.
Store timezone-aware ISO 8601 timestamps and their source timezone (normally
`America/Los_Angeles` for the Academy schedule); compare instants in UTC.

* **Early read:** nomination announcement plus **24 elapsed hours**, including
  daylight-saving transitions. Public availability must be **at or before** it.
* **Primary:** immediately before final voting opens. Public availability must
  be **strictly before** the voting-start instant. Store that instant and `<`,
  not an arbitrarily subtracted second or microsecond.

The voting start must follow the early-read cutoff. `ForecastCutoffs` requires
the nomination announcement and rejects invalid ordering. It cannot establish
a pre-nomination product. Other interim cutoffs are **unvalidated** and rejected
by strict eligibility, until separately specified and backtested.

`AvailabilityEvidence` records public availability, timestamp status, supporting
reference, and optional retrieval time. Strict inclusion requires status
`verified`, an aware availability instant, and a nonblank evidence reference.
These fields are assertions requiring source review, not automatic verification
by the helper. An event's occurrence alone does not establish publication.
Unknown or date-only timing is excluded, not converted to an invented instant.
Retrieval time is never substituted for availability. A later-retrieved archive
can support an earlier publication only with independently verified evidence;
an archived final pundit chart is not automatically a nomination-day feature.
Unverifiable timing may be studied only in separately labeled
**retrospective, non-deployable** experiments, never mixed into strict metrics.

## Contest, category, snapshot, and model identity

Use ceremony year, not film-release or eligibility year. A contest is
`(ceremony_id, category_id)`; each prediction identifies the actual
`ballot_entry_id`. Preserve distinct songs from the same film and multiple
credited recipients; do not replace ballot entries with film or person rows.
Use independently verified ceremony-specific category/rule records, retaining
original labels, eligibility windows, nominee-count exceptions, mergers,
transitions, and official ties. Do not infer expected categories from observed
ballots alone. Casting and other sparse categories receive coverage/status and
a transparent baseline or explicitly experimental forecast, not a claim of
validated category-specific ML.

Each prediction records the product, cutoff instant and comparison operator,
policy version, model version, immutable data snapshot ID, entry/contest IDs,
probability, and reliability status. The snapshot ID is the SHA-256 of a
canonical immutable manifest linking source IDs, versions, content checksums,
retrieval times, and availability evidence/status. Schedule/rule provenance and
feature-specification versions also belong in that manifest. Model versions
identify frozen transforms, training years, feature and fallback rules, and
calibration choices; do not overwrite them silently. Probability sums must be
one within each contest under the later shared inference contract.

## Missingness, mapped precursors, and ties

Keep **not nominated**, **event not yet held**, **category not applicable**, and
**source missing** distinct. Unknown availability is source-missing with a
timestamp reason, never evidence of no nomination/win. A verified zero is not
missing. Imputation is learned only within the training window. Signals apply
only to the mapped contest (DGA/directing, PGA/picture, corresponding acting
guild categories), not winning any guild award. Non-Oscar-nominated precursor
winners remain in source data.

Before model fitting, declare and freeze the tied-winner training treatment.
Official-winner top-choice accuracy accepts any official winner; probability
metrics use equal target mass across the official winners. Report sensitivity
excluding these contests. For equal predicted top probabilities, select the
lowest stable ballot-entry ID deterministically and report the tie count; never
break prediction ties using observed outcomes or input row order.

## Research partitions and selection

* **2010–2016:** initial training.
* **2017–2023:** expanding-window, one-season-ahead development. For year `y`,
  only eligible completed ceremonies from 2010 through `y - 1` train the fold.
* **2024–2026:** quarantined final test. Before opening, data-quality/coverage
  checks are allowed; exploratory feature/outcome relationships, tuning,
  calibration, feature selection, articles, and model comparisons are not.

Keep each entire ceremony and its contests together. Random nominee-row splits
are prohibited. All preprocessing and optional calibration stay inside the
appropriate training window; calibration uses earlier-year out-of-fold
predictions, not in-sample scores or held-out outcomes.

Select on the **primary** cutoff. Prefer the regularized model unless a
challenger consistently improves development-period probability quality
without meaningful calibration or coverage regressions; baseline-only results
are valid. Numeric thresholds, transforms, feature groups, tie/fallback rules,
and a successful dual-cutoff development dry run must be preregistered before
opening the test. This specification does not pretend those thresholds or
experiments already exist.

Report the early read separately on matched contests, including per-precursor
counts of timestamp-verified nomination/win signals available by each cutoff
and season/category. Early-read winner signals may exist mainly in older
seasons; quantify that timing sparsity before interpreting any coefficient.
Do not claim a learned early-read coefficient or strongest early-read model
from these fixtures.

Once frozen, predict 2024, 2025, and 2026 sequentially using only earlier
completed seasons; adding earlier test seasons to the next training window is
allowed only under the already frozen protocol. Do not revise choices from
test performance. Log any post-opening bug, fix, and before/after results
publicly. Report year/category accuracy, contest log loss and multiclass Brier
score, coverage, matched baselines, and calibration where support permits.
Bootstrap development uncertainty by ceremony. For the three-year final test,
report per-year results and paired contest-level baseline differences, with
**no ceremony-bootstrap interval**. Refit eligible 2010–2026 records for 2027
only after the frozen test result is reported.

## 2027 execution gate

The plan's **January 22, 2027 early-read calendar label is provisional**, not an
official timestamp and not a pre-nomination forecast. Both the nomination
announcement time (which determines the elapsed-24-hour cutoff) and the final
voting opening date/time require official Academy schedule confirmation with
timezone and retained source evidence before execution. No unknown official
2027 timestamp is hardcoded in the config or implementation. Schedule changes
require a new recorded schedule snapshot; a calendar label cannot override the
computed cutoff. This task does not claim official schedule verification,
historical data eligibility, trained models, or validated forecasts.
