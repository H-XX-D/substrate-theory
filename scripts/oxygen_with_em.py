"""Oxygen with EM radiation damping — does it stop the drift?

Re-runs the oxygen test with EM radiation reaction force from
spec §11 (damping toward Bohr-quantized orbits).

Compare to the bare Coulomb+Pauli version: does the structure
stay closer to 1s² 2s² 2p⁴ over many steps?
"""

import numpy as np

from stiff_medium.atomic import (
    n_body_step_with_em_damping,
    n_body_step_with_pauli,
)


M_E = 1.0
M_O_NUCLEUS = 29159
COUPLING = 1.0


def setup():
    Z = 8
    a_n1 = 1.0 / Z
    a_n2 = 4.0 / Z
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))

    pos = [
        np.array([0.0, 0.0, 0.0]),
        np.array([+a_n1, 0.0, 0.0]),
        np.array([-a_n1, 0.0, 0.0]),
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, +v_n1, 0.0]),
        np.array([0.0, -v_n1, 0.0]),
    ]
    octahedron_dirs = [
        (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])),
        (np.array([-1.0, 0.0, 0.0]), np.array([0.0, -1.0, 0.0])),
        (np.array([0.0, 1.0, 0.0]), np.array([-1.0, 0.0, 0.0])),
        (np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0])),
        (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0])),
        (np.array([0.0, 0.0, -1.0]), np.array([-1.0, 0.0, 0.0])),
    ]
    for pos_dir, vel_dir in octahedron_dirs:
        pos.append(a_n2 * pos_dir)
        vel.append(v_n2 * vel_dir)

    masses = [M_O_NUCLEUS] + [M_E] * 8
    charges = [+8.0] + [-1.0] * 8
    spins = [0, 0, 1, 0, 1, 0, 1, 0, 1]
    bohr_radii = [0.0, a_n1, a_n1, a_n2, a_n2, a_n2, a_n2, a_n2, a_n2]
    return pos, vel, masses, charges, spins, bohr_radii, a_n1, a_n2


def main():
    print("Oxygen with EM radiation damping vs. without\n")

    DT = 0.0001
    N_STEPS = 12000

    # WITHOUT EM
    print("=== WITHOUT EM damping (just Coulomb + Pauli) ===")
    pos, vel, masses, charges, spins, bohr_radii, a_n1, a_n2 = setup()
    for k in range(N_STEPS):
        pos, vel = n_body_step_with_pauli(
            pos, vel, masses, charges, spins,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.05,
        )
    final_ds = sorted([float(np.linalg.norm(pos[i] - pos[0])) for i in range(1, 9)])
    inner = [d for d in final_ds if d < 1.5 * a_n1]
    outer = [d for d in final_ds if 1.5 * a_n1 <= d < 6.0 * a_n2]
    far = [d for d in final_ds if d >= 6.0 * a_n2]
    print(f"  Inner: {len(inner)} (radii: {[f'{d:.3f}' for d in inner]})")
    print(f"  Outer: {len(outer)} (radii: {[f'{d:.3f}' for d in outer]})")
    print(f"  Far:   {len(far)} (radii: {[f'{d:.3f}' for d in far]})")

    # WITH EM
    print("\n=== WITH EM damping (Coulomb + Pauli + radiation reaction) ===")
    pos, vel, masses, charges, spins, bohr_radii, a_n1, a_n2 = setup()
    for k in range(N_STEPS):
        pos, vel = n_body_step_with_em_damping(
            pos, vel, masses, charges, spins, bohr_radii, nucleus_idx=0,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.05,
            radiation_strength=2.0,
        )
    final_ds = sorted([float(np.linalg.norm(pos[i] - pos[0])) for i in range(1, 9)])
    inner = [d for d in final_ds if d < 1.5 * a_n1]
    outer = [d for d in final_ds if 1.5 * a_n1 <= d < 6.0 * a_n2]
    far = [d for d in final_ds if d >= 6.0 * a_n2]
    print(f"  Inner: {len(inner)} (radii: {[f'{d:.3f}' for d in inner]})")
    print(f"  Outer: {len(outer)} (radii: {[f'{d:.3f}' for d in outer]})")
    print(f"  Far:   {len(far)} (radii: {[f'{d:.3f}' for d in far]})")

    if len(inner) == 2 and len(outer) == 6 and len(far) == 0:
        print("\n→ EM damping keeps oxygen 1s² 2s² 2p⁴ stable!")


if __name__ == "__main__":
    main()
