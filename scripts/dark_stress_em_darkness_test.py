#!/usr/bin/env python3
"""Report EM-darkness gates for hybrid dark substrate stress."""

from __future__ import annotations

from stiff_medium.dark_stress_em_darkness import assess_em_darkness


def main() -> None:
    result = assess_em_darkness()
    heavy = result.heavy_neutral_kink
    coherent = result.coherent_polarization

    print("DARK-STRESS EM DARKNESS")
    print("\nHeavy neutral mobile stress:")
    print(f"  mass = {heavy.mass_gev:.3f} GeV")
    print(f"  halo radius = {heavy.halo_radius_fm:.3f} fm")
    print(f"  Compton wavelength = {heavy.compton_wavelength_fm:.6f} fm")
    print(f"  halo de Broglie wavelength = {heavy.halo_de_broglie_wavelength_fm:.3f} fm")
    print(f"  Compton frequency = {heavy.compton_frequency_hz:.3e} Hz")
    print(f"  shear-mode frequency = {heavy.shear_mode_frequency_hz:.3e} Hz")
    print(f"  shear-mode energy = {heavy.shear_mode_energy_ev:.3e} eV")
    print(f"  EM-dark = {heavy.gate.em_dark}")
    print(f"  reason = {heavy.gate.reason}")

    print("\nCoherent locked polarization:")
    print(f"  coherence length = {coherent.coherence_length_kpc:.6f} kpc")
    print(f"  memory time = {coherent.memory_time_myr:.6f} Myr")
    print(f"  memory frequency = {coherent.memory_frequency_hz:.3e} Hz")
    print(f"  memory quantum energy = {coherent.memory_quantum_energy_ev:.3e} eV")
    print(
        "  light wavelength at memory frequency = "
        f"{coherent.light_wavelength_for_memory_frequency_kpc:.3e} kpc"
    )
    print(f"  EM-dark = {coherent.gate.em_dark}")
    print(f"  reason = {coherent.gate.reason}")

    print("\nOverall:")
    print(f"  ordinary EM detection expected = {result.ordinary_em_detection_expected}")
    print(f"  gravitational detection expected = {result.gravitational_detection_expected}")
    print(f"  verdict = {result.verdict}")


if __name__ == "__main__":
    main()
