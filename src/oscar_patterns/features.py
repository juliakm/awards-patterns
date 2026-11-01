"""Leakage-safe, source-agnostic feature transforms (no acquisition or fitting).

Inputs are assertions from reviewed upstream records, not automatic source
verification. IDs are exact, reviewed identities; no title/person fuzzy joins.
Each nomination and positive win has independent public-availability evidence.
Ceremonies without cutoffs supply older career history, including pre-2010.

Completeness evidence is indispensable for negatives and totals:
``NominationCoverage(category_id=None)`` covers *all* competitive season entries;
category coverage covers one entire ballot. ``CareerCoverage`` asserts complete
lifetime acting/directing history through its year, not just the research window.
Precursor nomination/result completeness covers the entire exact event contest,
including nominees/winners who were not Oscar nominees. Missing assertions never
become zero. Observed count columns are lower-bound diagnostics, not totals.

Current career features count the union of distinct earlier ballot entries
credited to any available current actor/director recipient. Multiple recipients
do not multiply a shared historical ballot entry. Only acting/directing credits
in acting/directing contests contribute. Neither current nor later Oscar wins
are output or used. Metadata, revenue, reviews, popularity and pundits are excluded.

Schedules, rules, completeness and publication evidence must be source-reviewed
before real use. Fixtures prove transform behavior, not real coverage, permissions,
historical availability, model performance or official schedule verification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import pandas as pd

from oscar_patterns.forecast_policy import (
    POLICY_VERSION,
    PRODUCTS,
    AvailabilityEvidence,
    ForecastCutoffs,
    is_strictly_eligible,
)

FEATURE_VERSION = "1.0.0"
MAPPED_CONTESTS = {
    "directing": ("DGA", "directing", "directing"),
    "picture": ("PGA", "picture", "picture"),
    "actor_leading": ("SAG", "actor_leading", "acting"),
    "actress_leading": ("SAG", "actress_leading", "acting"),
    "actor_supporting": ("SAG", "actor_supporting", "acting"),
    "actress_supporting": ("SAG", "actress_supporting", "acting"),
}
_CAREER_ROLES = {"actor": "acting", "director": "directing"}
_NUMERIC_COLUMNS = (
    "ceremony_year",
    "expected_nominees",
    "field_size",
    "field_size_observed",
    "same_film_nominations",
    "same_film_nominations_observed",
    "prior_oscar_nominations",
    "prior_oscar_nominations_observed",
    "prior_oscar_wins",
    "prior_oscar_wins_observed",
    "nominated_mapped_precursor",
    "won_mapped_precursor",
    "nominated_mapped_precursor_acting",
    "won_mapped_precursor_acting",
    "nominated_mapped_precursor_directing",
    "won_mapped_precursor_directing",
    "nominated_mapped_precursor_picture",
    "won_mapped_precursor_picture",
)
OUTPUT_COLUMNS = (
    "ceremony_id",
    "ceremony_year",
    "category_id",
    "ballot_entry_id",
    "film_id",
    "forecast_product",
    "cutoff_at",
    "cutoff_operator",
    "policy_version",
    "feature_version",
    "data_snapshot_id",
    "input_status",
    "category_family",
    "original_category_label",
    "rule_regime",
    "expected_nominees",
    "rule_status",
    "rule_reason",
    "field_size",
    "field_size_observed",
    "field_size_status",
    "field_size_reason",
    "same_film_nominations",
    "same_film_nominations_observed",
    "same_film_nominations_status",
    "same_film_nominations_reason",
    "prior_oscar_nominations",
    "prior_oscar_nominations_observed",
    "prior_oscar_nominations_status",
    "prior_oscar_nominations_reason",
    "prior_oscar_wins",
    "prior_oscar_wins_observed",
    "prior_oscar_wins_status",
    "prior_oscar_wins_reason",
    "mapped_precursor_guild",
    "nominated_mapped_precursor",
    "nominated_mapped_precursor_status",
    "nominated_mapped_precursor_reason",
    "won_mapped_precursor",
    "won_mapped_precursor_status",
    "won_mapped_precursor_reason",
    "nominated_mapped_precursor_acting",
    "won_mapped_precursor_acting",
    "nominated_mapped_precursor_directing",
    "won_mapped_precursor_directing",
    "nominated_mapped_precursor_picture",
    "won_mapped_precursor_picture",
)


@dataclass(frozen=True)
class Ceremony:
    ceremony_id: str
    ceremony_year: int
    cutoffs: ForecastCutoffs | None = None
    schedule_reference: str | None = None


@dataclass(frozen=True)
class CategoryRule:
    ceremony_id: str
    category_id: str
    category_family: str
    original_label: str
    rule_regime: str
    expected_nominees: int | None
    availability: AvailabilityEvidence


@dataclass(frozen=True)
class BallotEntry:
    ballot_entry_id: str
    ceremony_id: str
    category_id: str
    film_id: str | None
    nomination: AvailabilityEvidence
    win: AvailabilityEvidence | None = None


@dataclass(frozen=True)
class EntryPerson:
    ballot_entry_id: str
    person_id: str
    role: str
    availability: AvailabilityEvidence


@dataclass(frozen=True)
class NominationCoverage:
    ceremony_id: str
    category_id: str | None
    complete: AvailabilityEvidence


@dataclass(frozen=True)
class CareerCoverage:
    """Complete lifetime history through this year; nomination/results separate."""

    person_id: str
    through_ceremony_year: int
    nominations_complete: AvailabilityEvidence
    wins_complete: AvailabilityEvidence


@dataclass(frozen=True)
class PrecursorEvent:
    """One guild contest mapped to an Oscar ceremony, not event calendar year.

    ``held_at`` is occurrence, NOT public result availability. A known future
    event requires eligible ``schedule`` evidence to report not-yet-held.
    Unknown times remain None; never create midnight dates.
    """

    event_id: str
    ceremony_id: str
    guild: str
    contest_category: str
    nominations_complete: AvailabilityEvidence = field(
        default_factory=AvailabilityEvidence
    )
    results_complete: AvailabilityEvidence = field(default_factory=AvailabilityEvidence)
    held_at: datetime | None = None
    schedule: AvailabilityEvidence = field(default_factory=AvailabilityEvidence)


@dataclass(frozen=True)
class PrecursorEntry:
    precursor_entry_id: str
    event_id: str
    film_id: str
    person_id: str | None
    nomination: AvailabilityEvidence
    win: AvailabilityEvidence | None = None


@dataclass(frozen=True)
class FeatureInputs:
    """Immutable transform contract. ``source_records`` does not certify sources."""

    snapshot_label: str
    input_status: str
    ceremonies: tuple[Ceremony, ...]
    rules: tuple[CategoryRule, ...]
    entries: tuple[BallotEntry, ...]
    people: tuple[EntryPerson, ...] = ()
    nomination_coverage: tuple[NominationCoverage, ...] = ()
    career_coverage: tuple[CareerCoverage, ...] = ()
    precursor_events: tuple[PrecursorEvent, ...] = ()
    precursor_entries: tuple[PrecursorEntry, ...] = ()


def _text(value: object, name: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a nonblank, trimmed string")


def _year(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 9999:
        raise ValueError(f"{name} must be an integer year in 1..9999")


def _time(value: object, name: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(f"{name} must be a timezone-aware datetime")


def _evidence(value: object, name: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, AvailabilityEvidence):
        raise ValueError(f"{name} must be AvailabilityEvidence")
    for attr in ("available_at", "retrieved_at"):
        if getattr(value, attr) is not None:
            _time(getattr(value, attr), f"{name}.{attr}")
    if value.evidence_reference is not None:
        _text(value.evidence_reference, f"{name}.evidence_reference")


def _unique(records: tuple, key, name: str) -> dict:
    result = {}
    for record in records:
        identity = key(record)
        if identity in result:
            raise ValueError(f"duplicate {name}: {identity!r}")
        result[identity] = record
    return result


def validate_inputs(inputs: FeatureInputs) -> None:
    """Reject duplicate identities, broken bridges and malformed contracts."""
    if not isinstance(inputs, FeatureInputs):
        raise ValueError("inputs must be FeatureInputs")
    _text(inputs.snapshot_label, "snapshot_label")
    if inputs.input_status not in ("synthetic_fixture", "source_records"):
        raise ValueError("input_status must be synthetic_fixture or source_records")
    types = {
        "ceremonies": Ceremony,
        "rules": CategoryRule,
        "entries": BallotEntry,
        "people": EntryPerson,
        "nomination_coverage": NominationCoverage,
        "career_coverage": CareerCoverage,
        "precursor_events": PrecursorEvent,
        "precursor_entries": PrecursorEntry,
    }
    for name, record_type in types.items():
        records = getattr(inputs, name)
        if not isinstance(records, tuple) or any(
            not isinstance(record, record_type) for record in records
        ):
            raise ValueError(f"{name} must be a tuple of {record_type.__name__}")
    ceremonies = _unique(inputs.ceremonies, lambda r: r.ceremony_id, "ceremony")
    _unique(inputs.ceremonies, lambda r: r.ceremony_year, "ceremony year")
    rules = _unique(
        inputs.rules, lambda r: (r.ceremony_id, r.category_id), "category rule"
    )
    entries = _unique(inputs.entries, lambda r: r.ballot_entry_id, "ballot entry")
    _unique(
        inputs.people,
        lambda r: (r.ballot_entry_id, r.person_id, r.role),
        "entry/person/role bridge",
    )
    _unique(
        inputs.nomination_coverage,
        lambda r: (r.ceremony_id, r.category_id),
        "nomination coverage",
    )
    _unique(
        inputs.career_coverage,
        lambda r: (r.person_id, r.through_ceremony_year),
        "career coverage",
    )
    events = _unique(inputs.precursor_events, lambda r: r.event_id, "precursor event")
    _unique(
        inputs.precursor_events,
        lambda r: (r.ceremony_id, r.guild, r.contest_category),
        "precursor contest",
    )
    _unique(
        inputs.precursor_entries,
        lambda r: r.precursor_entry_id,
        "precursor entry",
    )
    _unique(
        inputs.precursor_entries,
        lambda r: (r.event_id, r.film_id, r.person_id),
        "precursor entity",
    )
    for ceremony in inputs.ceremonies:
        _text(ceremony.ceremony_id, "ceremony_id")
        _year(ceremony.ceremony_year, "ceremony_year")
        if ceremony.cutoffs is not None:
            if not isinstance(ceremony.cutoffs, ForecastCutoffs):
                raise ValueError("cutoffs must be ForecastCutoffs")
            _text(ceremony.schedule_reference, "schedule_reference")
    for rule in inputs.rules:
        for name in (
            "ceremony_id",
            "category_id",
            "category_family",
            "original_label",
            "rule_regime",
        ):
            _text(getattr(rule, name), name)
        if rule.ceremony_id not in ceremonies:
            raise ValueError(f"category rule has unknown ceremony: {rule.ceremony_id}")
        mapping = MAPPED_CONTESTS.get(rule.category_id)
        if mapping and rule.category_family != mapping[2]:
            raise ValueError(
                f"category family conflicts with mapping: {rule.category_id}"
            )
        if rule.expected_nominees is not None and (
            isinstance(rule.expected_nominees, bool)
            or not isinstance(rule.expected_nominees, int)
            or rule.expected_nominees < 1
        ):
            raise ValueError("expected_nominees must be a positive integer or None")
        _evidence(rule.availability, "rule availability")
    for entry in inputs.entries:
        for name in ("ballot_entry_id", "ceremony_id", "category_id"):
            _text(getattr(entry, name), name)
        _text(entry.film_id, "film_id", nullable=True)
        if (entry.ceremony_id, entry.category_id) not in rules:
            raise ValueError(
                f"ballot entry has unknown contest: {entry.ballot_entry_id}"
            )
        _evidence(entry.nomination, "nomination")
        _evidence(entry.win, "win", nullable=True)
    for bridge in inputs.people:
        _text(bridge.person_id, "person_id")
        if bridge.ballot_entry_id not in entries:
            raise ValueError(f"broken entry/person bridge: {bridge.ballot_entry_id}")
        if bridge.role not in (*_CAREER_ROLES, "other"):
            raise ValueError("bridge role must be actor, director or other")
        entry = entries[bridge.ballot_entry_id]
        family = rules[(entry.ceremony_id, entry.category_id)].category_family
        if bridge.role in _CAREER_ROLES and family != _CAREER_ROLES[bridge.role]:
            raise ValueError(
                f"bridge role conflicts with contest: {bridge.ballot_entry_id}"
            )
        _evidence(bridge.availability, "bridge availability")
    for coverage in inputs.nomination_coverage:
        if coverage.ceremony_id not in ceremonies or (
            coverage.category_id is not None
            and (coverage.ceremony_id, coverage.category_id) not in rules
        ):
            raise ValueError("nomination coverage has unknown ceremony/contest")
        _evidence(coverage.complete, "nomination completeness")
    for coverage in inputs.career_coverage:
        _text(coverage.person_id, "career person_id")
        _year(coverage.through_ceremony_year, "through_ceremony_year")
        _evidence(coverage.nominations_complete, "career nomination completeness")
        _evidence(coverage.wins_complete, "career win completeness")
    for event in inputs.precursor_events:
        _text(event.event_id, "event_id")
        _text(event.contest_category, "contest_category")
        if event.ceremony_id not in ceremonies:
            raise ValueError(f"precursor event has unknown ceremony: {event.event_id}")
        if event.guild not in ("DGA", "PGA", "SAG"):
            raise ValueError("precursor guild must be DGA, PGA or SAG")
        _evidence(event.nominations_complete, "precursor nomination completeness")
        _evidence(event.results_complete, "precursor result completeness")
        _evidence(event.schedule, "precursor schedule")
        if event.held_at is not None:
            _time(event.held_at, "held_at")
    for entry in inputs.precursor_entries:
        _text(entry.precursor_entry_id, "precursor_entry_id")
        _text(entry.film_id, "precursor film_id")
        _text(entry.person_id, "precursor person_id", nullable=True)
        if entry.event_id not in events:
            raise ValueError(f"broken precursor event bridge: {entry.event_id}")
        event = events[entry.event_id]
        if (
            (
                event.guild == "PGA"
                and event.contest_category == "picture"
                and entry.person_id is not None
            )
            or (event.guild, event.contest_category)
            in {
                (guild, category)
                for guild, category, _ in MAPPED_CONTESTS.values()
                if guild != "PGA"
            }
            and entry.person_id is None
        ):
            raise ValueError(
                f"precursor requires exact mapped entity: {entry.event_id}"
            )
        _evidence(entry.nomination, "precursor nomination")
        _evidence(entry.win, "precursor win", nullable=True)


def _eligible(evidence, cutoffs, product) -> bool:
    return evidence is not None and is_strictly_eligible(evidence, cutoffs, product)


def _missing_reason(evidence, cutoffs, product) -> str:
    if evidence is None:
        return "coverage_absent"
    if evidence.timestamp_status != "verified" or evidence.available_at is None:
        return "timestamp_unknown_or_date_only"
    if not evidence.evidence_reference:
        return "evidence_reference_missing"
    if not _eligible(evidence, cutoffs, product):
        return "after_cutoff"
    return "available"


def _put(row, name, value, status, reason) -> None:
    row[name] = value
    row[f"{name}_status"] = status
    row[f"{name}_reason"] = reason


def _snapshot_id(inputs: FeatureInputs) -> str:
    payload = asdict(inputs)
    for name, value in payload.items():
        if isinstance(value, tuple):
            payload[name] = sorted(
                value,
                key=lambda record: json.dumps(
                    record, default=_serialize, sort_keys=True
                ),
            )
    canonical = json.dumps(
        {
            "feature_version": FEATURE_VERSION,
            "policy_version": POLICY_VERSION,
            "inputs": payload,
        },
        default=_serialize,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def _serialize(value):
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _career(row, inputs, entry, ceremony, rules, people, cutoffs, product):
    rule = rules[(entry.ceremony_id, entry.category_id)]
    current = people.get(entry.ballot_entry_id, ())
    applicable = _eligible(rule.availability, cutoffs, product)
    for feature, evidence_attr, coverage_attr in (
        ("prior_oscar_nominations", "nomination", "nominations_complete"),
        ("prior_oscar_wins", "win", "wins_complete"),
    ):
        row[f"{feature}_observed"] = None
        if applicable and rule.category_family not in _CAREER_ROLES.values():
            _put(
                row, feature, None, "category_not_applicable", "not_acting_or_directing"
            )
            continue
        credited = {
            bridge.person_id
            for bridge in current
            if bridge.role in _CAREER_ROLES
            and _eligible(bridge.availability, cutoffs, product)
        }
        if (
            not applicable
            or not credited
            or any(
                bridge.role in _CAREER_ROLES
                and not _eligible(bridge.availability, cutoffs, product)
                for bridge in current
            )
        ):
            _put(
                row,
                feature,
                None,
                "source_missing",
                "current_credit_or_rule_unavailable",
            )
            continue
        observed = set()
        unavailable_history = False
        for older in inputs.entries:
            if (
                ceremony[older.ceremony_id].ceremony_year
                >= ceremony[entry.ceremony_id].ceremony_year
            ):
                continue
            relevant_bridges = [
                bridge
                for bridge in people.get(older.ballot_entry_id, ())
                if bridge.person_id in credited and bridge.role in _CAREER_ROLES
            ]
            observation = getattr(older, evidence_attr)
            if not relevant_bridges or observation is None:
                continue
            older_rule = rules[(older.ceremony_id, older.category_id)]
            if (
                not _eligible(older_rule.availability, cutoffs, product)
                or not _eligible(observation, cutoffs, product)
                or any(
                    not _eligible(b.availability, cutoffs, product)
                    for b in relevant_bridges
                )
            ):
                unavailable_history = True
                continue
            observed.add(older.ballot_entry_id)
        row[f"{feature}_observed"] = len(observed)
        complete = (
            all(
                any(
                    c.person_id == person
                    and c.through_ceremony_year
                    >= ceremony[entry.ceremony_id].ceremony_year - 1
                    and _eligible(getattr(c, coverage_attr), cutoffs, product)
                    for c in inputs.career_coverage
                )
                for person in credited
            )
            and not unavailable_history
        )
        _put(
            row,
            feature,
            len(observed) if complete else None,
            "available" if complete else "source_missing",
            "complete_lifetime_history"
            if complete
            else (
                "history_observation_unavailable"
                if unavailable_history
                else "lifetime_coverage_unavailable"
            ),
        )


def _precursor(row, inputs, entry, people, cutoffs, product):
    mapping = MAPPED_CONTESTS.get(entry.category_id)
    features = ("nominated_mapped_precursor", "won_mapped_precursor")
    if row["rule_status"] != "available":
        row["mapped_precursor_guild"] = None
        for feature in features:
            _put(row, feature, None, "source_missing", "category_rule_unavailable")
        return
    if mapping is None:
        row["mapped_precursor_guild"] = None
        for feature in features:
            _put(row, feature, None, "category_not_applicable", "no_launch_mapping")
        return
    guild, contest, family = mapping
    row["mapped_precursor_guild"] = guild
    event = next(
        (
            event
            for event in inputs.precursor_events
            if (event.ceremony_id, event.guild, event.contest_category)
            == (entry.ceremony_id, guild, contest)
        ),
        None,
    )
    bridges = people.get(entry.ballot_entry_id, ())
    role = "director" if guild == "DGA" else "actor"
    identities = {
        bridge.person_id
        for bridge in bridges
        if bridge.role == role and _eligible(bridge.availability, cutoffs, product)
    }
    if (
        event is None
        or entry.film_id is None
        or (
            guild != "PGA"
            and (
                not identities
                or any(
                    bridge.role == role
                    and not _eligible(bridge.availability, cutoffs, product)
                    for bridge in bridges
                )
            )
        )
    ):
        for feature in features:
            _put(row, feature, None, "source_missing", "event_or_identity_unavailable")
        return
    matches = [
        p
        for p in inputs.precursor_entries
        if p.event_id == event.event_id
        and p.film_id == entry.film_id
        and (guild == "PGA" or p.person_id in identities)
    ]
    for feature, attribute, complete in (
        (features[0], "nomination", event.nominations_complete),
        (features[1], "win", event.results_complete),
    ):
        evidence = [getattr(match, attribute) for match in matches]
        if any(_eligible(e, cutoffs, product) for e in evidence):
            _put(
                row,
                feature,
                1,
                "nominated" if attribute == "nomination" else "won",
                "matched_public_observation",
            )
        elif any(
            e is not None and _missing_reason(e, cutoffs, product) != "after_cutoff"
            for e in evidence
        ):
            reason = next(
                _missing_reason(e, cutoffs, product)
                for e in evidence
                if e is not None
                and _missing_reason(e, cutoffs, product) != "after_cutoff"
            )
            _put(row, feature, None, "source_missing", reason)
        elif (
            attribute == "win"
            and event.held_at is not None
            and (
                _eligible(event.schedule, cutoffs, product)
                and (
                    event.held_at > cutoffs.early_read_at
                    if product == "early_read"
                    else event.held_at >= cutoffs.primary_before
                )
            )
        ):
            _put(row, feature, None, "event_not_yet_held", "verified_schedule")
        elif any(e is not None for e in evidence):
            _put(row, feature, None, "source_missing", "after_cutoff")
        elif _eligible(complete, cutoffs, product):
            status = "not_nominated" if attribute == "nomination" else "not_won"
            _put(row, feature, 0, status, "complete_exact_event_contest")
        else:
            _put(
                row,
                feature,
                None,
                "source_missing",
                _missing_reason(complete, cutoffs, product),
            )
    for interaction_family in ("acting", "directing", "picture"):
        for feature in features:
            # Only a verified mapped value yields an interaction, never missing=0.
            value = row[feature]
            row[f"{feature}_{interaction_family}"] = (
                None if value is None else value if family == interaction_family else 0
            )


def build_feature_snapshots(inputs: FeatureInputs) -> pd.DataFrame:
    """Return one row per eligible nominee/product, with nullable strict features.

    Entries with unknown or post-cutoff nominations are omitted even if their
    winner is known. Rules and coverage must independently be eligible. No
    imputation, training, outcome attachment or permission approval occurs here.
    """
    validate_inputs(inputs)
    snapshot_id = _snapshot_id(inputs)
    ceremonies = {c.ceremony_id: c for c in inputs.ceremonies}
    rules = {(r.ceremony_id, r.category_id): r for r in inputs.rules}
    coverage = {
        (c.ceremony_id, c.category_id): c.complete for c in inputs.nomination_coverage
    }
    people = {}
    for bridge in inputs.people:
        people.setdefault(bridge.ballot_entry_id, []).append(bridge)
    rows = []
    for ceremony in sorted(
        inputs.ceremonies, key=lambda c: (c.ceremony_year, c.ceremony_id)
    ):
        if ceremony.cutoffs is None:
            continue
        cutoffs = ceremony.cutoffs
        for product in PRODUCTS:
            available = [
                entry
                for entry in inputs.entries
                if entry.ceremony_id == ceremony.ceremony_id
                and _eligible(entry.nomination, cutoffs, product)
            ]
            for entry in sorted(
                available, key=lambda e: (e.category_id, e.ballot_entry_id)
            ):
                row = dict.fromkeys(OUTPUT_COLUMNS)
                row.update(
                    ceremony_id=entry.ceremony_id,
                    ceremony_year=ceremony.ceremony_year,
                    category_id=entry.category_id,
                    ballot_entry_id=entry.ballot_entry_id,
                    film_id=entry.film_id,
                    forecast_product=product,
                    cutoff_at=(
                        cutoffs.early_read_at
                        if product == "early_read"
                        else cutoffs.primary_before
                    ),
                    cutoff_operator="<=" if product == "early_read" else "<",
                    policy_version=POLICY_VERSION,
                    feature_version=FEATURE_VERSION,
                    data_snapshot_id=snapshot_id,
                    input_status=inputs.input_status,
                )
                rule = rules[(entry.ceremony_id, entry.category_id)]
                rule_ok = _eligible(rule.availability, cutoffs, product)
                row.update(
                    category_family=rule.category_family if rule_ok else None,
                    original_category_label=rule.original_label if rule_ok else None,
                    rule_regime=rule.rule_regime if rule_ok else None,
                    expected_nominees=rule.expected_nominees if rule_ok else None,
                    rule_status="available" if rule_ok else "source_missing",
                    rule_reason=_missing_reason(rule.availability, cutoffs, product),
                )
                for feature, matches, scope in (
                    (
                        "field_size",
                        [e for e in available if e.category_id == entry.category_id],
                        entry.category_id,
                    ),
                    (
                        "same_film_nominations",
                        [
                            e
                            for e in available
                            if entry.film_id is not None and e.film_id == entry.film_id
                        ],
                        None,
                    ),
                ):
                    if feature == "same_film_nominations" and entry.film_id is None:
                        row[f"{feature}_observed"] = None
                        _put(
                            row,
                            feature,
                            None,
                            "category_not_applicable",
                            "no_film_identity",
                        )
                        continue
                    count = len({e.ballot_entry_id for e in matches})
                    row[f"{feature}_observed"] = count
                    complete = coverage.get((entry.ceremony_id, scope))
                    if not _eligible(complete, cutoffs, product) and scope is not None:
                        complete = coverage.get((entry.ceremony_id, None), complete)
                    ok = _eligible(complete, cutoffs, product)
                    # A complete ballot cannot conceal an unknown/future nomination.
                    scoped = [
                        e
                        for e in inputs.entries
                        if e.ceremony_id == entry.ceremony_id
                        and (scope is None or e.category_id == scope)
                    ]
                    if ok and any(
                        not _eligible(e.nomination, cutoffs, product) for e in scoped
                    ):
                        ok = False
                        reason = "nomination_observation_unavailable"
                    else:
                        reason = _missing_reason(complete, cutoffs, product)
                    if (
                        feature == "field_size"
                        and ok
                        and rule_ok
                        and (
                            rule.expected_nominees is not None
                            and count != rule.expected_nominees
                        )
                    ):
                        raise ValueError(
                            f"complete ballot violates expected_nominees: "
                            f"{entry.ceremony_id}/{entry.category_id}"
                        )
                    _put(
                        row,
                        feature,
                        count if ok else None,
                        "available" if ok else "source_missing",
                        reason,
                    )
                _career(row, inputs, entry, ceremonies, rules, people, cutoffs, product)
                _precursor(row, inputs, entry, people, cutoffs, product)
                rows.append(row)
    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    for column in _NUMERIC_COLUMNS:
        result[column] = pd.array(result[column], dtype="Int64")
    return result


def coverage_report(inputs: FeatureInputs) -> dict:
    """Input/feature counts only, never empirical Oscar coverage/performance.

    Eligible-win seasons count exact mapped events with ANY timestamp-eligible
    winner (including non-Oscar nominees), independently of nomination dates.
    Signal rows additionally require a matching eligible Oscar nominee identity.
    """
    snapshots = build_feature_snapshots(inputs)
    by_product = {}
    for product in PRODUCTS:
        frame = snapshots[snapshots.forecast_product == product]
        event_counts = {}
        for guild in ("DGA", "PGA", "SAG"):
            eligible_events = []
            nomination_events = []
            for event in inputs.precursor_events:
                ceremony = next(
                    c for c in inputs.ceremonies if c.ceremony_id == event.ceremony_id
                )
                if (
                    ceremony.cutoffs is None
                    or not any(
                        (event.guild, event.contest_category) == (g, category)
                        for g, category, _ in MAPPED_CONTESTS.values()
                    )
                    or event.guild != guild
                ):
                    continue
                event_entries = [
                    e for e in inputs.precursor_entries if e.event_id == event.event_id
                ]
                if any(
                    _eligible(e.win, ceremony.cutoffs, product) for e in event_entries
                ):
                    eligible_events.append(event)
                if any(
                    _eligible(e.nomination, ceremony.cutoffs, product)
                    for e in event_entries
                ):
                    nomination_events.append(event)
            years = sorted(
                {
                    next(
                        c.ceremony_year
                        for c in inputs.ceremonies
                        if c.ceremony_id == e.ceremony_id
                    )
                    for e in eligible_events
                }
            )
            event_counts[guild] = {
                "eligible_nomination_events": len(nomination_events),
                "eligible_win_events": len(eligible_events),
                "eligible_win_seasons": years,
                "eligible_win_season_count": len(years),
                "matched_nomination_signal_rows": int(
                    (
                        (frame.mapped_precursor_guild == guild)
                        & (frame.nominated_mapped_precursor == 1)
                    ).sum()
                ),
                "matched_win_signal_rows": int(
                    (
                        (frame.mapped_precursor_guild == guild)
                        & (frame.won_mapped_precursor == 1)
                    ).sum()
                ),
            }
        target_entries = [
            e
            for e in inputs.entries
            if next(
                c for c in inputs.ceremonies if c.ceremony_id == e.ceremony_id
            ).cutoffs
            is not None
        ]
        by_product[product] = {
            "snapshot_rows": len(frame),
            "omitted_nomination_rows": len(target_entries) - len(frame),
            "contests": len(frame[["ceremony_id", "category_id"]].drop_duplicates()),
            "feature_status_counts": {
                column.removesuffix("_status"): {
                    str(status): int(count)
                    for status, count in frame[column].value_counts().items()
                }
                for column in frame.columns
                if column.endswith("_status") and column != "input_status"
            },
            "mapped_precursors": event_counts,
        }
    return {
        "input_status": inputs.input_status,
        "coverage_basis": "input_assertions_only_not_independent_source_validation",
        "real_data_coverage_verified": False,
        "products": by_product,
    }


def feature_manifest(inputs: FeatureInputs) -> dict:
    """JSON-ready reproducible specification and fixture/source-input report."""
    report = coverage_report(inputs)
    return {
        "feature_version": FEATURE_VERSION,
        "policy_version": POLICY_VERSION,
        "snapshot_label": inputs.snapshot_label,
        "data_snapshot_id": _snapshot_id(inputs),
        "snapshot_hash_scope": "canonical_feature_input_contract_not_upstream_source_files",
        "input_status": inputs.input_status,
        "input_counts": {
            name: len(getattr(inputs, name))
            for name in (
                "ceremonies",
                "rules",
                "entries",
                "people",
                "nomination_coverage",
                "career_coverage",
                "precursor_events",
                "precursor_entries",
            )
        },
        "output_columns": list(OUTPUT_COLUMNS),
        "strict_numeric_features": [
            name
            for name in _NUMERIC_COLUMNS
            if not name.endswith("_observed") and name != "ceremony_year"
        ],
        "observed_counts": "lower_bounds_diagnostics_only_not_complete_features",
        "career_aggregation": "distinct_older_acting_directing_entries_union_over_recipients",
        "mapped_contests": {
            category: {"guild": guild, "contest": contest, "family": family}
            for category, (guild, contest, family) in MAPPED_CONTESTS.items()
        },
        "excluded_features": [
            "current_or_future_oscar_results",
            "any_guild_win",
            "raw_lifetime_revenue",
            "budgets",
            "reviews",
            "popularity",
            "pundits",
            "post_oscar_honors",
            "static_metadata_or_distributor_without_historical_evidence",
        ],
        "source_gates": {
            "precursors": "Nov 22 go/no-go remains external",
            "optional_features": "Nov 29 go/no-go remains external",
            "real_data_acceptance": "requires_permissions_acquisition_independent_coverage",
        },
        "coverage": report,
        "limitations": (
            "Transforms establish neither real source access/coverage nor empirical "
            "results. Synthetic fixtures are not Oscar records. No model is trained."
        ),
    }
