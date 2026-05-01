"""Tests for the 2D lattice substrate field solver."""

from __future__ import annotations

import numpy as np
import pytest

from src.stiff_medium.lattice_substrate_2d import (
    LatticeSubstrate2D,
    kink_centre_x,
    gaussian_width,
)


# ---------------------------------------------------------------------------
# (a) Energy conservation, γ = 0
# ---------------------------------------------------------------------------

def test_energy_conservation_no_drag():
    """Energy drift should be < 1% over 1000 steps with γ = 0."""
    sub = LatticeSubstrate2D(Nx=64, Ny=64, dx=0.4, dt=0.05,
                              gamma=0.0, bc="periodic")
    sub.gaussian_pulse_initial(amplitude=0.2, width=2.0)
    E0 = sub.total_energy()
    assert E0 > 0.0
    sub.evolve(1000)
    E1 = sub.total_energy()
    drift = abs(E1 - E0) / E0
    assert drift < 0.01, f"Energy drift {drift:.2e} > 1%"


# ---------------------------------------------------------------------------
# (b) Drag dissipates monotonically
# ---------------------------------------------------------------------------

def test_energy_decreases_with_drag():
    """Energy should decrease monotonically when γ > 0."""
    sub = LatticeSubstrate2D(Nx=64, Ny=64, dx=0.4, dt=0.05,
                              gamma=0.1, bc="periodic")
    sub.gaussian_pulse_initial(amplitude=0.3, width=2.0)
    energies = [sub.total_energy()]
    for _ in range(20):
        sub.evolve(20)
        energies.append(sub.total_energy())
    energies = np.array(energies)
    diffs = np.diff(energies)
    # Allow tiny positive drift from discretisation; require strict decrease overall
    assert (diffs <= 1e-8).all(), f"Energy increased: max diff {diffs.max():.3e}"
    assert energies[-1] < energies[0] * 0.95, (
        f"Drag did not dissipate enough: {energies[0]:.4f} -> {energies[-1]:.4f}"
    )


# ---------------------------------------------------------------------------
# (c) Kink propagation at expected speed
# ---------------------------------------------------------------------------

def test_kink_propagation_speed():
    """A boosted kink line should translate at the expected speed."""
    sub = LatticeSubstrate2D(Nx=128, Ny=32, dx=0.4, dt=0.05,
                              gamma=0.0, bc="periodic")
    speed = 0.3  # in units of c = 1
    sub.kink_initial(direction="x", x0=-8.0, speed=speed)
    x0 = kink_centre_x(sub.u, sub.x)
    assert np.isfinite(x0)
    sub.evolve(400)
    t = sub.t
    x1 = kink_centre_x(sub.u, sub.x)
    assert np.isfinite(x1)
    measured = (x1 - x0) / t
    rel_err = abs(measured - speed) / speed
    assert rel_err < 0.10, (
        f"Kink speed {measured:.4f} differs from expected {speed} by {rel_err:.2%}"
    )


# ---------------------------------------------------------------------------
# (d) Vortex remains stable (not catastrophic blow-up) for 500 steps
# ---------------------------------------------------------------------------

def test_vortex_stable():
    """A winding-1 vortex should not blow up over 500 steps."""
    # Use neumann BC + small drag to avoid runaway from the atan2 branch-cut
    # discontinuity (vortex is not a true static sine-Gordon solution by
    # Derrick's theorem, so some radiation is expected).
    sub = LatticeSubstrate2D(Nx=64, Ny=64, dx=0.4, dt=0.04,
                              gamma=0.05, bc="neumann")
    sub.vortex_initial(x0=0.0, y0=0.0, winding=1, core=1.5)
    E0 = sub.total_energy()
    u_max0 = float(np.max(np.abs(sub.u)))
    sub.evolve(500)
    E1 = sub.total_energy()
    u_max1 = float(np.max(np.abs(sub.u)))
    assert np.isfinite(E1), "Energy diverged"
    assert u_max1 < 5.0 * u_max0 + 10.0, "Field amplitude blew up"
    # With drag, energy must decrease (Derrick instability + dissipation)
    assert E1 < E0, f"Energy did not dissipate: {E0:.3f} -> {E1:.3f}"


# ---------------------------------------------------------------------------
# (e) Gaussian pulse spreads (dispersion)
# ---------------------------------------------------------------------------

def test_gaussian_pulse_spreads():
    """A small-amplitude Gaussian should spread under linear KG dispersion."""
    sub = LatticeSubstrate2D(Nx=128, Ny=128, dx=0.3, dt=0.04,
                              gamma=0.0, bc="periodic")
    sub.gaussian_pulse_initial(amplitude=0.05, width=2.0)
    w0 = gaussian_width(sub.u, sub.X, sub.Y)
    sub.evolve(400)
    w1 = gaussian_width(sub.u, sub.X, sub.Y)
    # Pulse should spread (width grows) — Klein-Gordon dispersion + radiation
    assert w1 > w0, f"Pulse did not spread: w0={w0:.3f} -> w1={w1:.3f}"


# ---------------------------------------------------------------------------
# Sanity: energy components are non-negative
# ---------------------------------------------------------------------------

def test_energy_components_nonneg():
    sub = LatticeSubstrate2D(Nx=32, Ny=32, dx=0.5, dt=0.05)
    sub.gaussian_pulse_initial(amplitude=0.5, width=1.5)
    comps = sub.energy_components()
    assert comps["kinetic"] >= 0.0
    assert comps["gradient"] >= 0.0
    assert comps["potential"] >= 0.0
    assert comps["total"] == pytest.approx(
        comps["kinetic"] + comps["gradient"] + comps["potential"]
    )
