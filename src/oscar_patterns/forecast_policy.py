"""Version 1.0.0 rules for announced-nominee forecast information."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

POLICY_VERSION = "1.0.0"
PRODUCTS = ("early_read", "primary")
TIMESTAMP_STATUSES = ("verified", "unknown", "date_only")


def _utc(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class ForecastCutoffs:
    """An established schedule; dates without verified times are not inputs."""

    nominations_announced_at: datetime
    final_voting_starts_at: datetime

    def __post_init__(self) -> None:
        nominations = _utc(self.nominations_announced_at, "nominations_announced_at")
        voting = _utc(self.final_voting_starts_at, "final_voting_starts_at")
        if voting <= nominations + timedelta(hours=24):
            raise ValueError("final voting must start after the early-read cutoff")

    @property
    def early_read_at(self) -> datetime:
        # Add elapsed hours in UTC, not wall-clock hours across a DST transition.
        return (
            _utc(self.nominations_announced_at, "nominations_announced_at")
            + timedelta(hours=24)
        ).astimezone(self.nominations_announced_at.tzinfo)

    @property
    def primary_before(self) -> datetime:
        """Exclusive boundary, not a fabricated 'last microsecond' timestamp."""
        return self.final_voting_starts_at


@dataclass(frozen=True)
class AvailabilityEvidence:
    """Source-supported public availability, distinct from retrieval/event time."""

    available_at: datetime | None = None
    timestamp_status: str = "unknown"
    evidence_reference: str | None = None
    retrieved_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.timestamp_status not in TIMESTAMP_STATUSES:
            raise ValueError(f"timestamp_status must be one of {TIMESTAMP_STATUSES}")
        if self.available_at is not None:
            _utc(self.available_at, "available_at")
        if self.retrieved_at is not None:
            _utc(self.retrieved_at, "retrieved_at")


def is_strictly_eligible(
    evidence: AvailabilityEvidence,
    cutoffs: ForecastCutoffs,
    product: str,
) -> bool:
    """Fail closed without verified availability; never infer it from retrieval."""
    if product not in PRODUCTS:
        raise ValueError(
            f"product must be one of {PRODUCTS}; interim cutoffs are unvalidated"
        )
    if (
        evidence.timestamp_status != "verified"
        or evidence.available_at is None
        or not evidence.evidence_reference
        or not evidence.evidence_reference.strip()
    ):
        return False
    available = _utc(evidence.available_at, "available_at")
    if product == "early_read":
        return available <= _utc(cutoffs.early_read_at, "early_read_at")
    return available < _utc(cutoffs.primary_before, "primary_before")


def ceremony_partition(ceremony_year: int) -> str:
    """Classify research years without releasing the held-out outcome quarantine."""
    if isinstance(ceremony_year, bool) or not isinstance(ceremony_year, int):
        raise TypeError("ceremony_year must be an integer")
    if 2010 <= ceremony_year <= 2016:
        return "initial_training"
    if 2017 <= ceremony_year <= 2023:
        return "development"
    if 2024 <= ceremony_year <= 2026:
        return "quarantined_test"
    raise ValueError("research partitions cover ceremony years 2010–2026 only")
