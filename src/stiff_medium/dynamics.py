"""Dynamics rules. See spec §5 for the load-bearing displacement rule."""

import numpy as np
from stiff_medium.neutrino import Neutrino


def propagate(n: Neutrino, dt: float) -> Neutrino:
    """Advance position by velocity*dt. Velocity unchanged (spec §5)."""
    return Neutrino(
        position=n.position + n.velocity * dt,
        velocity=n.velocity.copy(),
    )
