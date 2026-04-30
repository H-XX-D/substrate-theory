"""Path C v3: 3D simulation testing whether 2D orbital motion emerges.

Per spec §6, the electron is a 2D bound orbit in a plane, swept into a
3D cone by rotation around its symmetry axis. Path C v1/v2 (2D
simulation) showed the displacement-only rule produces a 1D bound
oscillation along the line of approach, never 2D rotation. The
hypothesis was that 2D simulation collapsed the velocity cone (U(1)
freedom in 3D) to 4 discrete directions and that 3D would unlock 2D
orbital structure.

This script tests that hypothesis by running several initial-condition
configurations and measuring whether the relative-position vector
*rotates* (→ 2D orbit) or stays along the approach line (→ 1D bound).

Per spec §2: parameters chosen once on physical grounds. No tuning
across runs to produce a desired outcome.
"""

import numpy as np

from stiff_medium.neutrino import C
from stiff_medium.three_d import Neutrino3D, make_on_cone, step


# Shared parameters -----------------------------------------------------

DT = 0.01
R_OVERLAP = 0.05
PUSH = 0.05
R_BOUND = 0.5
N_STEPS = 2000


def run_and_analyze(name: str, a: Neutrino3D, b: Neutrino3D) -> None:
    """Run one configuration; report bound-state result and angular structure."""
    print(f"\n=== {name} ===")
    print(f"A: pos={a.position}, vel={a.velocity}, axis={a.axis}")
    print(f"B: pos={b.position}, vel={b.velocity}, axis={b.axis}")

    state = [a, b]
    rel_history: list[tuple[int, np.ndarray, float]] = []  # (step, rel_pos, dist)

    for k in range(N_STEPS):
        state = step(state, dt=DT, r_overlap=R_OVERLAP, push=PUSH)
        rel = state[1].position - state[0].position
        dist = float(np.linalg.norm(rel))
        if k in (0, 100, 200, 280, 297, 350, 500, 1000, 1500, 1999):
            rel_history.append((k, rel.copy(), dist))

    # Print trajectory samples
    print(f"{'step':>5} | {'rel_x':>8} | {'rel_y':>8} | {'rel_z':>8} | {'dist':>8}")
    print("-" * 60)
    for k, rel, dist in rel_history:
        print(f"{k:>5} | {rel[0]:>8.4f} | {rel[1]:>8.4f} | {rel[2]:>8.4f} | {dist:>8.4f}")

    # Analyze whether the relative position rotates (2D orbit) or stays
    # along an axis (1D bound). Specifically, after binding, examine the
    # spread of the unit-vector of the relative position. A 1D bound
    # state has near-zero angular spread (relative direction locked).
    # A 2D orbit shows large angular spread (vector rotates).
    bound_samples = [(k, rel, d) for (k, rel, d) in rel_history if d < R_BOUND and k > 200]

    if not bound_samples:
        print("\n→ NO bound state observed (distance never < R_BOUND after step 200).")
        return

    print(f"\n{len(bound_samples)} bound-state samples after step 200.")

    # Compute pairwise angles between consecutive bound-state directions.
    units = [rel / np.linalg.norm(rel) for (_, rel, _) in bound_samples]
    pairwise_angles = []
    for i in range(1, len(units)):
        cos_angle = float(np.clip(np.dot(units[i], units[0]), -1.0, 1.0))
        angle_deg = float(np.degrees(np.arccos(abs(cos_angle))))
        # use abs(cos_angle) so 180° flip counts as "same axis" (bound oscillates back and forth)
        pairwise_angles.append(angle_deg)

    if pairwise_angles:
        max_angle = max(pairwise_angles)
        print(f"Max angle of relative-position direction from initial bound direction: "
              f"{max_angle:.2f} degrees.")
        if max_angle > 30:
            print("→ Relative direction rotates substantially: 2D ORBITAL motion.")
        elif max_angle > 5:
            print("→ Relative direction wobbles: partial / nascent rotation.")
        else:
            print("→ Relative direction locked: 1D BOUND oscillation along a fixed line.")


def main() -> None:
    z_axis = np.array([0.0, 0.0, 1.0])
    neg_z_axis = np.array([0.0, 0.0, -1.0])
    s = C / np.sqrt(2.0)

    # Configuration 1: same-axis (+z), antiparallel xy velocity components.
    # Equivalent to 2D v1 but in 3D — should give 1D bound + z-drift.
    run_and_analyze(
        "config 1: same-axis (+z), antiparallel xy (mirrors 2D v1)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=0.0),  # v_xy = +x
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=np.pi),  # v_xy = -x
            axis=z_axis,
        ),
    )

    # Configuration 2: opposite axes (+z, -z), opposite xy components.
    # COM y-z momentum should cancel; particles approach on the diagonal.
    run_and_analyze(
        "config 2: opposite axes (+z, -z), opposite xy (zero net momentum)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=0.0),  # +x, +z
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([2.0, 0.0, 0.0]),
            velocity=make_on_cone(neg_z_axis, azimuth=np.pi),  # -x, -z
            axis=neg_z_axis,
        ),
    )

    # Configuration 3: same-axis (+z), perpendicular xy components.
    # A's v_xy is +x, B's v_xy is +y — perpendicular, not antiparallel.
    run_and_analyze(
        "config 3: same-axis (+z), perpendicular xy components",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=0.0),  # v_xy = +x
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([0.0, -2.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=np.pi / 2),  # v_xy = +y
            axis=z_axis,
        ),
    )

    # Configuration 4: orthogonal axes (+z and +x).
    run_and_analyze(
        "config 4: orthogonal axes (+z, +x)",
        Neutrino3D(
            position=np.array([-2.0, 0.0, 0.0]),
            velocity=make_on_cone(z_axis, azimuth=0.0),
            axis=z_axis,
        ),
        Neutrino3D(
            position=np.array([0.0, 0.0, -2.0]),
            velocity=make_on_cone(np.array([1.0, 0.0, 0.0]), azimuth=0.0),
            axis=np.array([1.0, 0.0, 0.0]),
        ),
    )


if __name__ == "__main__":
    main()
