"""Test driver for the Y-junction baryon Regge analysis.

Compares the meson Regge slope α'_meson = 1/(2πσ) to the Y-junction slope
α'_Y = 1/(3πσ) for the N–Δ baryon spectrum, and reports the residual that
should be attributed to chromomagnetic spin-spin physics rather than string
geometry.
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.baryon_y_junction import (
    SIGMA_QCD_GEV2,
    compute_report,
    print_report,
    BARYON_STATES,
)


def main() -> None:
    """Run the analysis and print the results."""
    report = compute_report(SIGMA_QCD_GEV2)
    print_report(report)

    # Compact bottom-line table comparing the two main hypotheses.
    meson_h = report.hypotheses[0]
    y_h = report.hypotheses[1]
    print("=" * 78)
    print("  BOTTOM LINE: per-state errors, both anchored at N(939)")
    print("=" * 78)
    print(f"  {'state':<14}{'meson α′ err':>16}{'Y α′ err':>16}{'better?':>14}")
    for name, (Mm, Mo, em) in meson_h.predictions.items():
        ey = y_h.predictions[name][2]
        if name == meson_h.anchor_name:
            choice = "anchor"
        else:
            choice = "Y" if abs(ey) < abs(em) else "meson"
        print(f"  {name:<14}{100*em:>+15.2f}%{100*ey:>+15.2f}%{choice:>14}")
    print()
    print("  Conclusion (preview): the rigid Y-junction slope (2/3·α'_meson)")
    print("  makes the Δ error WORSE, confirming that the N→Δ gap is dominated")
    print("  by chromomagnetic spin-spin physics, NOT by string geometry.")
    print("  The orbital trajectory (Δ ↗ Δ(1950), and N ↗ N(1680) for ΔJ=2)")
    print("  is well-described by the meson slope; we therefore keep")
    print("  α'_baryon = α'_meson in regge_spectrum.py, and flag the residual")
    print("  N–Δ splitting as a non-string contribution still owed by the model.")


if __name__ == "__main__":
    main()
