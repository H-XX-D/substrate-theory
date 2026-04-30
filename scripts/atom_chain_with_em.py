"""Multi-atom chain with EM radiation damping — H, He, Li, Be, C, O, Ne.

Verify that adding EM radiation reaction (per spec §18.19) gives stable
ground states across the periodic table's first row.

Real ground states:
- H (Z=1): 1s¹ — 1 electron in n=1
- He (Z=2): 1s² — 2 in n=1
- Li (Z=3): 1s² 2s¹ — 2 in n=1, 1 in n=2
- Be (Z=4): 1s² 2s² — 2 in n=1, 2 in n=2
- C (Z=6): 1s² 2s² 2p² — 2 in n=1, 4 in n=2
- O (Z=8): 1s² 2s² 2p⁴ — 2 in n=1, 6 in n=2
- Ne (Z=10): 1s² 2s² 2p⁶ — 2 in n=1, 8 in n=2 (full)
"""

import numpy as np

from stiff_medium.atomic import n_body_step_with_em_damping


M_E = 1.0
COUPLING = 1.0


def setup_atom(Z: int, n_electrons: int):
    """Set up an atom with Z protons and n_electrons. Place electrons:
    first 2 in n=1 shell, rest in n=2."""
    a_n1 = 1.0 / Z
    a_n2 = 4.0 / Z
    v_n1 = float(np.sqrt(Z / a_n1))
    v_n2 = float(np.sqrt(Z / a_n2))

    pos = [np.array([0.0, 0.0, 0.0])]
    vel = [np.array([0.0, 0.0, 0.0])]
    masses = [Z * 1836.0]
    charges = [float(Z)]
    spins = [0]
    bohr_radii = [0.0]

    # n=1 shell: up to 2 electrons
    n1_dirs = [
        (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 0),
        (np.array([-1.0, 0.0, 0.0]), np.array([0.0, -1.0, 0.0]), 1),
    ]
    for i in range(min(2, n_electrons)):
        pos_dir, vel_dir, spin = n1_dirs[i]
        pos.append(a_n1 * pos_dir)
        vel.append(v_n1 * vel_dir)
        masses.append(M_E)
        charges.append(-1.0)
        spins.append(spin)
        bohr_radii.append(a_n1)

    # n=2 shell: up to 8 electrons (octahedral + 2 axial pairs)
    n2_dirs = [
        (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 0),
        (np.array([-1.0, 0.0, 0.0]), np.array([0.0, -1.0, 0.0]), 1),
        (np.array([0.0, 1.0, 0.0]), np.array([-1.0, 0.0, 0.0]), 0),
        (np.array([0.0, -1.0, 0.0]), np.array([1.0, 0.0, 0.0]), 1),
        (np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]), 0),
        (np.array([0.0, 0.0, -1.0]), np.array([-1.0, 0.0, 0.0]), 1),
        (np.array([1.0, 1.0, 0.0]) / np.sqrt(2), np.array([-1.0, 1.0, 0.0]) / np.sqrt(2), 0),
        (np.array([-1.0, -1.0, 0.0]) / np.sqrt(2), np.array([1.0, -1.0, 0.0]) / np.sqrt(2), 1),
    ]
    n_outer = max(0, n_electrons - 2)
    for i in range(min(8, n_outer)):
        pos_dir, vel_dir, spin = n2_dirs[i]
        pos.append(a_n2 * pos_dir)
        vel.append(v_n2 * vel_dir)
        masses.append(M_E)
        charges.append(-1.0)
        spins.append(spin)
        bohr_radii.append(a_n2)

    return pos, vel, masses, charges, spins, bohr_radii, a_n1, a_n2


def run_atom(name: str, Z: int, n_electrons: int):
    pos, vel, masses, charges, spins, bohr_radii, a_n1, a_n2 = setup_atom(Z, n_electrons)
    expected_inner = min(2, n_electrons)
    expected_outer = max(0, n_electrons - 2)

    DT = 0.0001
    N_STEPS = 10000

    for k in range(N_STEPS):
        pos, vel = n_body_step_with_em_damping(
            pos, vel, masses, charges, spins, bohr_radii, nucleus_idx=0,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.05,
            radiation_strength=2.0,
        )

    final_ds = sorted([float(np.linalg.norm(pos[i] - pos[0])) for i in range(1, n_electrons + 1)])
    inner = sum(1 for d in final_ds if d < 1.5 * a_n1)
    outer = sum(1 for d in final_ds if 1.5 * a_n1 <= d < 6.0 * a_n2)
    far = sum(1 for d in final_ds if d >= 6.0 * a_n2)

    success = (inner == expected_inner) and (outer == expected_outer) and (far == 0)
    marker = "✓" if success else "✗"
    print(f"  {name:>2} (Z={Z:>2}, e={n_electrons:>2}): "
          f"inner={inner}/{expected_inner} outer={outer}/{expected_outer} far={far} {marker}")


def main():
    print("Multi-atom chain with EM damping (spec §18.19)\n")
    print("Atom: inner=actual/expected outer=actual/expected escaped result\n")

    for name, Z, n_e in [
        ("H", 1, 1),
        ("He", 2, 2),
        ("Li", 3, 3),
        ("Be", 4, 4),
        ("C", 6, 6),
        ("O", 8, 8),
        ("Ne", 10, 10),
    ]:
        run_atom(name, Z, n_e)


if __name__ == "__main__":
    main()
