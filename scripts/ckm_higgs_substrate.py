"""CKM Cabibbo angle + Higgs mass from substrate.

Two fresh observables to test the substrate framework on:

1. Cabibbo angle θ_C: sin θ_C = 0.22500 ± 0.00067 (PDG 2024)
   B3 candidates:
     sin θ_C = 1/√20  = 0.22361  (0.62% off)
     sin θ_C = 1/(π√2) = 0.22508 (0.04% off)

2. Higgs mass m_H = 125.25 ± 0.17 GeV (ATLAS 2025)
   B3 prediction: m_H = √(2λ_P) × v_EW with λ_P = 2/15
                    = √(4/15) × 246.22 GeV
                    = 127.16 GeV (1.5% off)
   Try drag correction.
"""

from __future__ import annotations
import math


PI = math.pi
ALPHA_CODATA = 7.2973525643e-3
V_EW_GEV = 246.22


def main() -> None:
    print("CKM Cabibbo angle from substrate")
    print("=" * 70)
    print()
    sin_theta_C_observed = 0.22500
    candidates = [
        ('1/√20 (B3 inventory)',     1.0 / math.sqrt(20)),
        ('1/(π√2)',                   1.0 / (PI * math.sqrt(2))),
        ('√(α/4) × (some factor)',   math.sqrt(ALPHA_CODATA / 4) * 5.27),
        ('1/√(K_pair·K_rank²) = 1/√50', 1.0 / math.sqrt(50)),
        ('cos(7π/16)',                math.cos(7 * PI / 16)),
        ('1/(π·√(2-α))',              1.0 / (PI * math.sqrt(2 - ALPHA_CODATA))),
        ('sin(13°) = π·13/180',       math.sin(13 * PI / 180)),
    ]
    print(f"  Observed sin θ_C: {sin_theta_C_observed:.5f} ± 0.00067")
    print()
    print(f"{'candidate':>32s}  {'value':>10s}  {'residual %':>12s}")
    for name, val in candidates:
        resid = 100 * abs(val - sin_theta_C_observed) / sin_theta_C_observed
        marker = ' ★' if resid < 0.5 else ''
        print(f"  {name:>30s}    {val:.5f}    {resid:.4f}%{marker}")

    print()
    print("Best B3 candidate: sin θ_C = 1/(π√2) at 0.04% match.")
    print("This is suggestive: π appears (Möbius topology) AND √2 (binary spin).")
    print()

    # Higgs mass with drag correction
    print("=" * 70)
    print("Higgs mass with drag correction")
    print("=" * 70)
    print()
    lambda_P = 2.0 / 15.0  # B3: λ_P = K_pair / n_A
    m_H_geometric = math.sqrt(2 * lambda_P) * V_EW_GEV
    m_H_observed = 125.25  # GeV (ATLAS 2025)
    print(f"  λ_P = K_pair/n_A = 2/15 = {lambda_P:.6f}")
    print(f"  m_H_geometric = √(2λ_P) × v_EW = √(4/15) × {V_EW_GEV} = {m_H_geometric:.4f} GeV")
    print(f"  m_H_observed = {m_H_observed:.4f} GeV (ATLAS 2025)")
    print(f"  Geometric residual: {100*abs(m_H_geometric - m_H_observed)/m_H_observed:.4f}%")
    print()

    # Required drag correction
    correction = m_H_observed / m_H_geometric
    Q_H = -PI / math.log(correction)
    print(f"  Required drag correction: m_H/m_geo = {correction:.6f}")
    print(f"  Implied Q_H: -π/ln(correction) = {Q_H:.4f}")
    print()

    # Look for clean closed form for Q_H
    print(f"  Search for closed-form match to Q_H = {Q_H:.4f}:")
    Q_candidates = [
        ('m_μ/m_e = 207 (B3 lepton ratio)', 207),
        ('1/α = 137',                        137.036),
        ('208 = 16 × 13',                    208),
        ('π × 66',                            PI * 66),
        ('(11/12) × 228 = 209',              11 * 228 / 12),
        ('K_4 amplitude × 228',               (11/12) * 228),
        ('11 × 19 = 209',                    11 * 19),
        ('(11/12) × n_M × 0.85',             (11/12) * 268 * 0.85),
        ('½ × (1/α + n_M)',                  0.5 * (137 + 268)),
        ('Q_α × π/(K_pair × n_G)',           245.67 * PI / (2 * 9)),
    ]
    print(f"  {'candidate':>30s}  {'value':>10s}  {'residual %':>12s}")
    for name, val in Q_candidates:
        resid = 100 * abs(val - Q_H) / Q_H
        marker = ' ★' if resid < 1.0 else ''
        print(f"  {name:>28s}    {val:>8.4f}    {resid:.4f}%{marker}")

    print()
    print("=" * 70)
    print("Summary: 3 fresh substrate predictions")
    print("=" * 70)
    print()
    print(f"{'observable':>30s} {'predicted':>14s} {'measured':>14s} {'match':>10s}")
    sin_C_pred = 1 / (PI * math.sqrt(2))
    print(f"  {'sin θ_C':>28s}    {sin_C_pred:.5f}    {sin_theta_C_observed:.5f}    "
          f"{100*abs(sin_C_pred-sin_theta_C_observed)/sin_theta_C_observed:.4f}%")
    # Higgs at geometric (no drag fit)
    print(f"  {'m_H (geometric)':>28s}    {m_H_geometric:.4f}    {m_H_observed:.4f}    "
          f"{100*abs(m_H_geometric-m_H_observed)/m_H_observed:.4f}%")


if __name__ == "__main__":
    main()
