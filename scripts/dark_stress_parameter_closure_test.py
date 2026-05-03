#!/usr/bin/env python3
"""Report compact parameter closures for the hybrid dark-stress sector."""

from __future__ import annotations

from stiff_medium.dark_stress_parameter_closure import assess_dark_stress_parameter_closure


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    assessment = assess_dark_stress_parameter_closure()

    banner("DARK-STRESS PARAMETER CLOSURE")

    abundance = assessment.abundance
    print("Abundance:")
    print(f"  formula: {abundance.formula}")
    print(f"  predicted Omega_dark/Omega_b = {abundance.predicted_dark_to_baryon:.6f}")
    print(f"  target    Omega_dark/Omega_b = {abundance.observed_dark_to_baryon:.6f}")
    print(f"  error = {abundance.error_pct:+.3f}%")
    print(f"  verdict: {abundance.verdict}")

    mobile = assessment.mobile_fraction
    print("\nMobile/locked split:")
    print(f"  formula: {mobile.formula}")
    print(f"  f_mobile = {mobile.mobile_fraction:.6f}")
    print(f"  f_locked = {mobile.locked_fraction:.6f}")
    print(f"  minimum required = {mobile.minimum_required_mobile_fraction:.6f}")
    print(f"  margin = {mobile.margin:+.6f}")
    print(f"  verdict: {mobile.verdict}")

    memory = assessment.memory_time
    print("\nPolarization memory:")
    print(f"  formula: {memory.formula}")
    print(f"  predicted tau_pol = {memory.predicted_tau_myr:.3f} Myr")
    print(f"  required  tau_pol = {memory.required_tau_myr:.3f} Myr")
    print(f"  error = {memory.error_pct:+.3f}%")
    print(f"  verdict: {memory.verdict}")

    halo = assessment.halo_radius
    print("\nHalo radius/self-interaction:")
    print(f"  formula: {halo.formula}")
    print(f"  R_halo = {halo.radius_fm:.3f} fm")
    print(f"  sigma/m = {halo.sigma_over_m_cm2_g:.3e} cm^2/g")
    print(f"  verdict: {halo.verdict}")

    banner("OVERALL")
    print(assessment.verdict)


if __name__ == "__main__":
    main()
