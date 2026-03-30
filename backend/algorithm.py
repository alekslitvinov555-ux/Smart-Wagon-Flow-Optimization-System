from typing import List, TypedDict


class OptimizationResult(TypedDict):
    old_time: int
    new_time: int
    old_route: List[str]
    new_route: List[str]


def get_mock_optimization(source: str, target: str) -> OptimizationResult:
    return {
        "old_time": 120,
        "new_time": 95,
        "old_route": [source, "C", target],
        "new_route": [source, "D", target],
    }
