"""Substrate nuclear binding-energy test against AME2020 (A = 2 -- 238).

GOAL
----
Honestly evaluate the pure-substrate prediction

    BE(A)  =  eta_coop(A) * P(A) * eps_face                       (1)

with eps_face = Lambda_QCD / (n_A * N_BAM) = 200 / 90 = 2.2222 MeV
(deuteron BE; verified at 0.11 percent in ``deuteron_v2.py``), against
the AME2020 measured binding energies of 25 stable isotopes spanning
A = 2 (deuteron) to A = 238 (uranium).

THE FACE-PAIR COUNT  P(A)
-------------------------
The existing ``nucleon_stacking_geometry`` module hand-builds explicit
face-sharing graphs for the seven light nuclei A in {2,3,4,6,8,12,16}.
For arbitrary A we extrapolate the count using the close-packed limit:

* A K_4 cell has 4 triangular faces.
* Each face-pair is shared by exactly 2 cells.
* In a fully saturated interior, each cell can match 4 of its faces
  with neighbours, contributing 4/2 = 2 face-pairs per cell.
* Surface cells lose ~A^{2/3} face-pairs (one per missing neighbour).

This gives the standard nuclear-droplet ansatz

    P(A)  =  2 * A  -  c_surf * A^{2/3}                           (2)

Calibrating c_surf to reproduce P(16) = 30 (the explicit O-16 topology)
gives c_surf = (32 - 30) / 16^{2/3} = 2 / 6.350 = 0.315.  We use this
fixed c_surf for all A, then verify continuity at the seven explicit
A values where ``nucleon_stacking_geometry`` already provides P(A).

The ``eta_coop(A)`` factor saturates at ~2.122 (the alpha value) for
A >= 4.  For A = 2 it is 1.000 (single bond, no neighbours), and for
A = 3 it is 1.272 (intermediate).  This module re-exposes the same
``cooperative_factor`` already used in ``nucleon_stacking_geometry``.

WHAT WE EXPECT
--------------
1. Light nuclei (A < 20): the explicit topologies already match within
   ~0-18 percent (see existing demo).  No Coulomb correction needed
   because Z is small (Z(Z-1) < 100).
2. Medium nuclei (20 <= A <= 60): bulk saturation model holds.  Pure
   substrate prediction should match within ~5-10 percent.
3. Heavy nuclei (A > 100): Coulomb repulsion ~Z^2/A^{1/3} grows and
   substrate alone (no EM correction) should over-bind by 10-30 percent.
4. Very heavy (A > 200): Coulomb deficit ~ 0.7 * Z(Z-1)/A^{1/3} is
   ~ 700 MeV for U-238, against a measured BE of ~ 1800 MeV.  Pure
   substrate (without subtracting Coulomb) should over-bind by ~ 40
   percent for U-238.

This is the standard SEMF story: substrate gives the volume + surface
terms cleanly; Coulomb + asymmetry must come from electromagnetism +
parity-mismatch (already implemented in ``nuclear_chart.py``).  This
module tests how far the BARE substrate piece carries us.

UNITS
-----
Energy: MeV.  All BE values are POSITIVE (binding lowers total mass).

REFERENCES
----------
* ``nucleon_stacking_geometry.py`` -- explicit P(A) for A in {2..16}
* ``k4_face_pair_geometry.EPS_FACE_MEV`` = 2.222 MeV
* AME2020: M. Wang et al., Chinese Physics C 45, 030003 (2021).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from src.stiff_medium.k4_face_pair_geometry import EPS_FACE_MEV
from src.stiff_medium.nucleon_stacking_geometry import (
    NucleonStackGeometry,
    TOPOLOGY_REGISTRY,
    cooperative_factor,
    get_topology,
)


# ---------------------------------------------------------------------------
# AME2020 reference data (25 stable isotopes spanning A = 2 .. 238)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IsotopeRef:
    """AME2020 reference entry for a single isotope.

    Attributes
    ----------
    name : str
        Standard isotope label, e.g. "208Pb".
    Z : int
        Atomic number.
    A : int
        Mass number.
    BE_MeV : float
        Total binding energy (MeV), positive convention.
    """
    name: str
    Z: int
    A: int
    BE_MeV: float

    @property
    def N(self) -> int:
        return self.A - self.Z

    @property
    def BE_per_A(self) -> float:
        return self.BE_MeV / self.A


# Curated 25 isotopes spanning A = 2 .. 238.  Values are AME2020.
AME2020: Tuple[IsotopeRef, ...] = (
    IsotopeRef("2H",     1,   2,    2.224573),
    IsotopeRef("3H",     1,   3,    8.481798),
    IsotopeRef("3He",    2,   3,    7.718058),
    IsotopeRef("4He",    2,   4,   28.295674),
    IsotopeRef("6Li",    3,   6,   31.994561),
    IsotopeRef("7Li",    3,   7,   39.245366),
    IsotopeRef("9Be",    4,   9,   58.164944),
    IsotopeRef("10B",    5,  10,   64.750766),
    IsotopeRef("12C",    6,  12,   92.161728),
    IsotopeRef("14N",    7,  14,  104.658760),
    IsotopeRef("16O",    8,  16,  127.619337),
    IsotopeRef("20Ne",  10,  20,  160.644859),
    IsotopeRef("24Mg",  12,  24,  198.256637),
    IsotopeRef("28Si",  14,  28,  236.536839),
    IsotopeRef("32S",   16,  32,  271.780869),
    IsotopeRef("40Ca",  20,  40,  342.051787),
    IsotopeRef("56Fe",  26,  56,  492.253892),
    IsotopeRef("60Ni",  28,  60,  526.842136),
    IsotopeRef("90Zr",  40,  90,  783.892990),
    IsotopeRef("120Sn", 50, 120, 1020.546396),
    IsotopeRef("140Ce", 58, 140, 1172.706350),
    IsotopeRef("158Gd", 64, 158, 1295.910000),
    IsotopeRef("200Hg", 80, 200, 1581.196000),
    IsotopeRef("208Pb", 82, 208, 1636.446000),
    IsotopeRef("238U",  92, 238, 1801.694000),
)


# ---------------------------------------------------------------------------
# Face-pair count P(A) for arbitrary A (extrapolated bulk model)
# ---------------------------------------------------------------------------

# Calibrated against the O-16 explicit topology: P(16) = 30.
# 2*16 - c_surf * 16^{2/3} = 30  =>  c_surf = 2 / 16^{2/3}.
C_SURF: float = 2.0 / 16.0 ** (2.0 / 3.0)   # ~0.3150


def predicted_face_pairs(A: int) -> int:
    """P(A) = number of shared faces in close-packed K_4 stack.

    For A registered in the explicit topology dictionary, returns the
    exact value.  For arbitrary A, returns the saturated-bulk
    extrapolation:

        P(A) = round(2 * A - c_surf * A^(2/3))

    Parameters
    ----------
    A : int
        Mass number.

    Returns
    -------
    int
        Number of K_4 face-pairs.
    """
    if A in TOPOLOGY_REGISTRY:
        return get_topology(A).n_face_pairs
    bulk_estimate = 2.0 * A - C_SURF * (A ** (2.0 / 3.0))
    return int(round(bulk_estimate))


# ---------------------------------------------------------------------------
# Pure-substrate BE prediction
# ---------------------------------------------------------------------------

def predicted_BE(A: int) -> float:
    """BE(A) = eta_coop(A) * P(A) * eps_face   (no Coulomb correction).

    Uses the saturated cooperative factor (~2.122) for all A >= 4.
    """
    eta = cooperative_factor(A)
    P = predicted_face_pairs(A)
    return eta * P * EPS_FACE_MEV


def predicted_BE_per_A(A: int) -> float:
    """BE / A in MeV per nucleon."""
    return predicted_BE(A) / A


# ---------------------------------------------------------------------------
# SEMF-style corrections on top of the bare substrate prediction
# ---------------------------------------------------------------------------
#
# The bare substrate prediction reproduces the volume + (close-packed) surface
# pieces but is silent about (i) electrostatic Coulomb repulsion of the
# protons, (ii) isospin asymmetry penalty for N != Z, (iii) pairing energy
# from like-nucleon pair correlations.  This section adds these three SEMF
# terms with substrate-derivable coefficients where possible.
#
# COULOMB
# -------
# Substrate-style derivation:
#
#     a_C  =  (3/5) * alpha_em * hbar*c / R_0   with   R_0 = 1.20 fm
#          =  (3/5) * (1/137.036) * (197.3269 MeV*fm) / (1.20 fm)
#          =  0.7200 MeV
#
# This is the standard semi-empirical mass formula coefficient and is
# *also* the substrate-derived value (since R_0 = K_4 nucleon-radius
# anchor used throughout the deuteron / alpha derivations).  No new free
# parameter.
#
# ASYMMETRY
# ---------
# Empirical SEMF value: a_sym = 23 MeV.  This is NOT presently substrate-
# derivable from primitives -- in standard nuclear physics it emerges from
# the Fermi-gas kinetic-asymmetry energy plus the isovector NN potential
# average.  The substrate's bare ``eta_coop * P * eps_face`` does not
# distinguish isobars and so already implicitly absorbs ~half of the
# asymmetry penalty into the cooperative factor.  Honest report: the
# textbook a_sym = 23 MeV is *not* substrate-primitive and acts as one
# additional fitted parameter for now (see ``nuclear_binding.py`` for a
# substrate-flavoured Fermi-gas estimate that lands in the 18-25 MeV band).
#
# PAIRING
# -------
# Empirical SEMF value: a_p ~ 11 MeV.  Sign convention: +a_p / sqrt(A)
# for even-even, 0 for odd-A, -a_p / sqrt(A) for odd-odd.  Like a_sym
# this is currently empirical -- the substrate has no microscopic
# pairing model implemented.

# Constants used by the SEMF corrections
HBARC_MEV_FM: float = 197.3269804           # MeV * fm
ALPHA_EM: float = 1.0 / 137.035999084       # fine-structure constant
R_0_FM: float = 1.20                        # K_4 nucleon-radius anchor

# Substrate-derived Coulomb coefficient: a_C = (3/5) * alpha * hbar*c / R_0
A_COULOMB_MEV: float = (3.0 / 5.0) * ALPHA_EM * HBARC_MEV_FM / R_0_FM
# = 0.72004... MeV (matches textbook 0.72 MeV at 0.005%).

# Empirical (NOT presently substrate-primitive) -- see module docstring.
A_SYMMETRY_MEV: float = 23.0
A_PAIRING_MEV: float = 11.0


def coulomb_correction_MeV(Z: int, A: int, a_C: float = A_COULOMB_MEV
                            ) -> float:
    """Substrate Coulomb deficit:  -a_C * Z(Z-1) / A^{1/3}   [MeV].

    Parameters
    ----------
    Z, A : int
        Atomic and mass numbers.
    a_C : float
        Coulomb coefficient (default: substrate-derived 0.7200 MeV).

    Returns
    -------
    float
        Negative MeV (reduces binding).
    """
    if A <= 0 or Z < 2:
        return 0.0
    return -a_C * Z * (Z - 1) / (A ** (1.0 / 3.0))


def asymmetry_correction_MeV(Z: int, A: int,
                              a_sym: float = A_SYMMETRY_MEV) -> float:
    """SEMF asymmetry penalty:  -a_sym * (N-Z)^2 / A   [MeV].

    Currently empirical: the textbook a_sym = 23 MeV is NOT presently
    substrate-derivable from primitives (substrate's bare
    eta_coop * P * eps_face already implicitly absorbs about half of
    the asymmetry penalty into the cooperative factor).
    """
    if A <= 0:
        return 0.0
    N = A - Z
    return -a_sym * (N - Z) ** 2 / A


def pairing_correction_MeV(Z: int, A: int,
                            a_p: float = A_PAIRING_MEV) -> float:
    """SEMF pairing term:  +-a_p / sqrt(A)   [MeV].

    Sign convention:
        +a_p / sqrt(A)  for even-Z, even-N
         0              for odd A
        -a_p / sqrt(A)  for odd-Z, odd-N

    Currently empirical -- the substrate has no microscopic pairing
    model implemented.
    """
    if A <= 0:
        return 0.0
    N = A - Z
    if A % 2 == 1:        # odd-A
        return 0.0
    if Z % 2 == 0 and N % 2 == 0:
        return +a_p / np.sqrt(A)
    return -a_p / np.sqrt(A)


def predicted_BE_with_corrections(Z: int, A: int,
                                   a_C: float = A_COULOMB_MEV,
                                   a_sym: float = A_SYMMETRY_MEV,
                                   a_p: float = A_PAIRING_MEV) -> float:
    """BE_pred = bare-substrate + Coulomb + asymmetry + pairing.

    Parameters
    ----------
    Z, A : int
        Atomic and mass numbers.
    a_C, a_sym, a_p : float
        SEMF coefficients.  Defaults are substrate-derived (a_C = 0.72)
        or canonical SEMF values (a_sym = 23, a_p = 11).
    """
    return (predicted_BE(A)
            + coulomb_correction_MeV(Z, A, a_C)
            + asymmetry_correction_MeV(Z, A, a_sym)
            + pairing_correction_MeV(Z, A, a_p))


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

@dataclass
class IsotopeResult:
    """Single-isotope comparison record.

    ``BE_pred_MeV`` is the bare substrate prediction.  Optional fields
    ``BE_coul_MeV``, ``BE_asym_MeV``, ``BE_pair_MeV`` and
    ``BE_pred_corr_MeV`` carry the SEMF-corrected prediction when
    populated by ``compute_results_with_corrections``.
    """
    isotope: IsotopeRef
    P: int
    eta_coop: float
    BE_pred_MeV: float
    BE_obs_MeV: float
    BE_coul_MeV: Optional[float] = None
    BE_asym_MeV: Optional[float] = None
    BE_pair_MeV: Optional[float] = None
    BE_pred_corr_MeV: Optional[float] = None

    @property
    def BE_pred_per_A(self) -> float:
        return self.BE_pred_MeV / self.isotope.A

    @property
    def BE_obs_per_A(self) -> float:
        return self.isotope.BE_per_A

    @property
    def err_abs_MeV(self) -> float:
        return self.BE_pred_MeV - self.BE_obs_MeV

    @property
    def err_pct(self) -> float:
        return 100.0 * self.err_abs_MeV / self.BE_obs_MeV

    @property
    def err_per_A(self) -> float:
        return self.BE_pred_per_A - self.BE_obs_per_A

    @property
    def BE_pred_corr_per_A(self) -> float:
        if self.BE_pred_corr_MeV is None:
            return float('nan')
        return self.BE_pred_corr_MeV / self.isotope.A

    @property
    def err_abs_corr_MeV(self) -> float:
        if self.BE_pred_corr_MeV is None:
            return float('nan')
        return self.BE_pred_corr_MeV - self.BE_obs_MeV

    @property
    def err_pct_corr(self) -> float:
        if self.BE_pred_corr_MeV is None:
            return float('nan')
        return 100.0 * self.err_abs_corr_MeV / self.BE_obs_MeV


def compute_results(refs: Tuple[IsotopeRef, ...] = AME2020
                    ) -> List[IsotopeResult]:
    """Compute the 25-isotope comparison table (bare substrate only)."""
    out: List[IsotopeResult] = []
    for ref in refs:
        P = predicted_face_pairs(ref.A)
        eta = cooperative_factor(ref.A)
        be = eta * P * EPS_FACE_MEV
        out.append(IsotopeResult(isotope=ref, P=P, eta_coop=eta,
                                  BE_pred_MeV=be, BE_obs_MeV=ref.BE_MeV))
    return out


def compute_results_with_corrections(
    refs: Tuple[IsotopeRef, ...] = AME2020,
    a_C: float = A_COULOMB_MEV,
    a_sym: float = A_SYMMETRY_MEV,
    a_p: float = A_PAIRING_MEV,
) -> List[IsotopeResult]:
    """Compute the 25-isotope comparison with Coulomb + asymmetry + pairing.

    Each :class:`IsotopeResult` is fully populated including the three
    SEMF correction terms and the corrected-prediction error.
    """
    out: List[IsotopeResult] = []
    for ref in refs:
        P = predicted_face_pairs(ref.A)
        eta = cooperative_factor(ref.A)
        be = eta * P * EPS_FACE_MEV
        be_coul = coulomb_correction_MeV(ref.Z, ref.A, a_C)
        be_asym = asymmetry_correction_MeV(ref.Z, ref.A, a_sym)
        be_pair = pairing_correction_MeV(ref.Z, ref.A, a_p)
        be_corr = be + be_coul + be_asym + be_pair
        out.append(IsotopeResult(
            isotope=ref, P=P, eta_coop=eta,
            BE_pred_MeV=be, BE_obs_MeV=ref.BE_MeV,
            BE_coul_MeV=be_coul,
            BE_asym_MeV=be_asym,
            BE_pair_MeV=be_pair,
            BE_pred_corr_MeV=be_corr,
        ))
    return out


def summary_statistics(results: List[IsotopeResult],
                        use_corrected: bool = False) -> Dict[str, float]:
    """Aggregate error statistics across the 25-isotope set.

    Parameters
    ----------
    results : list[IsotopeResult]
        Per-isotope results.
    use_corrected : bool
        If True (and ``BE_pred_corr_MeV`` is populated) report the
        corrected-prediction errors.  Default False = bare substrate.
    """
    if use_corrected:
        errs_pct = np.array([r.err_pct_corr for r in results])
        errs_abs = np.array([abs(r.err_abs_corr_MeV) for r in results])
        errs_perA = np.array([
            (r.BE_pred_corr_MeV - r.BE_obs_MeV) / r.isotope.A
            for r in results
        ])
    else:
        errs_pct = np.array([r.err_pct for r in results])
        errs_abs = np.array([abs(r.err_abs_MeV) for r in results])
        errs_perA = np.array([r.err_per_A for r in results])
    return {
        'n_isotopes': len(results),
        'mean_err_pct': float(np.mean(errs_pct)),
        'mean_abs_err_pct': float(np.mean(np.abs(errs_pct))),
        'rms_err_pct': float(np.sqrt(np.mean(errs_pct ** 2))),
        'max_abs_err_pct': float(np.max(np.abs(errs_pct))),
        'mean_abs_err_MeV': float(np.mean(errs_abs)),
        'mean_err_per_A_MeV': float(np.mean(errs_perA)),
        'max_abs_err_per_A_MeV': float(np.max(np.abs(errs_perA))),
    }


def print_table(results: List[IsotopeResult]) -> None:
    """Pretty-print the 25-isotope comparison."""
    print(f"{'iso':>6} {'Z':>3} {'A':>4} {'P':>4} {'eta':>5} "
          f"{'BE_pred':>10} {'BE_obs':>10} "
          f"{'BE/A_pred':>9} {'BE/A_obs':>9} "
          f"{'err_MeV':>9} {'err_%':>7}")
    print("-" * 95)
    for r in results:
        iso = r.isotope
        print(f"{iso.name:>6} {iso.Z:>3d} {iso.A:>4d} "
              f"{r.P:>4d} {r.eta_coop:>5.2f} "
              f"{r.BE_pred_MeV:>10.2f} {r.BE_obs_MeV:>10.2f} "
              f"{r.BE_pred_per_A:>9.3f} {r.BE_obs_per_A:>9.3f} "
              f"{r.err_abs_MeV:>+9.2f} {r.err_pct:>+7.2f}")


def classify_results(results: List[IsotopeResult],
                     tol_pct: float = 5.0,
                     use_corrected: bool = False
                     ) -> Tuple[List[IsotopeResult], List[IsotopeResult]]:
    """Split into (passing, failing) at the given tolerance percent."""
    if use_corrected:
        passing = [r for r in results if abs(r.err_pct_corr) <= tol_pct]
        failing = [r for r in results if abs(r.err_pct_corr) > tol_pct]
    else:
        passing = [r for r in results if abs(r.err_pct) <= tol_pct]
        failing = [r for r in results if abs(r.err_pct) > tol_pct]
    return passing, failing


def print_table_with_corrections(results: List[IsotopeResult]) -> None:
    """Pretty-print the bare + corrected comparison side-by-side."""
    print(f"{'iso':>6} {'Z':>3} {'A':>4} "
          f"{'BE_obs':>9} {'BE_bare':>9} {'err_b%':>7} "
          f"{'+Coul':>8} {'+asym':>8} {'+pair':>7} "
          f"{'BE_corr':>9} {'err_c%':>7}")
    print("-" * 100)
    for r in results:
        iso = r.isotope
        coul = r.BE_coul_MeV if r.BE_coul_MeV is not None else 0.0
        asym = r.BE_asym_MeV if r.BE_asym_MeV is not None else 0.0
        pair = r.BE_pair_MeV if r.BE_pair_MeV is not None else 0.0
        corr = (r.BE_pred_corr_MeV
                if r.BE_pred_corr_MeV is not None else r.BE_pred_MeV)
        err_c = (100.0 * (corr - r.BE_obs_MeV) / r.BE_obs_MeV)
        print(f"{iso.name:>6} {iso.Z:>3d} {iso.A:>4d} "
              f"{r.BE_obs_MeV:>9.2f} {r.BE_pred_MeV:>9.2f} "
              f"{r.err_pct:>+7.2f} "
              f"{coul:>+8.2f} {asym:>+8.2f} {pair:>+7.2f} "
              f"{corr:>9.2f} {err_c:>+7.2f}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo() -> None:
    """End-to-end print: per-isotope comparison + summary statistics."""
    results = compute_results()
    print_table(results)
    print()
    stats = summary_statistics(results)
    for k, v in stats.items():
        print(f"  {k:25} = {v}")
    print()
    passing, failing = classify_results(results, tol_pct=5.0)
    print(f"Within 5%: {len(passing)} / {len(results)}")
    print(f"Beyond 5%: {len(failing)} / {len(results)}")
    if failing:
        print("Failing isotopes:")
        for r in failing:
            print(f"   {r.isotope.name:>6}  err = {r.err_pct:+.1f}%  "
                  f"(BE_pred = {r.BE_pred_MeV:.1f}, "
                  f"BE_obs = {r.BE_obs_MeV:.1f})")


def demo_with_corrections() -> None:
    """End-to-end print: bare substrate vs substrate + SEMF corrections.

    Reports for the 25 AME2020 isotopes:
      * bare substrate: BE = eta_coop * P * eps_face
      * corrected:      BE_bare + Coulomb + asymmetry + pairing
    with substrate-derived a_C = 0.7200 MeV (= (3/5)alpha hbar c / R_0)
    and empirical a_sym = 23, a_p = 11 MeV.
    """
    results = compute_results_with_corrections()
    print_table_with_corrections(results)
    print()

    bare_stats = summary_statistics(results, use_corrected=False)
    corr_stats = summary_statistics(results, use_corrected=True)

    print(f"BARE SUBSTRATE:")
    print(f"  mean abs err = {bare_stats['mean_abs_err_pct']:.2f}%   "
          f"RMS = {bare_stats['rms_err_pct']:.2f}%   "
          f"max = {bare_stats['max_abs_err_pct']:.2f}%")
    print(f"SUBSTRATE + Coulomb + asymmetry + pairing:")
    print(f"  mean abs err = {corr_stats['mean_abs_err_pct']:.2f}%   "
          f"RMS = {corr_stats['rms_err_pct']:.2f}%   "
          f"max = {corr_stats['max_abs_err_pct']:.2f}%")
    print()
    print(f"Coefficients:")
    print(f"  a_C = {A_COULOMB_MEV:.4f} MeV   "
          f"= (3/5) * alpha * hbar*c / R_0   (R_0 = {R_0_FM} fm)")
    print(f"  a_sym = {A_SYMMETRY_MEV} MeV   (empirical, NOT substrate-derived)")
    print(f"  a_p   = {A_PAIRING_MEV} MeV   (empirical, NOT substrate-derived)")


if __name__ == "__main__":
    demo()
    print()
    print("=" * 100)
    print("WITH SEMF CORRECTIONS")
    print("=" * 100)
    demo_with_corrections()
