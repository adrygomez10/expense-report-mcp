"""Verify monetary invariants and expense policy decisions."""

import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal

from expense_report.domain.category import Category
from expense_report.domain.decision import Decision
from expense_report.domain.expense_error import ExpenseError
from expense_report.domain.expense_policy import ExpensePolicy
from expense_report.domain.money import Money
from expense_report.domain.receipt import Receipt
from expense_report.domain.trip import Trip


class PolicyTests(unittest.TestCase):
    """Exercise business rules independently of files and frameworks."""

    def setUp(self):
        """Create an inclusive two-day trip and its policy."""
        self.trip = Trip(
            trip_id="trip",
            employee_id="employee",
            destination="Madrid",
            starts_on=date(2026, 10, 19),
            ends_on=date(2026, 10, 20),
        )
        self.policy = ExpensePolicy()

    def receipt(self, receipt_id="one", amount="20.00", **changes):
        """Create a valid meal receipt with explicit test variations."""
        receipt = Receipt(
            receipt_id=receipt_id,
            vendor="Demo Vendor",
            invoice_number=receipt_id,
            spent_on=date(2026, 10, 19),
            category=Category.MEAL,
            money=Money(Decimal(amount), "EUR"),
            evidence_reference="demo:evidence",
        )
        return replace(receipt, **changes)

    def test_money_rejects_nonfinite_nonpositive_and_extra_precision(self):
        """Reject values that would corrupt report totals."""
        for value in ("NaN", "Infinity", "0", "-1", "1.001"):
            with self.subTest(value=value), self.assertRaises(ExpenseError):
                Money(Decimal(value), "EUR")

    def test_money_rejects_float(self):
        """Avoid accidentally calculating money with binary floats."""
        with self.assertRaises(ExpenseError):
            Money(0.1, "EUR")

    def test_money_rejects_invalid_currency(self):
        """Require normalized three-letter currency identifiers."""
        for currency in ("eur", "EU", "E12", "€€€"):
            with (
                self.subTest(currency=currency),
                self.assertRaises(ExpenseError),
            ):
                Money(Decimal("1.00"), currency)

    def test_values_are_frozen(self):
        """Prevent mutation that bypasses validated constructors."""
        money = Money(Decimal("20.00"), "EUR")
        with self.assertRaises(FrozenInstanceError):
            money.amount = Decimal("-1")

    def test_trip_rejects_reversed_dates(self):
        """Keep trip intervals ordered."""
        with self.assertRaises(ExpenseError):
            replace(self.trip, starts_on=date(2026, 10, 21))

    def test_daily_meals_are_aggregated(self):
        """Flag both receipts when their daily sum exceeds the cap."""
        report = self.policy.evaluate(
            self.trip,
            (self.receipt("one", "20"), self.receipt("two", "25")),
        )
        self.assertEqual(Decimal("45"), report.total(Decision.REVIEW))
        self.assertTrue(
            all(
                "daily_meal_limit_exceeded" in item.reasons
                for item in report.assessments
            )
        )

    def test_daily_cap_is_inclusive(self):
        """Allow exactly the daily meal allowance."""
        report = self.policy.evaluate(self.trip, (self.receipt(amount="35"),))
        self.assertEqual(Decision.ELIGIBLE, report.assessments[0].decision)

    def test_meals_on_different_days_do_not_share_a_cap(self):
        """Apply the limit independently to each calendar day."""
        receipts = (
            self.receipt(),
            self.receipt("two", spent_on=self.trip.ends_on),
        )
        report = self.policy.evaluate(self.trip, receipts)
        self.assertEqual(Decimal("40.00"), report.total(Decision.ELIGIBLE))

    def test_duplicates_do_not_inflate_daily_meals(self):
        """Exclude a normalized invoice copy before calculating the cap."""
        first = self.receipt()
        copy = replace(first, receipt_id="copy", vendor=" DEMO VENDOR ")
        report = self.policy.evaluate(self.trip, (first, copy))
        self.assertEqual(Decision.ELIGIBLE, report.assessments[0].decision)
        self.assertEqual(("duplicate_of:one",), report.assessments[1].reasons)

    def test_changed_amount_still_identifies_same_invoice(self):
        """Do not let another amount bypass invoice duplicate detection."""
        first = self.receipt()
        copy = replace(
            first, receipt_id="copy", money=Money(Decimal("21"), "EUR")
        )
        report = self.policy.evaluate(self.trip, (first, copy))
        self.assertEqual(Decision.DUPLICATE, report.assessments[1].decision)

    def test_missing_evidence_and_invoice_require_review(self):
        """Retain incomplete receipts and explain each missing field."""
        receipt = self.receipt(invoice_number=None, evidence_reference=None)
        report = self.policy.evaluate(self.trip, (receipt,))
        self.assertEqual(
            ("missing_invoice_number", "missing_evidence"),
            report.assessments[0].reasons,
        )

    def test_foreign_currency_is_not_added_to_eur_totals(self):
        """Keep an unconverted receipt visible and out of EUR sums."""
        receipt = self.receipt(money=Money(Decimal("20"), "USD"))
        report = self.policy.evaluate(self.trip, (receipt,))
        self.assertEqual(Decimal("0"), report.total())
        self.assertIn("unsupported_currency", report.assessments[0].reasons)

    def test_dates_outside_trip_require_review(self):
        """Flag a receipt outside the inclusive travel period."""
        receipt = self.receipt(spent_on=date(2026, 10, 18))
        report = self.policy.evaluate(self.trip, (receipt,))
        self.assertIn("outside_trip_dates", report.assessments[0].reasons)

    def test_hotel_limit_is_per_receipt(self):
        """Require review above the documented hotel receipt allowance."""
        receipt = self.receipt(amount="180.01", category=Category.HOTEL)
        report = self.policy.evaluate(self.trip, (receipt,))
        self.assertEqual(
            ("hotel_receipt_limit_exceeded",), report.assessments[0].reasons
        )

    def test_repeated_receipt_ids_are_invalid(self):
        """Reject ambiguous identifiers before evaluating invoice copies."""
        with self.assertRaises(ExpenseError):
            self.policy.evaluate(self.trip, (self.receipt(), self.receipt()))

    def test_partition_totals_equal_total(self):
        """Preserve every EUR amount in exactly one decision partition."""
        first = self.receipt()
        receipts = (
            first,
            replace(first, receipt_id="copy"),
            self.receipt("three", "40"),
        )
        report = self.policy.evaluate(self.trip, receipts)
        self.assertEqual(
            report.total(), sum(report.total(d) for d in Decision)
        )
