"""Driver for src/stiff_medium/substrate_planck_scale.py.

Tests whether the substrate's saturation barrier σ_max = 1/2 sets the
Planck length WITHOUT using G as input. The honest answer (per §18.61.6)
is no — σ̃ = σ_SI/(K ξ²) = σ_lat ≈ 0.51 at every scale, so saturation
is not a UV barrier to be hit but a scale-invariant fact about the
substrate's string tension.

Usage:
    python scripts/substrate_planck_scale_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from stiff_medium.substrate_planck_scale import (  # noqa: E402
    L_PLANCK_OBS,
    M_E_SI,
    M_PLANCK_OBS,
    SIGMA_LAT,
    SIGMA_MAX,
    XI_E,
    assess,
    check_scale_invariance,
    planck_candidates,
    report,
)


def banner(s: str) -> None:
    print()
    print("=" * 78)
    print(s)
    print("=" * 78)


def main() -> None:
    banner("SUBSTRATE PLANCK SCALE — does σ_max = 1/2 set l_Planck?  (§18.61.6)")
    print(f"  ξ_e (Compton)       = {XI_E:.4e} m")
    print(f"  l_Planck (uses G)    = {L_PLANCK_OBS:.4e} m")
    print(f"  ratio l_P / ξ_e      = {L_PLANCK_OBS / XI_E:.3e}")
    print(f"  m_e / M_Planck       = {M_E_SI / M_PLANCK_OBS:.3e}  (= l_P/ξ_e by tautology)")
    print()
    print(f"  σ_max  = {SIGMA_MAX}    (§18.39 elastic limit)")
    print(f"  σ_lat  = {SIGMA_LAT}    (3D relaxation lattice)")
    print(f"  Δ       = {abs(SIGMA_LAT - SIGMA_MAX):.3f}  (≈ 2 %)")
    print()

    banner("Step 1 — Verify σ_SI/(K ξ²) = σ_lat is scale-invariant")
    inv = check_scale_invariance()
    print(f"  Tested ξ values: {inv.xi_test}")
    for xi, sd in zip(inv.xi_test, inv.sigma_dimless):
        print(f"    ξ = {xi:.2e} m  ⇒  σ̃ = {sd:.10f}")
    print(f"  max relative deviation from σ_lat: {inv.max_deviation_from_sigma_lat:.3e}")
    print()
    print("  ⇒", inv.statement)
    print()

    banner("Step 2 — Substrate-only candidates for l_Planck")
    cands = planck_candidates()
    print(f"  {'Name':<32s} {'Value [m]':>14s} {'log10(ratio)':>14s}  Verdict")
    print("  " + "-" * 76)
    for c in cands:
        marker = " (G!)" if c.uses_G else ""
        print(f"  {c.name:<32s} {c.value_m:>14.3e} {c.log10_ratio:>14.2f}  {c.verdict}{marker}")
    print()

    banner("Step 3 — Honest assessment")
    a = assess()
    print(f"  Substrate primitives + σ_max alone fix the Planck scale:  {a.sets_planck_scale}")
    print(f"  observed l_Planck              = {a.observed_l_Planck:.4e} m  (uses G)")
    print(f"  best substrate-only length     = {a.best_substrate_only_length:.4e} m")
    print(f"  ratio                           = {a.best_ratio:.4e}")
    print()
    print("  KEY FINDING:")
    sentences = a.key_finding.split(". ")
    for s in sentences:
        s = s.strip()
        if s:
            print(f"    {s}.")
    print()
    print("  WHAT WOULD BE NEEDED:")
    for n in a.what_would_be_needed:
        print(f"    • {n}")
    print()

    banner("Full report")
    print(report())


if __name__ == "__main__":
    main()
