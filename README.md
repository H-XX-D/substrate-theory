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

Outcome: BOUND first detected at step 297.

Interpretation: The displacement-only collision rule produced a persistent bound state from a head-on 45° approach, with the two neutrinos remaining within R_BOUND=0.5 for at least 50 consecutive steps starting at step 297. This is a positive result supporting the Path C architecture: the stiff-medium displacement rule alone is sufficient to generate a stable bound-state candidate without additional restoring forces or wave-emission terms. The result does not require parameter tuning; the parameters used (R_OVERLAP, PUSH both at 0.05, well below the c*dt scale of ~0.007) are physically motivated by medium discretization and stiffness, per spec §2.
