"""Dynamics rules. See spec §5 for the load-bearing displacement rule."""

import numpy as np
from stiff_medium.neutrino import Neutrino


def propagate(n: Neutrino, dt: float) -> Neutrino:
    """Advance position by velocity*dt. Velocity unchanged (spec §5)."""
    return Neutrino(
        position=n.position + n.velocity * dt,
        velocity=n.velocity.copy(),
    )


def detect_overlap(a: Neutrino, b: Neutrino, r_overlap: float) -> bool:
    """Return True if two neutrinos are within r_overlap of each other.

    This is the trigger for the displacement rule (spec §5).
    """
    distance = float(np.linalg.norm(a.position - b.position))
    return distance < r_overlap
