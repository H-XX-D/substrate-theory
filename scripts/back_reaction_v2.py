"""Polished back-reaction simulation: velocity-Verlet integrator,
45° cone projection after each step, longer runs.

Cone projection:
- Each particle has an intrinsic axis â.
- After each velocity update, project the velocity back to the 45° cone:
  v_new = (C/√2) * â + (C/√2) * unit_perp(v - (v·â)â).
- This preserves the spec invariants: |v|=C and angle(v, â)=45°.
- The medium back-reaction can only rotate the velocity around the cone
  (change azimuth), not change its magnitude or cone-angle.

Velocity-Verlet integrator: better energy behavior than Euler. The cone
projection introduces some non-conservation but the impulsive
back-reaction is replaced with a smoother centered-force evaluation.
"""

import numpy as np


# Parameters (per spec §2: chosen once on physical grounds)
DT = 0.005
C = 1.0
S = C / np.sqrt(2.0)

R_OVERLAP = 0.05
R_EQ = 0.20
R_CAPTURE = 1.0
K_PUSH = 5.0
K_PULL = 5.0
N_STEPS = 6000


def project_to_cone(v: np.ndarray, axis: np.ndarray) -> np.ndarray:
    """Project a velocity vector onto the 45° cone around axis.

    Result has magnitude C and angle 45° to axis. Azimuthal direction
    (rotation around axis) is preserved from the input v's perpendicular
    component. If v has no perpendicular component, an arbitrary
    perpendicular is chosen.
    """
    v_along = float(np.dot(v, axis)) * axis
    v_perp = v - v_along
    perp_norm = float(np.linalg.norm(v_perp))
    if perp_norm < 1e-9:
        # Degenerate: pick an arbitrary perpendicular.
        if abs(axis[0]) < 0.9:
            ref = np.array([1.0, 0.0, 0.0])
        else:
            ref = np.array([0.0, 1.0, 0.0])
        v_perp = ref - float(np.dot(ref, axis)) * axis
        v_perp = v_perp / float(np.linalg.norm(v_perp))
    else:
        v_perp = v_perp / perp_norm
    return S * axis + S * v_perp


def back_reaction(pos_a: np.ndarray, pos_b: np.ndarray) -> np.ndarray:
    """Force on A from B; F on B is -F on A. Spring around r_eq."""
    diff = pos_b - pos_a
    d = float(np.linalg.norm(diff))
    if d > R_CAPTURE or d < 1e-12:
        return np.zeros(3)
    unit = diff / d
    if d > R_EQ:
        return K_PULL * (d - R_EQ) * unit  # attractive
    else:
        return K_PUSH * (R_EQ - d) * (-unit)  # repulsive


def vverlet_step(state, axis_a, axis_b):
    """One velocity-Verlet step with cone projection at each velocity update."""
    pos_a, vel_a, pos_b, vel_b = state

    f_a = back_reaction(pos_a, pos_b)
    f_b = -f_a

    vel_a_half = vel_a + 0.5 * f_a * DT
    vel_b_half = vel_b + 0.5 * f_b * DT
    vel_a_half = project_to_cone(vel_a_half, axis_a)
    vel_b_half = project_to_cone(vel_b_half, axis_b)

    new_pos_a = pos_a + vel_a_half * DT
    new_pos_b = pos_b + vel_b_half * DT

    new_f_a = back_reaction(new_pos_a, new_pos_b)
    new_f_b = -new_f_a

    new_vel_a = vel_a_half + 0.5 * new_f_a * DT
    new_vel_b = vel_b_half + 0.5 * new_f_b * DT
    new_vel_a = project_to_cone(new_vel_a, axis_a)
    new_vel_b = project_to_cone(new_vel_b, axis_b)

    return (new_pos_a, new_vel_a, new_pos_b, new_vel_b)


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
