#!/usr/bin/env python3
"""Report whether pure substrate polarization can replace dark matter."""

from __future__ import annotations

from stiff_medium.substrate_polarization_dm import assess_pure_polarization


def banner(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    assessment = assess_pure_polarization()

    banner("PURE SUBSTRATE POLARIZATION AS DARK-MATTER REPLACEMENT")
    print(f"a0 = c H0/(2pi) = {assessment.a0_m_s2:.3e} m/s^2")

    banner("1. GALAXY ROTATION")
    rot = assessment.rotation
    print(f"Baryonic mass: {rot.baryonic_mass_msun:.3e} Msun")
    print(f"BTFR asymptotic velocity: {rot.btfr_velocity_km_s:.2f} km/s")
    for r, v in zip(rot.radii_kpc, rot.velocities_km_s):
        print(f"  r={r:6.1f} kpc  v={v:8.2f} km/s")
    print(f"Flatness fraction: {rot.flatness_fraction:.3f}")
    print(f"M_eff/M_b at outer radius: {rot.mass_ratio_at_outer_radius:.2f}")
    print(f"Verdict: {rot.verdict}")

    banner("2. SOLAR-SYSTEM SHUTOFF")
    solar = assessment.solar_system
    print(f"g_N(1 AU) = {solar.g_newton:.3e} m/s^2")
    print(f"fractional excess = {solar.fractional_excess:.3e}")
    print(f"Verdict: {solar.verdict}")

    banner("3. CLUSTER MASS/LIGHT SEPARATION")
    cluster = assessment.cluster
    print(f"Offset target: {cluster.offset_kpc:.1f} kpc")
    print(f"Collision speed: {cluster.collision_speed_km_s:.0f} km/s")
    print(f"Required polarization memory: {cluster.required_memory_myr:.2f} Myr")
    print(f"Instantaneous local polarization passes: {cluster.instantaneous_local_passes}")
    print(f"Memory becomes dark stress component: {cluster.memory_turns_into_dark_stress}")
    print(f"Verdict: {cluster.verdict}")

    banner("OVERALL")
    print(f"Strict no-DM passes: {assessment.strict_no_dm_passes}")
    print(f"Hybrid required: {assessment.hybrid_required}")
    print(f"Verdict: {assessment.verdict}")


if __name__ == "__main__":
    main()
