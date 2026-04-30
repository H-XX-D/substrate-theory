"""Beryllium (Z=4, 4 electrons) — multi-shell test.

Real Be ground state: 1s² 2s² (2 electrons in n=1 shell, 2 in n=2).
With Pauli respected, putting 2 same-spin electrons in n=1 should
fail; putting 2 opposite-spin in n=1 + 2 opposite-spin in n=2 should
work.

Bohr-like radii for Z=4:
  - n=1 shell: a_0/Z = 0.25
  - n=2 shell: 4 × a_0/Z = 1.0

Test setup: 4 electrons placed in correct shells with correct spin
assignments (2 in inner with opposite spins, 2 in outer with opposite
spins). Run and see if the structure persists.
"""

import numpy as np

from stiff_medium.atomic import n_body_step_with_pauli, reduced_mass


M_E = 1.0
M_BE_NUCLEUS = 16424  # Be-9 mass / m_e
COUPLING = 1.0


def main():
    Z = 4
    print(f"Beryllium (Z={Z}) ground-state simulation\n")

    a_n1 = 1.0 / Z   # n=1 Bohr-like radius for Z=4
    a_n2 = 4.0 / Z   # n=2 Bohr-like radius for Z=4
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))

    print(f"n=1 radius: {a_n1:.4f}, orbital v: {v_n1:.4f}")
    print(f"n=2 radius: {a_n2:.4f}, orbital v: {v_n2:.4f}\n")

    # Place 4 electrons at correct shell radii with correct spins.
    # Inner pair (n=1): spin 0 at +x, spin 1 at -x — opposite spins, opposite sides.
    # Outer pair (n=2): spin 0 at +y, spin 1 at -y — opposite spins, opposite sides.
    pos = [
        np.array([0.0, 0.0, 0.0]),                      # nucleus
        np.array([+a_n1, 0.0, 0.0]),                    # e0: n=1, spin 0
        np.array([-a_n1, 0.0, 0.0]),                    # e1: n=1, spin 1
        np.array([0.0, +a_n2, 0.0]),                    # e2: n=2, spin 0
        np.array([0.0, -a_n2, 0.0]),                    # e3: n=2, spin 1
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, +v_n1, 0.0]),                    # e0 orbits
        np.array([0.0, -v_n1, 0.0]),                    # e1 orbits opposite
        np.array([-v_n2, 0.0, 0.0]),                    # e2 orbits
        np.array([+v_n2, 0.0, 0.0]),                    # e3 orbits opposite
    ]
    masses = [M_BE_NUCLEUS, M_E, M_E, M_E, M_E]
    charges = [+4.0, -1.0, -1.0, -1.0, -1.0]
    spins = [0, 0, 1, 0, 1]  # nucleus spin irrelevant; e0/e2 same spin, e1/e3 same spin

    DT = 0.0001
    N_STEPS = 20000

    samples = []
    for k in range(N_STEPS):
        pos, vel = n_body_step_with_pauli(
            pos, vel, masses, charges, spins,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.1,
        )
        if k in (0, 5000, 10000, 15000, 19999):
            ds = [float(np.linalg.norm(pos[i] - pos[0])) for i in (1, 2, 3, 4)]
            samples.append((k, ds))

    print(f"{'step':>6} | {'e0(0,n=1)':>10} | {'e1(1,n=1)':>10} | {'e2(0,n=2)':>10} | {'e3(1,n=2)':>10}")
    print("-" * 65)
    for k, ds in samples:
        print(f"{k:>6} | {ds[0]:>10.4f} | {ds[1]:>10.4f} | {ds[2]:>10.4f} | {ds[3]:>10.4f}")

    final_ds = samples[-1][1]
    inner_count = sum(1 for d in final_ds if d < 1.5 * a_n1)
    outer_count = sum(1 for d in final_ds if 1.5 * a_n1 <= d < 3.0 * a_n2)
    far_count = sum(1 for d in final_ds if d >= 3.0 * a_n2)

    print(f"\nFinal shell occupancy:")
    print(f"  Inner (n=1, within 1.5× a_n1): {inner_count}")
    print(f"  Outer (n=2): {outer_count}")
    print(f"  Far (escaped): {far_count}")
    if inner_count == 2 and outer_count == 2 and far_count == 0:
        print("→ Beryllium ground state structurally reproduced.")
    else:
        print("→ Configuration drifted from idealized 1s² 2s² ground state.")


if __name__ == "__main__":
    main()
