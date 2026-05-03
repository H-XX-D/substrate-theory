#!/usr/bin/env python3
"""Report the finite-speed dark-stress transport consistency check."""

from __future__ import annotations

from stiff_medium.dark_stress_transport import assess_transport_profiles


def main() -> None:
    result = assess_transport_profiles()

    print("DARK-STRESS TRANSPORT")
    print(f"baryon mass = {result.baryon_mass:.6f}")
    print(f"mobile mass = {result.mobile_mass:.6f}")
    print(f"locked polarization mass = {result.locked_mass:.6f}")
    print(f"total lensing mass = {result.total_lensing_mass:.6f}")

    print("\nPeak locations:")
    print(f"baryon peak = {result.baryon_peak_kpc:.3f} kpc")
    print(f"polarization peak = {result.polarization_peak_kpc:.3f} kpc")
    print(f"mobile peak = {result.mobile_peak_kpc:.3f} kpc")
    print(f"total lensing peak = {result.total_peak_kpc:.3f} kpc")
    print(f"total peak offset error = {result.total_peak_offset_error_kpc:+.3f} kpc")

    print("\nPeak contrast:")
    print(f"central total density = {result.central_total_density:.6e}")
    print(f"mobile peak total density = {result.mobile_peak_total_density:.6e}")
    print(
        "mobile/central total density = "
        f"{result.mobile_to_central_peak_ratio:.6f}"
    )
    print(
        "polarization density at mobile peak = "
        f"{result.polarization_density_at_mobile_peak:.6e}"
    )
    print(
        "polarization leakage outside horizon = "
        f"{result.polarization_leakage_fraction:.3e}"
    )

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
