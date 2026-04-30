"""Hydrogen + isotopes (D, T): predict the orbital-frequency isotope shift.

Real measurements:
- m_p / m_e = 1836.15
- m_d / m_e = 3670.48
- m_t / m_e = 5496.92
- Rydberg ratio (D/H − 1): +272 ppm
- Rydberg ratio (T/H − 1): +363 ppm

In a Bohr-like 2-body atom, orbital frequency ∝ reduced mass μ:
  μ_H = m_e · m_p / (m_e + m_p)
  μ_D = m_e · m_d / (m_e + m_d)
  μ_T = m_e · m_t / (m_e + m_t)

Predicted shift: (μ_D / μ_H − 1) × 10⁶ ppm = 272 ppm
                 (μ_T / μ_H − 1) × 10⁶ ppm = 363 ppm

The simulation must reproduce these ratios from the back-reaction
dynamics — that's a real test, no parameter tuning, no scale needed.

Per spec §2: only inputs are m_e (set to 1.0), m_p/m_e/m_d/m_t (real
mass ratios), and the same back-reaction parameters as the spin-½ test.
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.back_reaction import back_reaction_force, vverlet_step
from stiff_medium.spinor import unwrap_azimuth_history


# Real mass ratios
M_E = 1.0
M_P = 1836.15
M_D = 3670.48
M_T = 5496.92

# Back-reaction parameters (same as Test 2 in the spin check)
DT = 0.005
S = C / np.sqrt(2.0)
R_EQ = 0.20
R_CAPTURE = 1.0
K_PUSH = 5.0
K_PULL = 5.0
N_STEPS = 12000  # longer run for sharper frequency measurement


def force(pa, pb):
    return back_reaction_force(
        pa, pb, r_eq=R_EQ, r_capture=R_CAPTURE, k_push=K_PUSH, k_pull=K_PULL
    )


def reduced_mass(m_light: float, m_heavy: float) -> float:
    return m_light * m_heavy / (m_light + m_heavy)


def run_atom(name: str, m_nucleus: float):
    """Simulate light particle (electron) + heavy particle (nucleus) bound state.
    Return orbital frequency (in 1/step units)."""
    z = np.array([0.0, 0.0, 1.0])

    # Place electron and nucleus at 1.5x r_eq apart, tangential velocities.
    # In the heavy-nucleus limit, the electron orbits and the nucleus barely moves.
    pos_e = np.array([-1.5 * R_EQ / 2, 0.0, 0.0])
    vel_e = np.array([0.0, S, S])
    pos_n = np.array([1.5 * R_EQ / 2, 0.0, 0.0])
    vel_n = np.array([0.0, -S, S])

    rel_angles = []
    state = (pos_e, vel_e, pos_n, vel_n)

    for k in range(N_STEPS):
        new_pe, new_ve, new_pn, new_vn = vverlet_step(
            state[0], state[1], z, state[2], state[3], z,
            dt=DT, force_fn=force,
            mass_a=M_E, mass_b=m_nucleus,
        )
        state = (new_pe, new_ve, new_pn, new_vn)
        rel = new_pn - new_pe
        if abs(rel[0]) > 1e-9 or abs(rel[1]) > 1e-9:
            rel_angles.append(float(np.arctan2(rel[1], rel[0])))

    # Use the second half (after binding stabilizes) to measure frequency
    half = len(rel_angles) // 2
    rel_window = unwrap_azimuth_history(rel_angles[half:])
    total_angle = float(rel_window[-1] - rel_window[0])
    n_steps_window = len(rel_window) - 1
    angular_velocity = total_angle / (n_steps_window * DT)
    orbital_frequency = abs(angular_velocity) / (2.0 * np.pi)

    print(f"{name:>2}: m_n/m_e = {m_nucleus/M_E:>9.2f}  "
          f"reduced μ = {reduced_mass(M_E, m_nucleus):.6f}  "
          f"angular_velocity = {angular_velocity:>8.4f}  "
          f"freq = {orbital_frequency:.4f}")
    return orbital_frequency


def main():
    print("Hydrogen-isotope simulation\n")
    print("Inputs: m_e = 1.0 (fixed); nucleus mass varies for H, D, T.")
    print("Same back-reaction parameters as the spin-½ test (§5.5).\n")

    f_h = run_atom("H", M_P)
    f_d = run_atom("D", M_D)
    f_t = run_atom("T", M_T)

    print()
    print("Predicted isotope shifts (orbital frequency ratio − 1):")
    print(f"  D/H − 1: {(f_d/f_h - 1) * 1e6:>8.1f} ppm   (real Rydberg shift: +272 ppm)")
    print(f"  T/H − 1: {(f_t/f_h - 1) * 1e6:>8.1f} ppm   (real Rydberg shift: +363 ppm)")

    # Reduced-mass-only prediction (the Bohr-like limit)
    mu_h = reduced_mass(M_E, M_P)
    mu_d = reduced_mass(M_E, M_D)
    mu_t = reduced_mass(M_E, M_T)
    print()
    print("Reduced-mass-only ratios (the Bohr-Rydberg prediction):")
    print(f"  μ_D/μ_H − 1: {(mu_d/mu_h - 1) * 1e6:>8.1f} ppm")
    print(f"  μ_T/μ_H − 1: {(mu_t/mu_h - 1) * 1e6:>8.1f} ppm")

    print()
    print("Test: does the back-reaction simulation reproduce the reduced-mass scaling?")
    print(f"  Simulation D/H ratio:   {(f_d/f_h - 1) * 1e6:>8.1f} ppm")
    print(f"  Reduced-mass D/H ratio: {(mu_d/mu_h - 1) * 1e6:>8.1f} ppm")
    if abs((f_d/f_h - 1) - (mu_d/mu_h - 1)) / abs(mu_d/mu_h - 1) < 0.1:
        print("  → Match within 10%: simulation reproduces reduced-mass scaling.")
    else:
        print("  → Mismatch: the simulation gives different scaling than Bohr-Rydberg.")
        print("     This is informative — either parameters need adjustment for atomic")
        print("     regime, or the back-reaction's frequency dependence on mass is not")
        print("     1/μ and the spec needs revision.")


if __name__ == "__main__":
    main()
