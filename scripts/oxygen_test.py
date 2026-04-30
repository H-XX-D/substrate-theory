"""Oxygen (Z=8) — eight electrons, ground state 1s² 2s² 2p⁴.

Real oxygen: 2 in n=1 (1s²), 6 in n=2 (2s² 2p⁴).
"""

import numpy as np

from stiff_medium.atomic import n_body_step_with_pauli, reduced_mass


M_E = 1.0
M_O_NUCLEUS = 29159  # 16O / m_e
COUPLING = 1.0


def main():
    Z = 8
    print(f"Oxygen (Z={Z}) ground-state simulation\n")

    a_n1 = 1.0 / Z
    a_n2 = 4.0 / Z
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))

    print(f"n=1: r={a_n1:.4f}, v={v_n1:.4f}")
    print(f"n=2: r={a_n2:.4f}, v={v_n2:.4f}\n")

    # 8 electrons. Inner pair in n=1 (opposite spins).
    # Outer 6 distributed around the atom in n=2.
    pos = [
        np.array([0.0, 0.0, 0.0]),  # nucleus
        np.array([+a_n1, 0.0, 0.0]),  # e0: n=1, spin 0
        np.array([-a_n1, 0.0, 0.0]),  # e1: n=1, spin 1
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, +v_n1, 0.0]),
        np.array([0.0, -v_n1, 0.0]),
    ]
    # Place 6 outer electrons at vertices of an octahedron, alternating spin
    octahedron_dirs = [
        (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])),
        (np.array([-1.0, 0.0, 0.0]), np.array([0.0, -1.0, 0.0])),
        (np.array([0.0, 1.0, 0.0]), np.array([-1.0, 0.0, 0.0])),
        (np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0])),
        (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0])),
        (np.array([0.0, 0.0, -1.0]), np.array([-1.0, 0.0, 0.0])),
    ]
    for i, (pos_dir, vel_dir) in enumerate(octahedron_dirs):
        pos.append(a_n2 * pos_dir)
        vel.append(v_n2 * vel_dir)

    masses = [M_O_NUCLEUS] + [M_E] * 8
    charges = [+8.0] + [-1.0] * 8
    spins = [0, 0, 1, 0, 1, 0, 1, 0, 1]  # alternating spins on outer 6

    DT = 0.0001
    N_STEPS = 12000

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

    print(f"Final shell occupancy after {N_STEPS} steps:")
    print(f"  Inner (n=1): {len(inner)} (radii: {[f'{d:.3f}' for d in inner]})")
    print(f"  Outer (n=2): {len(outer)} (radii: {[f'{d:.3f}' for d in outer]})")
    print(f"  Far/escaped: {len(far)}")
    if len(inner) == 2 and len(outer) == 6:
        print("→ Oxygen 1s² 2s² 2p⁴ shell structure (qualitatively).")
    elif len(inner) >= 2 and len(outer) >= 4:
        print(f"→ Approximately the right shell structure.")
    else:
        print(f"→ Configuration drifted significantly.")


if __name__ == "__main__":
    main()
