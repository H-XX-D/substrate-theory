import numpy as np
from stiff_medium.neutrino import Neutrino, C
from stiff_medium.dynamics import propagate, detect_overlap


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


def test_detect_overlap_when_close():
    n1 = Neutrino(
        position=np.array([0.0, 0.0]),
        velocity=np.array([C / np.sqrt(2), C / np.sqrt(2)]),
    )
    n2 = Neutrino(
        position=np.array([0.05, 0.05]),
        velocity=np.array([-C / np.sqrt(2), -C / np.sqrt(2)]),
    )
    assert detect_overlap(n1, n2, r_overlap=0.1) is True


def test_no_overlap_when_far():
    n1 = Neutrino(
        position=np.array([0.0, 0.0]),
        velocity=np.array([C / np.sqrt(2), C / np.sqrt(2)]),
    )
    n2 = Neutrino(
        position=np.array([10.0, 10.0]),
        velocity=np.array([-C / np.sqrt(2), -C / np.sqrt(2)]),
    )
    assert detect_overlap(n1, n2, r_overlap=0.1) is False
