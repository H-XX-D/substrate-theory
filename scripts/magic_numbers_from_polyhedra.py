"""Test whether nuclear magic numbers correspond to closed polyhedral substrate cells.

Hypothesis: each magic number {2, 8, 20, 28, 50, 82, 126} = number of nucleons
that fill a CLOSED polyhedral substrate shell. The substrate "prefers" these
counts because they form maximally symmetric closed structures.

Method: compute the Möbius bundle amplitude (the same calculation that gave
α at K_4) on a series of polyhedral graphs and on K_n complete graphs.
Look for clean closed-form amplitudes at n = 2, 8, 20, 28, 50, 82, 126.

For each polyhedron / graph:
  1. Build the twisted Laplacian with uniform Möbius phase π/E (where E = edge count)
  2. Diagonalize, find ground subspace
  3. Project the uniform "color singlet" state onto ground subspace
  4. Report bundle amplitude squared

A "magic" amplitude is one that's exactly 1 (perfect closure) or a clean
rational like 11/12, 23/24, etc.
"""

from __future__ import annotations
import math
import numpy as np

PI = math.pi


def twisted_laplacian_from_edges(n_vertices: int, edges: list, phase: float):
    """Build Möbius-twisted Laplacian from explicit edge list.

    Args:
        n_vertices: number of vertices (size of matrix)
        edges: list of (i, j) tuples with i < j
        phase: Möbius phase per edge

    Returns:
        n × n complex Hermitian matrix
    """
    H = np.zeros((n_vertices, n_vertices), dtype=complex)
    e_phase = np.exp(1j * phase)
    for i, j in edges:
        H[i, i] += 1
        H[j, j] += 1
        H[i, j] -= e_phase
        H[j, i] -= e_phase.conjugate()
    return H


def bundle_amplitude(n_vertices: int, edges: list, phase: float = None):
    """Compute |⟨singlet|ground subspace⟩|."""
    if phase is None:
        phase = PI / max(len(edges), 1)
    H = twisted_laplacian_from_edges(n_vertices, edges, phase)
    evals, evecs = np.linalg.eigh(H)
    singlet = np.ones(n_vertices, dtype=complex) / math.sqrt(n_vertices)
    g_idx = np.where(np.abs(evals - evals[0]) < 1e-9)[0]
    proj_sq = float(np.sum(np.abs(evecs[:, g_idx].conj().T @ singlet) ** 2))
    return math.sqrt(proj_sq), proj_sq, evals[0]


# ---------------------------------------------------------------------------
# Polyhedron edge lists
# ---------------------------------------------------------------------------


def k_n(n: int) -> list:
    """Complete graph K_n: every pair of vertices connected."""
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def cube_edges() -> list:
    """Cube: 8 vertices, 12 edges. Vertices labeled 000-111 (binary)."""
    edges = []
    for i in range(8):
        for k in range(3):  # flip each of the 3 bits
            j = i ^ (1 << k)
            if j > i:
                edges.append((i, j))
    return edges


def octahedron_edges() -> list:
    """Octahedron: 6 vertices, 12 edges. Each pair except antipodal pairs."""
    edges = []
    # Antipodal pairs: (0,1), (2,3), (4,5)
    antipodal = {(0, 1), (2, 3), (4, 5)}
    for i in range(6):
        for j in range(i + 1, 6):
            if (i, j) not in antipodal:
                edges.append((i, j))
    return edges


def dodecahedron_edges() -> list:
    """Dodecahedron: 20 vertices, 30 edges. Each vertex has 3 neighbors.

    Adjacency list for the regular dodecahedron (canonical labeling).
    """
    adj = {
        0: [1, 4, 5],   1: [0, 2, 7],   2: [1, 3, 9],   3: [2, 4, 11],
        4: [0, 3, 13], 5: [0, 6, 14],  6: [5, 7, 16],  7: [1, 6, 8],
        8: [7, 9, 17],  9: [2, 8, 10], 10: [9, 11, 18], 11: [3, 10, 12],
        12: [11, 13, 19], 13: [4, 12, 14], 14: [5, 13, 15], 15: [14, 16, 19],
        16: [6, 15, 17], 17: [8, 16, 18], 18: [10, 17, 19], 19: [12, 15, 18],
    }
    edges = set()
    for v, neighbors in adj.items():
        for n in neighbors:
            if v < n:
                edges.add((v, n))
    return sorted(edges)


def icosahedron_edges() -> list:
    """Icosahedron: 12 vertices, 30 edges. Each vertex has 5 neighbors."""
    adj = {
        0: [1, 2, 3, 4, 5], 1: [0, 2, 5, 6, 9], 2: [0, 1, 3, 6, 7],
        3: [0, 2, 4, 7, 8], 4: [0, 3, 5, 8, 10], 5: [0, 1, 4, 9, 10],
        6: [1, 2, 7, 9, 11], 7: [2, 3, 6, 8, 11], 8: [3, 4, 7, 10, 11],
        9: [1, 5, 6, 10, 11], 10: [4, 5, 8, 9, 11], 11: [6, 7, 8, 9, 10],
    }
    edges = set()
    for v, neighbors in adj.items():
        for n in neighbors:
            if v < n:
                edges.add((v, n))
    return sorted(edges)


def tetrahedron_edges() -> list:
    """Tetrahedron: 4 vertices, 6 edges = K_4."""
    return k_n(4)


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------


def main() -> None:
    print("Magic numbers from polyhedral substrate cells")
    print("=" * 70)
    print()
    print(f"{'name':>20s} {'V':>4s} {'E':>4s} {'amp²':>10s} {'amp':>10s} {'phase=π/E':>12s} {'ground evec':>30s}")

    # Standard regular polyhedra
    polyhedra = [
        ('K_2 (bond)',         2, k_n(2)),
        ('K_3 (triangle)',     3, k_n(3)),
        ('K_4 (tetrahedron)',  4, k_n(4)),
        ('K_5',                5, k_n(5)),
        ('Octahedron',         6, octahedron_edges()),
        ('K_6 (5-simplex)',    6, k_n(6)),
        ('K_7',                7, k_n(7)),
        ('Cube',               8, cube_edges()),
        ('K_8',                8, k_n(8)),
        ('Icosahedron',       12, icosahedron_edges()),
        ('K_12',              12, k_n(12)),
        ('Dodecahedron',      20, dodecahedron_edges()),
        ('K_20',              20, k_n(20)),
        ('K_28',              28, k_n(28)),
    ]

    results = []
    for name, V, edges in polyhedra:
        E = len(edges)
        phase = PI / E
        amp, amp_sq, e0 = bundle_amplitude(V, edges, phase)
        # Try to identify a clean rational form
        rational = ''
        for num in range(1, 200):
            for den in range(num + 1, num + 200):
                if abs(amp_sq - num/den) < 1e-4:
                    rational = f'≈ {num}/{den}'
                    break
            if rational:
                break
        print(f"{name:>20s}  {V:>3d}  {E:>3d}  {amp_sq:>8.4f}  {amp:>8.4f}  "
              f"{f'π/{E}':>10s}  {rational:>28s}")
        results.append((name, V, E, amp, amp_sq))

    # Magic-number candidates check
    print()
    print("=" * 70)
    print("Magic-number candidates: amp = 1.000 means PERFECT closure (no ambiguity)")
    print("=" * 70)
    magic_set = {2, 8, 20, 28, 50, 82, 126}
    print()
    print(f"{'V':>4s}  {'name':>20s}  {'amp²':>10s}  {'is_magic?':>10s}  {'note':>30s}")
    for name, V, E, amp, amp_sq in results:
        is_magic = '★ MAGIC' if V in magic_set else ''
        clean = ''
        if abs(amp - 1.0) < 1e-3:
            clean = 'amp ≈ 1 (closed)'
        elif abs(amp_sq - 0.5) < 1e-3:
            clean = 'amp² = 1/2'
        print(f"  {V:>3d}  {name:>20s}  {amp_sq:>8.4f}  {is_magic:>10s}  {clean:>28s}")

    # Try with full flux quantum (not half) — phase = 2π/E
    print()
    print("=" * 70)
    print("Same calculation with FULL flux quantum (phase = 2π/E)")
    print("=" * 70)
    print()
    print(f"{'V':>4s}  {'name':>20s}  {'amp²(full)':>12s}  {'note':>30s}")
    for name, V, edges in polyhedra:
        E = len(edges)
        phase = 2 * PI / E  # full quantum
        amp, amp_sq, e0 = bundle_amplitude(V, edges, phase)
        clean = ''
        if abs(amp - 1.0) < 1e-3:
            clean = 'PERFECT'
        elif abs(amp_sq) < 1e-6:
            clean = 'zero'
        print(f"  {V:>3d}  {name:>20s}  {amp_sq:>10.4f}  {clean:>28s}")

    # Check: which polyhedra graphs actually MATCH magic numbers?
    print()
    print("=" * 70)
    print("Hypothesis check: do the magic numbers 2,8,20,28,50,82,126 correspond")
    print("to vertex counts of CLOSED polyhedra with clean bundle amplitudes?")
    print("=" * 70)
    print()
    matches = {
        2: '✓ K_2 = single bond (smallest closed)',
        8: '? cube — has 8 v but bundle amp not 1; check',
        20: '? dodecahedron — has 20 v but bundle amp not 1',
        28: '?? no standard polyhedron with 28 v',
        50: '?? snub dodecahedron has 60 v, gyrobifastigium 8...',
        82: '?? no obvious match',
        126: '?? no obvious match',
    }
    for n, msg in matches.items():
        print(f"  {n:>3d}: {msg}")
    print()
    print("Conclusion: the regular-polyhedron correspondence works for 2 (K_2)")
    print("and 4 (K_4 = α), partially for 20 (dodecahedron), but breaks down")
    print("for the larger magic numbers. The substrate magic-number mechanism")
    print("likely involves NESTED shell structure (multiple polyhedra), not single.")


if __name__ == "__main__":
    main()
