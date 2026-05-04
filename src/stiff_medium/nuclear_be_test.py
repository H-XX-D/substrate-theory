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
# Comparison table
# ---------------------------------------------------------------------------

@dataclass
class IsotopeResult:
    """Single-isotope comparison record."""
    isotope: IsotopeRef
    P: int
    eta_coop: float
    BE_pred_MeV: float
    BE_obs_MeV: float

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


def compute_results(refs: Tuple[IsotopeRef, ...] = AME2020
                    ) -> List[IsotopeResult]:
    """Compute the 25-isotope comparison table."""
    out: List[IsotopeResult] = []
    for ref in refs:
        P = predicted_face_pairs(ref.A)
        eta = cooperative_factor(ref.A)
        be = eta * P * EPS_FACE_MEV
        out.append(IsotopeResult(isotope=ref, P=P, eta_coop=eta,
                                  BE_pred_MeV=be, BE_obs_MeV=ref.BE_MeV))
    return out


def summary_statistics(results: List[IsotopeResult]) -> Dict[str, float]:
    """Aggregate error statistics across the 25-isotope set."""
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
                     tol_pct: float = 5.0
                     ) -> Tuple[List[IsotopeResult], List[IsotopeResult]]:
    """Split into (passing, failing) at the given tolerance percent."""
    passing = [r for r in results if abs(r.err_pct) <= tol_pct]
    failing = [r for r in results if abs(r.err_pct) > tol_pct]
    return passing, failing


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


if __name__ == "__main__":
    demo()
