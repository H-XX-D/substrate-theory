"""Kinetic energy in the substrate framework: derivation and physical meaning.

Standard:
  Newtonian KE = ½ m v²
  Relativistic KE = (γ - 1) m c²
  Total energy E = γ m c² = √((mc²)² + (pc)²)

Substrate derivation: a particle is a bound-state excitation of the
substrate field u(x, t). When the particle moves at velocity v,
the substrate pattern translates → ADDITIONAL strain energy from the
translational motion. This IS kinetic energy.

The derivation:
  L_substrate = ½ρ(∂_t u)² - ½K|∇u|² - V(u) - γ u·∂_t u

For static bound state at rest: u(x, t) = u_0(x) × cos(ω_b t)
  Total energy: E_rest = ℏω_b = m c² (rest energy from cone-bouncing)

For moving bound state: u(x, t) = u_0(x - vt) × oscillation
  ∂_t u contains an extra -v · ∇u_0 piece → extra strain energy

The extra strain energy = KE = ½ × (∫ρ(∇u_0)² d³x) × v² = ½ m v²
  (in non-relativistic limit; m identified with ∫ρ(∇u_0)² d³x)

So Newton's KE = ½mv² is just the substrate strain energy of a
translating bound-state, in the linear regime.
"""

from __future__ import annotations
import math


PI = math.pi
M_E_KG = 9.109e-31
C_M_S = 2.998e8


def main() -> None:
    print("Kinetic energy in substrate framework: derivation")
    print("=" * 70)
    print()

    # ===== Static rest energy =====
    print("=" * 70)
    print("1. Rest energy E₀ = mc²")
    print("=" * 70)
    print()
    print("Particle at rest: bound-state oscillates at cone-bouncing frequency ω_b")
    print("Substrate field: u(x, t) = u₀(x) × cos(ω_b t)")
    print()
    print("Substrate energy at rest:")
    print("  E_rest = ∫[½ρ(∂_t u)² + ½K|∇u|²] d³x")
    print("        = ∫[½ρ ω_b² u₀²(x) cos² + ½K|∇u₀|² cos²] d³x")
    print("        ⟨time-averaged⟩ → ½ × Total energy density")
    print()
    print("Equating internal substrate strain energy to ℏω_b (one quantum):")
    print("  E_rest = ℏ × ω_b = m c²")
    print()
    print("So m c² is the substrate's quantum of bound-state oscillation energy.")
    print()

    # ===== Translation kinetic energy =====
    print("=" * 70)
    print("2. Translational kinetic energy ½mv²")
    print("=" * 70)
    print()
    print("Moving particle: bound-state pattern translates at velocity v")
    print("Substrate field: u(x, t) = u₀(x - vt) × cos(ω_b' t)")
    print()
    print("Time derivative now includes BOTH oscillation AND translation:")
    print("  ∂_t u = -v·∇u₀ × cos(ω_b' t) - u₀ × ω_b' sin(ω_b' t)")
    print()
    print("Strain energy gets extra term from translation:")
    print("  E_kin = ∫½ρ |v·∇u₀|² d³x")
    print("        = ½ v² × ∫ρ |∇u₀|² d³x")
    print("        = ½ M v²    (with M = ∫ρ|∇u₀|² d³x = inertial mass)")
    print()
    print("This is Newton's KE = ½mv² emerging from substrate strain.")
    print("M is the SAME mass that gives rest energy mc² (equivalence)")
    print("because the same substrate strain pattern determines both.")
    print()

    # ===== Numerical example =====
    print("=" * 70)
    print("3. Numerical example: electron")
    print("=" * 70)
    print()
    M_E_GEV = 5.11e-4  # GeV
    KE_at_v01_c = 0.5 * M_E_GEV * (0.1)**2  # at v = 0.1c
    print(f"  Electron rest energy: mc² = {M_E_GEV*1000:.4f} MeV")
    print(f"  KE at v = 0.1c (NR limit): ½mv² = {KE_at_v01_c*1000:.4f} MeV")
    print()
    print("  Both energies are SUBSTRATE STRAIN ENERGIES:")
    print("  - Rest: internal cone-bouncing oscillation")
    print("  - Kinetic: translational pattern propagation")
    print()

    # ===== Relativistic case =====
    print("=" * 70)
    print("4. Relativistic kinetic energy KE = (γ-1) mc²")
    print("=" * 70)
    print()
    print("As v → c, substrate strain σ around moving bound-state grows.")
    print("Eventually approaches saturation σ → 1/2 (analogous to BH horizon).")
    print()
    print("The cone-bouncing frequency itself scales:")
    print("  ω_b'(v) = ω_b(0) × γ(v) where γ = 1/√(1-v²/c²)")
    print()
    print("Total energy:")
    print("  E_total = ℏ × ω_b'(v) = γ × m c²")
    print("  KE = E_total - mc² = (γ-1) × mc²")
    print()
    print("This automatically gives the relativistic KE formula.")
    print()
    print("Specific numerical example:")
    print(f"{'v/c':>8s}  {'γ':>10s}  {'KE/mc² (NR ½v²/c²)':>22s}  {'KE/mc² (rel γ-1)':>22s}")
    for v_over_c in [0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99, 0.999]:
        gamma = 1/math.sqrt(1 - v_over_c**2)
        ke_nr = 0.5 * v_over_c**2
        ke_rel = gamma - 1
        print(f"  {v_over_c:>6.3f}    {gamma:>8.4f}      {ke_nr:>16.6f}      "
              f"{ke_rel:>16.6f}")
    print()

    # ===== Where does KE go when something stops? =====
    print("=" * 70)
    print("5. Where does KE go when a particle stops?")
    print("=" * 70)
    print()
    print("Standard physics: KE → heat (random molecular motion)")
    print()
    print("Substrate: KE is the translational substrate strain pattern.")
    print("When particle decelerates (e.g., by collision):")
    print("  - Translational strain pattern is disrupted")
    print("  - Energy → DISSIPATED via substrate drag γ")
    print("  - Final state: substrate fluctuations at lower frequency")
    print("    (= thermal motion of substrate field)")
    print()
    print("This is the substrate-mechanical version of the second law of")
    print("thermodynamics: ordered translational strain → disordered substrate")
    print("fluctuations. Drag γ provides the dissipation channel.")
    print()
    print("Heat = substrate field oscillation at frequencies/scales corresponding")
    print("to ambient temperature. KE → heat = substrate strain pattern transformation.")
    print()

    # ===== Connections =====
    print("=" * 70)
    print("6. Kinetic energy connects to other substrate phenomena")
    print("=" * 70)
    print()
    print("Same substrate KE mechanism gives:")
    print("  - Newton's ½mv² (low-velocity)")
    print("  - Relativistic (γ-1)mc² (high-velocity)")
    print("  - Heat capacity (thermal substrate excitations)")
    print("  - Friction (drag γ converts ordered KE → disordered substrate motion)")
    print("  - Brownian motion (thermal substrate fluctuations push on particles)")
    print("  - Orbital mechanics (KE-PE balance in gravitational potential)")
    print()
    print("All from one substrate strain energy formula:")
    print("  E_strain(x, t) = ½ρ(∂_t u)² + ½K|∇u|² - γ u ∂_t u")
    print()
    print("Different physical regimes:")
    print("  - Bound state oscillating: rest energy mc²")
    print("  - Translating pattern: kinetic energy ½mv²")
    print("  - Random fluctuations: heat (thermal energy)")
    print("  - Gradient field: potential energy (G, EM, etc.)")
    print()
    print("All forms of ENERGY in physics are substrate strain energy")
    print("in different patterns/configurations.")


if __name__ == "__main__":
    main()
