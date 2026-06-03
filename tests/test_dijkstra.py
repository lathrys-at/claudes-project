"""Tests for Dijkstra shortest-path example."""

import pytest
import random
import heapq
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source
from pebble.types import PebbleHash, PebbleList
import io
import sys


def load_dijkstra_example():
    """Load dijkstra.pebble and return env."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "dijkstra.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


@pytest.fixture(scope="module")
def dijkstra_env_and_output():
    """Load dijkstra.pebble once and capture its output."""
    return load_dijkstra_example()


class TestDijkstraDemo:
    """Test the demo output when dijkstra.pebble is evaluated."""

    def test_demo_output_exists(self, dijkstra_env_and_output):
        """Test that the demo code produces output without errors."""
        env, demo_output = dijkstra_env_and_output
        lines = demo_output.strip().split('\n')
        # Should have 5 demo lines
        assert len(lines) >= 5


class TestDijkstraBasic:
    """Test basic Dijkstra functionality with simple known graphs."""

    def test_simple_chain(self, dijkstra_env_and_output):
        """Test shortest paths in a simple linear chain: A->B->C->D."""
        env, _ = dijkstra_env_and_output

        code = """
        (define chain-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list (list "C" 1))
            "C" (list (list "D" 1))
            "D" (list)))

        (dijkstra chain-graph "A")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleHash)

        # Check distances
        assert result._data["A"] == 0
        assert result._data["B"] == 1
        assert result._data["C"] == 2
        assert result._data["D"] == 3

    def test_diamond_graph(self, dijkstra_env_and_output):
        """Test diamond-shaped graph where shorter route must be chosen."""
        env, _ = dijkstra_env_and_output

        code = """
        (define diamond-graph
          (make-hash
            "A" (list (list "B" 10) (list "C" 1))
            "B" (list (list "D" 1))
            "C" (list (list "D" 10))
            "D" (list)))

        (dijkstra diamond-graph "A")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleHash)

        # Shorter path is A->C->D (11) not A->B->D (11)
        # Both are optimal, but distances should be correct
        assert result._data["A"] == 0
        assert result._data["B"] == 10
        assert result._data["C"] == 1
        assert result._data["D"] == 11

    def test_unreachable_node(self, dijkstra_env_and_output):
        """Test that unreachable nodes are absent from result."""
        env, _ = dijkstra_env_and_output

        code = """
        (define disconnected-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list)
            "C" (list (list "D" 1))
            "D" (list)))

        (dijkstra disconnected-graph "A")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleHash)

        # A and B are reachable from A
        assert "A" in result
        assert "B" in result
        # C and D are not reachable
        assert "C" not in result
        assert "D" not in result

    def test_source_to_self(self, dijkstra_env_and_output):
        """Test distance from source to itself is 0."""
        env, _ = dijkstra_env_and_output

        code = """
        (define simple-graph
          (make-hash
            "A" (list (list "B" 5))
            "B" (list)))

        (shortest-distance simple-graph "A" "A")
        """

        result = eval_source(code, env)
        assert result == 0


class TestShortestDistance:
    """Test shortest-distance function."""

    def test_reachable_node(self, dijkstra_env_and_output):
        """Test distance to a reachable node."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 3) (list "C" 5))
            "B" (list (list "C" 2))
            "C" (list)))

        (shortest-distance test-graph "A" "C")
        """

        result = eval_source(code, env)
        # A->B->C is 3+2=5; A->C is 5; both are optimal
        assert result == 5

    def test_unreachable_node_returns_false(self, dijkstra_env_and_output):
        """Test that unreachable node returns false."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list)
            "C" (list)))

        (shortest-distance test-graph "A" "C")
        """

        result = eval_source(code, env)
        assert result is False


class TestShortestPath:
    """Test shortest-path function."""

    def test_path_to_self(self, dijkstra_env_and_output):
        """Test path from source to itself is just the source."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list)))

        (shortest-path test-graph "A" "A")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        path = [str(x) for x in result]
        assert path == ["A"]

    def test_direct_edge(self, dijkstra_env_and_output):
        """Test path with a direct edge."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list)))

        (shortest-path test-graph "A" "B")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        path = [str(x) for x in result]
        assert path == ["A", "B"]

    def test_path_through_intermediate_nodes(self, dijkstra_env_and_output):
        """Test path through multiple intermediate nodes."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list (list "C" 1))
            "C" (list (list "D" 1))
            "D" (list)))

        (shortest-path test-graph "A" "D")
        """

        result = eval_source(code, env)
        assert isinstance(result, PebbleList)
        path = [str(x) for x in result]
        assert path == ["A", "B", "C", "D"]

    def test_unreachable_path_returns_false(self, dijkstra_env_and_output):
        """Test that path to unreachable node returns false."""
        env, _ = dijkstra_env_and_output

        code = """
        (define test-graph
          (make-hash
            "A" (list (list "B" 1))
            "B" (list)
            "C" (list)))

        (shortest-path test-graph "A" "C")
        """

        result = eval_source(code, env)
        assert result is False


class TestDijkstraOracle:
    """Oracle-based cross-check: compare Pebble against a pure-Python Dijkstra."""

    @staticmethod
    def python_dijkstra(graph, source):
        """Pure-Python Dijkstra implementation for oracle testing.

        graph: dict node -> list of (neighbor, weight) tuples
        returns: dict node -> distance
        """
        distances = {source: 0}
        visited = set()
        pq = [(0, source)]  # (distance, node)

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current_dist > distances.get(current, float('inf')):
                continue

            if current in graph:
                for neighbor, weight in graph[current]:
                    new_dist = current_dist + weight
                    if new_dist < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))

        return distances

    def graph_to_pebble_source(self, graph):
        """Convert Python graph dict to Pebble source code."""
        entries = []
        for node in graph:
            edges = graph[node]
            edge_list = " ".join(f'(list "{neighbor}" {weight})' for neighbor, weight in edges)
            entries.append(f'"{node}" (list {edge_list})')

        return f"(make-hash {' '.join(entries)})"

    def test_random_graphs(self, dijkstra_env_and_output):
        """Test against multiple random graphs."""
        env, _ = dijkstra_env_and_output
        random.seed(42)

        num_graphs = 30

        for graph_idx in range(num_graphs):
            # Generate random graph: 6-10 nodes, varying edge density
            num_nodes = random.randint(6, 10)
            nodes = [str(chr(65 + i)) for i in range(num_nodes)]  # A, B, C, ...

            graph = {node: [] for node in nodes}

            # Add random edges with non-negative weights
            for u in nodes:
                for v in nodes:
                    if u != v and random.random() < 0.3:  # ~30% edge density
                        weight = random.randint(1, 10)
                        graph[u].append((v, weight))

            # Pick a random source
            source = random.choice(nodes)

            # Compute with oracle
            oracle_distances = self.python_dijkstra(graph, source)

            # Compute with Pebble
            pebble_graph_source = self.graph_to_pebble_source(graph)
            code = f"""
            (define test-graph {pebble_graph_source})
            (dijkstra test-graph "{source}")
            """

            pebble_result = eval_source(code, env)

            # Convert Pebble result to comparable form
            pebble_distances = {}
            if isinstance(pebble_result, PebbleHash):
                for node in nodes:
                    if node in pebble_result._data:
                        pebble_distances[node] = pebble_result._data[node]

            # Check that reachable nodes match
            for node in nodes:
                oracle_reachable = node in oracle_distances
                pebble_reachable = node in pebble_distances

                assert oracle_reachable == pebble_reachable, \
                    f"Graph {graph_idx}, node {node}: reachability mismatch " \
                    f"(oracle: {oracle_reachable}, pebble: {pebble_reachable})"

                # Check distances match for reachable nodes
                if oracle_reachable:
                    oracle_dist = oracle_distances[node]
                    pebble_dist = pebble_distances[node]
                    assert oracle_dist == pebble_dist, \
                        f"Graph {graph_idx}, node {node}: distance mismatch " \
                        f"(oracle: {oracle_dist}, pebble: {pebble_dist})"

    def test_path_validity_and_optimality(self, dijkstra_env_and_output):
        """Test that returned paths are valid and have optimal weight."""
        env, _ = dijkstra_env_and_output
        random.seed(123)

        num_tests = 10

        for test_idx in range(num_tests):
            # Generate random graph
            num_nodes = random.randint(5, 8)
            nodes = [str(chr(65 + i)) for i in range(num_nodes)]

            graph = {node: [] for node in nodes}
            for u in nodes:
                for v in nodes:
                    if u != v and random.random() < 0.4:
                        weight = random.randint(1, 10)
                        graph[u].append((v, weight))

            # Compute oracle distances
            source = random.choice(nodes)
            oracle_distances = self.python_dijkstra(graph, source)

            # Pick several source-target pairs
            for _ in range(3):
                target = random.choice(nodes)

                if target not in oracle_distances:
                    # Should be unreachable
                    code = f"""
                    (define test-graph {self.graph_to_pebble_source(graph)})
                    (shortest-path test-graph "{source}" "{target}")
                    """
                    result = eval_source(code, env)
                    assert result is False, \
                        f"Test {test_idx}: Expected false for unreachable node {target}"
                else:
                    # Should return a valid path
                    code = f"""
                    (define test-graph {self.graph_to_pebble_source(graph)})
                    (shortest-path test-graph "{source}" "{target}")
                    """
                    path_result = eval_source(code, env)
                    assert isinstance(path_result, PebbleList) or path_result is False, \
                        f"Test {test_idx}: Path should be list or false"

                    if isinstance(path_result, PebbleList):
                        path = [str(x) for x in path_result]

                        # Verify path starts with source and ends with target
                        assert path[0] == source, f"Path should start with {source}"
                        assert path[-1] == target, f"Path should end with {target}"

                        # Verify consecutive nodes are connected
                        total_weight = 0
                        for i in range(len(path) - 1):
                            current = path[i]
                            next_node = path[i + 1]

                            # Find edge weight
                            found = False
                            for neighbor, weight in graph.get(current, []):
                                if neighbor == next_node:
                                    total_weight += weight
                                    found = True
                                    break

                            assert found, \
                                f"Test {test_idx}: No edge from {current} to {next_node}"

                        # Verify total weight equals oracle distance
                        oracle_dist = oracle_distances[target]
                        assert total_weight == oracle_dist, \
                            f"Test {test_idx}: Path weight {total_weight} != " \
                            f"oracle distance {oracle_dist}"
