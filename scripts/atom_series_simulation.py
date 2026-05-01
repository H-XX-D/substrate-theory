"""Atom series: H → D → T → ³He → ⁴He as fused-tetrahedron substrate cells.

Builds successively larger nucleus + electron-cloud configurations and:
  1. Sweeps k_strong / k_em ratio to find the natural force hierarchy
  2. Computes static energies and bundle amplitudes
  3. Runs vector-dynamics simulations showing energy propagation

Geometric construction:
  Each nucleon = K_4 tetrahedron (4v: 1 apex + 3 quarks)
  Adjacent nucleons share their quark-triangle face (the 3 equatorial quarks)
  Each electron = single vertex attached to one nucleon's apex
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

PI = math.pi


# ---------------------------------------------------------------------------
# Atom builder
# ---------------------------------------------------------------------------


@dataclass
class Atom:
    """Substrate-cell representation of an atom.

    Vertices: ordered list of node names.
    Edges: list of (node_a, node_b, edge_class) where edge_class ∈
        {'lateral', 'equatorial', 'electron'}.
    """
    name: str
    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str, str]] = field(default_factory=list)

    def index(self, node: str) -> int:
        return self.nodes.index(node)

    def n_nodes(self) -> int:
        return len(self.nodes)

    def n_edges(self) -> int:
        return len(self.edges)

    def edges_of_class(self, cls: str) -> list[tuple[str, str]]:
        return [(a, b) for a, b, c in self.edges if c == cls]


def build_hydrogen() -> Atom:
    """H = proton + electron. 4-vertex proton tetrahedron + 1 electron."""
    a = Atom('H')
    a.nodes = ['N', 'Q1', 'Q2', 'Q3', 'E']
    # Proton tetrahedron edges
    for u, v in [('N', 'Q1'), ('N', 'Q2'), ('N', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    for u, v in [('Q1', 'Q2'), ('Q2', 'Q3'), ('Q3', 'Q1')]:
        a.edges.append((u, v, 'equatorial'))
    a.edges.append(('E', 'N', 'electron'))
    return a


def build_deuterium() -> Atom:
    """D = proton + neutron + electron. Bipyramid + electron at proton apex."""
    a = Atom('D')
    a.nodes = ['N', 'Q1', 'Q2', 'Q3', 'S', 'E']
    for u, v in [('N', 'Q1'), ('N', 'Q2'), ('N', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    for u, v in [('Q1', 'Q2'), ('Q2', 'Q3'), ('Q3', 'Q1')]:
        a.edges.append((u, v, 'equatorial'))
    for u, v in [('S', 'Q1'), ('S', 'Q2'), ('S', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    a.edges.append(('E', 'N', 'electron'))
    return a


def build_tritium() -> Atom:
    """T = proton + 2 neutrons + electron.

    Geometry: the 3rd nucleon (2nd neutron) attaches to the proton's apex,
    sharing the proton's 3-quark face from below... no — each nucleon needs
    its own quark-triangle. The natural extension: stack a 2nd neutron on
    the OTHER side of the bipyramid, sharing the 3-quark face from below.
    Wait — that's only 5 vertices then.

    Actually the bipyramid already has the neutron on one apex side. To add
    a 2nd neutron, we need ANOTHER 3-quark face. Geometric option: extend
    the 2nd neutron with a NEW 3-quark face that it shares with the 1st
    neutron OR with the proton via a different vertex.

    Cleanest: the 2nd neutron forms a tetrahedron sharing the SOUTH apex's
    3-vertex face (which is just S + 2 of the original quarks + 1 new quark).
    But that's not a clean shared face.

    Practical model: tritium = bipyramid (5 vertices) + extra apex T
    attached to one EQUATORIAL quark (let's say Q1). This represents the
    2nd neutron as an extra branch off the existing nucleus.

    Total: 5 + 1 (extra apex T) + 1 (electron) = 7 nodes.
    """
    a = Atom('T')
    a.nodes = ['N', 'Q1', 'Q2', 'Q3', 'S', 'T2', 'E']
    for u, v in [('N', 'Q1'), ('N', 'Q2'), ('N', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    for u, v in [('Q1', 'Q2'), ('Q2', 'Q3'), ('Q3', 'Q1')]:
        a.edges.append((u, v, 'equatorial'))
    for u, v in [('S', 'Q1'), ('S', 'Q2'), ('S', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    # 2nd neutron T2 shares 3 quarks (forms a 2nd neutron-tetrahedron with
    # the same equatorial triangle but a different apex)
    for u, v in [('T2', 'Q1'), ('T2', 'Q2'), ('T2', 'Q3')]:
        a.edges.append((u, v, 'lateral'))
    a.edges.append(('E', 'N', 'electron'))
    return a


def build_helium4() -> Atom:
    """⁴He = 2p + 2n + 2e.

    Geometry: alpha-particle structure is highly symmetric. Use the
    tetrahedral-of-tetrahedra: 4 nucleons at vertices of a meta-tetrahedron,
    each sharing 3 quark-vertices with the central core.

    Simpler concrete model:
      - Central 3-quark core (Q1, Q2, Q3) shared by ALL 4 nucleons
      - 4 apices (N1, N2 = protons; N3, N4 = neutrons) sticking out
      - 2 electrons (E1, E2), each attached to one proton apex

    Total: 3 (core quarks) + 4 (nucleon apices) + 2 (electrons) = 9 nodes.
    """
    a = Atom('He4')
    a.nodes = ['Q1', 'Q2', 'Q3', 'N1', 'N2', 'N3', 'N4', 'E1', 'E2']
    # Core equatorial triangle
    for u, v in [('Q1', 'Q2'), ('Q2', 'Q3'), ('Q3', 'Q1')]:
        a.edges.append((u, v, 'equatorial'))
    # 4 nucleon apices, each connected to all 3 quarks
    for apex in ['N1', 'N2', 'N3', 'N4']:
        for q in ['Q1', 'Q2', 'Q3']:
            a.edges.append((apex, q, 'lateral'))
    # 2 electrons attached to the 2 proton apices
    a.edges.append(('E1', 'N1', 'electron'))
    a.edges.append(('E2', 'N2', 'electron'))
    return a


# ---------------------------------------------------------------------------
# Möbius-twisted Laplacian + analysis
# ---------------------------------------------------------------------------


def twisted_laplacian(atom: Atom, *, k_strong=1.0, k_em=1.0, phase_lat=PI/6,
                       phase_eq=PI/6, phase_em=PI/2) -> np.ndarray:
    """Möbius-twisted Laplacian. Different edge classes can have different
    stiffness and Möbius phase."""
    n = atom.n_nodes()
    H = np.zeros((n, n), dtype=complex)
    for u, v, cls in atom.edges:
        i, j = atom.index(u), atom.index(v)
        if cls == 'lateral':
            k, phi = k_strong, phase_lat
        elif cls == 'equatorial':
            k, phi = k_strong, phase_eq
        else:  # electron
            k, phi = k_em, phase_em
        H[i, i] += k
        H[j, j] += k
        H[i, j] -= k * np.exp(1j * phi)
        H[j, i] -= k * np.exp(-1j * phi)
    return H


def real_laplacian(atom: Atom, *, k_strong=1.0, k_em=1.0) -> np.ndarray:
    """Real Laplacian for dynamics simulation."""
    n = atom.n_nodes()
    L = np.zeros((n, n), dtype=float)
    for u, v, cls in atom.edges:
        i, j = atom.index(u), atom.index(v)
        k = k_em if cls == 'electron' else k_strong
        L[i, i] += k
        L[j, j] += k
        L[i, j] -= k
        L[j, i] -= k
    return L


def binding_energy(atom: Atom, *, k_strong=1.0, k_em=1.0) -> float:
    """Sum of substrate strain energies in the ground state.

    Approximated as ½ × trace(L) for the ground mode normalized to unit norm.
    More precisely: the binding is the sum of edge strain energies for the
    substrate bound state.
    """
    L = real_laplacian(atom, k_strong=k_strong, k_em=k_em)
    evals, evecs = np.linalg.eigh(L)
    # Ground mode (smallest eigenvalue, but ignore the zero/uniform mode)
    # The binding energy is in the LOWEST non-trivial mode
    # Sum of edge strain energies in that mode:
    nontrivial = [i for i, e in enumerate(evals) if e > 1e-9]
    if not nontrivial:
        return 0.0
    ground_idx = nontrivial[0]
    psi = evecs[:, ground_idx]
    e_total = 0.0
    for u, v, cls in atom.edges:
        i, j = atom.index(u), atom.index(v)
        k = k_em if cls == 'electron' else k_strong
        e_total += 0.5 * k * (psi[i] - psi[j]) ** 2
    return float(e_total)


def total_strain_energy_per_class(atom: Atom, u_state: np.ndarray, *,
                                   k_strong=1.0, k_em=1.0) -> dict:
    """Return strain energy per edge class for a given displacement state."""
    e_class = {'lateral': 0.0, 'equatorial': 0.0, 'electron': 0.0}
    for uu, vv, cls in atom.edges:
        i, j = atom.index(uu), atom.index(vv)
        k = k_em if cls == 'electron' else k_strong
        du = u_state[i] - u_state[j]
        e_class[cls] += 0.5 * k * du * du
    return e_class


# ---------------------------------------------------------------------------
# Force-strength hierarchy sweep
# ---------------------------------------------------------------------------


def hierarchy_sweep(atom: Atom, k_em_values=None) -> list[dict]:
    """Sweep k_em / k_strong ratio and report binding energies."""
    if k_em_values is None:
        k_em_values = [1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    results = []
    for k_em in k_em_values:
        be = binding_energy(atom, k_strong=1.0, k_em=k_em)
        L = real_laplacian(atom, k_strong=1.0, k_em=k_em)
        evals = np.linalg.eigvalsh(L)
        results.append({
            'k_em': k_em,
            'binding_energy': be,
            'gap': float(evals[1]) if len(evals) > 1 else 0.0,
            'top_mode': float(evals[-1]),
        })
    return results


# ---------------------------------------------------------------------------
# Vector-dynamics simulation
# ---------------------------------------------------------------------------


def simulate(atom: Atom, *, k_strong=1.0, k_em=0.01, n_steps=400, dt=0.05,
             initial_node='E') -> dict:
    """Run substrate-strain dynamics with electron initially excited."""
    L = real_laplacian(atom, k_strong=k_strong, k_em=k_em)
    n = atom.n_nodes()
    u = np.zeros(n)
    v = np.zeros(n)
    if initial_node in atom.nodes:
        u[atom.index(initial_node)] = 1.0

    history = {'t': [], 'lateral': [], 'equatorial': [], 'electron': [], 'total': []}
    for step in range(n_steps):
        v -= dt * L @ u
        u += dt * v
        e = total_strain_energy_per_class(atom, u, k_strong=k_strong, k_em=k_em)
        kinetic = 0.5 * float(np.sum(v * v))
        history['t'].append(step * dt)
        history['lateral'].append(e['lateral'])
        history['equatorial'].append(e['equatorial'])
        history['electron'].append(e['electron'])
        history['total'].append(e['lateral'] + e['equatorial'] + e['electron'] + kinetic)
    return {k: np.array(v) for k, v in history.items()}


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------


def report_atom(atom: Atom) -> None:
    print(f"\n{'='*70}")
    print(f"Atom: {atom.name}")
    print(f"{'='*70}")
    print(f"Vertices ({atom.n_nodes()}): {atom.nodes}")
    edges_by_class = {}
    for _, _, c in atom.edges:
        edges_by_class[c] = edges_by_class.get(c, 0) + 1
    print(f"Edges ({atom.n_edges()}): {edges_by_class}")

    print(f"\n--- Force-hierarchy sweep ---")
    print(f"{'k_em':>10s} {'binding':>12s} {'gap':>10s} {'top_mode':>10s}")
    for r in hierarchy_sweep(atom):
        print(f"  {r['k_em']:>8.0e}  {r['binding_energy']:>10.4f}  {r['gap']:>8.4f}  {r['top_mode']:>8.4f}")

    # Pick first available electron node
    e_nodes = [n for n in atom.nodes if n.startswith('E')]
    init_node = e_nodes[0] if e_nodes else atom.nodes[0]
    print(f"\n--- Dynamics: kick {init_node} at t=0, k_em/k_strong = 0.01 ---")
    sim = simulate(atom, k_strong=1.0, k_em=0.01, n_steps=400, dt=0.05,
                   initial_node=init_node)
    print(f"{'t':>8s} {'lateral':>12s} {'equator':>12s} {'electron':>12s} {'total':>10s}")
    for snap_t in [0.0, 1.0, 5.0, 10.0, 15.0, 19.95]:
        idx = min(int(snap_t / 0.05), len(sim['t']) - 1)
        print(f"  {sim['t'][idx]:>6.2f}   {sim['lateral'][idx]:>10.4f}   "
              f"{sim['equatorial'][idx]:>10.4f}   {sim['electron'][idx]:>10.4f}   "
              f"{sim['total'][idx]:>8.4f}")
    drift = (sim['total'][-1] - sim['total'][0]) / sim['total'][0]
    print(f"  Energy drift: {100*drift:.4f}%")


def main() -> None:
    print("Atom-series substrate-cell simulation")
    print("=====================================")
    print("Each nucleon = K_4 tetrahedron (4 vertices: 1 apex + 3 quarks)")
    print("Adjacent nucleons share the 3-quark equatorial face")
    print("Electrons attach to nucleon apices via single 'electron' edges")
    print()

    atoms = [
        build_hydrogen(),
        build_deuterium(),
        build_tritium(),
        build_helium4(),
    ]

    for atom in atoms:
        report_atom(atom)

    # ------- Cross-atom comparison -------
    print()
    print("=" * 70)
    print("Cross-atom comparison (k_em / k_strong = 0.01)")
    print("=" * 70)
    print(f"{'atom':>8s} {'nodes':>6s} {'edges':>6s} {'BE_low':>10s} {'BE_total':>12s} {'BE_total/A':>12s}")
    for atom in atoms:
        be_lowmode = binding_energy(atom, k_strong=1.0, k_em=0.01)
        # Better proxy: total bound-state strain integrated across ALL bound modes.
        # For a complete K_n graph, this scales with the sum of nontrivial eigenvalues.
        L = real_laplacian(atom, k_strong=1.0, k_em=0.01)
        evals = np.linalg.eigvalsh(L)
        # Bound modes: all nontrivial (excluding the global zero/translation mode)
        nontrivial = sorted([e for e in evals if e > 1e-9])
        be_total = sum(nontrivial)
        # Nucleon count = vertex count minus electron count minus quark count beyond apex
        n_apex = sum(1 for n in atom.nodes if n.startswith('N') or n in ('S', 'T2'))
        A = max(n_apex, 1)
        print(f"  {atom.name:>6s}  {atom.n_nodes():>4d}  {atom.n_edges():>4d}  "
              f"{be_lowmode:>8.4f}  {be_total:>10.4f}  {be_total/A:>10.4f}")
    print()
    print("BE_total = sum of bound-state mode energies; BE_total/A normalizes by")
    print("nucleon count. ⁴He per-A = 'binding per nucleon' analog for α-particle.")


if __name__ == "__main__":
    main()
