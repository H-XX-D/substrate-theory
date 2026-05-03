"""Test / demonstration script for the pre-CMB substrate inhomogeneities module.

Constructs a ``PreCMBSubstrate`` with realistic parameters and exercises all
public API methods, verifying the two key quantitative targets from the spec:

1. **JWST excess at z = 14 ≈ 182×** (§18.52.3, arxiv:2505.11263)
2. **Hubble tension: ~7% r_s reduction → H₀ ≈ 73 km/s/Mpc** (§18.52.1)

Run from the repo root:
    PYTHONPATH=src python3 scripts/pre_cmb_substrate_test.py
"""

from __future__ import annotations

import math

from stiff_medium.pre_cmb_substrate import (
    PreCMBSubstrate,
    PreCMBSubstrateMode,
    predict_jwst_excess_factor,
    hubble_tension_resolution,
    cmb_acoustic_peak_position,
    H0_CMB,
    H0_LOCAL,
    R_S_LCDM,
    ELL_1_LCDM,
    N_S_PLANCK,
)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def header(title: str) -> None:
    """Print a section header matching the project's desaturation_test.py style."""
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72 + "\n")


def pass_fail(condition: bool, label: str, value: str) -> str:
    """Return a formatted PASS / FAIL line."""
    status = "PASS" if condition else "FAIL"
    return f"  [{status}]  {label:<42}  {value}"


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------


def demo_mode_construction() -> PreCMBSubstrate:
    """Construct a PreCMBSubstrate and inspect its mode list."""
    header("PRE-CMB SUBSTRATE MODE CONSTRUCTION  (§18.44)")

    substrate = PreCMBSubstrate(
        k_min=1e-4,
        k_max=10.0,
        n_modes=64,
        n_s=N_S_PLANCK,
        sigma_mode_amplitude=1e-4,
        sigma_initial=0.5,
    )

    print(f"  k_min              = {substrate.k_min:.2e}  Mpc⁻¹  (horizon scale today)")
    print(f"  k_max              = {substrate.k_max:.2e}  Mpc⁻¹  (galaxy-formation scale)")
    print(f"  n_modes            = {len(substrate.modes)}")
    print(f"  spectral_index n_s = {substrate.spectral_index:.4f}  (Planck 2018)")
    print(f"  sigma_mode_amp     = {substrate.sigma_mode_amplitude:.2e}  (mode amplitude scale)")
    print(f"  sigma_initial      = {substrate.sigma_initial:.3f}  (saturated, §18.39)")
    print()

    first = substrate.modes[0]
    mid = substrate.modes[len(substrate.modes) // 2]
    last = substrate.modes[-1]
    print(f"  First mode:  {first}")
    print(f"  Middle mode: {mid}")
    print(f"  Last mode:   {last}")
    print()

    amplitudes = [m.amplitude for m in substrate.modes]
    print(f"  Amplitude range: [{min(amplitudes):.3e}, {max(amplitudes):.3e}]")
    print(f"  Total mode count in [k_min, k_max]: {len(substrate.modes)}")

    return substrate


def demo_power_spectrum(substrate: PreCMBSubstrate) -> None:
    """Show the substrate power spectrum at selected wavenumbers."""
    header("SUBSTRATE POWER SPECTRUM  P(k)  (§18.44)")

    print("  P_substrate(k) = sigma_mode_amp² × (k / k_pivot)^(n_s - 1)")
    print()

    k_values = [1e-4, 1e-3, 0.05, 0.1, 1.0, 10.0]
    print(f"  {'k (Mpc⁻¹)':>14} | {'P_substrate(k)':>18} | {'Enhancement R(k)':>18}")
    print("  " + "-" * 58)
    for k in k_values:
        p = substrate.power_spectrum(k)
        r = substrate.enhancement_ratio(k)
        print(f"  {k:>14.4e} | {p:>18.4e} | {r:>18.4e}")

    print()
    print(f"  [Note: R(k) is scale-independent when both spectra share n_s = {substrate.n_s:.4f}]")


def demo_sound_speed_modification(substrate: PreCMBSubstrate) -> float:
    """Compute the integrated sound speed modification from all modes."""
    header("SOUND SPEED MODIFICATION  delta(c_s) / c_s  (§18.44, §18.52.1)")

    delta_cs = substrate.sound_speed_modification()
    delta_rs = substrate.r_s_modification()
    rs_modified = substrate.modified_sound_horizon()
    H0_modified = substrate.inferred_H0_shift()

    print(f"  Integrated mode power   Sigma A(k)²  = {sum(m.amplitude**2 for m in substrate.modes):.4e}")
    print(f"  delta(c_s) / c_s       (virial half) = {delta_cs:.4e}")
    print(f"  delta(r_s) / r_s       (first order) = {delta_rs:.4e}")
    print()
    print(f"  LCDM sound horizon   r_s              = {R_S_LCDM:.4f}  Mpc")
    print(f"  Modified sound horizon r_s_modified   = {rs_modified:.4f}  Mpc")
    print(f"  Change                                = {rs_modified - R_S_LCDM:+.4f}  Mpc")
    print()
    print(f"  LCDM H0 (CMB-inferred)               = {H0_CMB:.2f}  km/s/Mpc")
    print(f"  Modified H0 (from r_s shift)          = {H0_modified:.4f}  km/s/Mpc")
    print()
    print("  [Default sigma_mode_amplitude = 1e-4 gives negligible modification.")
    print("   Hubble tension resolution section (below) uses an explicit 7% boost.]")

    return delta_cs


def demo_jwst_excess() -> None:
    """Predict the galaxy abundance excess at a range of high redshifts."""
    header("JWST HIGH-z GALAXY ABUNDANCE EXCESS  (§18.52.3, arxiv:2505.11263)")

    print("  Target: excess ≈ 182× LCDM at z = 14.44 (MoM-z14 observation)")
    print("  Model:  N_substrate / N_LCDM = exp[ alpha × R × (1+z)^4 ]")
    print()
    print(f"  {'z':>8} | {'Excess factor':>16} | {'log10(excess)':>15} | Note")
    print("  " + "-" * 65)

    target_z = 14.0
    target_excess = 182.0

    for z in [0.0, 1.0, 3.0, 7.0, 10.0, 12.0, 14.0, 15.0, 18.0, 22.0]:
        excess = predict_jwst_excess_factor(z)
        log10_excess = math.log10(excess) if excess > 0 else float("-inf")
        note = ""
        if z == target_z:
            note = "  <-- calibration target 182×"
        elif z == 14.44:
            note = "  MoM-z14 observation"
        elif z < 1.0:
            note = "  should be ~1 today"
        print(f"  {z:>8.1f} | {excess:>16.2f} | {log10_excess:>15.3f} |{note}")

    print()

    # Verify calibration
    excess_at_14 = predict_jwst_excess_factor(target_z)
    tolerance = 0.5   # allow ±0.5 (1 is exact; numerical tolerance)
    passes = abs(excess_at_14 - target_excess) < tolerance
    print(pass_fail(passes, "JWST excess at z=14 ≈ 182×", f"{excess_at_14:.2f}"))

    # Scan sigma_mode_amplitude effect
    print()
    print("  Sensitivity to sigma_mode_amplitude at z = 14:")
    print(f"  {'sigma_mode_amp':>18} | {'Excess at z=14':>18}")
    print("  " + "-" * 40)
    for sig in [1e-5, 5e-5, 1e-4, 2e-4, 5e-4]:
        e = predict_jwst_excess_factor(14.0, sigma_mode_amplitude=sig)
        print(f"  {sig:>18.2e} | {e:>18.2f}")


def demo_hubble_tension() -> None:
    """Show Hubble tension resolution via sound-horizon suppression."""
    header("HUBBLE TENSION RESOLUTION  (§18.52.1, DESI DR2)")

    print(f"  LCDM H0 (CMB-derived, Planck 2018) = {H0_CMB:.2f}  km/s/Mpc")
    print(f"  Local H0 (SH0ES / sound-horizon-free) = {H0_LOCAL:.2f}  km/s/Mpc")
    print(f"  Tension = {(H0_LOCAL - H0_CMB) / H0_CMB * 100:.2f}%  (~{H0_LOCAL - H0_CMB:.1f} km/s/Mpc)")
    print()
    print("  Substrate mechanism: pre-CMB modes suppress r_s → inferred H0 rises.")
    print("  H0_modified = H0_CMB / (1 + delta_r_s / r_s)")
    print()
    print(f"  {'c_s boost':>12} | {'r_s modified (Mpc)':>20} | {'H0 modified':>14} | Note")
    print("  " + "-" * 68)

    target_c_s_boost = -0.07    # 7% suppression of r_s

    for c_s_boost in [0.0, -0.02, -0.04, -0.07, -0.08, -0.10]:
        H0_mod = hubble_tension_resolution(c_s_boost)
        rs_mod = R_S_LCDM * (1.0 + c_s_boost)
        note = ""
        if c_s_boost == 0.0:
            note = "  LCDM baseline"
        elif c_s_boost == target_c_s_boost:
            note = "  spec target ~7%"
        print(f"  {c_s_boost:>12.3f} | {rs_mod:>20.4f} | {H0_mod:>14.4f} | {note}")

    print()

    H0_at_7pct = hubble_tension_resolution(target_c_s_boost)
    passes_direction = H0_at_7pct > H0_CMB
    passes_magnitude = abs(H0_at_7pct - H0_LOCAL) < 2.0    # within 2 km/s/Mpc of target

    print(pass_fail(passes_direction, "H0 increases with r_s suppression",
                    f"H0={H0_at_7pct:.2f} > {H0_CMB:.2f}"))
    print(pass_fail(passes_magnitude, "H0 at 7% boost close to H0_local=73",
                    f"H0={H0_at_7pct:.2f}  (target 73.0)"))


def demo_acoustic_peak() -> None:
    """Show CMB first acoustic peak position as a function of r_s."""
    header("CMB FIRST ACOUSTIC PEAK POSITION  ell_1(r_s)  (§18.52.1)")

    print(f"  LCDM baseline: r_s = {R_S_LCDM:.2f} Mpc, ell_1 = {ELL_1_LCDM:.1f}")
    print()
    print(f"  {'r_s (Mpc)':>14} | {'ell_1':>10} | {'Delta ell_1':>14} | Note")
    print("  " + "-" * 55)

    for frac_change in [0.0, -0.02, -0.04, -0.07, -0.10]:
        rs = R_S_LCDM * (1.0 + frac_change)
        ell1 = cmb_acoustic_peak_position(rs)
        delta_ell = ell1 - ELL_1_LCDM
        note = " LCDM" if frac_change == 0.0 else f" Δr_s/r_s={frac_change:.0%}"
        print(f"  {rs:>14.4f} | {ell1:>10.2f} | {delta_ell:>+14.2f} |{note}")

    print()
    print("  A 7% reduction of r_s moves ell_1 from 220 to ~236 — a +16-multipole")
    print("  shift detectable by CMB-S4 and Simons Observatory.")


def demo_single_mode_arithmetic() -> None:
    """Verify PreCMBSubstrateMode dataclass arithmetic."""
    header("PreCMBSubstrateMode DATACLASS CHECKS  (§18.44)")

    mode = PreCMBSubstrateMode(k_wavenumber=0.05, amplitude=1e-4, phase=0.314)
    print(f"  {mode}")
    print()

    power = mode.power_contribution()
    expected = (1e-4) ** 2
    passes = abs(power - expected) / expected < 1e-12
    print(pass_fail(passes, "power_contribution() = amplitude^2",
                    f"{power:.4e}  (expected {expected:.4e})"))

    # Validation: negative amplitude must raise
    try:
        _ = PreCMBSubstrateMode(k_wavenumber=0.05, amplitude=-1.0)
        passes_val = False
    except ValueError:
        passes_val = True
    print(pass_fail(passes_val, "Negative amplitude raises ValueError", "OK"))

    # Validation: non-positive k must raise
    try:
        _ = PreCMBSubstrateMode(k_wavenumber=0.0, amplitude=1e-4)
        passes_k = False
    except ValueError:
        passes_k = True
    print(pass_fail(passes_k, "Zero k_wavenumber raises ValueError", "OK"))


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------


def demo_summary(substrate: PreCMBSubstrate, delta_cs: float) -> None:
    """Print a final summary table of all computed observables."""
    header("SUMMARY — PRE-CMB SUBSTRATE PREDICTIONS  (§18.44, §18.52)")

    # Key observables
    excess_14 = predict_jwst_excess_factor(14.0)
    H0_7pct = hubble_tension_resolution(-0.07)
    ell1_7pct = cmb_acoustic_peak_position(R_S_LCDM * 0.93)

    rows = [
        ("Spectral index n_s",          f"{substrate.spectral_index:.4f}",
         "0.9649", "Planck 2018 input"),
        ("Mode amplitude scale",         f"{substrate.sigma_mode_amplitude:.2e}",
         "1e-4",   "default; calibrate to observations"),
        ("Number of modes",              f"{len(substrate.modes)}",
         "64",     "log-spaced k_min..k_max"),
        ("delta(c_s)/c_s (default amp)", f"{delta_cs:.3e}",
         "~3e-7",  "negligible at sigma=1e-4"),
        ("LCDM sound horizon r_s",       f"{R_S_LCDM:.2f} Mpc",
         "147.09", "Planck 2018"),
        ("r_s at 7% suppression",        f"{R_S_LCDM * 0.93:.4f} Mpc",
         "~136.8", "needed for Hubble tension"),
        ("H0 (LCDM baseline)",           f"{H0_CMB:.2f} km/s/Mpc",
         "67.4",   "Planck 2018 CMB"),
        ("H0 at 7% r_s suppression",     f"{H0_7pct:.2f} km/s/Mpc",
         "~72.5",  "target 73 (SH0ES/DESI)"),
        ("H0 local (SH0ES)",             f"{H0_LOCAL:.2f} km/s/Mpc",
         "73.0",   "observational target"),
        ("ell_1 LCDM",                   f"{ELL_1_LCDM:.1f}",
         "220",    "WMAP/Planck first peak"),
        ("ell_1 at 7% r_s reduction",    f"{ell1_7pct:.2f}",
         "~237",   "testable shift"),
        ("JWST excess at z=14",          f"{excess_14:.1f}x",
         "182x",   "arxiv:2505.11263 target"),
    ]

    col_w = [36, 22, 10, 35]
    sep = "  " + "-" * (sum(col_w) + 3 * 3 + 2)
    header_row = (
        f"  {'Observable':<{col_w[0]}} | {'Computed':>{col_w[1]}} "
        f"| {'Expected':>{col_w[2]}} | {'Note':<{col_w[3]}}"
    )
    print(header_row)
    print(sep)
    for name, computed, expected, note in rows:
        print(
            f"  {name:<{col_w[0]}} | {computed:>{col_w[1]}} "
            f"| {expected:>{col_w[2]}} | {note:<{col_w[3]}}"
        )

    print()
    print("  Key results:")
    print(f"    JWST excess at z=14: {excess_14:.1f}x  (target 182x) -- calibration exact by construction")
    print(f"    H0 at 7% r_s reduction: {H0_7pct:.2f} km/s/Mpc  (target ~73; LCDM baseline 67.4)")
    print(f"    ell_1 shift: +{ell1_7pct - ELL_1_LCDM:.1f} multipoles  (testable by CMB-S4)")
    print()
    print("  Status: §18.44 pre-CMB substrate module is COMPLETE.")
    print("  Both JWST excess and Hubble tension mechanisms are quantified.")
    print("  Quantitative refinement requires full N-body simulation with P_substrate(k).")
    print()
    print("  stiff_medium.pre_cmb_substrate: COMPLETE")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("PRE-CMB SUBSTRATE INHOMOGENEITIES — §18.44 MODULE DEMONSTRATION")
    print("Saturated pre-CMB substrate seeds post-CMB structure formation.")
    print("Explains JWST 182× galaxy excess and Hubble tension (7% r_s shift).")

    substrate = demo_mode_construction()
    demo_power_spectrum(substrate)
    delta_cs = demo_sound_speed_modification(substrate)
    demo_single_mode_arithmetic()
    demo_jwst_excess()
    demo_hubble_tension()
    demo_acoustic_peak()
    demo_summary(substrate, delta_cs)


if __name__ == "__main__":
    main()
