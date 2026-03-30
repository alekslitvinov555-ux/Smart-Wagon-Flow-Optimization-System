import heapq
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypedDict


class OptimizationResult(TypedDict):
    old_time: int
    new_time: int
    old_route: List[str]
    new_route: List[str]


class GraphData(TypedDict):
    stations: List[str]
    connections: List["Connection"]
    congestion: Dict[str, int]


class Connection(TypedDict):
    from_: str
    to: str
    time: int


def _load_graph_data() -> GraphData:
    data_path = Path(__file__).with_name("data.json")
    with data_path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    connections: List[Connection] = []
    for connection in raw_data["connections"]:
        connections.append(
            {
                "from_": str(connection["from"]),
                "to": str(connection["to"]),
                "time": int(connection["time"]),
            }
        )

    congestion: Dict[str, int] = {
        str(station): int(penalty)
        for station, penalty in raw_data.get("congestion", {}).items()
    }

    return {
        "stations": [str(station) for station in raw_data["stations"]],
        "connections": connections,
        "congestion": congestion,
    }


def _build_graph(connections: List[Connection]) -> Dict[str, List[Tuple[str, int]]]:
    graph: Dict[str, List[Tuple[str, int]]] = {}
    for connection in connections:
        from_station = connection["from_"]
        to_station = connection["to"]
        base_time = connection["time"]

        graph.setdefault(from_station, []).append((to_station, base_time))
        graph.setdefault(to_station, []).append((from_station, base_time))
    return graph


def _reconstruct_path(
    previous: Dict[str, Optional[str]], source: str, target: str
) -> List[str]:
    if source == target:
        return [source]
    if target not in previous:
        return []

    route = [target]
    current = target
    while current != source:
        parent = previous.get(current)
        if parent is None:
            return []
        route.append(parent)
        current = parent
    route.reverse()
    return route


def _shortest_path(
    graph: Dict[str, List[Tuple[str, int]]], source: str, target: str
) -> Tuple[int, List[str]]:
    if source not in graph or target not in graph:
        return 0, []

    distances: Dict[str, int] = {source: 0}
    previous: Dict[str, Optional[str]] = {source: None}
    queue: List[Tuple[int, str]] = [(0, source)]

    while queue:
        current_distance, node = heapq.heappop(queue)
        known_distance = distances.get(node)
        if known_distance is None or current_distance > known_distance:
            continue
        if node == target:
            break

        for neighbor, edge_weight in graph.get(node, []):
            candidate = current_distance + edge_weight
            neighbor_distance = distances.get(neighbor)
            if neighbor_distance is None or candidate < neighbor_distance:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if target not in distances:
        return 0, []

    return distances[target], _reconstruct_path(previous, source, target)


def _shortest_path_with_congestion(
    graph: Dict[str, List[Tuple[str, int]]],
    source: str,
    target: str,
    congestion: Dict[str, int],
) -> Tuple[int, List[str]]:
    if source not in graph or target not in graph:
        return 0, []

    distances: Dict[str, int] = {source: 0}
    previous: Dict[str, Optional[str]] = {source: None}
    queue: List[Tuple[int, str]] = [(0, source)]

    while queue:
        current_distance, node = heapq.heappop(queue)
        known_distance = distances.get(node)
        if known_distance is None or current_distance > known_distance:
            continue
        if node == target:
            break

        for neighbor, edge_weight in graph.get(node, []):
            penalty = int(congestion.get(neighbor, 0)) if neighbor != target else 0
            candidate = current_distance + edge_weight + penalty
            neighbor_distance = distances.get(neighbor)
            if neighbor_distance is None or candidate < neighbor_distance:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if target not in distances:
        return 0, []

    return distances[target], _reconstruct_path(previous, source, target)


def _calculate_path_time(
    route: List[str],
    connections: List[Connection],
    congestion: Dict[str, int],
    include_congestion: bool,
) -> int:
    if len(route) <= 1:
        return 0

    edge_times: Dict[frozenset[str], int] = {}
    for connection in connections:
        edge_times[frozenset({connection["from_"], connection["to"]})] = connection["time"]

    total = 0
    for start, end in zip(route, route[1:]):
        total += edge_times[frozenset({start, end})]
        if include_congestion and end != route[-1]:
            total += int(congestion.get(end, 0))
    return total


def optimize_route(source: str, target: str) -> OptimizationResult:
    dataset = _load_graph_data()
    connections = dataset["connections"]
    congestion = dataset.get("congestion", {})

    graph = _build_graph(connections=connections)

    _, old_route = _shortest_path(graph, source, target)
    old_time = _calculate_path_time(
        old_route, connections, congestion, include_congestion=True
    )
    _, new_route = _shortest_path_with_congestion(graph, source, target, congestion)
    new_time = _calculate_path_time(
        new_route, connections, congestion, include_congestion=False
    )

    return {
        "old_time": old_time,
        "new_time": new_time,
        "old_route": old_route,
        "new_route": new_route,
    }
