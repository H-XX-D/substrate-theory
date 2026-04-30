"""H₂ molecule formation: first chemistry-scale prediction.

Setup:
- 2 protons (charge +1, mass m_p ≈ 1836 m_e)
- 2 electrons (charge −1, mass 1 m_e), opposite spins (Pauli-allowed)

Expected result if our model produces real chemistry:
- Stable bound state with proton-proton distance ≈ 2 × a₀ (real H₂ bond
  length is ~1.4 × a₀ ≈ 74 pm; in our units a₀ = 1, so bond length ~1.4)
- Bond energy ~ 0.17 hartree ≈ 4.48 eV (real H₂ binding)

The mechanism: opposite-spin electrons can both occupy the region
between the two protons. This concentration of negative charge
between the protons creates effective attraction that overcomes
proton-proton Coulomb repulsion, producing a stable molecule.

If protons fly apart → no bond.
If protons coincide → simulation breaks (need short-range repulsion).
If they stabilize at some intermediate distance → covalent bond.
"""

import numpy as np

from stiff_medium.atomic import n_body_step_with_pauli, reduced_mass


M_E = 1.0
M_P = 1836.15
COUPLING = 1.0


def run_h2(name: str, initial_pp_distance: float):
    """Simulate two H atoms approaching each other, see if they bond."""
    print(f"\n=== {name} ===")
    print(f"Initial proton-proton distance: {initial_pp_distance:.4f}")

    # Layout: protons on x-axis at ±d/2, electrons orbiting their respective
    # protons initially.
    d = initial_pp_distance
    # Each electron starts at the Bohr radius of its associated proton
    a0 = 1.0  # Bohr radius in our natural units (with COUPLING=1, M_E=1, HBAR=1)
    v_e = float(np.sqrt(1.0 / a0))  # circular orbit velocity for hydrogen

    # Place protons on x-axis. Place each electron a Bohr radius "above" its
    # proton, with tangential velocity in +y or -y. This roughly corresponds
    # to two free hydrogen atoms.
    pos = [
        np.array([-d / 2, 0.0, 0.0]),  # proton 1
        np.array([d / 2, 0.0, 0.0]),   # proton 2
        np.array([-d / 2, a0, 0.0]),   # electron 1 (up-spin)
        np.array([d / 2, -a0, 0.0]),    # electron 2 (down-spin)
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        np.array([v_e, 0.0, 0.0]),     # electron 1 orbiting proton 1
        np.array([-v_e, 0.0, 0.0]),    # electron 2 orbiting proton 2
    ]
    masses = [M_P, M_P, M_E, M_E]
    charges = [+1.0, +1.0, -1.0, -1.0]
    spins = [0, 1, 0, 1]  # opposite spins on the two electrons (Pauli-allowed)

    DT = 0.001
    N_STEPS = 50000

    # Track proton-proton distance over time
    pp_history = []
    samples = []

    for k in range(N_STEPS):
        pos, vel = n_body_step_with_pauli(
            pos, vel, masses, charges, spins,
            dt=DT, coupling=COUPLING,
            pauli_strength=0.5, pauli_radius=0.3,
        )
        pp_dist = float(np.linalg.norm(pos[1] - pos[0]))
        pp_history.append(pp_dist)
        if k in (0, 5000, 10000, 20000, 30000, 40000, 49999):
            d_p1e1 = float(np.linalg.norm(pos[2] - pos[0]))
            d_p2e2 = float(np.linalg.norm(pos[3] - pos[1]))
            samples.append((k, pp_dist, d_p1e1, d_p2e2))

    print(f"\n{'step':>6} | {'p-p dist':>9} | {'p1-e1':>7} | {'p2-e2':>7}")
    print("-" * 42)
    for k, pp, p1e1, p2e2 in samples:
        print(f"{k:>6} | {pp:>9.4f} | {p1e1:>7.4f} | {p2e2:>7.4f}")

    # Diagnose: did the protons stay bound?
    pp_history = np.asarray(pp_history)
    half = N_STEPS // 2
    pp_window = pp_history[half:]

    pp_min = float(pp_window.min())
    pp_max = float(pp_window.max())
    pp_mean = float(pp_window.mean())

    print(f"\nSecond-half p-p distance: min={pp_min:.4f}, max={pp_max:.4f}, mean={pp_mean:.4f}")

    if pp_max > 4.0 * initial_pp_distance:
        print("→ Protons FLEW APART. No bond formed.")
    elif pp_min < 0.1:
        print("→ Protons COLLIDED. Need stronger short-range repulsion.")
    elif pp_max < 2.0 * initial_pp_distance:
        print(f"→ STABLE BOND. Mean proton-proton distance: {pp_mean:.4f}.")
        print(f"   Real H₂ bond length: ~1.4 × a₀.")
    else:
        print(f"→ Oscillating: range {pp_min:.4f} to {pp_max:.4f}.")


def main():
    print("H₂ molecule bond-formation simulation\n")
    print("Two protons + two electrons (opposite spins).")
    print("Real H₂ bond length: 1.4 × a₀ (where a₀ = 1 in our natural units).")
    print("Real H₂ binding energy: 0.17 hartree.\n")

    # Try several starting distances to see if there's a stable bond
    for d_init in (1.0, 1.5, 2.0, 3.0, 5.0):
        run_h2(f"Initial p-p distance = {d_init} a₀", d_init)


if __name__ == "__main__":
    main()
