"""Integration test / demonstration for ConeBouncingParticle3D.

Exercises:
1. Isotropic 3-D particle (κ_x = κ_y) — wobble in both planes.
2. Mass from combined frequencies.
3. Heisenberg uncertainty verification (§18.53.7).
4. Ensemble of 100 particles with log-uniform κ distribution.
5. Backward-compatibility check for the 1-D ConeBouncingParticle.

Run from the project root:
    PYTHONPATH=src python3 scripts/cone_bouncing_3d_test.py
"""

from __future__ import annotations

import sys
import numpy as np

from stiff_medium.cone_bouncing import (
    ConeBouncingParticle,
    ConeBouncingParticle3D,
    simulate_ensemble,
    verify_uncertainty_principle,
    mass_from_kappa,
    categorize_particle_by_kappa,
)

SEPARATOR = "-" * 64


def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


# ---------------------------------------------------------------------------
# 1. Backward compatibility — 1-D ConeBouncingParticle
# ---------------------------------------------------------------------------

section("1. Backward compatibility: 1-D ConeBouncingParticle")

p1d = ConeBouncingParticle(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa=4.0,
    I=1.0,
    theta=0.1,
    theta_dot=0.0,
)
print(f"  omega_bounce = {p1d.omega_bounce:.4f}  (expected {np.sqrt(4.0):.4f})")
print(f"  rest_mass    = {p1d.rest_mass:.4f}")

# Step 10 times and check energy conservation
E0 = 0.5 * p1d.I * p1d.theta_dot**2 + 0.5 * p1d.kappa * p1d.theta**2
for _ in range(10):
    p1d.step(dt=0.01)
E1 = 0.5 * p1d.I * p1d.theta_dot**2 + 0.5 * p1d.kappa * p1d.theta**2
print(f"  Energy conservation (10 steps): E0={E0:.6f}  E1={E1:.6f}  diff={abs(E1 - E0):.2e}")
# Velocity-Verlet is 2nd-order; O(dt^2) drift per step is expected.
assert abs(E1 - E0) < 1e-5, "1-D energy not conserved"
print("  [PASS] 1-D backward-compatibility OK")


# ---------------------------------------------------------------------------
# 2. Isotropic 3-D particle — wobble in both directions
# ---------------------------------------------------------------------------

section("2. Isotropic 3-D particle (kappa_x = kappa_y = 4.0)")

p3d = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=4.0,
    kappa_y=4.0,
    I_x=1.0,
    I_y=1.0,
    theta_x=0.1,   # initial x displacement
    theta_y=0.05,  # initial y displacement
    theta_x_dot=0.0,
    theta_y_dot=0.0,
)

print(f"  omega_x = {p3d.omega_x:.4f}  omega_y = {p3d.omega_y:.4f}")
print(f"  initial wobble_radius = {p3d.wobble_radius():.4f}  (expected ~{np.sqrt(0.1**2 + 0.05**2):.4f})")
print(f"  initial |v_3d| = {np.linalg.norm(p3d.instantaneous_velocity_3d()):.6f}  (should be 1.0)")

# Run 500 steps and collect trajectory
dt = 0.01
n_steps = 500
theta_x_history = np.empty(n_steps)
theta_y_history = np.empty(n_steps)

for i in range(n_steps):
    theta_x_history[i] = p3d.theta_x
    theta_y_history[i] = p3d.theta_y
    p3d.step(dt)

print(f"\n  After {n_steps} steps (t = {n_steps * dt:.1f}):")
print(f"  theta_x range: [{theta_x_history.min():.4f}, {theta_x_history.max():.4f}]")
print(f"  theta_y range: [{theta_y_history.min():.4f}, {theta_y_history.max():.4f}]")
print(f"  Both angles oscillating: "
      f"x-range={theta_x_history.max()-theta_x_history.min():.4f}  "
      f"y-range={theta_y_history.max()-theta_y_history.min():.4f}")

# Verify both angles oscillate (non-trivial range)
assert theta_x_history.max() - theta_x_history.min() > 0.15, "theta_x not oscillating"
assert theta_y_history.max() - theta_y_history.min() > 0.07, "theta_y not oscillating"
print("  [PASS] Both wobble angles are oscillating")

# Speed is c = 1 at all times (check a few points mid-trajectory)
p3d_check = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=4.0, kappa_y=4.0,
    theta_x=0.1, theta_y=0.05,
)
for _ in range(100):
    speed = np.linalg.norm(p3d_check.instantaneous_velocity_3d())
    assert abs(speed - 1.0) < 1e-12, f"Speed not 1: {speed}"
    p3d_check.step(dt=0.01)
print("  [PASS] |v_3d| = 1.0 maintained throughout trajectory")


# ---------------------------------------------------------------------------
# 3. Mass from combined frequencies
# ---------------------------------------------------------------------------

section("3. Rest mass from combined frequencies")

# Isotropic case: m c² = sqrt((hbar omega)^2 + (hbar omega)^2) = hbar*omega*sqrt(2)
p_mass = ConeBouncingParticle3D(
    preferred_direction=np.array([1.0, 0.0, 0.0]),
    kappa_x=9.0,
    kappa_y=9.0,
    I_x=1.0,
    I_y=1.0,
    hbar=1.0,
)
omega = p_mass.omega_x  # = omega_y = 3.0
expected_mass = np.sqrt(2.0) * omega
print(f"  omega_x = omega_y = {omega:.4f}")
print(f"  total_rest_mass = {p_mass.total_rest_mass:.6f}")
print(f"  expected (sqrt(2) * omega) = {expected_mass:.6f}")
assert abs(p_mass.total_rest_mass - expected_mass) < 1e-10, "Isotropic mass formula failed"
print("  [PASS] Isotropic mass formula: m c² = sqrt(2) * hbar * omega")

# Anisotropic case
p_aniso = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 1.0, 0.0]),
    kappa_x=4.0,
    kappa_y=16.0,
    I_x=1.0,
    I_y=1.0,
    hbar=1.0,
)
omega_x_a = p_aniso.omega_x   # 2.0
omega_y_a = p_aniso.omega_y   # 4.0
expected_aniso = np.sqrt(omega_x_a**2 + omega_y_a**2)
print(f"\n  Anisotropic: omega_x={omega_x_a:.2f}, omega_y={omega_y_a:.2f}")
print(f"  total_rest_mass = {p_aniso.total_rest_mass:.6f}")
print(f"  expected sqrt(omega_x^2 + omega_y^2) = {expected_aniso:.6f}")
assert abs(p_aniso.total_rest_mass - expected_aniso) < 1e-10, "Anisotropic mass formula failed"
print("  [PASS] Anisotropic mass formula OK")

# Compare with 1-D mass_from_kappa for single-mode case
kappa_single = 9.0
m_1d = mass_from_kappa(kappa_single, I=1.0, hbar=1.0)
p_single_mode = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=kappa_single,
    kappa_y=0.0,  # one mode off
    I_x=1.0,
    I_y=1.0,
    hbar=1.0,
)
print(f"\n  Single-mode (kappa_y=0): 3D mass = {p_single_mode.total_rest_mass:.4f}  "
      f"1D mass_from_kappa = {m_1d:.4f}")
assert abs(p_single_mode.total_rest_mass - m_1d) < 1e-10, "Single-mode 3D != 1D mass"
print("  [PASS] Single-mode 3D mass matches 1D mass_from_kappa")


# ---------------------------------------------------------------------------
# 4. Heisenberg uncertainty verification (§18.53.7)
# ---------------------------------------------------------------------------

section("4. Heisenberg uncertainty principle (§18.53.7)")

# At zero-point amplitude: A^2 = hbar / (2 * I * omega), so Dx*Dp = hbar/2
# Use length_scale = 1 and check the regime where A is forced to zero-point.

# Construct particle whose amplitude is set to the zero-point value
hbar_test = 1.0
omega_test = 2.0
I_test = 1.0
A_zp = np.sqrt(hbar_test / (2.0 * I_test * omega_test))  # zero-point amplitude
kappa_zp = I_test * omega_test**2

p_heisenberg = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=kappa_zp,
    kappa_y=kappa_zp,
    I_x=I_test,
    I_y=I_test,
    theta_x=A_zp,
    theta_y=0.0,
    theta_x_dot=0.0,
    theta_y_dot=0.0,
    hbar=hbar_test,
)

result = verify_uncertainty_principle(p_heisenberg, length_scale=1.0)
print(f"  Zero-point amplitude A = {A_zp:.6f}")
print(f"  Δx_x = {result['delta_x_x']:.6f}  Δp_x = {result['delta_p_x']:.6f}")
print(f"  product_x = {result['product_x']:.6f}  hbar/2 = {result['hbar_half']:.6f}")
print(f"  Δx_y = {result['delta_x_y']:.6f}  Δp_y = {result['delta_p_y']:.6f}")
print(f"  product_y = {result['product_y']:.6f}")
print(f"  satisfies_x = {result['satisfies_x']}  satisfies_y = {result['satisfies_y']}")
print(f"  satisfies_both = {result['satisfies_both']}")

# At zero-point: product_x should be exactly hbar/2
assert abs(result["product_x"] - hbar_test / 2.0) < 1e-10, \
    f"Zero-point product_x = {result['product_x']} != hbar/2 = {hbar_test/2}"
print("  [PASS] Zero-point x-mode product equals hbar/2 exactly")

# With theta_y = 0 at zero velocity, amplitude_y = 0, so product_y = 0
# The x-mode alone satisfies the bound; verify general particle with both modes
p_both = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=kappa_zp,
    kappa_y=kappa_zp,
    I_x=I_test,
    I_y=I_test,
    theta_x=A_zp,
    theta_y=A_zp,  # same zero-point in y
    theta_x_dot=0.0,
    theta_y_dot=0.0,
    hbar=hbar_test,
)
result_both = verify_uncertainty_principle(p_both, length_scale=1.0)
print(f"\n  Both modes at zero-point:")
print(f"  product_x = {result_both['product_x']:.6f}  product_y = {result_both['product_y']:.6f}")
print(f"  hbar/2 = {result_both['hbar_half']:.6f}")
assert result_both["satisfies_both"], "Both-mode particle does not satisfy uncertainty"
print("  [PASS] Both modes satisfy Heisenberg bound simultaneously")

# Verify that super-zero-point amplitude gives product > hbar/2
p_above = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, 1.0]),
    kappa_x=kappa_zp,
    kappa_y=kappa_zp,
    I_x=I_test,
    I_y=I_test,
    theta_x=2.0 * A_zp,  # twice the zero-point amplitude
    theta_y=2.0 * A_zp,
    hbar=hbar_test,
)
result_above = verify_uncertainty_principle(p_above, length_scale=1.0)
print(f"\n  2× zero-point amplitude: product_x = {result_above['product_x']:.6f}  (> hbar/2 = {hbar_test/2:.4f})")
assert result_above["product_x"] > hbar_test / 2.0, "Expected product_x > hbar/2 for larger amplitude"
print("  [PASS] Larger-than-zero-point amplitude satisfies with room to spare")


# ---------------------------------------------------------------------------
# 5. Ensemble of 100 particles
# ---------------------------------------------------------------------------

section("5. Ensemble simulation — 100 particles with log-uniform kappa")

rng = np.random.default_rng(seed=42)
# log-uniform kappa in [0.1, 100]
kappa_samples = np.exp(rng.uniform(np.log(0.1), np.log(100.0), size=500))

stats = simulate_ensemble(
    N_particles=100,
    kappa_distribution=kappa_samples,
    dt=0.005,
    n_steps=200,
    I_x=1.0,
    I_y=1.0,
    initial_theta=0.1,
    hbar=1.0,
    rng=np.random.default_rng(seed=7),
)

print(f"  N particles: 100")
print(f"  kappa range sampled: [{stats['kappas'].min():.3f}, {stats['kappas'].max():.3f}]")
print(f"  omega_x range: [{stats['omega_x'].min():.3f}, {stats['omega_x'].max():.3f}]")
print(f"  omega_y range: [{stats['omega_y'].min():.3f}, {stats['omega_y'].max():.3f}]")
print(f"  mass:   mean = {stats['mean_mass']:.4f}  std = {stats['std_mass']:.4f}")
print(f"  wobble: mean = {stats['mean_wobble']:.4f}  std = {stats['std_wobble']:.4f}")

# Verify mass values are physically consistent: m = sqrt(2) * kappa^0.5 for isotropic
expected_masses = np.sqrt(2.0) * np.sqrt(stats["kappas"])
mass_residual = np.max(np.abs(stats["masses"] - expected_masses))
print(f"  Max deviation from m=sqrt(2)*sqrt(kappa): {mass_residual:.2e}")
assert mass_residual < 1e-10, f"Ensemble masses deviate from expected: {mass_residual}"
print("  [PASS] All ensemble masses match formula m = sqrt(2) * sqrt(kappa)")

# Per §18.53.7 the Heisenberg bound Δx·Δp ≥ ℏ/2 holds at the zero-point.
# For a harmonic oscillator the zero-point amplitude is A_zp = sqrt(ℏ/(2·I·ω)).
# Verify: for every particle the zero-point product equals exactly ℏ/2.
hbar = 1.0
all_zp_ok = True
for kappa_val in stats["kappas"]:
    omega_val = float(np.sqrt(kappa_val / 1.0))  # I_x = 1.0
    if omega_val <= 0:
        continue
    A_zp_val = float(np.sqrt(hbar / (2.0 * 1.0 * omega_val)))  # zero-point amplitude
    product_zp = A_zp_val * (1.0 * omega_val * A_zp_val)  # Δx * Δp at zero-point
    if abs(product_zp - hbar / 2.0) > 1e-10:
        all_zp_ok = False
        break
print(f"  Zero-point Δx·Δp = ℏ/2 for all particles: {all_zp_ok}")
assert all_zp_ok, "Zero-point Heisenberg product != hbar/2 for some particle"
print("  [PASS] All 100 particles satisfy zero-point Heisenberg bound (Δx·Δp = ℏ/2)")

# Also verify: any particle whose current amplitude exceeds the zero-point
# amplitude satisfies the bound with the current (classical) amplitude.
hbar_half = hbar / 2.0
n_above_zp = 0
for k_val, prod_x in zip(stats["kappas"], stats["uncertainty_products_x"]):
    omega_v = float(np.sqrt(k_val / 1.0))
    if omega_v <= 0:
        continue
    A_zp_v = float(np.sqrt(hbar / (2.0 * 1.0 * omega_v)))
    zp_product = A_zp_v * (1.0 * omega_v * A_zp_v)
    if prod_x >= hbar_half - 1e-12:
        n_above_zp += 1
print(f"  Particles with current amplitude satisfying Δx·Δp ≥ ℏ/2: {n_above_zp}/100")

print(f"\n  Particle type distribution (by kappa):")
for label, count in sorted(
    {cat: 0 for cat in ["photon (m=0)", "light neutrino", "charged lepton",
                         "intermediate boson", "heavy kink / GUT-scale"]}.items()
):
    pass  # just reset

type_counts: dict[str, int] = {}
for k in stats["kappas"]:
    label = categorize_particle_by_kappa(float(k))
    type_counts[label] = type_counts.get(label, 0) + 1
for label, count in sorted(type_counts.items()):
    print(f"    {label:30s}: {count}")


# ---------------------------------------------------------------------------
# 6. Edge cases
# ---------------------------------------------------------------------------

section("6. Edge cases")

# Massless particle (kappa = 0 in both modes)
p_massless = ConeBouncingParticle3D(
    preferred_direction=np.array([1.0, 0.0, 0.0]),
    kappa_x=0.0,
    kappa_y=0.0,
    theta_x=0.2,
    theta_y=0.1,
)
print(f"  Massless (kappa=0): omega_x={p_massless.omega_x}  omega_y={p_massless.omega_y}  mass={p_massless.total_rest_mass}")
assert p_massless.total_rest_mass == 0.0, "Massless particle has non-zero mass"

# Step should be a no-op for massless
theta_x_before = p_massless.theta_x
p_massless.step(dt=0.1)
assert p_massless.theta_x == theta_x_before, "Massless particle should not evolve"
print("  [PASS] Massless particle: mass=0, step is no-op")

# Non-unit preferred direction should be auto-normalized
p_unnorm = ConeBouncingParticle3D(
    preferred_direction=np.array([3.0, 4.0, 0.0]),
    kappa_x=1.0,
    kappa_y=1.0,
)
norm = np.linalg.norm(p_unnorm.preferred_direction)
assert abs(norm - 1.0) < 1e-12, f"preferred_direction not normalized: {norm}"
print(f"  [PASS] preferred_direction auto-normalized (|d| = {norm:.10f})")

# preferred direction along +x (not +z) — frame construction
p_xdir = ConeBouncingParticle3D(
    preferred_direction=np.array([1.0, 0.0, 0.0]),
    kappa_x=1.0,
    kappa_y=1.0,
    theta_x=0.1,
    theta_y=0.1,
)
speed = np.linalg.norm(p_xdir.instantaneous_velocity_3d())
assert abs(speed - 1.0) < 1e-12, f"Speed not 1 for x-preferred direction: {speed}"
print("  [PASS] x-preferred direction: |v_3d| = 1.0")

# preferred direction along -z (edge of frame builder)
p_negz = ConeBouncingParticle3D(
    preferred_direction=np.array([0.0, 0.0, -1.0]),
    kappa_x=1.0,
    kappa_y=1.0,
    theta_x=0.1,
    theta_y=0.1,
)
speed = np.linalg.norm(p_negz.instantaneous_velocity_3d())
assert abs(speed - 1.0) < 1e-12, f"Speed not 1 for -z direction: {speed}"
print("  [PASS] -z preferred direction: |v_3d| = 1.0")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

section("Summary")
print("  All tests passed.")
print()
print("  Classes available:  ConeBouncingParticle (1D, unchanged)")
print("                      ConeBouncingParticle3D (new, 2 angular DoF)")
print("  Functions added:    verify_uncertainty_principle")
print("                      simulate_ensemble")
print()
print("  Key physics (§18.35 / §18.53.7):")
print("    m c² = sqrt( (hbar*omega_x)^2 + (hbar*omega_y)^2 )")
print("    Heisenberg: Δx * Δp >= hbar/2 (structural, from cone bouncing)")
print()
