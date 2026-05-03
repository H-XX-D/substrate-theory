#!/usr/bin/env python3
"""Report memory-clock trials for hybrid dark substrate stress."""

from __future__ import annotations

from stiff_medium.dark_stress_memory_clock import assess_memory_clock


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    assessment = assess_memory_clock()

    banner("DARK-STRESS MEMORY CLOCK")
    print(f"N_relax = 4*pi^2 + 3*pi = {assessment.relaxation_count:.6f}")

    c = assessment.coherence_clock
    print("\nCoherence-crossing clock:")
    print(f"  ell_pol = {c.ell_pol_kpc:.3f} kpc")
    print(f"  v_dark = {c.velocity_km_s:.1f} km/s")
    print(f"  tau_clock = {c.tau_clock_myr:.6f} Myr")
    print(f"  tau_pol = {c.tau_pol_myr:.3f} Myr")
    print(f"  required = {c.required_tau_myr:.3f} Myr")
    print(f"  error = {c.error_pct:+.3f}%")
    print(f"  verdict: {c.verdict}")

    s = assessment.self_interaction_clock
    print("\nSelf-interaction mean-free clock:")
    print(f"  rho = {s.density_kg_m3:.3e} kg/m^3")
    print(f"  sigma/m = {s.sigma_over_m_m2_kg:.3e} m^2/kg")
    print(f"  tau_clock = {s.tau_clock_myr:.3e} Myr")
    print(f"  tau_pol = {s.tau_pol_myr:.3e} Myr")
    print(f"  density for tau_required = {s.density_required_kg_m3:.3e} kg/m^3")
    print(f"  density for tau_required = {s.density_required_msun_kpc3:.3e} Msun/kpc^3")
    print(f"  verdict: {s.verdict}")

    f = assessment.free_fall_clock
    print("\nFree-fall/dynamical clock:")
    print(f"  trial density = {f.density_kg_m3:.3e} kg/m^3")
    print(f"  t_ff = {f.tau_ff_myr:.3f} Myr")
    print(f"  required density = {f.required_density_kg_m3:.3e} kg/m^3")
    print(f"  required density = {f.required_density_msun_kpc3:.3e} Msun/kpc^3")
    print(f"  verdict: {f.verdict}")

    banner("OVERALL")
    print(assessment.verdict)


if __name__ == "__main__":
    main()
