# Stiff-Medium Path C Simulation

2D lattice-gas simulation testing whether the displacement-only neutrino dynamics described in `docs/superpowers/specs/2026-04-29-stiff-medium-theory-design.md` produce stable electron formation.

## Setup
```
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run experiment
```
python scripts/electron_formation.py
```

## Test
```
pytest
```

## What this tests

Two neutrinos on collision course at 45° angles. If the rules produce a bound orbital state, that's a positive result for the theory. If they don't, the rules need revision.

## Result of v1 experiment

Run on: 2026-04-29
Parameters: DT=0.01, R_OVERLAP=0.05, PUSH=0.05, R_BOUND=0.5, PERSISTENCE=50, N_STEPS=1000.
Scale check: c·dt = 0.01; R_OVERLAP and PUSH (both 0.05) are 5× c·dt — small relative to the simulation domain (~4 units initial separation) but a few times the per-step travel distance.

### Outcome

BOUND state first detected at step 297, and **persisted for the remaining 703 steps** of the run. Inspected trajectory:

| step | x_A | y_A | x_B | y_B | dist |
|---:|---:|---:|---:|---:|---:|
| 0   | -2.000 | 0.000 |  2.000 | 0.000 | 4.000 |
| 247 | -0.253 | 1.747 |  0.253 | 1.747 | 0.507 |
| 280 | -0.045 | 1.980 |  0.045 | 1.980 | 0.090 |
| 400 | -0.047 | 2.828 |  0.047 | 2.828 | 0.093 |
| 700 | -0.025 | 4.950 |  0.025 | 4.950 | 0.051 |
| 1000 | -0.029 | 7.071 |  0.029 | 7.071 | 0.058 |

The pair-distance oscillates between ~0.05 and ~0.10 from step ~280 onward and never re-separates within the observation window.

### Interpretation (honest)

This is a **partial positive result** for spec §5 (the displacement-only dynamics rule). The rule alone, with no restoring force, no wave emission, no other added structure, produces a *persistent bound state* — that's stronger than was anticipated.

Important caveat: **the bound state is 1D, not 2D.** It is a relative-coordinate confinement in x with linear drift in y (the COM moves up at +c/√2 ≈ 0.707, exactly the original y-momentum the two particles brought in). The y-momentum is conserved (as the spec demands — vectors never reorient). The x-momentum is repeatedly exchanged between the two particles via displacement, producing the oscillation.

This is not yet the **2D orbital cone** the spec §6 expects for a true electron — it is a 1D bound oscillation co-moving with a y-drift. Whether the 2D cone emerges with different initial conditions (e.g., velocities chosen so net y-momentum cancels) or requires further structure in the rule is the natural Path C v2 question.

### What this tells us about the theory

- Spec §5 (displacement-only, vectors preserved) is **strong enough to produce binding** — the "stiff medium gives a gyroscope" picture works mechanically. Not a falsification.
- Spec §6 (electron as 2D bound orbit sweeping a 3D cone) is **not yet demonstrated** — what we got is a 1D x-oscillation with y-drift, not a 2D rotation. v2 needs to test initial conditions where the COM is at rest.
- Spec §2 (no correction loops) was honored: the parameters were chosen once based on physical scale and not adjusted. The result is what the rule produced, not what we wanted to see.

### Suggested Path C v2

1. Initial conditions with zero net momentum: e.g., A at (-2, 0) velocity (s, s), B at (2, 0) velocity (-s, -s). Test whether 2D circulation emerges.
2. Parameter sweep over R_OVERLAP and PUSH at fixed c, dt: check whether the bound state survives or degrades, and whether the orbit radius depends predictably on these (as A+E in spec §6 predicts).
3. Run longer (10⁵ steps) and check for slow drift, dissipation, or eventual unbinding.

## Result of v2 experiment (zero net momentum)

Run on: 2026-04-29
Initial conditions: A at (-2, -2) heading NE (s, s); B at (2, 2) heading SW (-s, -s). Center of mass at origin, zero net momentum. 2000 steps, otherwise same parameters as v1.

### Outcome

Bound state first detected at step 307 (essentially the same step as v1 once the diagonal geometry is accounted for) and persisted through all 2000 steps. Final relative distance: 0.057.

**Relative-position angle: locked at 45° throughout. Spread across 21 samples after binding: 0.00 degrees.** The relative-position vector (B − A) does not rotate. The bound state is a 1D oscillation along the approach diagonal, with zero 2D orbital character.

### Interpretation: 2D orbits are geometrically unreachable in 2D under the 45° constraint

In 2D, the only allowed velocity vectors are (±s, ±s) — four discrete directions at 45° to the axes. For zero net momentum, the two particles' velocities must be exactly antiparallel (v_B = −v_A). Antiparallel head-on approach geometrically forces a 1D oscillation along the line of approach — there is no velocity component perpendicular to that line, and the displacement rule cannot manufacture one (vectors never reorient, per spec §5).

This is a **structural finding, not a simulation artifact**: under spec §5 (vectors preserved) plus the 45° quantization, **a 2D orbit is mathematically impossible in 2D simulation**, regardless of initial position or parameter choice.

### What this means for the spec

- **Spec §5 (displacement rule, vectors preserved) is again validated for binding.** The bound state is even tighter and more persistent than v1.
- **Spec §6 (electron as a 2D bound orbit sweeping a 3D cone) is NOT achievable in 2D.** It requires either:
  1. **3D simulation** — in 3D, "45° to one axis" specifies a *cone* of directions (a continuous U(1) family), giving the velocity components needed for tangential orbital motion. This is the cleanest path forward and matches the spec's "rotation sweeps a 3D cone" language.
  2. **Revise the 45° constraint** — allow more discrete velocity directions in 2D, or relax to a continuum.
  3. **Add structure beyond bare displacement** — e.g., medium back-reaction or wave emission that creates a centripetal effect.

The cleanest move is option 1 (upgrade to 3D) since the spec already says the medium is 3D. The 2D simulation was a v1 simplification, and we now know it was a load-bearing simplification: it filtered out exactly the structure (3D orbital cone) the theory predicts.

Per spec §2: this is *not* a falsification of the theory — the rules are working, and the limitation is the simulation's dimensionality, not the rules themselves. But the spec's claim that the electron is a 2D bound orbit needs to be tested in 3D before claiming victory.
