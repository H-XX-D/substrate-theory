"""Atomic-scale dynamics: bound-state COMs, NOT cone-constrained.

The cone constraint of spec §5 applies to the underlying neutrinos.
At the atomic scale, the relevant objects are already-bound multi-neutrino
configurations (electrons, nucleons) whose center-of-mass dynamics is
free — the COM velocity is not constrained to c, even though the
internal neutrinos all move at c on their cones.

This module provides Newton-like dynamics for COM particles, suitable
for modeling atoms (electron + nucleus) and their isotope variants.

The interaction force at this scale is Coulomb-like (1/r² attractive
for opposite slope shapes; per spec §10), reflecting the medium's
back-reaction averaged over the bound states' internal structure.
"""

from typing import Callable
import numpy as np


def coulomb_attraction(
    pos_a: np.ndarray,
    pos_b: np.ndarray,
    coupling: float = 1.0,
) -> np.ndarray:
    """Attractive 1/r² central force on A from B (and minus this on B).

    F = -coupling / r² · r̂  (attractive: pulls A toward B).

    Per spec §10: at the atomic scale, slope-shape complementarity
    (electron's trough fits proton's hill) gives an attractive force
    that scales as 1/r² in the far field. The coupling parameter
    encodes the medium's effective response strength at this scale.
    """
    diff = pos_b - pos_a
    d = float(np.linalg.norm(diff))
    if d < 1e-12:
        return np.zeros(3)
    unit = diff / d
    return (coupling / (d * d)) * unit  # toward B


def newton_step(
    pos_a: np.ndarray,
    vel_a: np.ndarray,
    mass_a: float,
    pos_b: np.ndarray,
    vel_b: np.ndarray,
    mass_b: float,
    dt: float,
    force_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """One velocity-Verlet step for two COM particles. No cone constraint.

    `force_fn(pos_a, pos_b)` returns the force ON a from b. Force on b
    is the negative (Newton's third law).
    """
    f_a = force_fn(pos_a, pos_b)
    f_b = -f_a

    half_vel_a = vel_a + 0.5 * (f_a / mass_a) * dt
    half_vel_b = vel_b + 0.5 * (f_b / mass_b) * dt

    new_pos_a = pos_a + half_vel_a * dt
    new_pos_b = pos_b + half_vel_b * dt

    new_f_a = force_fn(new_pos_a, new_pos_b)
    new_f_b = -new_f_a

    new_vel_a = half_vel_a + 0.5 * (new_f_a / mass_a) * dt
    new_vel_b = half_vel_b + 0.5 * (new_f_b / mass_b) * dt

    return new_pos_a, new_vel_a, new_pos_b, new_vel_b


def reduced_mass(m_light: float, m_heavy: float) -> float:
    """μ = m_light · m_heavy / (m_light + m_heavy)."""
    return m_light * m_heavy / (m_light + m_heavy)
