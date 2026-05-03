#!/usr/bin/env python3
"""Report small-integer degeneracy in dark-stress scale closure."""

from __future__ import annotations

from stiff_medium.dark_stress_factor_scan import (
    assess_factor_scan,
    is_physical_candidate,
    scan_factor_candidates,
)


def format_candidate(prefix: str, candidate) -> str:
    return (
        f"{prefix}: ell=alpha^{candidate.ell_power}(c/H0)/sqrt({candidate.ell_projection}), "
        f"v=alpha^{candidate.speed_power}c/sqrt({candidate.shear_modes}), "
        f"ell_pol={candidate.ell_pol_kpc:.6f} kpc, "
        f"v_dark={candidate.v_dark_km_s:.6f} km/s, "
        f"tau_pol={candidate.tau_pol_myr:.6f} Myr, "
        f"error={candidate.tau_error_pct:+.3f}%"
    )


def main() -> None:
    assessment = assess_factor_scan()
    candidates = scan_factor_candidates()
    physical = [item for item in candidates if is_physical_candidate(item)]

    print("DARK-STRESS FACTOR SCAN")
    print(f"total candidates: {assessment.total_candidates}")
    print(f"physical candidates: {assessment.physical_candidates}")
    print(f"subpercent tau candidates: {assessment.subpercent_tau_candidates}")
    print(
        "physical subpercent tau candidates: "
        f"{assessment.physical_subpercent_tau_candidates}"
    )

    print("\nBest combined-memory candidates:")
    for item in candidates[:5]:
        print("  " + format_candidate("candidate", item))

    print("\nBest physical candidates:")
    for item in physical[:5]:
        print("  " + format_candidate("candidate", item))

    print("\nVerdict:")
    print(assessment.verdict)


if __name__ == "__main__":
    main()
