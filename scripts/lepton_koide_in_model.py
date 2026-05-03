"""Lepton spectrum analysis — Koide's relation as constraint on κ values
in our model (§18.35 mass mechanism).

Per spec §18.35: m c² = ℏ × ω_bounce = ℏ × √(κ/I), so m² ∝ κ.

The empirical Koide relation:
    Q ≡ (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)² = 2/3

is observationally exact (Q = 0.6667 to ~10⁻⁵). In our model, this
becomes a constraint on the directional-stiffness values κ_n:
    Q = Σ √κ_n / (Σ κ_n^(1/4))² = 2/3

This script:
1. Verifies Koide's relation numerically for the measured leptons.
2. Translates to κ-language in our model.
3. Documents the structural openness: 3 free κ values (one per generation),
   constrained by Koide to 2 free parameters.
4. Notes this matches the SM's status (3 free Yukawa couplings → 2 after Koide).

The lepton spectrum is GENUINELY open — same status as in the SM —
but Koide's relation provides a 1-parameter constraint that any
theoretical treatment (ours or SM) must respect.
"""

import numpy as np


# Lepton masses (PDG 2024 values, MeV/c²)
m_e = 0.51099895069
m_mu = 105.6583755
m_tau = 1776.86


def koide_Q(m_e, m_mu, m_tau):
    """Q = (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)²"""
    sum_m = m_e + m_mu + m_tau
    sum_sqrt_m = np.sqrt(m_e) + np.sqrt(m_mu) + np.sqrt(m_tau)
    return sum_m / sum_sqrt_m**2


def koide_kappa_form(kappa_e, kappa_mu, kappa_tau):
    """Q in κ-language (since m ∝ √κ in our model):
    Q = Σ √κ / (Σ κ^(1/4))²"""
    sum_sqrt_kappa = np.sqrt(kappa_e) + np.sqrt(kappa_mu) + np.sqrt(kappa_tau)
    sum_quartic = kappa_e**0.25 + kappa_mu**0.25 + kappa_tau**0.25
    return sum_sqrt_kappa / sum_quartic**2


def main():
    print("=" * 70)
    print("LEPTON SPECTRUM ANALYSIS — Koide's relation in our model (§18.35)")
    print("=" * 70)
    print()

    # Step 1: verify Koide relation
    print("Step 1: empirical lepton masses (PDG 2024):")
    print(f"  m_e   = {m_e:.6f} MeV/c²")
    print(f"  m_μ   = {m_mu:.6f} MeV/c²")
    print(f"  m_τ   = {m_tau:.6f} MeV/c²")
    print()

    Q = koide_Q(m_e, m_mu, m_tau)
    print(f"Q = (Σ m) / (Σ √m)² = {Q:.6f}")
    print(f"Koide predicts: Q = 2/3 = {2/3:.6f}")
    print(f"Deviation from 2/3: {abs(Q - 2/3):.6f} (i.e., {abs(Q - 2/3)/(2/3) * 100:.4f}%)")
    print()
    print("→ Koide's relation is satisfied to ~10⁻⁵ precision.")
    print("  This is observationally striking and demands explanation.")
    print()

    # Step 2: translate to κ-language
    print("=" * 70)
    print("Step 2: in our model (m ∝ √κ from §18.35), κ values:")
    print("=" * 70)
    print()

    # We can scale κ freely; pick κ_e = 1 (m² in units of m_e²)
    kappa_e = 1.0
    kappa_mu = (m_mu / m_e)**2  # 207.7² = 43133
    kappa_tau = (m_tau / m_e)**2  # 3477.5² = 12,089,306

    print(f"  κ_e = {kappa_e:.4f} (chosen scale)")
    print(f"  κ_μ = (m_μ/m_e)² = {kappa_mu:.4e}")
    print(f"  κ_τ = (m_τ/m_e)² = {kappa_tau:.4e}")
    print()

    Q_kappa = koide_kappa_form(kappa_e, kappa_mu, kappa_tau)
    print(f"Q in κ-form: Σ √κ / (Σ κ^(1/4))² = {Q_kappa:.6f}")
    print(f"  ✓ Same as Q from masses (since m ∝ √κ).")
    print()

    # Mass ratios
    print("Mass ratios:")
    print(f"  m_μ / m_e = {m_mu/m_e:.4f}      (= 207.7)")
    print(f"  m_τ / m_e = {m_tau/m_e:.4f}    (= 3477.5)")
    print(f"  m_τ / m_μ = {m_tau/m_mu:.4f}   (= 16.82)")
    print()

    # κ ratios
    print("Stiffness ratios:")
    print(f"  κ_μ / κ_e = {kappa_mu/kappa_e:.4e}")
    print(f"  κ_τ / κ_e = {kappa_tau/kappa_e:.4e}")
    print(f"  κ_τ / κ_μ = {kappa_tau/kappa_mu:.4e}")
    print()

    print("=" * 70)
    print("Step 3: where this leaves the model")
    print("=" * 70)
    print()
    print("Our model gives mass = ℏ × √(κ/I) where κ is the directional")
    print("stiffness of the bound configuration. The stress-loading mechanism")
    print("(§18.30) says muon and tau are stress-loaded electrons, but does")
    print("NOT predict the specific κ values from first principles.")
    print()
    print("Koide's relation Σ m / (Σ √m)² = 2/3 is observationally exact and")
    print("thus is a non-trivial constraint on whatever theory predicts the")
    print("κ values. It reduces the 3-parameter freedom to 2 parameters.")
    print()
    print("This is the SAME STATUS as in the Standard Model:")
    print("- SM has 3 free Yukawa couplings y_e, y_μ, y_τ")
    print("- Koide's constraint reduces effective freedom to 2")
    print("- Neither model derives all 3 from a deeper principle")
    print()
    print("The model HAS structural advantages over SM here:")
    print("- Predicts EXACTLY 3 generations (§6.4 vertex closure)")
    print("- Provides a mass MECHANISM (cone-bouncing, §18.35)")
    print("- Identifies why mass exists (preferred direction wobble)")
    print("- Photon masslessness is structural (no preferred direction)")
    print()
    print("But:")
    print("- Doesn't compute κ_n from §18.11 Lagrangian (open work)")
    print("- Same as SM doesn't compute Yukawa from a deeper theory")
    print()

    # Test multi-kink picture
    print("=" * 70)
    print("Multi-kink hypothesis check")
    print("=" * 70)
    print()
    print("Single-kink Dirac saturates at m_2/m_1 ≈ √2 (per `lepton_dirac_solver.py`).")
    print("Observed: m_μ/m_e ≈ 207. This requires going beyond single-kink.")
    print()

    # If we model muon as a 2-kink configuration with mass scale doubling
    print("Speculation: each stress quantum could double the topological winding")
    print("number, multiplying the effective mass scale ξ_eff by some factor F.")
    print(f"  For m_μ/m_e = 207: F = 207 (one stress quantum)")
    print(f"  Predicted m_τ/m_e if F is the same: F² = 42849 (NOT matching 3477)")
    print()
    print("→ Simple stress-loading (multiplicative) doesn't fit. The pattern")
    print("  is genuinely non-trivial.")
    print()

    print("=" * 70)
    print("CONCLUSION (honest)")
    print("=" * 70)
    print()
    print("§18.23 item 1 (specific lepton spectrum) remains genuinely open.")
    print("Our model has the SAME status as the SM:")
    print("- Structurally predicts 3 generations ✓")
    print("- Has a mechanism for mass (bouncing) ✓")
    print("- Cannot compute the 3 specific κ_n values without specifying")
    print("  the loaded-vertex Lagrangian explicitly.")
    print()
    print("Koide's 2/3 is a clue. Any future theoretical extension must")
    print("explain why this specific quadratic combination of √m equals")
    print("2/3. This is among the deepest open problems in particle physics.")
    print()
    print("The model offers framing (m² ∝ κ, stress-loaded vertex) but no")
    print("numerical prediction. Same as SM, neither better nor worse.")


if __name__ == "__main__":
    main()
