import time
import random
from typing import List, Tuple
import matplotlib.pyplot as plt


class Asset:
    def __init__(self, name: str, cost: int, expected_return: int):
        self.name = name
        self.cost = cost
        self.expected_return = expected_return


class PortfolioOptimizer:
    def __init__(self, assets: List[Asset], budget: int):
        self.assets = assets
        self.budget = budget

    # 1. Brute Force (Recursive / Exponental O(2^N))
    def solve_brute_force(self) -> Tuple[int, float]:
        def recursive_knapsack(index: int, remaining_budget: int) -> int:
            if index == 0 or remaining_budget == 0:
                return 0
            
            asset = self.assets[index - 1]
            if asset.cost > remaining_budget:
                return recursive_knapsack(index - 1, remaining_budget)
            else:
                # Max of (include asset, exclude asset)
                include = asset.expected_return + recursive_knapsack(
                    index - 1, remaining_budget - asset.cost
                )
                exclude = recursive_knapsack(index - 1, remaining_budget)
                return max(include, exclude)

        start_time = time.perf_counter()
        max_return = recursive_knapsack(len(self.assets), self.budget)
        exec_time = (time.perf_counter() - start_time) * 1000  # in ms
        return max_return, exec_time

    # 2. Dynamic Programming (O(N * B) Time, O(B) Space)
    def solve_dp(self) -> Tuple[int, float]:
        start_time = time.perf_counter()
        B = self.budget
        dp = [0] * (B + 1)

        for asset in self.assets:
            for b in range(B, asset.cost - 1, -1):
                if dp[b - asset.cost] + asset.expected_return > dp[b]:
                    dp[b] = dp[b - asset.cost] + asset.expected_return

        exec_time = (time.perf_counter() - start_time) * 1000  # in ms
        return dp[B], exec_time


# --- Benchmarking Function ---
def run_benchmark():
    asset_sizes = list(range(5, 23, 2))  # N = 5, 7, 9, ..., 21
    budget = 1000

    brute_force_times = []
    dp_times = []

    print(f"{'N Assets':<10} | {'Brute Force (ms)':<18} | {'DP Time (ms)':<15}")
    print("-" * 50)

    for n in asset_sizes:
        # Generate random assets for benchmarking
        random.seed(42 + n)
        test_assets = [
            Asset(
                name=f"Asset_{i}",
                cost=random.randint(50, 300),
                expected_return=random.randint(10, 100)
            )
            for i in range(n)
        ]

        optimizer = PortfolioOptimizer(test_assets, budget)

        # Measure Brute Force
        _, bf_time = optimizer.solve_brute_force()
        brute_force_times.append(bf_time)

        # Measure Dynamic Programming
        _, dp_time = optimizer.solve_dp()
        dp_times.append(dp_time)

        print(f"{n:<10} | {bf_time:<18.4f} | {dp_time:<15.4f}")

    # --- Plotting Results ---
    plt.figure(figsize=(10, 6))
    plt.plot(
        asset_sizes,
        brute_force_times,
        marker='o',
        color='red',
        linewidth=2,
        label='Brute Force O(2^N)'
    )
    plt.plot(
        asset_sizes,
        dp_times,
        marker='s',
        color='blue',
        linewidth=2,
        label='Dynamic Programming O(N * B)'
    )

    plt.yscale('log')  # Logarithmic scale highlights exponential divergence
    plt.title(
        'Execution Time Comparison: Brute Force vs. Dynamic Programming\n(Personal Finance Portfolio Selection)',
        fontsize=12,
        fontweight='bold'
    )
    plt.xlabel('Number of Candidate Assets (N)', fontsize=11)
    plt.ylabel('Execution Time in ms (Log Scale)', fontsize=11)
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend(fontsize=11)
    plt.tight_layout()

    # Save and show
    plt.savefig('portfolio_time_complexity_chart.png', dpi=300)
    print("\nBenchmark completed. Chart saved as 'portfolio_time_complexity_chart.png'.")
    plt.show()


if __name__ == "__main__":
    run_benchmark()
    