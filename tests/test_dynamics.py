import numpy as np
from stiff_medium.neutrino import Neutrino, C
from stiff_medium.dynamics import propagate


def test_propagate_advances_position_by_velocity_times_dt():
    s = C / np.sqrt(2)
    n = Neutrino(
        position=np.array([0.0, 0.0]),
        velocity=np.array([s, s]),
    )
    dt = 0.1
    moved = propagate(n, dt)
    assert np.allclose(moved.position, [s * dt, s * dt])


def test_propagate_preserves_velocity():
    s = C / np.sqrt(2)
    n = Neutrino(
        position=np.array([0.0, 0.0]),
        velocity=np.array([s, -s]),
    )
    moved = propagate(n, 1.0)
    assert np.allclose(moved.velocity, [s, -s])
