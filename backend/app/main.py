import os
import random
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .optimizer import Asset, PortfolioOptimizer


class AssetInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    cost: int = Field(gt=0, le=100_000)
    expected_return: int = Field(ge=0, le=1_000_000)


class OptimizeRequest(BaseModel):
    assets: list[AssetInput] = Field(min_length=1, max_length=25)
    budget: int = Field(ge=0, le=100_000)
    algorithm: Literal["dp", "brute_force"]


class BenchmarkRequest(BaseModel):
    max_assets: int = Field(default=19, ge=5, le=23)
    budget: int = Field(default=1000, ge=1, le=10_000)


app = FastAPI(title="Portfolio Optimizer API", version="1.0.0")
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/optimize")
def optimize(request: OptimizeRequest) -> dict[str, object]:
    if request.algorithm == "brute_force" and len(request.assets) > 23:
        raise HTTPException(status_code=422, detail="Brute force is limited to 23 assets")

    assets = [Asset(**asset.model_dump()) for asset in request.assets]
    max_return, selected, elapsed_ms = PortfolioOptimizer(assets, request.budget).solve(
        request.algorithm
    )
    return {
        "algorithm": request.algorithm,
        "max_expected_return": max_return,
        "selected_assets": [
            {
                "name": asset.name,
                "cost": asset.cost,
                "expected_return": asset.expected_return,
            }
            for asset in selected
        ],
        "total_cost": sum(asset.cost for asset in selected),
        "execution_time_ms": elapsed_ms,
        "time_complexity": "O(2^N)" if request.algorithm == "brute_force" else "O(N * B)",
        "space_complexity": "O(N) call stack" if request.algorithm == "brute_force" else "O(B) DP workspace",
    }


@app.post("/api/benchmark")
def benchmark(request: BenchmarkRequest) -> dict[str, object]:
    points = []
    for count in range(5, request.max_assets + 1, 2):
        generator = random.Random(42 + count)
        assets = [
            Asset(
                name=f"Asset {index + 1}",
                cost=generator.randint(50, 300),
                expected_return=generator.randint(10, 100),
            )
            for index in range(count)
        ]
        optimizer = PortfolioOptimizer(assets, request.budget)
        brute_return, _, brute_ms = optimizer.solve_brute_force()
        dp_return, _, dp_ms = optimizer.solve_dp()
        points.append(
            {
                "n": count,
                "brute_force_ms": brute_ms,
                "dp_ms": dp_ms,
                "brute_force_return": brute_return,
                "dp_return": dp_return,
            }
        )

    return {"budget": request.budget, "points": points}
