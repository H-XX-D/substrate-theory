"""Path C v3 (corrected): 3D simulation with velocities actually pointing
toward each other. Earlier electron_formation_3d.py had bad azimuth
choices that aimed particles away from collision. This script uses
direct velocity construction so the geometry is unambiguous.

Per the spec: 'push is centrifugal, bind is persistent linear c
turning into angular momentum'. We test whether the displacement rule
plus persistent linear c on the 45° cone produces:

(a) 1D bound oscillation along approach line + drift (same as 2D v1/v2)
(b) 2D rotational binding (relative-position vector rotates)
(c) No binding (particles fly apart through each other)
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.three_d import Neutrino3D, step


# Shared parameters (per spec §2: chosen once, not tuned)
DT = 0.01
R_OVERLAP = 0.05
PUSH = 0.05
R_BOUND = 0.5
N_STEPS = 2000

s = C / np.sqrt(2.0)  # along-axis and perpendicular components on the 45° cone
z_axis = np.array([0.0, 0.0, 1.0])
neg_z_axis = np.array([0.0, 0.0, -1.0])


def run(name: str, a: Neutrino3D, b: Neutrino3D) -> None:
    print(f"\n=== {name} ===")
    print(f"A: pos={a.position}, vel={a.velocity}, axis={a.axis}")
    print(f"B: pos={b.position}, vel={b.velocity}, axis={b.axis}")

    # Initial angular momentum about the COM (z-axis component)
    com = (a.position + b.position) / 2.0
    p_a = a.velocity  # mass=1 in natural units
    p_b = b.velocity
    rA = a.position - com
    rB = b.position - com
    L = np.cross(rA, p_a) + np.cross(rB, p_b)
    print(f"Initial L (about COM): {L}")

    state = [a, b]
    samples = []
    for k in range(N_STEPS):
        state = step(state, dt=DT, r_overlap=R_OVERLAP, push=PUSH)
        if k in (0, 50, 100, 150, 200, 250, 280, 297, 350, 500, 1000, 1500, 1999):
            rel = state[1].position - state[0].position
            dist = float(np.linalg.norm(rel))
            samples.append((k, rel.copy(), dist))

    print(f"\n{'step':>5} | {'rel_x':>8} | {'rel_y':>8} | {'rel_z':>8} | {'dist':>8}")
    print("-" * 60)
    for k, rel, dist in samples:
        print(f"{k:>5} | {rel[0]:>8.3f} | {rel[1]:>8.3f} | {rel[2]:>8.3f} | {dist:>8.4f}")

    # Find samples after binding
    bound = [(k, rel, d) for (k, rel, d) in samples if d < R_BOUND and k > 200]
    if not bound:
        # Look for transient close-approach instead
        min_dist_idx = min(range(len(samples)), key=lambda i: samples[i][2])
        k_min, _, d_min = samples[min_dist_idx]
        print(f"\n→ NO sustained binding. Min observed distance: "
              f"{d_min:.3f} at step {k_min}.")
        return

    print(f"\n{len(bound)} bound-state samples (dist < {R_BOUND} after step 200).")

    # Direction-vector rotation analysis
    units = [rel / np.linalg.norm(rel) for (_, rel, _) in bound]
    angles_from_first = []
    for u in units:
        cos_a = float(np.clip(np.dot(u, units[0]), -1.0, 1.0))
        # use 180°-flip-equivalent: same axis = cos=±1
        angles_from_first.append(float(np.degrees(np.arccos(abs(cos_a)))))

    max_rotation = max(angles_from_first)
    print(f"Max angle of rel-direction from first bound sample: "
          f"{max_rotation:.2f} degrees (180-fold symmetry — 0° means same axis).")
    if max_rotation > 30:
        print("→ 2D ROTATIONAL binding: relative-position vector rotates substantially.")
    elif max_rotation > 5:
        print("→ Partial rotation: nascent 2D orbit (or 1D bound with wobble).")
    else:
        print("→ 1D BOUND: relative direction locked, no rotation.")


def main() -> None:
    # CONFIG A: 2D-v1 analog in 3D. Both axes +z, v_xy directly opposing.
    # Should give 1D bound in x with linear z-drift (same as 2D v1).
    run(
        "A. 2D-v1 analog in 3D (head-on x, both +z axis, v_xy ± along x)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=np.array([s, 0.0, s]),  # +x +z, on +z cone
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.0, 0.0]),
            velocity=np.array([-s, 0.0, s]),  # -x +z, on +z cone
            axis=z_axis,
        ),
    )

    # CONFIG B: 2D-v2 analog. Same axes but opposite v_z too (zero z-drift).
    run(
        "B. zero z-drift (head-on x, opposite axes, opposite v_z)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=np.array([s, 0.0, s]),
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.0, 0.0]),
            velocity=np.array([-s, 0.0, -s]),  # -x -z, on -z cone
            axis=neg_z_axis,
        ),
    )

    # CONFIG C: nonzero angular momentum.
    # Shift positions and pick velocities that give angular momentum about z.
    # A at (-2, -1, 0) heads toward upper-right; B at (2, 1, 0) heads toward lower-left.
    # Velocities must satisfy 45° cone of +z (so v_z = s).
    run(
        "C. nonzero angular momentum about z (offset positions)",
        Neutrino3D(
            position=np.array([-2.0, -1.0, 0.0]),
            velocity=np.array([s, 0.0, s]),  # +x +z; v_y = 0
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 1.0, 0.0]),
            velocity=np.array([-s, 0.0, s]),  # -x +z; v_y = 0
            axis=z_axis,
        ),
    )

    # CONFIG D: tangential approach (testing whether tangential velocities
    # produce a 2D orbit).
    # A at (-2, 0, 0) moving +y +z; B at (2, 0, 0) moving -y +z.
    # They don't approach in x at all; they fly past each other vertically.
    run(
        "D. tangential approach (no x-convergence)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=np.array([0.0, s, s]),
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.0, 0.0]),
            velocity=np.array([0.0, -s, s]),
            axis=z_axis,
        ),
    )

    # CONFIG E: oblique approach with a small y-offset and rotated v_xy.
    # Try to set up genuinely 2D orbital initial conditions.
    run(
        "E. oblique approach with y-offset (potential 2D orbit setup)",
        Neutrino3D(
            position=np.array([-2.0, -0.5, 0.0]),
            # v_xy points toward (+x, +y) at 45° within xy plane
            velocity=np.array([s / np.sqrt(2), s / np.sqrt(2), s]),
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.5, 0.0]),
            velocity=np.array([-s / np.sqrt(2), -s / np.sqrt(2), s]),
            axis=z_axis,
        ),
    )


if __name__ == "__main__":
    main()
