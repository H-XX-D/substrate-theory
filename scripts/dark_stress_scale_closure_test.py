#!/usr/bin/env python3
"""Report dark-stress coherence length and speed closure."""

from __future__ import annotations

from stiff_medium.dark_stress_scale_closure import (
    assess_dark_stress_scale_closure,
    hubble_length_kpc,
)


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    assessment = assess_dark_stress_scale_closure()

    banner("DARK-STRESS SCALE CLOSURE")
    print(f"Hubble length c/H0 = {hubble_length_kpc():.3e} kpc")

    coherence = assessment.coherence
    print("\nCoherence length:")
    print(f"  formula: {coherence.formula}")
    print(f"  ell_pol = {coherence.ell_pol_kpc:.6f} kpc")
    print(f"  mechanism: {coherence.mechanism}")
    print(f"  verdict: {coherence.verdict}")

    speed = assessment.speed
    print("\nDark-stress speed:")
    print(f"  formula: {speed.formula}")
    print(f"  v_dark = {speed.v_dark_km_s:.6f} km/s")
    print(f"  mechanism: {speed.mechanism}")
    print(f"  verdict: {speed.verdict}")

    print("\nMemory result:")
    print(f"  tau_clock = {assessment.tau_clock_myr:.6f} Myr")
    print(f"  tau_pol = {assessment.tau_pol_myr:.6f} Myr")
    print(f"  required = {assessment.required_tau_myr:.6f} Myr")
    print(f"  error = {assessment.tau_error_pct:+.3f}%")

    banner("OVERALL")
    print(assessment.verdict)


if __name__ == "__main__":
    main()
