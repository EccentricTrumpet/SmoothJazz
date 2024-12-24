from unittest import TestCase
from typing import Sequence, Tuple
from core.unit import Unit, Single, Pair, Tractor
from testing import initialize
from testing.spades import S3, S4, S5, S6, S7


class UnitTests(TestCase):
    def test_format_unit_single_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card] = initialize([S3, S4, S5])
        unit = Single(S3Card)

        cases: Sequence[Tuple[Unit, Sequence[Unit]]] = [
            # Single
            (Single(S4Card), [Single(S3Card)]),
            # Pair
            (Pair([S4Card, S4Card]), []),
            # Tractor
            (Tractor([Pair([S4Card, S4Card]), Pair([S5Card, S5Card])]), []),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)

    def test_format_unit_pair_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card] = initialize([S3, S4, S5])
        unit = Pair([S3Card, S3Card])

        cases: Sequence[Tuple[Unit, Sequence[Unit]]] = [
            # Single
            (Single(S4Card), [Single(S3Card), Single(S3Card)]),
            # Pair
            (Pair([S4Card, S4Card]), [Pair([S3Card, S3Card])]),
            # Tractor
            (Tractor([Pair([S4Card, S4Card]), Pair([S5Card, S5Card])]), []),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)

    def test_format_unit_tractor_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card, S6Card, S7Card] = initialize([S3, S4, S5, S6, S7])
        unit = Tractor(
            [Pair([S5Card, S5Card]), Pair([S6Card, S6Card]), Pair([S7Card, S7Card])]
        )

        cases: Sequence[Tuple[Unit, Sequence[Unit]]] = [
            # Single
            (
                Single(S4Card),
                [Single(c) for c in [S5Card, S5Card, S6Card, S6Card, S7Card, S7Card]],
            ),
            # Pair
            (
                Pair([S4Card, S4Card]),
                [
                    Pair([S5Card, S5Card]),
                    Pair([S6Card, S6Card]),
                    Pair([S7Card, S7Card]),
                ],
            ),
            # Tractor
            (
                Tractor([Pair([S3Card, S3Card]), Pair([S4Card, S4Card])]),
                [
                    Tractor([Pair([S5Card, S5Card]), Pair([S6Card, S6Card])]),
                    Tractor([Pair([S6Card, S6Card]), Pair([S7Card, S7Card])]),
                ],
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)
