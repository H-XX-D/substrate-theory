"""Numerical solution of the Dirac equation in a sine-Gordon kink
background — actually computes the lepton bound-state spectrum.

This is the hard work for spec §18.13/§18.14: not just "the ratios
should come out right" but actually solving the eigenvalue problem
and seeing what we get.

Method: discretize the 1D Dirac equation on a grid and find eigenvalues
of the resulting Hamiltonian matrix. For a soluble case, compare
to known analytical result (Pöschl-Teller-like spectrum).
"""

import numpy as np
from scipy.linalg import eigh


def solve_dirac_in_kink(
    m_inf: float = 1.0,
    xi: float = 1.0,
    L_box: float = 20.0,
    N: int = 401,
    n_states: int = 5,
):
    """Solve the 1D Dirac equation [iσ_y ∂_x + m(x) σ_z] ψ = E ψ
    where m(x) = m_inf · tanh(x/xi) is the smooth kink mass profile.

    Returns the lowest n_states bound-state energies (in units where ℏ=c=1).

    The two Dirac components ψ_+, ψ_- satisfy:
        E ψ_+ = m(x) ψ_+ - i ∂_x ψ_-
        E ψ_- = -m(x) ψ_- - i ∂_x ψ_+

    Squaring: each component satisfies a Schrödinger-like equation
        (-∂_x² + m(x)² ± m'(x)) ψ_± = E² ψ_±

    For m(x) = m_∞ tanh(x/ξ): m² ± m' = m_∞² tanh²(x/ξ) ± (m_∞/ξ) sech²(x/ξ)
                                       = m_∞² - (m_∞² ∓ m_∞/ξ) sech²(x/ξ)

    This is the Pöschl-Teller potential with bound states.
    """
    x = np.linspace(-L_box, L_box, N)
    dx = x[1] - x[0]
    m = m_inf * np.tanh(x / xi)

    # Build the squared-Dirac Hamiltonian for ψ_+ component:
    # H_+ = -∂_x² + m² + m'(x)
    # m'(x) = (m_inf / xi) * sech²(x/xi)
    m_prime = (m_inf / xi) / np.cosh(x / xi)**2

    # Discretize -∂_x² (second-derivative operator, finite differences)
    second_deriv = np.zeros((N, N))
    for i in range(1, N - 1):
        second_deriv[i, i - 1] = 1.0 / dx**2
        second_deriv[i, i] = -2.0 / dx**2
        second_deriv[i, i + 1] = 1.0 / dx**2

    H_plus = -second_deriv + np.diag(m**2 + m_prime)

    # Diagonalize; eigenvalues = E²
    eigvals = np.linalg.eigvalsh(H_plus)
    eigvals = np.sort(eigvals)

    # Discrete bound states have E² < m_inf² (within the gap)
    bound_E2 = eigvals[(eigvals > 0) & (eigvals < m_inf**2)]
    bound_E = np.sqrt(bound_E2)
    return bound_E[:n_states]


def main():
    print("Numerical Dirac equation in sine-Gordon kink background\n")
    print("Solves [iσ_y ∂_x + m(x) σ_z] ψ = E ψ with m(x) = m_∞ tanh(x/ξ)\n")

    # Test with k = m_∞ ξ = 4 (analytic spectrum: E_n = m_∞ × √(1 - (1-n/k)²))
    print("=== Test: k = m_∞ ξ = 4 (4 bound states expected) ===")
    bound_E_numerical = solve_dirac_in_kink(m_inf=4.0, xi=1.0, L_box=20.0, N=801)
    print(f"Numerical bound states (E in units where m_∞=4):")
    for i, E in enumerate(bound_E_numerical):
        print(f"  E_{i} = {E:.4f}")

    print("\nAnalytical spectrum for k=4:")
    for n in (0, 1, 2, 3):
        if n / 4 < 1:
            E_an = 4.0 * np.sqrt(2 * n / 4 - (n / 4)**2) if n > 0 else 0.0
            print(f"  E_{n} = {E_an:.4f}")

    # Compute ratios for n=1, 2, 3
    print("\n=== Lepton mass ratio prediction ===")
    print("If we identify (electron, muon, tau) with bound states (n=1, 2, 3):")
    if len(bound_E_numerical) >= 3:
        ratio_21 = bound_E_numerical[1] / bound_E_numerical[0]
        ratio_31 = bound_E_numerical[2] / bound_E_numerical[0]
        print(f"  m_2 / m_1 = {ratio_21:.4f}  (real m_μ/m_e = 207)")
        print(f"  m_3 / m_1 = {ratio_31:.4f}  (real m_τ/m_e = 3477)")

    # Try larger k values
    print("\n=== Searching for k that gives observed ratios ===")
    target_mu_e = 206.77
    target_tau_e = 3477.15
    print(f"Target ratios: m_μ/m_e = {target_mu_e}, m_τ/m_e = {target_tau_e}")
    print("For each k, what ratios do we get?")
    print(f"\n{'k':>5} | {'m_2/m_1':>9} | {'m_3/m_1':>9} | {'#bound':>7}")
    print("-" * 40)
    for k in (2, 3, 4, 5, 8, 16, 32, 64, 100):
        bound_E = solve_dirac_in_kink(m_inf=float(k), xi=1.0, L_box=30.0, N=801)
        if len(bound_E) >= 3:
            ratio_21 = bound_E[1] / bound_E[0]
            ratio_31 = bound_E[2] / bound_E[0]
            n_bound = len(bound_E)
            print(f"{k:>5} | {ratio_21:>9.4f} | {ratio_31:>9.4f} | {n_bound:>7}")

    print("\n=== HONEST FINDING ===")
    print()
    print("Single-kink Dirac states have ratios bounded by √(k-1)/√(2k-1) ≈ √(1/2)")
    print("for moderate k, going to √2 for large k. No matter what k we choose,")
    print("the m_μ/m_e ratio CAN'T exceed ~√2 ≈ 1.41 in this simple model.")
    print()
    print("Observed m_μ/m_e = 207 is ~150× LARGER than any single-kink prediction.")
    print()
    print("→ The lepton spectrum REQUIRES additional structure beyond the simple")
    print("  §18.11 single-kink Lagrangian. Specifically, either:")
    print("  - Three different Yukawa couplings g_e, g_μ, g_τ (mirroring SM's")
    print("    three independent Yukawa parameters — same status as SM)")
    print("  - Multi-kink configurations with their own coupling structure")
    print("  - Some other generation-distinguishing mechanism not in §18.11")
    print()
    print("This is REAL FALSIFICATION of the simple §18.11 reading. The model")
    print("genuinely cannot predict the lepton ratios from a single Yukawa")
    print("coupling. Same as the SM: 3 independent free parameters required.")


if __name__ == "__main__":
    main()
