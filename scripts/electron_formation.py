"""Path C experiment: do two colliding neutrinos form a bound state?

Setup:
- Neutrino A starts at (-2, 0) heading NE (vx=+s, vy=+s)
- Neutrino B starts at (+2, 0) heading NW (vx=-s, vy=+s)
- Their paths cross near (0, 2).
- Run 1000 steps, dt=0.01.

Per spec §2 (no correction loops): no parameter tuning beyond the basic
overlap radius and push amplitude — those represent the medium's
discretization and stiffness, NOT free fitting parameters.

Outcomes:
- BOUND: tracker flags persistent proximity → simulation produces an
  electron-like state, positive result.
- UNBOUND: particles pass through and separate → the displacement-only
  rule alone is insufficient; theory needs revision (per §2 methodology,
  this is a real falsification signal, not a tuning opportunity).
"""

import numpy as np
import matplotlib.pyplot as plt

from stiff_medium.neutrino import Neutrino, C
from stiff_medium.dynamics import step
from stiff_medium.detector import BoundStateTracker
from stiff_medium.visualize import animate


def main() -> None:
    s = C / np.sqrt(2)

    a = Neutrino(
        position=np.array([-2.0, 0.0]),
        velocity=np.array([s, s]),
    )
    b = Neutrino(
        position=np.array([2.0, 0.0]),
        velocity=np.array([-s, s]),
    )

    # Two simulation parameters: medium discretization (r_overlap) and
    # stiffness response (push). At ~5x c*dt = 5x 0.01 = 0.05 each, they
    # are small compared to the simulation domain (~4 units) but a few
    # times the per-step travel distance. Chosen once on physical grounds
    # per spec §2 — not tuned to produce a desired outcome.
    DT = 0.01
    R_OVERLAP = 0.05
    PUSH = 0.05
    R_BOUND = 0.5
    PERSISTENCE = 50  # consecutive steps within R_BOUND
    N_STEPS = 1000

    state = [a, b]
    tracker = BoundStateTracker(r_bound=R_BOUND, persistence=PERSISTENCE)
    history: list[list[Neutrino]] = [state]
    bound_flags: list[bool] = [False]

    bound_first_seen = -1
    for k in range(N_STEPS):
        state = step(state, dt=DT, r_overlap=R_OVERLAP, push=PUSH)
        flagged = tracker.update(state)
        history.append(state)
        bound_flags.append(flagged)
        if flagged and bound_first_seen < 0:
            bound_first_seen = k + 1

    if bound_first_seen >= 0:
        print(f"RESULT: BOUND state first detected at step {bound_first_seen}.")
    else:
        print("RESULT: NO bound state detected over 1000 steps.")
        print("       The displacement-only rule did not produce a stable orbit.")
        print("       Per spec §2 methodology, this is a falsification signal,")
        print("       not an invitation to tune parameters.")

    fig, _anim = animate(
        history, bound_flags,
        xlim=(-3, 3), ylim=(-3, 3),
        interval_ms=20,
    )
    plt.show()


if __name__ == "__main__":
    main()
