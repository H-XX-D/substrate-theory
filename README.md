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
