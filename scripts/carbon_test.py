"""Carbon (Z=6) — six electrons, ground state 1s² 2s² 2p².

Real carbon: 2 in n=1 (1s²), 2 in n=2 s-orbital (2s²), 2 in n=2 p-orbital (2p²).
For our simulation, we don't yet distinguish s/p sub-shells, so we treat all
n=2 electrons as in the same shell.

Bohr-like radii for Z=6:
  - n=1: 1/Z = 0.167
  - n=2: 4/Z = 0.667

Test: 6 electrons placed in correct shells with correct spin assignments,
run, see if structure persists.
"""

import numpy as np

from stiff_medium.atomic import n_body_step_with_pauli, reduced_mass


M_E = 1.0
M_C_NUCLEUS = 21864  # 12C mass / m_e
COUPLING = 1.0


def main():
    Z = 6
    print(f"Carbon (Z={Z}) ground-state simulation\n")

    a_n1 = 1.0 / Z
    a_n2 = 4.0 / Z
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))

    print(f"n=1 radius: {a_n1:.4f}, orbital v: {v_n1:.4f}")
    print(f"n=2 radius: {a_n2:.4f}, orbital v: {v_n2:.4f}\n")

    # 6 electrons: 2 in n=1 (opposite spins), 4 in n=2 (must include both spins)
    # Place n=1 pair on x-axis, n=2 quartet at 90° intervals around y/z plane.
    pos = [
        np.array([0.0, 0.0, 0.0]),                      # nucleus
        np.array([+a_n1, 0.0, 0.0]),                    # e0: n=1, spin 0
        np.array([-a_n1, 0.0, 0.0]),                    # e1: n=1, spin 1
        np.array([+a_n2, 0.0, 0.0]),                    # e2: n=2, spin 0
        np.array([-a_n2, 0.0, 0.0]),                    # e3: n=2, spin 1
        np.array([0.0, +a_n2, 0.0]),                    # e4: n=2, spin 0
        np.array([0.0, -a_n2, 0.0]),                    # e5: n=2, spin 1
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, +v_n1, 0.0]),
        np.array([0.0, -v_n1, 0.0]),
        np.array([0.0, +v_n2, 0.0]),
        np.array([0.0, -v_n2, 0.0]),
        np.array([+v_n2, 0.0, 0.0]),
        np.array([-v_n2, 0.0, 0.0]),
    ]
    masses = [M_C_NUCLEUS] + [M_E] * 6
    charges = [+6.0] + [-1.0] * 6
    spins = [0, 0, 1, 0, 1, 0, 1]  # nucleus spin irrelevant

    DT = 0.0001
    N_STEPS = 15000

    samples = []
    for k in range(N_STEPS):
        pos, vel = n_body_step_with_pauli(
            pos, vel, masses, charges, spins,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.1,
        )
        if k in (0, 5000, 10000, 14999):
            ds = [float(np.linalg.norm(pos[i] - pos[0])) for i in range(1, 7)]
            samples.append((k, ds))

    print(f"{'step':>6} | {'e0':>7} | {'e1':>7} | {'e2':>7} | {'e3':>7} | {'e4':>7} | {'e5':>7}")
    print("-" * 60)
    for k, ds in samples:
        print(f"{k:>6} | " + " | ".join(f"{d:>7.4f}" for d in ds))

    final_ds = sorted(samples[-1][1])
    inner = [d for d in final_ds if d < 1.5 * a_n1]
    outer = [d for d in final_ds if 1.5 * a_n1 <= d < 4.0 * a_n2]
    far = [d for d in final_ds if d >= 4.0 * a_n2]

    print(f"\nFinal shell occupancy:")
    print(f"  Inner (n=1): {len(inner)} electrons (radii: {[f'{d:.3f}' for d in inner]})")
    print(f"  Outer (n=2): {len(outer)} electrons (radii: {[f'{d:.3f}' for d in outer]})")
    print(f"  Far/escaped: {len(far)} electrons")
    if len(inner) == 2 and len(outer) == 4 and len(far) == 0:
        print("→ Carbon 1s² 2s² 2p² shell structure reproduced (treating 2s and 2p as same shell).")


if __name__ == "__main__":
    main()
