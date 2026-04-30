"""Test of Möbius dynamics + Pauli-via-twist:

- opposite-Möbius pair: should bind (5+ orbits, like the standard Test 2 result).
- same-Möbius pair: should NOT bind (the same-sign repulsion factor in
  the Möbius-aware force prevents stable binding).

This converts the spec's '§5.5.1 Pauli-like exclusion is mechanical' from
a hard-core-only claim into a *spin-state-dependent* claim — opposite-twist
pairs CAN bind, same-twist pairs CAN'T. Real Pauli's spin-dependence
shows up dynamically.
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.back_reaction import back_reaction_force, project_to_cone
from stiff_medium.mobius_dynamics import (
    MobiusState,
    mobius_aware_force,
    mobius_vverlet_step,
)


# Same parameters as Test 2
DT = 0.005
S = C / np.sqrt(2.0)
R_EQ = 0.20
R_CAPTURE = 1.0
K_PUSH = 5.0
K_PULL = 5.0
N_STEPS = 4000


def base_force(pos_a, pos_b):
    return back_reaction_force(
        pos_a, pos_b, r_eq=R_EQ, r_capture=R_CAPTURE, k_push=K_PUSH, k_pull=K_PULL
    )


def force_fn(a, b):
    return mobius_aware_force(a, b, base_force_fn=base_force)


def run_pair(name: str, initial_phase_a: float, initial_phase_b: float):
    z = np.array([0.0, 0.0, 1.0])
    a = MobiusState(
        position=np.array([-1.5 * R_EQ / 2, 0.0, 0.0]),
        velocity=np.array([0.0, S, S]),
        axis=z,
        accumulated_azimuth=0.0,
        initial_phase=initial_phase_a,
    )
    b = MobiusState(
        position=np.array([1.5 * R_EQ / 2, 0.0, 0.0]),
        velocity=np.array([0.0, -S, S]),
        axis=z,
        accumulated_azimuth=0.0,
        initial_phase=initial_phase_b,
    )

    print(f"\n=== {name} ===")
    print(f"A: initial_phase = {initial_phase_a:.4f}, slope_sign = {a.slope_sign:+d}")
    print(f"B: initial_phase = {initial_phase_b:.4f}, slope_sign = {b.slope_sign:+d}")

    samples = []
    for k in range(N_STEPS):
        a, b = mobius_vverlet_step(a, b, dt=DT, force_fn=force_fn, project_to_cone_fn=project_to_cone)
        if k in (0, 100, 500, 1000, 1500, 2000, 2500, 3000, 3500, 3999):
            d = float(np.linalg.norm(b.position - a.position))
            samples.append((k, d, a.slope_sign, b.slope_sign))

    print(f"\n{'step':>5} | {'distance':>9} | {'A slope':>8} | {'B slope':>8}")
    print("-" * 45)
    for step_idx, d, sa, sb in samples:
        print(f"{step_idx:>5} | {d:>9.4f} | {sa:>+8d} | {sb:>+8d}")

    half = N_STEPS // 2
    distances = [d for (k, d, _, _) in samples if k >= half]
    if distances:
        max_d = max(distances)
        if max_d < 1.0:
            print(f"\n→ BOUND: max distance after step {half} = {max_d:.4f} (< r_capture)")
        else:
            print(f"\n→ NOT BOUND: max distance after step {half} = {max_d:.4f}")


def main():
    # Opposite-Möbius pair: initial phases differ by π → opposite slope signs at start.
    # This is e⁺e⁻ — should bind via standard back-reaction.
    run_pair("Opposite-Möbius (electron-mode + positron-mode)", 0.0, np.pi)

    # Same-Möbius pair: identical initial phases → same slope sign at start.
    # This is e⁻e⁻ — should NOT bind because the same-sign repulsion factor
    # eliminates the attractive zone.
    run_pair("Same-Möbius (electron-mode + electron-mode)", 0.0, 0.0)


if __name__ == "__main__":
    main()
