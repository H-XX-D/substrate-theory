#!/usr/bin/env python3
"""Report the neutral-coupling stiffness needed for v_dark."""

from __future__ import annotations

from stiff_medium.neutral_coupling_suppression import (
    assess_neutral_coupling_suppression,
)


def main() -> None:
    result = assess_neutral_coupling_suppression()

    print("NEUTRAL-COUPLING SUPPRESSION")
    print(f"mode count = {result.mode_count}")
    print(f"target v_dark = {result.target_speed_km_s:.6f} km/s")
    print(f"required K_eff/K = {result.required_stiffness_ratio:.12e}")
    print(f"alpha^2 = {result.alpha_squared:.12e}")
    print(f"stiffness error = {result.stiffness_error_pct:+.3e}%")

    print("\nCandidates:")
    for candidate in result.candidates:
        print(f"  {candidate.name}")
        print(f"    K_eff/K = {candidate.stiffness_ratio:.12e}")
        print(f"    speed = {candidate.speed_km_s:.6f} km/s")
        print(f"    error = {candidate.speed_error_pct:+.3f}%")
        print(f"    verdict = {candidate.verdict}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
