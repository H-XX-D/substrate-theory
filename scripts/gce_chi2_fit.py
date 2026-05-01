"""GCE χ² fit: substrate cube-DM vs standard 30 GeV WIMP.

Uses approximate Daylan-style published binned spectrum (well-known in
the literature) and computes DM annihilation γ-ray spectra for various
masses. Does honest χ² comparison.

DATA: Daylan et al. 2014 (arXiv:1402.6703) Figure 4 binned spectrum
(approximate values, well-established in the field; precise re-fit
would need raw Fermi data).

DM TEMPLATES: parametric γ-ray spectrum from DM annihilation into
quark-antiquark pairs, hadronizing through pion cascade.
"""

from __future__ import annotations
import math
import numpy as np


PI = math.pi


# Approximate Daylan-style GC excess spectrum
# (E in GeV, E²dN/dE in GeV/cm²/s/sr, error in same units)
# Published values, ±20% systematic on overall normalization
GCE_DATA = [
    # (E_GeV, flux, error)
    (0.30,  1.5e-7,  0.4e-7),
    (0.50,  2.5e-7,  0.5e-7),
    (0.70,  3.5e-7,  0.6e-7),
    (1.0,   4.5e-7,  0.6e-7),
    (1.5,   5.5e-7,  0.6e-7),
    (2.0,   5.7e-7,  0.6e-7),  # approximate peak
    (3.0,   5.0e-7,  0.5e-7),
    (5.0,   3.5e-7,  0.4e-7),
    (8.0,   2.0e-7,  0.3e-7),
    (15.0,  0.7e-7,  0.2e-7),
    (25.0,  0.25e-7, 0.1e-7),
]


def dm_annihilation_spectrum(E_gev, M_DM_gev, channel='qq'):
    """Approximate γ-ray spectrum from DM-DM annihilation.

    For DM mass M_DM, channel 'qq' (light quarks) or 'bb' (b-quark):
    Hadronization produces pion cascade; π⁰ → 2γ gives γ-ray flux.

    Parameterization: log-parabola peaked at E_peak = M_DM / R,
    where R depends on channel:
      qq channel (light quarks): R ~ 4 (peak at M/4)
      bb channel (heavy quarks): R ~ 20 (peak at M/20)

    Returns dN/dE in arbitrary units (overall normalization fit later).
    """
    if channel == 'qq':
        E_peak = M_DM_gev / 4.0
        sigma = 0.6  # log-Gaussian width
    elif channel == 'bb':
        E_peak = M_DM_gev / 20.0
        sigma = 0.5
    else:
        raise ValueError(channel)

    # Cutoff at M_DM (kinematic limit)
    if E_gev > M_DM_gev:
        return 0.0

    # Log-Gaussian peak shape (approximation of full hadronization spectrum)
    log_ratio = math.log(E_gev / E_peak)
    return math.exp(-log_ratio**2 / (2 * sigma**2)) / E_gev


def model_flux(E_gev, M_DM_gev, channel, normalization):
    """Predicted E²·dN/dE flux for given DM mass × normalization."""
    spec = dm_annihilation_spectrum(E_gev, M_DM_gev, channel)
    return E_gev**2 * spec * normalization


def chi_squared(M_DM_gev, channel):
    """Compute χ² for DM model vs GCE data, optimizing over normalization."""
    # Fit normalization analytically (linear in N)
    # χ² = Σ ((data_i - N·model_i)/error_i)²
    # ∂/∂N = 0 → N = Σ(data·model/error²) / Σ(model²/error²)
    num = 0.0
    den = 0.0
    for E, flux, err in GCE_DATA:
        m = model_flux(E, M_DM_gev, channel, 1.0)
        num += flux * m / err**2
        den += m * m / err**2
    if den == 0:
        return float('inf'), 0.0
    N_fit = num / den
    chi2 = 0.0
    for E, flux, err in GCE_DATA:
        pred = model_flux(E, M_DM_gev, channel, N_fit)
        chi2 += ((flux - pred) / err)**2
    return chi2, N_fit


def main() -> None:
    print("GCE χ² fit: substrate cube-DM vs standard WIMP")
    print("=" * 70)
    print()
    print("Approximate Daylan-style GC excess spectrum (11 bins, 0.3-25 GeV):")
    print(f"{'E [GeV]':>10s}  {'flux':>14s}  {'error':>12s}")
    for E, flux, err in GCE_DATA:
        print(f"  {E:>8.2f}    {flux:>10.2e}    {err:>10.2e}")
    print()

    # Scan DM mass for both channels
    print("Scanning DM mass (qq̄ channel, light quarks):")
    print(f"  {'M_DM [GeV]':>12s}  {'χ²':>10s}  {'norm':>14s}")
    best_qq = (float('inf'), 0, 0)
    for M in [1.0, 1.5, 1.9, 2.5, 3.5, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0]:
        chi2, N = chi_squared(M, 'qq')
        marker = ' ★' if chi2 < best_qq[0] else ''
        if chi2 < best_qq[0]:
            best_qq = (chi2, M, N)
        print(f"    {M:>10.2f}    {chi2:>8.2f}    {N:>10.4e}{marker}")
    print()
    print(f"  Best qq̄ fit: M_DM = {best_qq[1]:.2f} GeV, χ² = {best_qq[0]:.2f}, "
          f"DOF = {len(GCE_DATA)-1} = {len(GCE_DATA)-1}")
    print(f"  Reduced χ²/DOF = {best_qq[0]/(len(GCE_DATA)-1):.3f}")
    print()

    print("Scanning DM mass (bb̄ channel, heavy quarks — standard WIMP):")
    print(f"  {'M_DM [GeV]':>12s}  {'χ²':>10s}  {'norm':>14s}")
    best_bb = (float('inf'), 0, 0)
    for M in [10.0, 20.0, 30.0, 36.0, 45.0, 50.0, 70.0, 100.0]:
        chi2, N = chi_squared(M, 'bb')
        marker = ' ★' if chi2 < best_bb[0] else ''
        if chi2 < best_bb[0]:
            best_bb = (chi2, M, N)
        print(f"    {M:>10.2f}    {chi2:>8.2f}    {N:>10.4e}{marker}")
    print()
    print(f"  Best bb̄ fit: M_DM = {best_bb[1]:.2f} GeV, χ² = {best_bb[0]:.2f}")
    print(f"  Reduced χ²/DOF = {best_bb[0]/(len(GCE_DATA)-1):.3f}")
    print()

    # Specific test: substrate cube-DM at 1.9 GeV
    chi2_substrate, _ = chi_squared(1.9, 'qq')
    print("=" * 70)
    print("VERDICT: Does substrate cube-DM at 1.9 GeV fit GC excess?")
    print("=" * 70)
    print()
    print(f"  Substrate prediction: M_DM = 1.9 GeV (qq̄ channel)")
    print(f"    χ² = {chi2_substrate:.2f} on 11 bins → reduced χ² = {chi2_substrate/10:.3f}")
    print()
    print(f"  Best-fit qq̄ DM mass: M_DM = {best_qq[1]:.1f} GeV (χ² = {best_qq[0]:.2f})")
    print(f"  Best-fit bb̄ DM mass: M_DM = {best_bb[1]:.1f} GeV (χ² = {best_bb[0]:.2f})")
    print()
    if chi2_substrate / 10 > 5:
        print(f"  ★ HONEST ASSESSMENT: 1.9 GeV is a POOR fit (reduced χ² > 5).")
        print(f"  The GC excess prefers higher DM mass — substrate's simple")
        print(f"  '2 × m_proton' estimate is too low.")
        print()
        print(f"  Substrate cube-DM mass needs revision:")
        print(f"  - Best-fit qq̄ channel: ~{best_qq[1]:.0f} GeV")
        print(f"  - Standard bb̄ channel:  ~{best_bb[1]:.0f} GeV")
        print()
        print(f"  Geometric reasoning to revisit: 8 vertices × constituent quark")
        print(f"  mass (~330 MeV) gives ~2.6 GeV; with binding-enhancement could")
        print(f"  reach 5-10 GeV. Need full QCD-substrate calculation for better")
        print(f"  estimate.")
    else:
        print(f"  ★ 1.9 GeV is a GOOD fit (reduced χ² < 5).")
    print()
    print("=" * 70)
    print("Caveats: this fit uses approximate spectrum (precise binned data")
    print("would need raw Fermi-LAT extraction). DM templates are also")
    print("simplified (full hadronization needs PYTHIA-level simulation).")
    print("Verdict is INDICATIVE not publication-grade.")


if __name__ == "__main__":
    main()
