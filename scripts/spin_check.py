"""Experiment: does the bound orbit from back_reaction_v2 Test 2 give
spin-½ under Möbius interpretation?

Re-runs Test 2 (the 5.62-orbit configuration), tracks each neutrino's
cone azimuth at each step, then asks: how many full azimuth rotations
per orbital revolution? Spin-½ requires exactly 1 (giving slope-flip
per orbit, return at 720°). Spin-1 would be 2.
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.back_reaction import back_reaction_force, vverlet_step
from stiff_medium.spinor import (
    cone_azimuth,
    spin_half_check,
    unwrap_azimuth_history,
)


# Test 2 parameters from back_reaction_v2.py
DT = 0.005
S = C / np.sqrt(2.0)
R_EQ = 0.20
R_CAPTURE = 1.0
K_PUSH = 5.0
K_PULL = 5.0
N_STEPS = 6000


def force(pa, pb):
    return back_reaction_force(
        pa, pb, r_eq=R_EQ, r_capture=R_CAPTURE, k_push=K_PUSH, k_pull=K_PULL
    )


def main() -> None:
    z = np.array([0.0, 0.0, 1.0])
    # Test 2 setup: tangential at 1.5x r_eq
    pos_a = np.array([-1.5 * R_EQ / 2, 0.0, 0.0])
    vel_a = np.array([0.0, S, S])
    pos_b = np.array([1.5 * R_EQ / 2, 0.0, 0.0])
    vel_b = np.array([0.0, -S, S])

    # Track:
    # - cone azimuth of each neutrino
    # - relative-position angle in xy plane (for orbital revolution count)
    az_a_history: list[float] = [cone_azimuth(vel_a, z)]
    az_b_history: list[float] = [cone_azimuth(vel_b, z)]
    rel_angle_history: list[float] = [
        float(np.arctan2(pos_b[1] - pos_a[1], pos_b[0] - pos_a[0]))
    ]

    state = (pos_a, vel_a, pos_b, vel_b)
    for k in range(N_STEPS):
        new_pa, new_va, new_pb, new_vb = vverlet_step(
            state[0], state[1], z, state[2], state[3], z,
            dt=DT, force_fn=force,
        )
        state = (new_pa, new_va, new_pb, new_vb)

        az_a_history.append(cone_azimuth(new_va, z))
        az_b_history.append(cone_azimuth(new_vb, z))
        rel_angle_history.append(
            float(np.arctan2(new_pb[1] - new_pa[1], new_pb[0] - new_pa[0]))
        )

    # Unwrap all to compute total rotations
    az_a_unwrapped = unwrap_azimuth_history(az_a_history)
    az_b_unwrapped = unwrap_azimuth_history(az_b_history)
    rel_angle_unwrapped = np.unwrap(np.asarray(rel_angle_history))

    # Use only the second half (after binding has stabilized)
    half = N_STEPS // 2
    az_a_window = az_a_unwrapped[half:]
    az_b_window = az_b_unwrapped[half:]
    rel_angle_window = rel_angle_unwrapped[half:]

    orbital_revolutions = float(
        (rel_angle_window[-1] - rel_angle_window[0]) / (2.0 * np.pi)
    )

    print(f"Path C back-reaction Test 2 — second half ({half}–{N_STEPS}):")
    print(f"  Orbital revolutions (rel-position angle): {orbital_revolutions:.3f}")
    print()

    for label, az_window in [("A", az_a_window), ("B", az_b_window)]:
        result = spin_half_check(az_window, orbital_revolutions)
        print(f"  Neutrino {label}:")
        print(f"    Total cone-azimuth rotation: "
              f"{result['total_azimuth_rotation']:.4f} rad "
              f"({result['azimuth_rotations']:.4f} full turns)")
        print(f"    Cone-azimuth rotations per orbital revolution: "
              f"{result['azimuth_per_orbit']:.4f}")
        print(f"    Implied spin: {result['implied_spin']}")
        print()

    # Summary
    print("Interpretation:")
    print("  Under Möbius internal twist (spec §13 gap #1):")
    print("  - Cone azimuth advance per orbit = 1 → slope flips per orbit → spin-½")
    print("  - Cone azimuth advance per orbit = 2 → no flip → spin-1 (bosonic)")
    print("  - The simulation reports above what the back-reaction-driven dynamics")
    print("    actually produce. This is the empirical answer to whether spec")
    print("    §6's electron is fermionic in this framework.")


if __name__ == "__main__":
    main()
