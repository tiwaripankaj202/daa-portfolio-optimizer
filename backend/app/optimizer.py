from dataclasses import dataclass
import time
from typing import Literal


@dataclass(frozen=True)
class Asset:
    name: str
    cost: int
    expected_return: int


Algorithm = Literal["dp", "brute_force"]


class PortfolioOptimizer:
    def __init__(self, assets: list[Asset], budget: int):
        if budget < 0:
            raise ValueError("Budget must be non-negative")
        if any(asset.cost <= 0 for asset in assets):
            raise ValueError("Asset costs must be positive")
        if any(asset.expected_return < 0 for asset in assets):
            raise ValueError("Expected returns must be non-negative")
        self.assets = assets
        self.budget = budget

    def solve_brute_force(self) -> tuple[int, list[Asset], float]:
        start = time.perf_counter()
        best_return = 0
        best_indices: list[int] = []
        selected: list[int] = []

        def search(index: int, remaining: int, current_return: int) -> None:
            nonlocal best_return, best_indices
            if index == len(self.assets):
                if current_return > best_return:
                    best_return = current_return
                    best_indices = selected.copy()
                return

            asset = self.assets[index]
            if asset.cost <= remaining:
                selected.append(index)
                search(index + 1, remaining - asset.cost, current_return + asset.expected_return)
                selected.pop()
            search(index + 1, remaining, current_return)

        search(0, self.budget, 0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return best_return, [self.assets[index] for index in best_indices], elapsed_ms

    @staticmethod
    def _values_for(
        assets: list[Asset], start: int, end: int, capacity: int
    ) -> list[int]:
        values = [0] * (capacity + 1)
        for index in range(start, end):
            asset = assets[index]
            for current_capacity in range(capacity, asset.cost - 1, -1):
                values[current_capacity] = max(
                    values[current_capacity],
                    values[current_capacity - asset.cost] + asset.expected_return,
                )
        return values

    def _reconstruct(self, start: int, end: int, capacity: int) -> list[Asset]:
        if start >= end or capacity <= 0:
            return []
        if end - start == 1:
            asset = self.assets[start]
            return [asset] if asset.cost <= capacity and asset.expected_return > 0 else []

        middle = (start + end) // 2
        left_values = self._values_for(self.assets, start, middle, capacity)
        right_values = self._values_for(self.assets, middle, end, capacity)
        left_capacity = max(
            range(capacity + 1),
            key=lambda available: left_values[available] + right_values[capacity - available],
        )
        del left_values, right_values

        return self._reconstruct(start, middle, left_capacity) + self._reconstruct(
            middle, end, capacity - left_capacity
        )

    def solve_dp(self) -> tuple[int, list[Asset], float]:
        start = time.perf_counter()
        selected = self._reconstruct(0, len(self.assets), self.budget)
        max_return = sum(asset.expected_return for asset in selected)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return max_return, selected, elapsed_ms

    def solve(self, algorithm: Algorithm) -> tuple[int, list[Asset], float]:
        if algorithm == "dp":
            return self.solve_dp()
        if algorithm == "brute_force":
            return self.solve_brute_force()
        raise ValueError(f"Unsupported algorithm: {algorithm}")
