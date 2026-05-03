"""Hadron spectrum from substrate σ via Regge trajectories.

This script takes the substrate-derived string tension σ = 0.18 GeV² (which
came from the running K(ξ) anchored at the electron Compton scale) and
populates the Regge trajectories to predict masses of:

  - Light mesons (π, ρ, a₂, ρ₃, a₄)
  - Strange mesons (K, K*, K₂*, K₃*)
  - ss-bar mesons (φ, f'_2)
  - Light baryons (N, Δ, N*, Δ*)
  - Strange baryons (Λ family)
  - Glueballs (0++, 2++, 0-+)

Each channel is anchored to ONE measured mass; all others are predictions.
The substrate model has NO free parameters in this test — σ is fixed by
the K(ξ) running and the slope is α' = 1/(2π σ) by Nambu-Goto.

Run:  PYTHONPATH=src python3 scripts/regge_spectrum_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stiff_medium.regge_spectrum import (
    SIGMA_QCD_GEV2,
    HADRON_DATA,
    compute_regge_summary,
    print_summary,
)


def main() -> None:
    """Run the full Regge analysis and print results."""
    print()
    print("=" * 70)
    print("HADRON SPECTRUM FROM SUBSTRATE STIFFNESS K(ξ)")
    print("=" * 70)
    print()
    print("Substrate inputs (from substrate_rg_running.py):")
    print(f"  σ at QCD scale:  {SIGMA_QCD_GEV2:.4f} GeV²")
    print(f"  K(ξ_QCD) running: K(ξ) = K_e (ξ_e/ξ)^5.69")
    print(f"  σ_QCD comes from K(ξ_QCD) via σ = σ_lat × K_QCD")
    print()
    print("Each trajectory is fitted with ONE anchor and predicts the rest.")
    print("Errors quoted as (M_pred − M_PDG)/M_PDG.")
    print()

    # Light meson trajectory
    summary = compute_regge_summary(sigma_GeV2=SIGMA_QCD_GEV2)
    print_summary(summary)

    # Aggregate quality
    print("=" * 70)
    print("AGGREGATE FIT QUALITY")
    print("=" * 70)

    all_predictions: list[tuple[str, float, float, float]] = []
    for fit in [summary.light_mesons, summary.strange_mesons,
                summary.baryons_light, summary.glueballs]:
        for name, (M_pred, M_obs, err) in fit.residuals.items():
            if name == fit.anchor_name:
                continue   # don't count anchor in aggregate
            if M_pred > 0:
                all_predictions.append((name, M_pred, M_obs, err))

    if all_predictions:
        n = len(all_predictions)
        abs_errs = [abs(err) for _, _, _, err in all_predictions]
        mean_err = sum(abs_errs) / n
        max_err = max(abs_errs)
        # RMS
        rms_err = (sum(e ** 2 for e in abs_errs) / n) ** 0.5

        print(f"  Number of non-anchor predictions: {n}")
        print(f"  Mean |fractional error|:          {100*mean_err:.2f}%")
        print(f"  RMS  fractional error:            {100*rms_err:.2f}%")
        print(f"  Max  |fractional error|:          {100*max_err:.2f}%")
        print()
        print("  Predictions sorted by error:")
        for name, M_pred, M_obs, err in sorted(all_predictions, key=lambda t: abs(t[3])):
            print(f"    {name:<20} {M_pred:>8.1f} vs {M_obs:>8.1f}  err = {100*err:+6.1f}%")

    # Sensitivity to σ
    print()
    print("=" * 70)
    print("SENSITIVITY TO σ (substrate input)")
    print("=" * 70)
    print()
    print("If σ shifts by ±5%, how much do the predictions move?")
    print()
    print(f"  {'σ [GeV²]':<10} {'ρ_anchor':<12} {'a2 pred':<10} {'N anchor':<10} {'Δ pred':<10}")
    for delta in [-0.05, 0.0, +0.05]:
        sigma_test = SIGMA_QCD_GEV2 * (1 + delta)
        s = compute_regge_summary(sigma_GeV2=sigma_test)
        rho = s.light_mesons.residuals.get("ρ(770)", (0,0,0))
        a2 = s.light_mesons.residuals.get("a2(1320)", (0,0,0))
        N = s.baryons_light.residuals.get("N(939)", (0,0,0))
        D = s.baryons_light.residuals.get("Δ(1232)", (0,0,0))
        print(f"  {sigma_test:.4f}     {rho[0]:>8.1f}     {a2[0]:>8.1f}   {N[0]:>8.1f}   {D[0]:>8.1f}")
    print()

    print("=" * 70)
    print("SUBSTRATE-PHYSICS BOTTOM LINE")
    print("=" * 70)
    print()
    print("This entire spectrum follows from ONE substrate input: the")
    print("running stiffness K(ξ) anchored at the electron Compton scale.")
    print("That single input + Nambu-Goto Regge dynamics fixes:")
    print(f"  • α' = 1/(2π σ) = {summary.alpha_prime_open:.4f} GeV⁻² (open string)")
    print(f"  • All meson and baryon mass ratios on each trajectory")
    print(f"  • The closed-string-to-open-string ratio of ½ -> glueballs")
    print()
    print("Free parameters: 1 anchor per trajectory (4 anchors total).")
    print("Predicted masses: ~15 hadrons.")


if __name__ == "__main__":
    main()
