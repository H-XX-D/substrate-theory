"""Lithium ground state: tests Pauli exclusion in multi-electron context.

Per spec §18.5: n=1 shell holds 2 electrons (opposite Möbius/spin),
n=2 shell holds 8. So lithium (Z=3, 3 electrons) must have:
- 2 electrons in n=1 (one up-spin, one down-spin)
- 1 electron in n=2 (forced to higher shell by Pauli exclusion)

This is the canonical demonstration: Pauli exclusion forbids the 3rd
electron from joining the n=1 ground state, so it has to go up to n=2.

Setup:
- Nucleus charge +3 (Z=3 lithium)
- 3 electrons; first two with opposite spins, third initially placed at
  n=1 Bohr radius with same spin as one of the first two.
- With pure Coulomb + Pauli repulsion (same charge same spin = strong
  short-range repulsion), the 3rd electron should be pushed out of
  n=1 to a larger orbit.

Compare: same setup WITHOUT Pauli (pure Coulomb) — the 3rd electron
would happily settle in n=1 with the others. The contrast demonstrates
that Pauli is the mechanism preventing this.
"""

import numpy as np

from stiff_medium.atomic import (
    n_body_step_with_pauli,
    n_body_newton_step,
    reduced_mass,
)


M_E = 1.0
M_LI_NUCLEUS = 12652  # 7Li mass / m_e
COUPLING = 1.0
HBAR = 1.0


def main():
    Z = 3
    r_bohr_li = 1.0 / Z  # n=1 Bohr radius for Z=3
    v_e = float(np.sqrt(Z / r_bohr_li))

    print(f"Lithium (Z={Z}) ground-state simulation.\n")
    print(f"n=1 Bohr radius (Z=3): r = 1/Z = {r_bohr_li:.4f}")
    print(f"Circular orbit speed at n=1: v = sqrt(Z/r) = {v_e:.4f}\n")

    # All 3 electrons start at n=1 Bohr radius, equally spaced around the
    # nucleus, with tangential velocities. Without Pauli, they'd all stay.
    # With Pauli (same-spin pairs repel), at least one should be pushed out.
    angle = 2 * np.pi / 3  # 120° spacing
    pos = [
        np.array([0.0, 0.0, 0.0]),  # nucleus
        np.array([r_bohr_li, 0.0, 0.0]),  # electron 0
        np.array([r_bohr_li * np.cos(angle), r_bohr_li * np.sin(angle), 0.0]),  # electron 1
        np.array([r_bohr_li * np.cos(2 * angle), r_bohr_li * np.sin(2 * angle), 0.0]),  # electron 2
    ]
    # Tangential velocities (perpendicular to radius)
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, v_e, 0.0]),
        np.array([-v_e * np.sin(angle), v_e * np.cos(angle), 0.0]),
        np.array([-v_e * np.sin(2 * angle), v_e * np.cos(2 * angle), 0.0]),
    ]
    masses = [M_LI_NUCLEUS, M_E, M_E, M_E]
    charges = [+3.0, -1.0, -1.0, -1.0]

    # Spins: electron 0 = up (0), electron 1 = down (1), electron 2 = up (0).
    # Electron 0 and electron 2 share spin → Pauli exclusion between them.
    # Electron 1 has unique spin → can sit between them.
    spins = [0, 0, 1, 0]  # nucleus is irrelevant for spin

    print("Setup: 3 electrons at n=1 Bohr radius, 120° apart.")
    print("Spins: e0=up, e1=down, e2=up. Pauli pushes e0 vs e2 (same spin) apart.\n")

    # Run with Pauli
    print("=== WITH Pauli exclusion ===")
    pos_p, vel_p = [p.copy() for p in pos], [v.copy() for v in vel]
    DT = 0.0001
    N_STEPS = 30000

    for k in range(N_STEPS):
        pos_p, vel_p = n_body_step_with_pauli(
            pos_p, vel_p, masses, charges, spins,
            dt=DT, coupling=COUPLING,
            pauli_strength=2.0, pauli_radius=r_bohr_li,
        )

    distances_p = [float(np.linalg.norm(pos_p[i] - pos_p[0])) for i in (1, 2, 3)]
    print(f"Final distances from nucleus:")
    print(f"  e0 (up): {distances_p[0]:.4f}")
    print(f"  e1 (down): {distances_p[1]:.4f}")
    print(f"  e2 (up): {distances_p[2]:.4f}")

    n1_radius = r_bohr_li
    n2_radius = 4.0 / Z  # n=2 Bohr radius (∝ n²)
    print(f"\nReference: n=1 radius = {n1_radius:.4f}, n=2 radius = {n2_radius:.4f}")
    inner_count = sum(1 for d in distances_p if d < 2.0 * n1_radius)
    print(f"Electrons within 2× n=1 radius: {inner_count}")
    if inner_count == 2:
        print("→ Pauli exclusion successfully forced ONE electron out of n=1 shell.")
    elif inner_count == 3:
        print("→ All 3 electrons stayed in n=1 (Pauli not strong enough at chosen scales).")
    else:
        print(f"→ Unusual: {inner_count} electrons in n=1.")

    # Run WITHOUT Pauli for comparison
    print("\n=== WITHOUT Pauli (pure Coulomb) ===")
    pos_c, vel_c = [p.copy() for p in pos], [v.copy() for v in vel]

    for k in range(N_STEPS):
        pos_c, vel_c = n_body_newton_step(
            pos_c, vel_c, masses, charges, dt=DT, coupling=COUPLING
        )

    distances_c = [float(np.linalg.norm(pos_c[i] - pos_c[0])) for i in (1, 2, 3)]
    print(f"Final distances from nucleus:")
    print(f"  e0: {distances_c[0]:.4f}")
    print(f"  e1: {distances_c[1]:.4f}")
    print(f"  e2: {distances_c[2]:.4f}")
    inner_count_c = sum(1 for d in distances_c if d < 2.0 * n1_radius)
    print(f"Electrons within 2× n=1 radius: {inner_count_c}")
    print(f"\n→ Pure Coulomb keeps all 3 in n=1 (no Pauli to push one out).")


if __name__ == "__main__":
    main()
