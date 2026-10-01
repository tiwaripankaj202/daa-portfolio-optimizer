import unittest

from backend.app.optimizer import Asset, PortfolioOptimizer


class PortfolioOptimizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assets = [
            Asset("Index fund", 6, 30),
            Asset("Bond fund", 3, 14),
            Asset("Growth fund", 4, 16),
            Asset("Cash reserve", 2, 9),
        ]

    def test_algorithms_return_same_optimum_and_valid_selection(self) -> None:
        optimizer = PortfolioOptimizer(self.assets, 9)
        dp_value, dp_items, _ = optimizer.solve_dp()
        brute_value, brute_items, _ = optimizer.solve_brute_force()

        self.assertEqual(dp_value, 44)
        self.assertEqual(dp_value, brute_value)
        for selected in (dp_items, brute_items):
            self.assertLessEqual(sum(asset.cost for asset in selected), 9)
            self.assertEqual(sum(asset.expected_return for asset in selected), dp_value)

    def test_zero_budget_selects_nothing(self) -> None:
        value, selected, _ = PortfolioOptimizer(self.assets, 0).solve_dp()
        self.assertEqual(value, 0)
        self.assertEqual(selected, [])

    def test_dp_handles_assets_over_budget(self) -> None:
        value, selected, _ = PortfolioOptimizer(self.assets, 1).solve_dp()
        self.assertEqual(value, 0)
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
