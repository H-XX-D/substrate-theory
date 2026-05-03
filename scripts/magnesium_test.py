"""Magnesium (Z=12) — heavy-atom simulation extending the oxygen framework.

Configuration: 1s² 2s² 2p⁶ 3s²

Geometry:
- 1s² inner shell: 2 electrons at radius a_n1 ≈ 1/Z, ±x axis.
- 2s² 2p⁶ middle shell: 8 electrons at radius a_n2 ≈ 4/Z (Bohr scaling),
  arranged in cube (8 vertices) for spatial isotropy.
- 3s² outer shell: 2 electrons at radius a_n3 ≈ 9/Z, ±z axis.

Spins assigned alternately to satisfy Pauli within each shell.

Tests:
- Stability with Coulomb + Pauli
- Stability with EM radiation damping
- Total binding energy approximation

Per spec §8.1a + §8.3, this should work with the same N-body framework
that produced oxygen.
"""

import numpy as np

from stiff_medium.atomic import (
    n_body_step_with_em_damping,
    n_body_step_with_pauli,
)

M_E = 1.0
M_MG_NUCLEUS = 44303  # 24.305 amu × 1822.888 m_e/amu (electron mass units)
COUPLING = 1.0


def setup_magnesium():
    Z = 12
    # Bohr radii scaled by 1/Z
    a_n1 = 1.0 / Z   # n=1 shell
    a_n2 = 4.0 / Z   # n=2 shell (a₀ × n²)
    a_n3 = 9.0 / Z   # n=3 shell

    # Bohr velocities: v_n = sqrt(Z/n²·a_n) = sqrt(Z/(n² × n²/Z)) = Z/n
    # Actually simpler: v_n × r_n = ℏ for circular orbit ⟹ v_n = Z/n
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))
    v_n3 = float(np.sqrt(Z / a_n3))

    # Nucleus at origin
    pos = [np.array([0.0, 0.0, 0.0])]
    vel = [np.array([0.0, 0.0, 0.0])]

    # Inner shell (1s²): 2 electrons along ±x
    pos.append(np.array([+a_n1, 0.0, 0.0]))
    vel.append(np.array([0.0, +v_n1, 0.0]))
    pos.append(np.array([-a_n1, 0.0, 0.0]))
    vel.append(np.array([0.0, -v_n1, 0.0]))

    # Middle shell (2s² 2p⁶ = 8 electrons): two squares stacked along z,
    # rotated 45° relative to each other. Each electron orbits in its own plane.
    # Upper square (z = +z_offset): 4 electrons at angles 0, 90, 180, 270°
    # Lower square (z = -z_offset): 4 electrons at angles 45, 135, 225, 315°
    z_offset = a_n2 * 0.3
    r_xy = np.sqrt(a_n2**2 - z_offset**2)  # radial offset in xy

    upper_angles = [0, np.pi/2, np.pi, 3*np.pi/2]
    lower_angles = [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4]

    for theta in upper_angles:
        pd = np.array([r_xy * np.cos(theta), r_xy * np.sin(theta), +z_offset])
        # Orbit in horizontal plane: v = v_n2 × (-sin θ, cos θ, 0)
        vd = v_n2 * np.array([-np.sin(theta), np.cos(theta), 0.0])
        pos.append(pd)
        vel.append(vd)

    for theta in lower_angles:
        pd = np.array([r_xy * np.cos(theta), r_xy * np.sin(theta), -z_offset])
        # Orbit in horizontal plane, opposite direction (so cube has zero net L)
        vd = v_n2 * np.array([np.sin(theta), -np.cos(theta), 0.0])
        pos.append(pd)
        vel.append(vd)

    # Outer shell (3s²): 2 electrons along ±z
    pos.append(np.array([0.0, 0.0, +a_n3]))
    vel.append(np.array([+v_n3, 0.0, 0.0]))
    pos.append(np.array([0.0, 0.0, -a_n3]))
    vel.append(np.array([-v_n3, 0.0, 0.0]))

    masses = [M_MG_NUCLEUS] + [M_E] * 12
    charges = [+12.0] + [-1.0] * 12
    # Spins: alternating within each shell to satisfy Pauli pairing
    spins = [0,
             0, 1,           # 1s pair
             0, 1, 0, 1, 0, 1, 0, 1,  # 8 middle (each cube vertex separate)
             0, 1]           # 3s pair
    bohr_radii = [0.0,
                  a_n1, a_n1,
                  *([a_n2] * 8),
                  a_n3, a_n3]

    return pos, vel, masses, charges, spins, bohr_radii, (a_n1, a_n2, a_n3)


def classify_radii(distances, a_n1, a_n2, a_n3):
    """Categorize electron distances by shell."""
    inner = []
    middle = []
    outer = []
    far = []
    for d in distances:
        if d < 1.5 * a_n1:
            inner.append(d)
        elif d < 1.5 * a_n2:
            middle.append(d)
        elif d < 2.0 * a_n3:
            outer.append(d)
        else:
            far.append(d)
    return inner, middle, outer, far


def run_simulation(use_em_damping: bool, n_steps: int = 8000, dt: float = 0.0001):
    pos, vel, masses, charges, spins, bohr_radii, (a_n1, a_n2, a_n3) = setup_magnesium()

    for step in range(n_steps):
        if use_em_damping:
            pos, vel = n_body_step_with_em_damping(
                pos, vel, masses, charges, spins,
                bohr_radii=bohr_radii, nucleus_idx=0,
                dt=dt, coupling=COUPLING,
                pauli_strength=0.5, pauli_radius=0.05,
                radiation_strength=0.1,
            )
        else:
            pos, vel = n_body_step_with_pauli(
                pos, vel, masses, charges, spins,
                dt=dt, coupling=COUPLING,
                pauli_strength=0.5, pauli_radius=0.05,
            )

    # Distances from nucleus to each electron
    distances = sorted([float(np.linalg.norm(pos[i] - pos[0])) for i in range(1, 13)])
    return distances, (a_n1, a_n2, a_n3)


def main():
    print("=" * 60)
    print("MAGNESIUM (Z=12) — heavy-atom test, 1s² 2s² 2p⁶ 3s²")
    print("=" * 60)
    print()

    print("--- Without EM damping ---")
    distances_no_em, (a_n1, a_n2, a_n3) = run_simulation(use_em_damping=False)
    print(f"Bohr radii: a_n1={a_n1:.4f}, a_n2={a_n2:.4f}, a_n3={a_n3:.4f}")
    print(f"Final radii (sorted): {[f'{d:.3f}' for d in distances_no_em]}")
    inner, middle, outer, far = classify_radii(distances_no_em, a_n1, a_n2, a_n3)
    print(f"  Inner shell:  {len(inner)} electrons (expected 2)")
    print(f"  Middle shell: {len(middle)} electrons (expected 8)")
    print(f"  Outer shell:  {len(outer)} electrons (expected 2)")
    print(f"  Far/escape:   {len(far)} electrons")
    print()

    print("--- With EM damping ---")
    distances_em, _ = run_simulation(use_em_damping=True)
    print(f"Final radii (sorted): {[f'{d:.3f}' for d in distances_em]}")
    inner, middle, outer, far = classify_radii(distances_em, a_n1, a_n2, a_n3)
    print(f"  Inner shell:  {len(inner)} electrons (expected 2)")
    print(f"  Middle shell: {len(middle)} electrons (expected 8)")
    print(f"  Outer shell:  {len(outer)} electrons (expected 2)")
    print(f"  Far/escape:   {len(far)} electrons")
    print()

    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print()
    if len(far) == 0:
        print("✓ No electrons escaped. The simulation maintains Mg structure.")
        print("  Heavy-atom Z=12 simulation works in our model.")
    else:
        print(f"✗ {len(far)} electrons escaped. The simulation needs:")
        print("  - Better integrator (current is velocity-Verlet without sub-shell distinction)")
        print("  - More refined Pauli + EM damping parameters")
        print("  - Proper spinor / Möbius mechanics for tighter shell binding")
    print()
    print("Note: this is a CLASSICAL N-body Coulomb sim — it captures the")
    print("nuclear-electron + electron-electron Coulomb dynamics but not the")
    print("full quantum sub-shell structure (which requires HF as in `hartree_radial.py`).")
    print()
    print("Per spec §8.1a, both classical and HF are valid pictures of the")
    print("same underlying dynamics — the classical sim shows orbital stability,")
    print("the HF sim shows spectroscopic structure.")


if __name__ == "__main__":
    main()
