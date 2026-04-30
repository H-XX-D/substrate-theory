"""Polished back-reaction simulation: velocity-Verlet integrator,
45° cone projection after each step, longer runs.

Uses the canonical implementations of project_to_cone, back_reaction_force,
and vverlet_step from `stiff_medium.back_reaction` (which is tested).
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.back_reaction import (
    back_reaction_force,
    vverlet_step as _vverlet_step,
)


# Parameters (per spec §2: chosen once on physical grounds)
DT = 0.005
S = C / np.sqrt(2.0)

R_OVERLAP = 0.05
R_EQ = 0.20
R_CAPTURE = 1.0
K_PUSH = 5.0
K_PULL = 5.0
N_STEPS = 6000


def back_reaction(pos_a: np.ndarray, pos_b: np.ndarray) -> np.ndarray:
    """Force on A from B (script-local closure over the module-level constants)."""
    return back_reaction_force(
        pos_a, pos_b,
        r_eq=R_EQ, r_capture=R_CAPTURE,
        k_push=K_PUSH, k_pull=K_PULL,
    )


def vverlet_step(state, axis_a, axis_b):
    """One velocity-Verlet step using the module's canonical implementation."""
    pos_a, vel_a, pos_b, vel_b = state
    return _vverlet_step(
        pos_a, vel_a, axis_a, pos_b, vel_b, axis_b,
        dt=DT, force_fn=back_reaction,
    )


def run(name, pos_a, vel_a, pos_b, vel_b, axis_a, axis_b, sample_steps=None):
    print(f"\n=== {name} ===")
    print(f"A: pos={pos_a}, vel={vel_a}, axis={axis_a}")
    print(f"B: pos={pos_b}, vel={vel_b}, axis={axis_b}")

    state = (pos_a.copy(), vel_a.copy(), pos_b.copy(), vel_b.copy())

    if sample_steps is None:
        sample_steps = list(range(0, N_STEPS, 250)) + [N_STEPS - 1]

    samples = []
    distances = []
    angles_xy = []
    for k in range(N_STEPS):
        state = vverlet_step(state, axis_a, axis_b)
        pa, va, pb, vb = state
        rel = pb - pa
        d = float(np.linalg.norm(rel))
        distances.append(d)
        # angle of rel vector in xy plane
        if abs(rel[0]) > 1e-9 or abs(rel[1]) > 1e-9:
            angles_xy.append(float(np.degrees(np.arctan2(rel[1], rel[0]))))
        else:
            angles_xy.append(float("nan"))

        if k in sample_steps:
            samples.append((k, rel.copy(), d, float(np.linalg.norm(va))))

    # Print samples
    print(f"\n{'step':>5} | {'rel_x':>7} | {'rel_y':>7} | {'rel_z':>7} | "
          f"{'dist':>7} | {'|v_A|':>6}")
    print("-" * 65)
    for k, rel, d, sa in samples:
        print(f"{k:>5} | {rel[0]:>7.3f} | {rel[1]:>7.3f} | {rel[2]:>7.3f} | "
              f"{d:>7.4f} | {sa:>6.4f}")

    # Stability metrics over the second half of the run
    half = N_STEPS // 2
    d_window = np.array(distances[half:])
    print(f"\nDistance over second half ({half}–{N_STEPS}): "
          f"min={d_window.min():.4f}, max={d_window.max():.4f}, "
          f"mean={d_window.mean():.4f}, std={d_window.std():.4f}")
    print(f"Mean compared to r_eq={R_EQ:.4f}: "
          f"{'within 30%' if abs(d_window.mean() - R_EQ) < 0.3 * R_EQ else 'OFF'}.")

    # Rotation analysis: angle range over the second half
    angles_arr = np.array([a for a in angles_xy[half:] if not np.isnan(a)])
    if len(angles_arr) > 0:
        # Unwrap to detect total rotation
        unwrapped = np.unwrap(np.radians(angles_arr))
        total_rot_deg = float(np.degrees(unwrapped[-1] - unwrapped[0]))
        # Range without unwrap (just max - min)
        rng = float(angles_arr.max() - angles_arr.min())
        print(f"Relative-position angle in xy plane (second half): "
              f"range = {rng:.1f}°, total unwrapped rotation = {total_rot_deg:.1f}°")
        if abs(total_rot_deg) > 360:
            print(f"→ MULTIPLE FULL ORBITS observed: {abs(total_rot_deg) / 360:.2f} revolutions.")
        elif abs(total_rot_deg) > 90:
            print(f"→ SUBSTANTIAL ROTATION: relative-position vector rotates >90°.")
        elif abs(total_rot_deg) > 30:
            print(f"→ Partial rotation observed.")
        else:
            print(f"→ Limited rotation (1D-bound-like).")


def main():
    z = np.array([0.0, 0.0, 1.0])

    # Tangential setup: place at r_eq apart, tangential velocities + z-drift.
    # If back-reaction holds them at r_eq while persistent c circulates them,
    # we get a stable orbit.
    run(
        "Tangential setup at r_eq (full velocity-Verlet + cone projection)",
        pos_a=np.array([-R_EQ / 2, 0.0, 0.0]),
        vel_a=np.array([0.0, S, S]),  # tangent +y, drift +z
        pos_b=np.array([R_EQ / 2, 0.0, 0.0]),
        vel_b=np.array([0.0, -S, S]),
        axis_a=z,
        axis_b=z,
    )

    # Slightly perturbed: same axes, different starting distance (test stability).
    run(
        "Tangential setup, perturbed distance (1.5x r_eq)",
        pos_a=np.array([-1.5 * R_EQ / 2, 0.0, 0.0]),
        vel_a=np.array([0.0, S, S]),
        pos_b=np.array([1.5 * R_EQ / 2, 0.0, 0.0]),
        vel_b=np.array([0.0, -S, S]),
        axis_a=z,
        axis_b=z,
    )

    # Tangential setup with different speed regime (closer to r_eq).
    run(
        "Tangential setup, slightly closer than r_eq (0.7x r_eq)",
        pos_a=np.array([-0.7 * R_EQ / 2, 0.0, 0.0]),
        vel_a=np.array([0.0, S, S]),
        pos_b=np.array([0.7 * R_EQ / 2, 0.0, 0.0]),
        vel_b=np.array([0.0, -S, S]),
        axis_a=z,
        axis_b=z,
    )


if __name__ == "__main__":
    main()
