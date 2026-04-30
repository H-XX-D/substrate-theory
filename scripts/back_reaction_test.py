"""Test: does medium back-reaction produce 2D orbital binding?

Adds a centripetal companion to the existing centrifugal push:
- When d < r_eq: medium pushes particles apart (centrifugal — what we already had).
- When r_eq < d < r_capture: medium pulls them together (centripetal — new).
- When d > r_capture: no interaction (free flight).
- At d = r_eq: zero net force; equilibrium orbital radius.

The pull is implemented as a force that modifies velocities (impulse per
dt). This violates the strict "vectors never reorient" rule of v1/v2,
which is exactly the point: spec §5 needs to allow back-reaction
reorientation if it is to deliver spec §6's 2D orbital cone.

Per spec §2: parameters chosen once on physical grounds. r_eq is the
medium's natural binding radius. k_pull and k_push are the strengths
of the centripetal and centrifugal components.

Three experiments:
- Exp 1: head-on approach, both axes +z (analogous to 2D-v1).
- Exp 2: zero net momentum, head-on diagonal.
- Exp 3: tangential initial conditions (start near orbital geometry).

For each, we look for:
- Does a bound state form? (distance settles near r_eq)
- Does the relative-position vector ROTATE (= 2D orbital motion)?
- What's the orbital period and does it depend on k_pull / k_push?
"""

import numpy as np


# Parameters
DT = 0.01
C = 1.0
S = C / np.sqrt(2.0)

R_OVERLAP = 0.05         # below this, push apart (centrifugal)
R_EQ = 0.20              # equilibrium orbit radius
R_CAPTURE = 1.0          # above this, no interaction
K_PUSH = 5.0             # strength of centrifugal push
K_PULL = 5.0             # strength of centripetal pull
N_STEPS = 3000


def back_react_force(pos_a, pos_b):
    """Force on A (returned) and on B (negative). Spring-like around r_eq.
    Outside r_capture, zero.
    """
    diff = pos_b - pos_a
    d = float(np.linalg.norm(diff))
    if d > R_CAPTURE or d < 1e-12:
        return np.zeros(3)
    unit = diff / d
    # Spring law: F = -k * (d - r_eq) * direction
    # When d > r_eq, force on A is +unit (toward B) → attractive
    # When d < r_eq, force on A is -unit (away from B) → repulsive
    if d > R_EQ:
        # attractive: pull A toward B
        return K_PULL * (d - R_EQ) * unit
    else:
        # repulsive: push A away from B (opposite to unit)
        return K_PUSH * (R_EQ - d) * (-unit)


def step_with_back_reaction(state):
    """One step: propagate + apply back-reaction force to velocities."""
    pos_a, vel_a, pos_b, vel_b = state

    # Propagate
    new_pos_a = pos_a + vel_a * DT
    new_pos_b = pos_b + vel_b * DT

    # Compute back-reaction force at NEW positions
    f_on_a = back_react_force(new_pos_a, new_pos_b)
    f_on_b = -f_on_a  # Newton's third law in this rule

    # Apply as velocity update (impulse-style)
    new_vel_a = vel_a + f_on_a * DT
    new_vel_b = vel_b + f_on_b * DT

    return new_pos_a, new_vel_a, new_pos_b, new_vel_b


def run(name, pos_a, vel_a, pos_b, vel_b):
    print(f"\n=== {name} ===")
    print(f"A pos={pos_a}, vel={vel_a}")
    print(f"B pos={pos_b}, vel={vel_b}")

    state = (pos_a.copy(), vel_a.copy(), pos_b.copy(), vel_b.copy())

    samples = []
    for k in range(N_STEPS):
        state = step_with_back_reaction(state)
        if k in (0, 50, 100, 200, 300, 500, 700, 1000, 1500, 2000, 2500, 2999):
            pa, va, pb, vb = state
            rel = pb - pa
            d = float(np.linalg.norm(rel))
            speed_a = float(np.linalg.norm(va))
            speed_b = float(np.linalg.norm(vb))
            samples.append((k, rel.copy(), d, speed_a, speed_b))

    print(f"\n{'step':>5} | {'rel_x':>7} | {'rel_y':>7} | {'rel_z':>7} | {'dist':>7} | "
          f"{'|v_A|':>6} | {'|v_B|':>6}")
    print("-" * 72)
    for k, rel, d, sa, sb in samples:
        print(f"{k:>5} | {rel[0]:>7.3f} | {rel[1]:>7.3f} | {rel[2]:>7.3f} | "
              f"{d:>7.4f} | {sa:>6.3f} | {sb:>6.3f}")

    # Bound-state analysis: is distance near R_EQ for sustained period?
    bound = [(k, rel, d) for (k, rel, d, _, _) in samples if k > 200 and abs(d - R_EQ) < R_EQ]
    if not bound:
        print("\n→ NO sustained binding near r_eq.")
        return

    # Rotation analysis on bound samples
    units = [rel / np.linalg.norm(rel) for (_, rel, _) in bound]
    angles_from_first = []
    for u in units:
        cos_a = float(np.clip(np.dot(u, units[0]), -1.0, 1.0))
        # Allow either same direction or 180° flip (oscillation along axis)
        angles_from_first.append(float(np.degrees(np.arccos(abs(cos_a)))))

    max_rotation = max(angles_from_first)
    print(f"\nBound samples: {len(bound)}. "
          f"Max rel-direction rotation from first: {max_rotation:.2f}° (180-fold).")
    if max_rotation > 30:
        print("→ 2D ROTATIONAL binding: relative-position vector rotates.")
    elif max_rotation > 5:
        print("→ Partial rotation: nascent orbit.")
    else:
        print("→ 1D BOUND: no rotation, oscillation along a fixed line.")


def main():
    z = np.array([0.0, 0.0, 1.0])

    # Exp 1: head-on x approach with z-drift (2D-v1 analog).
    run(
        "Exp 1: head-on x, shared +z drift",
        pos_a=np.array([-2.0, 0.0, 0.0]),
        vel_a=np.array([S, 0.0, S]),
        pos_b=np.array([2.0, 0.0, 0.0]),
        vel_b=np.array([-S, 0.0, S]),
    )

    # Exp 2: zero net momentum, head-on diagonal.
    run(
        "Exp 2: zero net momentum, head-on diagonal",
        pos_a=np.array([-2.0, 0.0, 0.0]),
        vel_a=np.array([S, 0.0, S]),
        pos_b=np.array([2.0, 0.0, 0.0]),
        vel_b=np.array([-S, 0.0, -S]),
    )

    # Exp 3: tangential initial conditions starting near r_eq.
    # Place particles at distance r_eq apart, with velocities perpendicular
    # to their connecting line. If back-reaction balances tangential motion,
    # orbit should be stable from the start.
    run(
        "Exp 3: tangential initial conditions at r_eq",
        pos_a=np.array([-R_EQ / 2, 0.0, 0.0]),
        vel_a=np.array([0.0, S, S]),  # tangent +y, drift +z
        pos_b=np.array([R_EQ / 2, 0.0, 0.0]),
        vel_b=np.array([0.0, -S, S]),  # tangent -y, drift +z
    )


if __name__ == "__main__":
    main()
