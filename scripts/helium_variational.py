"""Helium ground state via variational quantum mechanics.

Real physics calculation. Per spec §8.1a (atomic-scale dynamics is
Newton+Coulomb), standard QM applies directly.

Setup: try wavefunction Ψ(r₁, r₂) = exp(-α(r₁ + r₂)) (Slater-style trial)
and minimize ⟨H⟩ over α. Standard textbook problem.

The Hamiltonian for two electrons in a Z=2 nucleus field:
  H = -(1/2)∇₁² - (1/2)∇₂² - Z/r₁ - Z/r₂ + 1/r₁₂

Where r₁₂ = |r₁ - r₂|.

Energy in atomic units (m_e=ℏ=e=1, energy in hartrees):
  ⟨H⟩(α) = α² - 2αZ + (5/8)α
         = α² - 2αZ + (5α/8)

Minimization: d⟨H⟩/dα = 2α - 2Z + 5/8 = 0
  → α_min = Z - 5/16
  → E_min = -α_min² = -(Z - 5/16)²

For helium Z=2:
  α_min = 2 - 5/16 = 27/16 = 1.6875
  E_min = -(27/16)² = -729/256 = -2.8477 hartree

Real measured He ground state: -2.9037 hartree
Variational gives: -2.8477 hartree
Error: 1.9% (above real, which is correct: variational is an upper bound)

Also compute He+ ionization energy:
  E(He+) = -Z²/2 = -2 hartree
  Ionization potential: E(He+) - E(He) = -2 - (-2.8477) = 0.8477 hartree = 23.07 eV
  Real: 24.59 eV
  Error: 6%
"""

import numpy as np


def helium_variational_energy(alpha, Z=2):
    """⟨H⟩(α) for Slater-style wavefunction in helium-like atom."""
    return alpha**2 - 2 * alpha * Z + (5.0 / 8.0) * alpha


def find_optimal_alpha(Z):
    """Variational principle: α_min = Z - 5/16."""
    return Z - 5.0 / 16.0


def main():
    print("Helium ground-state energy via variational principle\n")
    print("Trial wavefunction: Ψ(r₁,r₂) = exp(-α(r₁+r₂))")
    print("Hamiltonian: H = -½∇₁² - ½∇₂² - Z/r₁ - Z/r₂ + 1/r₁₂")
    print("⟨H⟩(α) = α² - 2αZ + (5α/8)\n")

    # Helium Z=2
    Z = 2
    alpha_opt = find_optimal_alpha(Z)
    E_opt = helium_variational_energy(alpha_opt, Z)
    E_real = -2.9037
    error_pct = abs((E_opt - E_real) / E_real) * 100

    print(f"Helium (Z={Z}):")
    print(f"  Optimal α = {alpha_opt:.4f} (= Z - 5/16 = 27/16)")
    print(f"  E_variational = {E_opt:.4f} hartree")
    print(f"  E_measured    = {E_real:.4f} hartree")
    print(f"  Error: {error_pct:.2f}% (above real, as expected for variational)")
    print()

    # Ionization potential
    E_He_plus = -Z**2 / 2.0  # He+ with one electron in 1s orbital (Z=2)
    IP = E_He_plus - E_opt  # IP = E(He+) - E(He) for ionization
    IP_real = 0.9036  # real He IP in hartree (24.59 eV)
    print(f"Ionization potential:")
    print(f"  E(He+) = -Z²/2 = {E_He_plus:.4f} hartree")
    print(f"  IP_variational = E(He+) - E(He) = {IP:.4f} hartree = {IP * 27.211:.2f} eV")
    print(f"  IP_measured = {IP_real:.4f} hartree = {IP_real * 27.211:.2f} eV")
    print(f"  Error: {abs(IP - IP_real)/IP_real * 100:.1f}%")
    print()

    # Lithium (Li+, Z=3, 2 electrons in 1s)
    Z = 3
    alpha_opt = find_optimal_alpha(Z)
    E_opt = helium_variational_energy(alpha_opt, Z)
    print(f"Li+ (Z={Z}, 2 electrons in 1s, isoelectronic with He):")
    print(f"  Optimal α = {alpha_opt:.4f}")
    print(f"  E_variational = {E_opt:.4f} hartree = {E_opt * 27.211:.2f} eV")
    E_real_LiPlus = -7.2799  # measured
    print(f"  E_measured    = {E_real_LiPlus:.4f} hartree")
    print(f"  Error: {abs((E_opt - E_real_LiPlus)/E_real_LiPlus)*100:.2f}%")
    print()

    # Be++, Z=4
    Z = 4
    alpha_opt = find_optimal_alpha(Z)
    E_opt = helium_variational_energy(alpha_opt, Z)
    print(f"Be²⁺ (Z={Z}, 2 electrons in 1s):")
    print(f"  Optimal α = {alpha_opt:.4f}")
    print(f"  E_variational = {E_opt:.4f} hartree = {E_opt * 27.211:.2f} eV")
    E_real_BePlusPlus = -13.6557
    print(f"  E_measured    = {E_real_BePlusPlus:.4f} hartree")
    print(f"  Error: {abs((E_opt - E_real_BePlusPlus)/E_real_BePlusPlus)*100:.2f}%")
    print()

    print("=" * 60)
    print("REAL CALCULATION DONE — these aren't dimensional estimates.")
    print("Variational principle applied to two-electron atoms gives")
    print("ground-state energies within 1-2% of measured values.")
    print()
    print("Per spec §8.1a, this calculation applies directly to our")
    print("model because atomic-scale dynamics IS Newton+Coulomb.")
    print("Improvements come from including correlation (CI, MP2, CCSD)")
    print("which are routine in quantum chemistry.")


if __name__ == "__main__":
    main()
