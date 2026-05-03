#!/usr/bin/env python3
"""Report cluster dynamics implied by the dark-stress closures."""

from __future__ import annotations

from stiff_medium.dark_stress_cluster_dynamics import assess_cluster_dynamics


def main() -> None:
    result = assess_cluster_dynamics()

    print("DARK-STRESS CLUSTER DYNAMICS")
    print(f"Omega_dark/Omega_b = {result.dark_to_baryon:.6f}")
    print(f"f_mobile = {result.mobile_fraction_of_dark:.6f}")
    print(f"f_locked = {result.locked_fraction_of_dark:.6f}")
    print(f"mobile/baryon = {result.mobile_to_baryon:.6f}")
    print(f"locked/baryon = {result.locked_to_baryon:.6f}")
    print(
        "mobile fraction of total lensing = "
        f"{result.mobile_fraction_of_total_lensing:.6f}"
    )
    print(
        "mobile peak / gas+locked peak = "
        f"{result.mobile_peak_to_gas_locked_ratio:.6f}"
    )

    print("\nOffset and memory:")
    print(f"tau_pol = {result.tau_pol_myr:.6f} Myr")
    print(f"target offset = {result.target_offset_kpc:.6f} kpc")
    print(f"predicted memory offset = {result.predicted_memory_offset_kpc:.6f} kpc")
    print(f"offset error = {result.offset_error_pct:+.3f}%")
    print(f"centroid offset if gas+locked stay central = {result.centroid_offset_kpc:.6f} kpc")

    print("\nCausal dark-stress horizon:")
    print(f"ell_pol = {result.ell_pol_kpc:.6f} kpc")
    print(f"v_dark = {result.v_dark_km_s:.6f} km/s")
    print(f"stress horizon during tau_pol = {result.stress_horizon_kpc:.6f} kpc")
    print(
        "stress horizon / collision offset = "
        f"{result.stress_horizon_fraction_of_offset:.6f}"
    )
    print(f"coherence steps during memory = {result.coherence_steps_during_memory:.6f}")
    print(f"collision coherence steps = {result.collision_coherence_steps:.6f}")
    print(f"polarization alone spans offset = {result.polarization_alone_spans_offset}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
