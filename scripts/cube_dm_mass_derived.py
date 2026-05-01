"""Derive cube-cell DM mass from bound-state spectrum (not heuristic).

For K_4 (proton):
  Lowest eigenvalue ε_K4 of twisted Laplacian = 0.06815 (with phase π/6)
  This sets m_proton via m c² = ℏ × ω_bounce where ω ∝ ε

For cube (Q_3 graph, 8 vertices, 12 edges):
  Compute ε_cube with phase π/12
  Mass ratio: m_cube / m_proton = ε_cube / ε_K4

This is a proper substrate calculation, not "vertex-count-ratio".
"""

from __future__ import annotations
import math
import numpy as np


PI = math.pi
M_PROTON_GEV = 0.93827


def k4_twisted_laplacian():
    H = np.zeros((4, 4), dtype=complex)
    p = np.exp(1j * PI / 6)  # phase π/6 per edge for K_4 with Möbius half-flux
    for i in range(4):
        for j in range(i+1, 4):
            H[i,i] += 1
            H[j,j] += 1
            H[i,j] -= p
            H[j,i] -= p.conjugate()
    return H


def cube_twisted_laplacian():
    H = np.zeros((8, 8), dtype=complex)
    p = np.exp(1j * PI / 12)  # phase π/12 per edge for cube with Möbius half-flux
    edges = []
    for i in range(8):
        for k in range(3):  # 3 bit positions
            j = i ^ (1 << k)
            if j > i:
                edges.append((i, j))
    for i, j in edges:
        H[i,i] += 1
        H[j,j] += 1
        H[i,j] -= p
        H[j,i] -= p.conjugate()
    return H


def main() -> None:
    print("Cube-DM mass from substrate bound-state spectrum")
    print("=" * 70)
    print()

    # K_4 spectrum
    H4 = k4_twisted_laplacian()
    e4 = sorted(np.linalg.eigvalsh(H4))
    print("K_4 (nucleon cell, 4 vertices, 6 edges):")
    print(f"  Eigenvalues (sorted): {[f'{e:.4f}' for e in e4]}")
    print(f"  Lowest (bound-state): ε_K4 = {e4[0]:.6f}")
    print(f"  → calibrates m_proton = 938.27 MeV")
    print(f"  → mass-energy unit: ℏω/ε = {M_PROTON_GEV / e4[0]:.4f} GeV per ε-unit")
    print()

    # Cube spectrum
    H8 = cube_twisted_laplacian()
    e8 = sorted(np.linalg.eigvalsh(H8))
    print("Cube Q_3 (DM cell, 8 vertices, 12 edges):")
    print(f"  Eigenvalues (sorted): {[f'{e:.4f}' for e in e8]}")
    print(f"  Lowest (bound-state): ε_cube = {e8[0]:.6f}")
    print()

    # Mass ratio
    ratio = e8[0] / e4[0]
    m_DM_substrate = M_PROTON_GEV * ratio
    print(f"  Mass ratio m_DM / m_proton = ε_cube / ε_K4 = {ratio:.4f}")
    print(f"  m_DM (substrate-derived) = {m_DM_substrate:.4f} GeV")
    print()

    # Higher-eigenvalue bound states (excited cube modes)
    print(f"  All cube bound states (substrate excitation tower):")
    print(f"  {'eigenvalue':>14s}  {'mass [GeV]':>14s}")
    for e in e8:
        m = M_PROTON_GEV * e / e4[0]
        print(f"  {e:>12.6f}    {m:>10.4f}")
    print()

    # Compare to GCE preference
    print("=" * 70)
    print("Comparison to GCE preferred mass")
    print("=" * 70)
    print()
    GCE_PREFER = {
        'qq̄ channel (light quarks)': 5.0,
        'bb̄ channel (heavy quarks)': 36.0,
    }
    print(f"  Substrate cube-DM ground-state mass: {m_DM_substrate:.2f} GeV")
    for chan, m_pref in GCE_PREFER.items():
        ratio_p = m_DM_substrate / m_pref
        print(f"  GCE-preferred ({chan}): {m_pref} GeV")
        print(f"    Substrate / GCE ratio: {ratio_p:.3f}")
    print()

    # Excited states might be the real signature
    print(f"  Substrate cube excited states (could appear in Belle II / collider):")
    for i, e in enumerate(e8[1:], start=1):
        m = M_PROTON_GEV * e / e4[0]
        marker = ' ← matches qq̄ best fit (~5 GeV)' if 4.5 < m < 5.5 else (
                 ' ← matches bb̄ best fit (~36 GeV)' if 30 < m < 42 else '')
        print(f"    Mode {i}: m = {m:.2f} GeV{marker}")


if __name__ == "__main__":
    main()
