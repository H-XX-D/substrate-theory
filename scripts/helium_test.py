"""Helium ground state: simplest test of multi-electron atomic structure.

Setup:
- Nucleus with charge +2 (helium-4 alpha core), mass ~7300 m_e
- Two electrons, charges −1 each, masses 1 m_e
- Both electrons should bind in the n=1 shell (per §18.5 shell-filling
  derivation, n=1 holds 2 electrons of opposite Möbius twist)

Test 1: opposite-Möbius electrons → both bind (real helium configuration).
Test 2: same-Möbius electrons → only one binds (Pauli-forbidden state).

This is the first multi-particle test of the spec's foundation. Per
spec §18.8, multi-particle dynamics is additive pairwise at leading
order. Per §18.5, two electrons fit in n=1 shell as opposite-Möbius
pair.
"""

import numpy as np

from stiff_medium.atomic import n_body_newton_step, reduced_mass


# Real helium parameters (in m_e units)
M_E = 1.0
M_HE_NUCLEUS = 7294.3  # alpha-particle mass / electron mass
COUPLING = 1.0
HBAR = 1.0


def bohr_radius_for_helium(mu: float, z: int) -> float:
    """For nuclear charge Z, the n=1 Bohr radius is a_0 = ℏ²/(Z μ e²)."""
    return HBAR * HBAR / (z * mu * COUPLING)


def initial_velocity(mu: float, r: float, z: int) -> float:
    """Circular orbit velocity for charge Z at radius r."""
    return float(np.sqrt(z * COUPLING / (mu * r)))


def run_helium(name: str, electron_a_phase_offset: float):
    """Two electrons + nucleus, with electrons phase-offset by `electron_a_phase_offset`.
    Phase offset of π = opposite Möbius twist (Pauli-allowed pair).
    Phase offset of 0 = same Möbius twist (Pauli-forbidden pair, only one should bind).
    """
    print(f"\n=== {name} ===")
    z = 2  # helium nucleus charge

    # Use reduced mass for circular-orbit setup
    mu = reduced_mass(M_E, M_HE_NUCLEUS)
    r_bohr = bohr_radius_for_helium(mu, z)
    v_e = initial_velocity(mu, r_bohr, z)

    # In the COM frame, electrons orbit on opposite sides of the nucleus
    # to start. Setup: nucleus at origin, electron_a at (-r, 0, 0),
    # electron_b at (+r, 0, 0). Tangential velocities pointing in +y and -y.
    # (For the same-Möbius test, this initial geometry is identical; only
    # the implicit Pauli factor would change in a Möbius-aware sim. For now,
    # we run pure Coulomb dynamics — the test is whether 2 electrons CAN
    # bind to a Z=2 nucleus, not yet whether spin states differ.)
    pos = [
        np.array([0.0, 0.0, 0.0]),               # nucleus
        np.array([-r_bohr, 0.0, 0.0]),           # electron A
        np.array([r_bohr, 0.0, 0.0]),            # electron B
    ]
    vel = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, v_e, 0.0]),
        np.array([0.0, -v_e, 0.0]),
    ]
    masses = [M_HE_NUCLEUS, M_E, M_E]
    charges = [+2.0, -1.0, -1.0]

    print(f"Z = {z}, μ ≈ {mu:.4f}, r_bohr ≈ {r_bohr:.6f}, v_e ≈ {v_e:.4f}")
    print(f"Initial: nucleus at {pos[0]}, e_A at {pos[1]}, e_B at {pos[2]}")

    DT = 0.0001
    N_STEPS = 100000

    samples = []
    for k in range(N_STEPS):
        pos, vel = n_body_newton_step(pos, vel, masses, charges, dt=DT, coupling=COUPLING)
        if k in (0, 5000, 20000, 50000, 80000, 99999):
            d_a = float(np.linalg.norm(pos[1] - pos[0]))
            d_b = float(np.linalg.norm(pos[2] - pos[0]))
            d_ee = float(np.linalg.norm(pos[1] - pos[2]))
            samples.append((k, d_a, d_b, d_ee))

    print(f"\n{'step':>6} | {'d(N,e_A)':>9} | {'d(N,e_B)':>9} | {'d(e_A,e_B)':>11}")
    print("-" * 50)
    for k, d_a, d_b, d_ee in samples:
        print(f"{k:>6} | {d_a:>9.4f} | {d_b:>9.4f} | {d_ee:>11.4f}")

    # Are both electrons still bound? (within 10 × Bohr radius)
    final = samples[-1]
    bound_a = final[1] < 10 * r_bohr
    bound_b = final[2] < 10 * r_bohr
    print()
    print(f"Final state: e_A {'BOUND' if bound_a else 'UNBOUND'}, e_B {'BOUND' if bound_b else 'UNBOUND'}")


def main():
    print("Helium ground-state simulation\n")
    print("Nucleus (Z=2) + two electrons, both starting at n=1 Bohr radius")
    print("on opposite sides, tangential velocities for circular orbit.\n")

    run_helium("Two electrons orbiting Z=2 nucleus (Coulomb only, no Möbius)", 0.0)


if __name__ == "__main__":
    main()
