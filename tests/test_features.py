"""Synthetic contracts only: these are not real Oscar data or official dates."""

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from oscar_patterns.features import (
    BallotEntry,
    CareerCoverage,
    CategoryRule,
    Ceremony,
    EntryPerson,
    FeatureInputs,
    NominationCoverage,
    PrecursorEntry,
    PrecursorEvent,
    build_feature_snapshots,
    coverage_report,
    feature_manifest,
)
from oscar_patterns.forecast_policy import AvailabilityEvidence, ForecastCutoffs

NOMINATIONS = datetime(2023, 1, 10, 12, tzinfo=timezone.utc)
CUTOFFS = ForecastCutoffs(NOMINATIONS, NOMINATIONS + timedelta(days=20))
EARLY = CUTOFFS.early_read_at
PRIMARY = CUTOFFS.primary_before
PAST = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)


def evidence(at=NOMINATIONS, status="verified"):
    return AvailabilityEvidence(at, status, "fixture:reviewed-public-record")


def rule(category, family, count, ceremony="current", availability=None):
    return CategoryRule(
        ceremony,
        category,
        family,
        f"Fixture {category}",
        "fixture-regime",
        count,
        availability or evidence(PAST),
    )


def base():
    return FeatureInputs(
        "fixture-only-v1",
        "synthetic_fixture",
        (Ceremony("current", 2023, CUTOFFS, "fixture:schedule"),),
        (
            rule("picture", "picture", 2),
            rule("directing", "directing", 1),
            rule("actor_leading", "acting", 1),
            rule("song", "music", 2),
        ),
        (
            BallotEntry("picture-a", "current", "picture", "film-a", evidence()),
            BallotEntry("picture-b", "current", "picture", "film-b", evidence()),
            BallotEntry("director-a", "current", "directing", "film-a", evidence()),
            BallotEntry("actor-a", "current", "actor_leading", "film-a", evidence()),
            BallotEntry("song-a-1", "current", "song", "film-a", evidence()),
            BallotEntry("song-a-2", "current", "song", "film-a", evidence()),
        ),
        (
            EntryPerson("director-a", "person-a", "director", evidence()),
            EntryPerson("director-a", "person-b", "director", evidence()),
            EntryPerson("actor-a", "person-a", "actor", evidence()),
            EntryPerson("song-a-1", "writer-a", "other", evidence()),
            EntryPerson("song-a-1", "writer-b", "other", evidence()),
            EntryPerson("song-a-2", "writer-a", "other", evidence()),
        ),
        (NominationCoverage("current", None, evidence()),),
    )


def row(frame, entry="picture-a", product="early_read"):
    selected = frame[
        (frame.ballot_entry_id == entry) & (frame.forecast_product == product)
    ]
    assert len(selected) == 1
    return selected.iloc[0]


def test_distinct_ballot_grain_both_products_and_no_results():
    inputs = base()
    frame = build_feature_snapshots(inputs)
    assert len(frame) == 12
    for product in ("early_read", "primary"):
        snapshot = row(frame, product=product)
        assert snapshot.field_size == 2
        assert snapshot.expected_nominees == 2
        assert snapshot.same_film_nominations == 5
        assert snapshot.same_film_nominations_status == "available"
        assert row(frame, "song-a-1", product).field_size == 2
        assert snapshot.cutoff_operator == ("<=" if product == "early_read" else "<")
        assert row(frame, "song-a-2", product).prior_oscar_wins_status == (
            "category_not_applicable"
        )
    # Adding current victories changes input identity, never feature values.
    with_wins = replace(
        inputs, entries=tuple(replace(e, win=evidence()) for e in inputs.entries)
    )
    changed = build_feature_snapshots(with_wins)
    pd.testing.assert_frame_equal(
        frame.drop(columns="data_snapshot_id"), changed.drop(columns="data_snapshot_id")
    )
    assert "winner" not in frame and "win" not in frame


def test_nomination_observations_obey_both_exact_boundaries():
    inputs = base()
    deltas = [
        ("early-at", EARLY, {"early_read", "primary"}),
        ("early-after", EARLY + timedelta(microseconds=1), {"primary"}),
        ("primary-before", PRIMARY - timedelta(microseconds=1), {"primary"}),
        ("primary-at", PRIMARY, set()),
        ("primary-after", PRIMARY + timedelta(microseconds=1), set()),
        ("unknown", None, set()),
        ("date-only", EARLY, set()),
    ]
    extra = tuple(
        BallotEntry(
            name,
            "current",
            "song",
            "film-a",
            evidence(
                at,
                "date_only"
                if name == "date-only"
                else "unknown"
                if at is None
                else "verified",
            ),
        )
        for name, at, _ in deltas
    )
    frame = build_feature_snapshots(
        replace(
            inputs,
            entries=inputs.entries + extra,
            rules=tuple(replace(r, expected_nominees=None) for r in inputs.rules),
        )
    )
    for name, _, products in deltas:
        assert (
            set(frame.loc[frame.ballot_entry_id == name, "forecast_product"])
            == products
        )
    early, primary = row(frame), row(frame, product="primary")
    assert early.same_film_nominations_observed == 6
    assert primary.same_film_nominations_observed == 8
    # Even a claimed complete source cannot turn excluded rows into known totals.
    assert pd.isna(early.same_film_nominations)
    assert early.same_film_nominations_reason == "nomination_observation_unavailable"


def test_career_history_pre2010_results_independent_and_recipient_union():
    inputs = base()
    old_nomination = BallotEntry(
        "old-nomination",
        "old-2008",
        "directing",
        "old-film",
        evidence(PAST),
        evidence(EARLY + timedelta(microseconds=1)),
    )
    old_win = BallotEntry(
        "old-win",
        "old-2007",
        "actor_leading",
        "older-film",
        evidence(PRIMARY),
        evidence(EARLY),
    )
    future_win = BallotEntry(
        "future-win",
        "future",
        "directing",
        "future-film",
        evidence(PAST),
        evidence(PAST),
    )
    inputs = replace(
        inputs,
        ceremonies=inputs.ceremonies
        + (
            Ceremony("old-2008", 2008),
            Ceremony("old-2007", 2007),
            Ceremony("future", 2024),
        ),
        rules=inputs.rules
        + (
            rule("directing", "directing", 1, "old-2008"),
            rule("actor_leading", "acting", 1, "old-2007"),
            rule("directing", "directing", 1, "future"),
        ),
        entries=inputs.entries + (old_nomination, old_win, future_win),
        people=inputs.people
        + (
            EntryPerson("old-nomination", "person-a", "director", evidence(PAST)),
            EntryPerson("old-nomination", "person-b", "director", evidence(PAST)),
            EntryPerson("old-win", "person-a", "actor", evidence(PAST)),
            EntryPerson("future-win", "person-a", "director", evidence(PAST)),
        ),
        career_coverage=tuple(
            CareerCoverage(p, 2022, evidence(), evidence())
            for p in ("person-a", "person-b")
        ),
    )
    frame = build_feature_snapshots(inputs)
    early = row(frame, "director-a")
    primary = row(frame, "director-a", "primary")
    # Shared older co-director entry is counted once; future/current wins excluded.
    assert early.prior_oscar_nominations_observed == 1
    assert primary.prior_oscar_nominations_observed == 1
    assert pd.isna(early.prior_oscar_nominations)
    assert early.prior_oscar_nominations_reason == "history_observation_unavailable"
    assert early.prior_oscar_wins_observed == 1  # No eligible nomination is required.
    assert pd.isna(early.prior_oscar_wins)  # Another older result is still unavailable.
    assert primary.prior_oscar_wins == 2
    # Without the unavailable old nomination, complete lifetime nomination count works.
    known = replace(
        inputs,
        entries=tuple(
            replace(e, nomination=evidence(PAST))
            if e.ballot_entry_id == "old-win"
            else e
            for e in inputs.entries
        ),
    )
    assert (
        row(build_feature_snapshots(known), "director-a").prior_oscar_nominations == 2
    )
    # Unknown positive result timing is missing, never an invented negative.
    unknown = replace(
        inputs,
        entries=tuple(
            replace(e, win=AvailabilityEvidence())
            if e.ballot_entry_id == "old-win"
            else e
            for e in inputs.entries
        ),
    )
    assert pd.isna(
        row(build_feature_snapshots(unknown), "director-a", "primary").prior_oscar_wins
    )


def test_mapped_precursors_exact_contest_person_and_film_not_any_guild_win():
    inputs = base()
    inputs = replace(
        inputs,
        precursor_events=(
            PrecursorEvent("pga", "current", "PGA", "picture", evidence(), evidence()),
            PrecursorEvent(
                "dga", "current", "DGA", "directing", evidence(), evidence()
            ),
            PrecursorEvent(
                "sag", "current", "SAG", "actor_leading", evidence(), evidence()
            ),
            PrecursorEvent(
                "other-sag", "current", "SAG", "ensemble", evidence(), evidence()
            ),
        ),
        precursor_entries=(
            PrecursorEntry("pga-a", "pga", "film-a", None, evidence(), evidence(EARLY)),
            PrecursorEntry(
                "dga-other-film", "dga", "film-b", "person-a", evidence(), evidence()
            ),
            PrecursorEntry(
                "sag-wrong-person",
                "sag",
                "film-a",
                "another-person",
                evidence(),
                evidence(),
            ),
            PrecursorEntry(
                "sag-ensemble", "other-sag", "film-a", None, evidence(), evidence()
            ),
        ),
    )
    frame = build_feature_snapshots(inputs)
    assert row(frame).won_mapped_precursor == 1
    assert row(frame).won_mapped_precursor_picture == 1
    assert row(frame).won_mapped_precursor_acting == 0
    assert row(frame, "picture-b").nominated_mapped_precursor == 0
    for entry in ("director-a", "actor-a"):
        assert row(frame, entry).nominated_mapped_precursor_status == "not_nominated"
        assert row(frame, entry).won_mapped_precursor == 0
    assert (
        row(frame, "song-a-1").won_mapped_precursor_status == "category_not_applicable"
    )


def test_precursor_nomination_win_dates_independent_and_event_statuses():
    inputs = replace(
        base(),
        precursor_events=(
            PrecursorEvent(
                "pga",
                "current",
                "PGA",
                "picture",
                evidence(),
                evidence(PRIMARY),
                EARLY + timedelta(days=2),
                evidence(NOMINATIONS - timedelta(days=1)),
            ),
        ),
        precursor_entries=(
            PrecursorEntry(
                "pga-a", "pga", "film-a", None, evidence(EARLY), evidence(PRIMARY)
            ),
        ),
    )
    frame = build_feature_snapshots(inputs)
    assert row(frame).nominated_mapped_precursor == 1
    assert row(frame).won_mapped_precursor_status == "event_not_yet_held"
    assert pd.isna(row(frame).won_mapped_precursor)
    assert row(frame, product="primary").won_mapped_precursor_reason == "after_cutoff"
    assert row(frame, "director-a").won_mapped_precursor_status == "source_missing"
    assert (
        row(frame, "song-a-1").won_mapped_precursor_status == "category_not_applicable"
    )
    # A positive, publicly known winner does not borrow the nominee's date.
    independent = replace(
        inputs,
        precursor_entries=(
            replace(
                inputs.precursor_entries[0],
                nomination=evidence(PRIMARY),
                win=evidence(EARLY),
            ),
        ),
        precursor_events=(replace(inputs.precursor_events[0], held_at=EARLY),),
    )
    snapshot = row(build_feature_snapshots(independent))
    assert pd.isna(snapshot.nominated_mapped_precursor)
    assert snapshot.won_mapped_precursor == 1
    # Unknown positive dates remain source-missing even with event completeness.
    unknown = replace(
        inputs,
        precursor_entries=(
            replace(
                inputs.precursor_entries[0],
                nomination=AvailabilityEvidence(),
                win=AvailabilityEvidence(),
            ),
        ),
        precursor_events=(
            replace(inputs.precursor_events[0], results_complete=evidence()),
        ),
    )
    snapshot = row(build_feature_snapshots(unknown))
    assert pd.isna(snapshot.nominated_mapped_precursor)
    assert pd.isna(snapshot.won_mapped_precursor)
    assert snapshot.won_mapped_precursor_reason == "timestamp_unknown_or_date_only"


def test_absent_sources_vs_known_complete_events_and_static_rule_evidence():
    inputs = replace(base(), nomination_coverage=())
    frame = build_feature_snapshots(inputs)
    snapshot = row(frame)
    assert snapshot.field_size_observed == 2 and pd.isna(snapshot.field_size)
    assert snapshot.same_film_nominations_observed == 5
    assert pd.isna(snapshot.same_film_nominations)
    assert snapshot.nominated_mapped_precursor_status == "source_missing"
    assert pd.isna(row(frame, "actor-a").prior_oscar_nominations)
    complete_empty = replace(
        inputs,
        precursor_events=(
            PrecursorEvent(
                "empty-pga", "current", "PGA", "picture", evidence(), evidence()
            ),
        ),
    )
    complete = row(build_feature_snapshots(complete_empty))
    assert complete.nominated_mapped_precursor == 0
    assert complete.nominated_mapped_precursor_status == "not_nominated"
    assert complete.won_mapped_precursor == 0
    unknown_rule = replace(
        inputs,
        rules=tuple(
            replace(r, availability=AvailabilityEvidence()) for r in inputs.rules
        ),
    )
    snapshot = row(build_feature_snapshots(unknown_rule))
    assert pd.isna(snapshot.category_family)
    assert pd.isna(snapshot.expected_nominees)
    assert snapshot.rule_status == "source_missing"
    assert snapshot.won_mapped_precursor_reason == "category_rule_unavailable"


def test_manifest_truthful_fixture_counts_eligible_win_seasons_and_stable_hash():
    inputs = replace(
        base(),
        precursor_events=(
            PrecursorEvent("pga", "current", "PGA", "picture"),
            PrecursorEvent("dga", "current", "DGA", "directing"),
        ),
        precursor_entries=(
            # Keep non-Oscar-nominated winners; eligibility doesn't require nominee timing.
            PrecursorEntry(
                "non-oscar",
                "pga",
                "non-oscar-film",
                None,
                AvailabilityEvidence(),
                evidence(EARLY),
            ),
            PrecursorEntry(
                "late-dga", "dga", "film-a", "person-a", evidence(), evidence(PRIMARY)
            ),
        ),
    )
    report = coverage_report(inputs)
    pga = report["products"]["early_read"]["mapped_precursors"]["PGA"]
    assert pga["eligible_win_seasons"] == [2023]
    assert pga["eligible_win_season_count"] == 1
    assert pga["eligible_nomination_events"] == 0
    assert pga["matched_win_signal_rows"] == 0
    assert (
        report["products"]["primary"]["mapped_precursors"]["DGA"]["eligible_win_events"]
        == 0
    )
    manifest = feature_manifest(inputs)
    assert manifest["input_status"] == "synthetic_fixture"
    assert manifest["coverage"]["real_data_coverage_verified"] is False
    assert manifest["input_counts"]["entries"] == 6
    assert len(manifest["data_snapshot_id"]) == 64
    json.dumps(manifest, allow_nan=False)
    reordered = replace(
        inputs,
        entries=tuple(reversed(inputs.entries)),
        people=tuple(reversed(inputs.people)),
    )
    assert (
        feature_manifest(reordered)["data_snapshot_id"] == manifest["data_snapshot_id"]
    )
    empty = replace(
        inputs,
        entries=(),
        people=(),
        precursor_entries=(),
        nomination_coverage=(),
        rules=(),
    )
    assert build_feature_snapshots(empty).empty
    assert coverage_report(empty)["products"]["early_read"]["snapshot_rows"] == 0


def test_reject_duplicate_broken_identity_rule_and_timestamp_contracts():
    inputs = base()
    invalid = [
        (
            replace(inputs, entries=inputs.entries + (inputs.entries[0],)),
            "duplicate ballot",
        ),
        (
            replace(inputs, people=inputs.people + (inputs.people[0],)),
            "duplicate entry/person",
        ),
        (
            replace(
                inputs, people=(replace(inputs.people[0], ballot_entry_id="absent"),)
            ),
            "broken entry/person",
        ),
        (
            replace(
                inputs, entries=(replace(inputs.entries[0], category_id="absent"),)
            ),
            "unknown contest",
        ),
        (
            replace(
                inputs, rules=(replace(inputs.rules[0], category_family="acting"),)
            ),
            "conflicts with mapping",
        ),
        (
            replace(inputs, people=(replace(inputs.people[0], role="actor"),)),
            "role conflicts",
        ),
        (replace(inputs, input_status="verified_real_data"), "input_status"),
        (replace(inputs, entries=list(inputs.entries)), "tuple"),
        (
            replace(
                inputs,
                rules=tuple(replace(r, expected_nominees=99) for r in inputs.rules),
            ),
            "expected_nominees",
        ),
        (
            replace(
                inputs,
                precursor_entries=(
                    PrecursorEntry(
                        "broken", "absent-event", "film-a", None, evidence()
                    ),
                ),
            ),
            "broken precursor",
        ),
        (
            replace(
                inputs,
                precursor_events=(
                    PrecursorEvent("dga", "current", "DGA", "directing"),
                ),
                precursor_entries=(
                    PrecursorEntry("no-person", "dga", "film-a", None, evidence()),
                ),
            ),
            "exact mapped entity",
        ),
        (
            replace(
                inputs,
                precursor_events=(
                    PrecursorEvent(
                        "pga",
                        "current",
                        "PGA",
                        "picture",
                        held_at=NOMINATIONS.replace(tzinfo=None),
                    ),
                ),
            ),
            "timezone-aware",
        ),
    ]
    for contract, message in invalid:
        with pytest.raises(ValueError, match=message):
            build_feature_snapshots(contract)
    with pytest.raises(ValueError, match="timezone-aware"):
        AvailabilityEvidence(NOMINATIONS.replace(tzinfo=None), "verified", "fixture")
    with pytest.raises(ValueError, match="timestamp_status"):
        evidence(status="guessed")
