"""Cyclic cosmology timescales — §18.43.

Computes the characteristic timescales for the two end-states:
- End-state A (Saturation): matter accumulating into BHs that merge over cosmic time
- End-state B (Dissipation): Hawking evaporation, then quantum fluctuation nucleation

These set the period of cosmic cycles in our model.
"""

import numpy as np


# Constants
G = 6.674e-11
c = 2.998e8
hbar = 1.055e-34
k_B = 1.381e-23
M_sun = 1.989e30
year_sec = 3.156e7

# Universe parameters
H0_per_s = 2.27e-18  # ≈ 70 km/s/Mpc
age_universe_yr = 13.8e9  # current age


def hawking_evaporation_time(M_kg):
    """Time for a Schwarzschild BH of mass M to evaporate via Hawking radiation.
    t_evap ≈ 5120 π G² M³ / (ℏ c⁴)"""
    return 5120 * np.pi * G**2 * M_kg**3 / (hbar * c**4)


def main():
    print("=" * 70)
    print("§18.43 CYCLIC COSMOLOGY — END-STATE TIMESCALES")
    print("=" * 70)
    print()

    print("END-STATE A: All matter accumulates into supermassive black holes")
    print("-" * 70)
    print()
    print("Stages:")
    print("1. Stars exhaust nuclear fuel (~10¹⁴ years for low-mass stars)")
    print("2. Galactic dynamics collapse stellar remnants into central BHs")
    print("3. Galactic mergers combine SMBHs (current observable timescale)")
    print("4. Eventually one universe-spanning saturated region remains")
    print()
    print("Stellar lifetime estimates:")
    print(f"  Sun-like (1 M⊙): ~10¹⁰ years")
    print(f"  Red dwarfs (0.1 M⊙): ~10¹³-10¹⁴ years")
    print(f"  Smallest fusing star: ~10¹⁴ years")
    print()

    print()
    print("END-STATE B: Matter dissipates, BHs evaporate, equalized ground state")
    print("-" * 70)
    print()

    # Hawking evaporation times
    print(f"{'BH type':>20} | {'Mass (kg)':>14} | {'Evap time (years)':>22}")
    print("-" * 65)
    for label, M in [
        ("Stellar BH (3 M⊙)", 3 * M_sun),
        ("Sgr A* (4M⊙×10⁶)", 4e6 * M_sun),
        ("M87 (6.5×10⁹ M⊙)", 6.5e9 * M_sun),
        ("Universe horizon BH", 1e53),
    ]:
        t_evap = hawking_evaporation_time(M) / year_sec
        print(f"{label:>20} | {M:>14.4e} | {t_evap:>22.4e}")

    print()
    print("After all BHs evaporate, universe enters 'heat death' state.")
    print("Next phase: stochastic nucleation of high-strain regions.")
    print()

    # Stochastic nucleation timescale (very rough)
    # Boltzmann factor for fluctuating to saturation-strain region
    # Action S/ℏ for nucleating a region of size r at strain σ_max:
    # Roughly S ~ K × σ_max² × r⁴ / ℏ
    # For minimum viable size ~ Hubble radius: r_H ~ c/H
    K_Planck = c**7 / (hbar * G**2)
    r_min = 1e-15  # minimum nucleation scale (rough; could be Planck or larger)
    sigma_max = 0.5
    S_per_hbar_min = K_Planck * sigma_max**2 * r_min**4 / hbar

    print(f"Quantum nucleation: probability ∝ exp(-S/ℏ)")
    print(f"  Minimum action for saturated region of radius {r_min:.2e} m:")
    print(f"  S/ℏ ≈ {S_per_hbar_min:.4e}")
    print()
    print(f"  Even with this minimal estimate, S/ℏ is enormous → nucleation")
    print(f"  rate is extremely low. Typical timescale: t_nuc ~ exp(S/ℏ) × t_Planck")
    print()

    if S_per_hbar_min < 700:  # numerically representable
        rate_factor = np.exp(S_per_hbar_min)
        t_planck = np.sqrt(hbar * G / c**5)
        t_nuc = rate_factor * t_planck
        print(f"  Estimated nucleation time: {t_nuc:.4e} s = {t_nuc/year_sec:.4e} years")
    else:
        print(f"  S/ℏ too large to compute explicitly — but timescale dwarfs all")
        print(f"  other cosmic timescales by exp(S/ℏ).")

    print()
    print("=" * 70)
    print("CYCLE LENGTH ESTIMATE")
    print("=" * 70)
    print()

    universe_horizon_evap_years = hawking_evaporation_time(1e53) / year_sec
    print(f"Total cycle time (matter → saturation/dissipation → restart):")
    print(f"  Stellar lifetime stage: ~10¹⁴ years")
    print(f"  BH formation/merger stage: ~10²⁰-10⁴⁰ years")
    print(f"  Hawking evaporation stage: up to {universe_horizon_evap_years:.2e} years")
    print(f"  Quantum nucleation stage: vastly longer (or instant if End-state A)")
    print()
    print(f"Conclusion: a full cycle takes 10¹⁰⁰+ years (End-state B path)")
    print(f"or <<10⁴⁰ years (End-state A path, if matter accumulates faster than evaporation).")
    print()
    print(f"Current universe age: {age_universe_yr:.2e} years")
    print(f"  (We're VERY early in the current cycle — matter still organized into stars/galaxies.)")
    print()

    print("=" * 70)
    print("STRUCTURAL PREDICTION")
    print("=" * 70)
    print()
    print("Each cycle is initialized from the same medium-saturated state.")
    print("The substrate parameters (K, ρ, ξ, ...) are constant across cycles.")
    print("Each cycle's specific matter content depends on initial fluctuations.")
    print()
    print("This explains the 'why these constants?' question: they are NOT")
    print("randomly chosen for our universe. They are PROPERTIES OF THE MEDIUM,")
    print("which persists across all cycles. Anthropic selection isn't needed —")
    print("each cycle has the same physics.")


if __name__ == "__main__":
    main()
