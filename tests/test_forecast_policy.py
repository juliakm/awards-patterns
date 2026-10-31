"""Synthetic schedule fixtures; none assert official Academy dates."""

import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from oscar_patterns.forecast_policy import (
    AvailabilityEvidence,
    ForecastCutoffs,
    ceremony_partition,
    is_strictly_eligible,
)


class ForecastPolicyTests(unittest.TestCase):
    def setUp(self):
        self.nominations = datetime(2023, 1, 24, 13, 30, tzinfo=timezone.utc)
        self.voting = datetime(2023, 3, 2, 17, tzinfo=timezone.utc)
        self.cutoffs = ForecastCutoffs(self.nominations, self.voting)

    def evidence(self, at, **kwargs):
        return AvailabilityEvidence(
            available_at=at,
            timestamp_status="verified",
            evidence_reference="fixture:public-announcement",
            **kwargs,
        )

    def test_exact_early_boundary_is_inclusive(self):
        boundary = self.nominations + timedelta(hours=24)
        for delta, eligible in [
            (-timedelta(microseconds=1), True),
            (timedelta(0), True),
            (timedelta(microseconds=1), False),
        ]:
            with self.subTest(delta=delta):
                self.assertEqual(
                    is_strictly_eligible(
                        self.evidence(boundary + delta), self.cutoffs, "early_read"
                    ),
                    eligible,
                )

    def test_exact_primary_boundary_is_exclusive(self):
        for delta, eligible in [
            (-timedelta(microseconds=1), True),
            (timedelta(0), False),
            (timedelta(microseconds=1), False),
        ]:
            with self.subTest(delta=delta):
                self.assertEqual(
                    is_strictly_eligible(
                        self.evidence(self.voting + delta), self.cutoffs, "primary"
                    ),
                    eligible,
                )

    def test_offsets_and_named_zones_compare_instants(self):
        pacific = ZoneInfo("America/Los_Angeles")
        plus_five = timezone(timedelta(hours=5, minutes=30))
        local_cutoffs = ForecastCutoffs(
            self.nominations.astimezone(pacific), self.voting.astimezone(plus_five)
        )
        early = self.cutoffs.early_read_at.astimezone(plus_five)
        self.assertTrue(
            is_strictly_eligible(self.evidence(early), local_cutoffs, "early_read")
        )
        self.assertFalse(
            is_strictly_eligible(
                self.evidence(self.voting.astimezone(pacific)), local_cutoffs, "primary"
            )
        )
        self.assertTrue(
            is_strictly_eligible(
                self.evidence((self.voting - timedelta(seconds=1)).astimezone(pacific)),
                local_cutoffs,
                "primary",
            )
        )

    def test_naive_schedule_and_evidence_timestamps_are_rejected(self):
        naive = datetime(2023, 1, 24, 13, 30)
        with self.assertRaises(ValueError):
            ForecastCutoffs(naive, self.voting)
        with self.assertRaises(ValueError):
            ForecastCutoffs(self.nominations, naive)
        with self.assertRaises(ValueError):
            self.evidence(naive)
        with self.assertRaises(ValueError):
            AvailabilityEvidence(retrieved_at=naive)

    def test_nominations_are_required_and_voting_follows_early_read(self):
        with self.assertRaises(TypeError):
            ForecastCutoffs(None, self.voting)
        for voting in (
            self.nominations - timedelta(days=1),
            self.nominations,
            self.nominations + timedelta(hours=24),
        ):
            with self.subTest(voting=voting), self.assertRaises(ValueError):
                ForecastCutoffs(self.nominations, voting)
        self.assertEqual(
            self.cutoffs.early_read_at, self.nominations + timedelta(hours=24)
        )
        self.assertTrue(
            is_strictly_eligible(
                self.evidence(self.nominations), self.cutoffs, "early_read"
            )
        )

    def test_missing_unknown_date_only_or_unreferenced_availability_is_excluded(self):
        for evidence in (
            AvailabilityEvidence(),
            AvailabilityEvidence(
                timestamp_status="verified", evidence_reference="fixture"
            ),
            AvailabilityEvidence(
                available_at=self.nominations, evidence_reference="fixture"
            ),
            AvailabilityEvidence(self.nominations, "date_only", "fixture"),
            AvailabilityEvidence(self.nominations, "verified"),
            AvailabilityEvidence(self.nominations, "verified", " "),
        ):
            for product in ("early_read", "primary"):
                with self.subTest(evidence=evidence, product=product):
                    self.assertFalse(
                        is_strictly_eligible(evidence, self.cutoffs, product)
                    )
        with self.assertRaises(ValueError):
            AvailabilityEvidence(timestamp_status="estimated")

    def test_retrieval_time_is_never_an_availability_substitute(self):
        self.assertFalse(
            is_strictly_eligible(
                AvailabilityEvidence(
                    timestamp_status="verified",
                    evidence_reference="fixture",
                    retrieved_at=self.nominations,
                ),
                self.cutoffs,
                "early_read",
            )
        )
        # An archive retrieved later can establish a verified earlier publication.
        self.assertTrue(
            is_strictly_eligible(
                self.evidence(
                    self.nominations, retrieved_at=self.voting + timedelta(days=30)
                ),
                self.cutoffs,
                "early_read",
            )
        )
        self.assertFalse(
            is_strictly_eligible(
                self.evidence(self.voting, retrieved_at=self.nominations),
                self.cutoffs,
                "primary",
            )
        )

    def test_24_hours_means_elapsed_time_across_both_dst_transitions(self):
        pacific = ZoneInfo("America/Los_Angeles")
        for nominations, expected_hour in (
            (datetime(2023, 3, 11, 12, tzinfo=pacific), 13),
            (datetime(2023, 11, 4, 12, tzinfo=pacific), 11),
        ):
            cutoffs = ForecastCutoffs(
                nominations,
                (nominations.astimezone(timezone.utc) + timedelta(days=3)).astimezone(
                    pacific
                ),
            )
            with self.subTest(nominations=nominations):
                self.assertEqual(cutoffs.early_read_at.hour, expected_hour)
                self.assertEqual(
                    cutoffs.early_read_at.astimezone(timezone.utc)
                    - nominations.astimezone(timezone.utc),
                    timedelta(hours=24),
                )
                self.assertTrue(
                    is_strictly_eligible(
                        self.evidence(cutoffs.early_read_at), cutoffs, "early_read"
                    )
                )

    def test_unsupported_interim_cutoff_fails(self):
        with self.assertRaisesRegex(ValueError, "unvalidated"):
            is_strictly_eligible(
                self.evidence(self.nominations), self.cutoffs, "interim"
            )

    def test_research_partitions_keep_final_test_quarantined(self):
        for year in range(2010, 2027):
            expected = (
                "initial_training"
                if year <= 2016
                else "development"
                if year <= 2023
                else "quarantined_test"
            )
            with self.subTest(year=year):
                self.assertEqual(ceremony_partition(year), expected)
        for year in (2009, 2027):
            with self.assertRaises(ValueError):
                ceremony_partition(year)
        for year in (True, "2024"):
            with self.assertRaises(TypeError):
                ceremony_partition(year)


if __name__ == "__main__":
    unittest.main()
