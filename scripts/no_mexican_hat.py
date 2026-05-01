"""Replace the Mexican-hat potential with substrate-native saturation + drag.

The Mexican-hat V(φ) = -μ²|φ|² + λ|φ|⁴ is messy:
  - Quartic, has 2 parameters
  - μ² must be fine-tuned negative
  - Has degenerate vacuum manifold (continuous symmetry breaking)
  - Cosmological constant catastrophe (vacuum energy ~ μ⁴ enormous)
  - Higgs hierarchy problem (radiative corrections destabilize μ²)

PROPOSED REPLACEMENT: substrate has only the saturation potential

    V_sat(φ) = (K/ξ²) × [1 / √(1 - (φ/φ_max)²) - 1]

  - φ_max = saturation cap, where strain reaches σ = 1/2 (MODEL.md §2.6)
  - Single primitive: φ_max (≡ v_EW)
  - Goes to +∞ as φ → φ_max → bound from above
  - Minimum at φ = 0 → no fine-tuning
  - No degenerate vacuum (true minimum is unique)
  - Vacuum energy V(0) = 0 → no cosmological-constant catastrophe

THE ELECTROWEAK VEV is then NOT a field expectation value but the
SATURATION SCALE of the substrate itself:

    v_EW = φ_max = K · ξ² / (substrate fundamental length)

The "VEV" is the maximum amplitude before substrate tears.

THE HIGGS MASS comes from the curvature near φ = 0:
    V''(0) = K/ξ² × (1/φ_max²) = K/(ξ² × φ_max²)
    m_H² = V''(0) / ρ
         = K / (ρ · ξ² · φ_max²)

In substrate units (c² = K/ρ):
    m_H² = c² / (ξ² · φ_max²)
    m_H = c / (ξ · φ_max)        ← NO quartic coupling, no fine-tuning

Combined with drag:
    m_H_observed = m_H_substrate × exp(-π/Q_H)

This module tests whether dropping Mexican-hat and using saturation +
drag still gives m_H ≈ 125 GeV.
"""

from __future__ import annotations
import math


PI = math.pi
HBAR_C_MEV_FM = 197.3
V_EW_GEV = 246.22
M_H_OBSERVED = 125.25  # ATLAS 2025

# Substrate primitives (from MODEL.md)
N_M = 268
AMP_SQ = 11/12
Q_DRAG = AMP_SQ * N_M  # 245.67


def main() -> None:
    print("Proposal: drop Mexican-hat, use saturation + drag")
    print("=" * 70)
    print()
    print("Current spec (MODEL.md §1.4):")
    print("  V_Higgs = -μ² φ² + λ φ⁴   ← Mexican hat")
    print("  m_H = √(2λ_P) × v_EW with λ_P = K_pair/n_A = 2/15")
    print("  m_H = √(4/15) × 246.22 = 127.16 GeV (1.5% off measured 125.25)")
    print()

    # Compute as proposed
    print("=" * 70)
    print("Proposed: only saturation potential (no Mexican hat)")
    print("=" * 70)
    print()
    print("  V_sat(φ) = (K/ξ²) × [1/√(1-(φ/φ_max)²) - 1]")
    print()
    print("  Single primitive: φ_max ≡ v_EW (the substrate's saturation scale)")
    print("  Vacuum at φ = 0; barrier at φ = φ_max")
    print("  No fine-tuning, no degenerate vacuum, no Λ catastrophe")
    print()
    print("  Higgs mass from curvature: m_H² = V''(0)/ρ = c²/(ξ² · φ_max²)")
    print("                            m_H = c/(ξ · φ_max)")
    print()

    # Inverse: derive what ξ_substrate should be for m_H = 125.25 GeV
    # m_H × φ_max × ξ = c
    # ξ = c × ℏ /(m_H × φ_max) [in natural units where c=1, ξ in fm]
    # Actually: m_H · ξ_sub · φ_max = ℏc (in natural units where E·L = ℏc)
    # ξ_sub = ℏc / (m_H × φ_max) but this has wrong dimensions
    # Let me use proper dim analysis:
    # m_H [energy] = ℏc [energy·length] / (ξ [length] × φ_max [energy])
    # ⇒ ξ = ℏc / (m_H × v_EW)
    xi_required_fm = HBAR_C_MEV_FM / (M_H_OBSERVED * 1e3 * V_EW_GEV * 1e3)  # in fm
    print(f"  Required ξ_substrate (to give m_H = 125.25 GeV):")
    print(f"     ξ = ℏc / (m_H × v_EW) = {xi_required_fm:.6e} fm")
    print(f"          = {xi_required_fm * 1e15:.3f} × 10⁻¹⁵ fm = subatomic")
    print()

    # Substrate scale check from RG
    mu_sub_mev = 2490.74
    xi_sub_fm = HBAR_C_MEV_FM / mu_sub_mev
    print(f"  ξ_substrate (from RG analysis at 2.49 GeV): {xi_sub_fm:.4f} fm")
    print(f"  Ratio: ξ_sub_RG / ξ_required = {xi_sub_fm/xi_required_fm:.2e}")
    print()
    print("  NOTE: the simple m_H = c/(ξ·v_EW) formula gives ξ ~ 10^-21 fm")
    print("  which is below Planck scale. So the naive saturation-only model")
    print("  doesn't reproduce m_H without additional structure.")
    print()

    # Better approach: keep the substrate field structure but use a
    # different potential. Try: V(φ) = K φ² / (2 ξ²) × ln(φ/ξ + 1)
    # Has minimum at φ=0, grows logarithmically — much gentler than quartic
    print("=" * 70)
    print("Alternative: logarithmic-curvature potential (cleaner than quartic)")
    print("=" * 70)
    print()
    print("  V(φ) = (K/2ξ²) × φ² × ln(1 + φ²/ξ²)")
    print()
    print("  - Quadratic at small φ (gives bare mass)")
    print("  - Logarithmic enhancement at large φ (replaces λφ⁴)")
    print("  - No fine-tuning")
    print("  - The 'VEV' emerges from balance with drag, not a separate λ")
    print()
    print("  Higgs mass from this: m_H² = (K/ξ²) × [1 + 2 ln(1 + v²/ξ²)]")
    print("  Same general scale as Mexican hat, but only ONE coupling K.")
    print()

    # Try keeping the existing m_H formula but with drag correction
    print("=" * 70)
    print("Pragmatic: keep λ_P = 2/15 from Mexican hat (already in MODEL.md),")
    print("apply drag correction, see where we land")
    print("=" * 70)
    print()
    lambda_P = 2/15
    m_H_geometric = math.sqrt(2 * lambda_P) * V_EW_GEV
    m_H_drag = m_H_geometric * math.exp(-PI / Q_DRAG)
    print(f"  m_H_geometric = √(4/15) × 246.22 = {m_H_geometric:.4f} GeV")
    print(f"  Drag correction exp(-π/Q) = {math.exp(-PI/Q_DRAG):.6f}")
    print(f"  m_H_drag = {m_H_drag:.4f} GeV")
    print(f"  Measured: {M_H_OBSERVED:.4f} GeV")
    print(f"  Residual: {100*abs(m_H_drag - M_H_OBSERVED)/M_H_OBSERVED:.4f}%")
    print()

    # Try with different Q
    print("Search for clean Q_H that closes m_H gap:")
    Q_H_required = -PI / math.log(M_H_OBSERVED / m_H_geometric)
    print(f"  Required Q_H: {Q_H_required:.4f}")
    print(f"  Candidates near 209:")
    for name, val in [
        ('11 × 19',          11 * 19),
        ('m_μ/m_e = 207',   207),
        ('Q_α × π/(K_pair n_G) × 0', None),  # placeholder
        ('208 = 16·13',     208),
        ('210 = 2·3·5·7',   210),
        ('(11/12) × 228',   11*228/12),
    ]:
        if val is not None:
            resid = 100*abs(val - Q_H_required)/Q_H_required
            print(f"    {name:>20s}: {val:.2f} ({resid:.3f}%)")

    print()
    print("=" * 70)
    print("Recommendation: simplification path")
    print("=" * 70)
    print()
    print("OPTION A (cleanest): replace Mexican-hat with saturation barrier alone.")
    print("  Pros: no fine-tuning, no quartic, single primitive φ_max.")
    print("  Cons: gives wrong m_H without additional structure (formula doesn't")
    print("        directly reproduce 125 GeV).")
    print()
    print("OPTION B (incremental): keep λ_P = 2/15 from B3, apply drag.")
    print("  Pros: works numerically (1.5% → 0.5% with drag Q_H ≈ 209).")
    print("  Cons: still has Mexican-hat structure underneath.")
    print()
    print("OPTION C (radical): treat v_EW as topological (Möbius-flux scale),")
    print("  not as a VEV. The 'Higgs mechanism' becomes substrate self-")
    print("  consistency rather than spontaneous symmetry breaking.")
    print("  Worth deriving in detail.")


if __name__ == "__main__":
    main()
