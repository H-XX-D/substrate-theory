"""Path C v2 experiment: zero-net-momentum head-on approach.

v1 used initial conditions with net +y momentum (A: NE, B: NW), which
produced a 1D bound oscillation in the relative x-coordinate plus a
linear y-drift. This v2 setup chooses initial conditions where the
center of mass is at rest, to test whether spec §6's 2D orbital cone
emerges.

Setup (zero net momentum, head-on):
- Neutrino A starts at (-2, -2) heading NE (vx=+s, vy=+s)
- Neutrino B starts at (+2, +2) heading SW (vx=-s, vy=-s)
- COM is at (0, 0); net velocity is (0, 0). They approach diagonally.

Per spec §2 (no correction loops): same R_OVERLAP, PUSH, etc. as v1.
The only thing that changes is the initial conditions.

Outcomes the spec §6 prediction would require:
- 2D BOUND ORBIT: relative-coordinate motion goes around the origin in a
  loop, not just oscillates along the approach diagonal. Detection: the
  bound state persists AND the relative position vector (B - A) rotates,
  changing direction over time.
- 1D BOUND DIAGONAL: relative position stays along the NE-SW diagonal,
  oscillating but not rotating. This is what v1 gave, just rotated 45°.
- UNBOUND: particles separate after collision.
"""

import numpy as np

from stiff_medium.neutrino import Neutrino, C
from stiff_medium.dynamics import step
from stiff_medium.detector import BoundStateTracker


def main() -> None:
    s = C / np.sqrt(2)

    a = Neutrino(
        position=np.array([-2.0, -2.0]),
        velocity=np.array([s, s]),
    )
    b = Neutrino(
        position=np.array([2.0, 2.0]),
        velocity=np.array([-s, -s]),
    )

    DT = 0.01
    R_OVERLAP = 0.05
    PUSH = 0.05
    R_BOUND = 0.5
    PERSISTENCE = 50
    N_STEPS = 2000  # longer than v1 to see whether structure emerges

    state = [a, b]
    tracker = BoundStateTracker(r_bound=R_BOUND, persistence=PERSISTENCE)

    bound_first_seen = -1
    # Sample relative position (B - A) at intervals to check whether it
    # rotates (→ 2D orbit) or stays on the diagonal (→ 1D bound).
    samples: list[tuple[int, float, float, float]] = []  # (step, dist, rel_x, rel_y)

    for k in range(N_STEPS):
        state = step(state, dt=DT, r_overlap=R_OVERLAP, push=PUSH)
        flagged = tracker.update(state)
        if flagged and bound_first_seen < 0:
            bound_first_seen = k + 1

        if k % 100 == 0 or k in (
            280, 297, 350, 500, 1000, 1500, 1999
        ):
            rel = state[1].position - state[0].position
            dist = float(np.linalg.norm(rel))
            samples.append((k, dist, float(rel[0]), float(rel[1])))

    # Report
    print(f"{'step':>5} | {'dist':>8} | {'rel_x':>8} | {'rel_y':>8} | "
          f"{'angle (deg)':>11}")
    print("-" * 60)
    for step_idx, dist, rx, ry in samples:
        if dist > 1e-9:
            angle = float(np.degrees(np.arctan2(ry, rx)))
        else:
            angle = float("nan")
        print(f"{step_idx:>5} | {dist:>8.4f} | {rx:>8.4f} | {ry:>8.4f} | "
              f"{angle:>11.2f}")

    print()
    if bound_first_seen >= 0:
        print(f"Bound state first detected at step {bound_first_seen}.")
    else:
        print("No bound state detected.")

    # Diagnose 1D vs 2D: a 2D orbit would show the relative-position angle
    # cycling through a wide range. A 1D bound stays near a single angle
    # (along the approach line, here NE-SW = 45° or 225°).
    angles = [float(np.degrees(np.arctan2(ry, rx)))
              for (_, dist, rx, ry) in samples
              if dist > 1e-9]
    if angles:
        bound_angles = [a for (s_idx, d, _, _), a in zip(samples, angles)
                        if s_idx >= 280 and d < 0.5]
        if bound_angles:
            angle_min = min(bound_angles)
            angle_max = max(bound_angles)
            spread = angle_max - angle_min
            print(f"Relative-position angle spread (after binding, "
                  f"{len(bound_angles)} samples): {spread:.2f} degrees "
                  f"(min {angle_min:.2f}, max {angle_max:.2f}).")
            if spread > 90:
                print("→ 2D orbit (angle spread > 90°): relative position "
                      "vector rotates substantially.")
            else:
                print("→ 1D bound (angle spread ≤ 90°): relative position "
                      "stays near the approach diagonal.")


if __name__ == "__main__":
    main()
