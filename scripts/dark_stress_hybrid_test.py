#!/usr/bin/env python3
"""Report the neutral-kink / polarization hybrid dark-stress test."""

from __future__ import annotations

from stiff_medium.dark_stress_hybrid import assess_hybrid_dark_stress


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    assessment = assess_hybrid_dark_stress()

    banner("HYBRID DARK SUBSTRATE STRESS")
    eq = assessment.equations
    print(eq.poisson)
    print(eq.kink_continuity)
    print(eq.polarization_relaxation)
    print(eq.quasi_static_closure)

    banner("1. GALAXY DECOMPOSITION")
    galaxy = assessment.galaxy
    print(f"Rotation verdict: {galaxy.rotation_verdict}")
    print(f"Outer effective dark/baryon: {galaxy.outer_effective_dark_to_baryon:.3f}")
    print(f"Outer mobile kink/baryon: {galaxy.outer_mobile_to_baryon:.3f}")
    print(f"Outer polarization/baryon: {galaxy.outer_polarization_to_baryon:.3f}")
    print(
        "Outer mobile fraction of total lensing: "
        f"{galaxy.outer_mobile_fraction_of_total_lensing:.3f}"
    )
    print(f"Verdict: {galaxy.verdict}")

    banner("2. CLUSTER SEPARATION")
    cluster = assessment.cluster
    print(f"Cosmic dark/baryon used: {cluster.cosmic_dark_to_baryon:.3f}")
    print(f"Mobile fraction of dark stress: {cluster.mobile_fraction_of_dark:.3f}")
    print(
        "Minimum mobile fraction of dark stress for lensing dominance: "
        f"{cluster.minimum_mobile_fraction_of_dark:.3f}"
    )
    print(
        "Mobile fraction of total lensing mass: "
        f"{cluster.mobile_fraction_of_total_lensing:.3f}"
    )
    print(f"Required memory: {cluster.required_memory_myr:.2f} Myr")
    print(f"Polarization memory: {cluster.polarization_memory_myr:.2f} Myr")
    print(f"Memory-supported offset: {cluster.memory_offset_kpc:.1f} kpc")
    print(f"Passes mobile lensing: {cluster.passes_mobile_lensing}")
    print(f"Passes memory offset: {cluster.passes_memory_offset}")
    print(f"Verdict: {cluster.verdict}")

    banner("3. SELF-INTERACTION")
    sidm = assessment.self_interaction
    print(f"R = {sidm.radius_fm:.3f} fm")
    print(f"M = {sidm.mass_gev:.3f} GeV")
    print(f"sigma/m = {sidm.sigma_over_m_cm2_g:.3e} cm^2/g")
    print(f"Verdict: {sidm.verdict}")

    banner("OVERALL")
    print(f"Strict no-DM: {assessment.strict_no_dm}")
    print(f"Fundamental WIMP needed: {assessment.fundamental_wimp_needed}")
    print(f"Substrate dark stress needed: {assessment.substrate_dark_stress_needed}")
    print(f"Verdict: {assessment.verdict}")


if __name__ == "__main__":
    main()
