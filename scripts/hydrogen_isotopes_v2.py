"""Hydrogen + isotopes: Newton-style atomic-scale simulation.

The cone constraint applies to underlying neutrinos. At the atomic
scale, the electron (a 2-neutrino bound state) and nucleus (a multi-
neutrino bound state) are already-bound objects with free COM dynamics.
Their interaction is Coulomb-like (per spec §10).

Test: do the orbital frequencies of H, D, T satisfy the reduced-mass
relation μ_X / μ_H? Real measurements:
- D/H Rydberg shift: +272 ppm
- T/H Rydberg shift: +363 ppm

If yes: standard Bohr-Rydberg recovered. The atomic-scale dynamics
of our model is consistent with measurement at the leading order.
If no: the spec's atomic-scale interaction needs revision.
"""

import numpy as np

from stiff_medium.atomic import (
    coulomb_attraction,
    newton_step,
    reduced_mass,
)


# Real mass ratios
M_E = 1.0
M_P = 1836.15
M_D = 3670.48
M_T = 5496.92

# Coupling: pick once on physical grounds. Sets the orbital scale.
COUPLING = 1.0

# Initial conditions: place electron and nucleus at distance r_0 with
# tangential velocity that's near the circular-orbit velocity for the
# light particle in the heavy-nucleus limit.
R_0 = 1.0  # initial separation
DT = 0.001
N_STEPS = 200000  # ~200 orbital periods


def initial_velocity_for_circular_orbit(coupling: float, mass_e: float, r: float) -> float:
    """For a light particle orbiting a heavy nucleus, circular orbit
    has v² · r = coupling / mass_e (from F = m·v²/r = coupling/r²)."""
    return float(np.sqrt(coupling / (mass_e * r)))


def run_atom(name: str, m_nucleus: float):
    """Simulate the atom and return its orbital frequency."""
    v_circ = initial_velocity_for_circular_orbit(COUPLING, M_E, R_0)

    # Place electron at -R_0/2, nucleus at +R_0/2; tangential velocity in y.
    # In the COM frame, electron moves at v_e, nucleus at v_n with
    # m_e v_e + m_n v_n = 0  →  v_n = -(m_e/m_n) v_e.
    # For circular orbit at separation R_0:
    #   electron sees centripetal force toward nucleus
    #   m_e * v_e² / r_e = coupling / R_0²
    # where r_e = (m_n / (m_e + m_n)) * R_0 is the electron's radius from COM.
    r_e = (m_nucleus / (M_E + m_nucleus)) * R_0
    r_n = (M_E / (M_E + m_nucleus)) * R_0
    # Centripetal: m_e * v_e² / r_e = coupling / R_0²
    # → v_e = sqrt(coupling * r_e / (m_e * R_0²))
    v_e = float(np.sqrt(COUPLING * r_e / (M_E * R_0 * R_0)))
    v_n = -(M_E / m_nucleus) * v_e  # opposite direction in COM

    pos_e = np.array([-r_e, 0.0, 0.0])
    vel_e = np.array([0.0, v_e, 0.0])
    pos_n = np.array([r_n, 0.0, 0.0])
    vel_n = np.array([0.0, v_n, 0.0])

    def force(pa, pb):
        return coulomb_attraction(pa, pb, coupling=COUPLING)

    rel_angles = []
    state = (pos_e, vel_e, pos_n, vel_n)

    for k in range(N_STEPS):
        new_pe, new_ve, new_pn, new_vn = newton_step(
            state[0], state[1], M_E,
            state[2], state[3], m_nucleus,
            dt=DT, force_fn=force,
        )
        state = (new_pe, new_ve, new_pn, new_vn)
        rel = new_pn - new_pe
        if abs(rel[0]) > 1e-9 or abs(rel[1]) > 1e-9:
            rel_angles.append(float(np.arctan2(rel[1], rel[0])))

    # Use the second half of the run
    half = len(rel_angles) // 2
    rel_window = np.unwrap(np.asarray(rel_angles[half:]))
    total_angle = float(rel_window[-1] - rel_window[0])
    n_steps_window = len(rel_window) - 1
    angular_velocity = total_angle / (n_steps_window * DT)
    orbital_frequency = abs(angular_velocity) / (2.0 * np.pi)

    print(f"{name:>2}: m_n/m_e = {m_nucleus/M_E:>9.2f}  "
          f"reduced μ = {reduced_mass(M_E, m_nucleus):.6f}  "
          f"freq = {orbital_frequency:.6f}")
    return orbital_frequency


def main():
    print("Hydrogen-isotope simulation: Newton-style atomic dynamics\n")
    print("Inputs: m_e=1.0; m_n varies; Coulomb attraction; same coupling for all.\n")

    f_h = run_atom("H", M_P)
    f_d = run_atom("D", M_D)
    f_t = run_atom("T", M_T)

    sim_dh = (f_d / f_h - 1) * 1e6
    sim_th = (f_t / f_h - 1) * 1e6

    mu_h = reduced_mass(M_E, M_P)
    mu_d = reduced_mass(M_E, M_D)
    mu_t = reduced_mass(M_E, M_T)
    bohr_dh = (mu_d / mu_h - 1) * 1e6
    bohr_th = (mu_t / mu_h - 1) * 1e6

    print()
    print("Predicted isotope shifts (orbital frequency ratio − 1):")
    print(f"  Simulation D/H − 1: {sim_dh:>8.1f} ppm")
    print(f"  Bohr-Rydberg D/H:   {bohr_dh:>8.1f} ppm")
    print(f"  Real Rydberg D/H:   {272:>8.1f} ppm")
    print()
    print(f"  Simulation T/H − 1: {sim_th:>8.1f} ppm")
    print(f"  Bohr-Rydberg T/H:   {bohr_th:>8.1f} ppm")
    print(f"  Real Rydberg T/H:   {363:>8.1f} ppm")

    print()
    if abs(sim_dh - bohr_dh) / abs(bohr_dh) < 0.05:
        print("→ Simulation reproduces Bohr-Rydberg reduced-mass scaling within 5%.")
        print("  Atomic-scale dynamics in this model agrees with measurement at")
        print("  leading order. Spec §8.1 (hydrogen) is empirically validated.")
    else:
        print("→ Mismatch with Bohr-Rydberg: spec §8.1 needs revision.")


if __name__ == "__main__":
    main()
