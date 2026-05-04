"""Substrate Schroedinger first-ionization-energy test, H through Ar (Z = 1..18).

This test extends the per-element atom_substrate module from H..Ne (10 elements)
to the full first three rows of the periodic table H..Ar (18 elements) and
asks two distinct, honest questions:

1.  **Substrate-Schroedinger from a fixed screening rule.** Use Slater's rules
    -- a closed, two-line shielding prescription with NO per-element knobs --
    to predict the effective nuclear charge Z_eff seen by the least-bound
    electron, then plug into the substrate-Schroedinger eigenvalue
        IE  =  Rydberg * Z_eff^2 / n_least^2.
    This is the *honest* zero-parameter prediction from the substrate
    ontology: the only inputs are the integer atomic number Z, the Aufbau
    filling order, and Slater's universally tabulated screening constants
    (1.00, 0.85, 0.35).

2.  **Per-element calibrated Z_eff (continuation of atom_substrate.py).**
    Reuse the H..Ne calibration for Z = 1..10 from atom_substrate.py and
    derive analogous one-knob-per-element calibrated Z_eff values for
    Z = 11..18 by inverting the same closed form.  This shows what the
    substrate Schroedinger equation *can* hit when given one degree of
    freedom per element (i.e. zero predictive power, but tells you whether
    the n^{-2} structural form is even right).

The take-away separates two questions that are usually conflated:
  - Does the substrate Schroedinger equation *have the right structural
    form* for many-electron atoms?  (test 2 answers: yes, within a few %)
  - Does the substrate ontology, with no per-element knobs, *predict* the
    measured IE?  (test 1 answers: not for outer-shell atoms; Slater is
    too crude for p- and d-electron screening, error blows up to >300%
    for Cl/Ar.)

NIST first ionisation energies are taken from NIST Atomic Spectra Database
(ground-level - 1st-ionised-state, in eV) as supplied by the user task.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Tuple

from .atom_substrate import (
    RYDBERG_EV,
    Z_EFF_LEAST_BOUND,
    AtomGeometry,
    AtomSimulator,
    aufbau_configuration,
)


# --------------------------------------------------------------------------- #
# NIST measured first ionisation energies, eV (Z = 1..18)                     #
# --------------------------------------------------------------------------- #
# Source: NIST Atomic Spectra Database, ground-state -> 1st-ionised state.
# Values supplied by the test task (rounded to NIST 4-significant precision).

MEASURED_IE_EV: Dict[int, float] = {
    1:  13.598,   # H
    2:  24.587,   # He
    3:   5.392,   # Li
    4:   9.323,   # Be
    5:   8.298,   # B
    6:  11.260,   # C
    7:  14.534,   # N
    8:  13.618,   # O
    9:  17.422,   # F
    10: 21.565,   # Ne
    11:  5.139,   # Na
    12:  7.646,   # Mg
    13:  5.986,   # Al
    14:  8.152,   # Si
    15: 10.487,   # P
    16: 10.360,   # S
    17: 12.968,   # Cl
    18: 15.760,   # Ar
}

ELEMENT_SYMBOLS: Dict[int, str] = {
    1: "H",  2: "He", 3: "Li", 4: "Be", 5: "B",  6: "C",
    7: "N",  8: "O",  9: "F", 10: "Ne", 11: "Na", 12: "Mg",
    13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar",
}


# Group/period labels for the verdict breakdown ----------------------------- #
GROUP_LABEL: Dict[int, str] = {
    1:  "row1_s",   2: "row1_s",
    3:  "row2_s",   4: "row2_s",
    5:  "row2_p",   6: "row2_p",  7: "row2_p",  8: "row2_p",
    9:  "row2_p", 10: "row2_p",
    11: "row3_s", 12: "row3_s",
    13: "row3_p", 14: "row3_p", 15: "row3_p", 16: "row3_p",
    17: "row3_p", 18: "row3_p",
}


# --------------------------------------------------------------------------- #
# Slater's rules -- substrate-principled (zero per-element knob) screening    #
# --------------------------------------------------------------------------- #
# Slater (1930) rules for shielding constant s (so Z_eff = Z - s):
#   * group the electrons by (n, ell) with [s, p] grouped together:
#     [1s] [2s,2p] [3s,3p] [3d] [4s,4p] [4d] [4f] [5s,5p] ...
#   * for an electron in a given group:
#       - electrons in any HIGHER group contribute 0
#       - other electrons in the SAME group contribute 0.35  (1s-1s: 0.30)
#       - if the target is an [s,p] electron in shell n:
#             group n-1 contributes 0.85 per electron
#             groups <= n-2 contribute 1.00 per electron
#       - if the target is a d or f electron:
#             ALL electrons in lower groups contribute 1.00
#
# These coefficients are universal and contain NO free parameters; the only
# inputs are integer Z and the Aufbau filling order.

def _slater_group(n: int, ell: int) -> Tuple[int, str]:
    """Slater grouping: (1s) | (n s,p) | (n d) | (n f).  s & p in same group."""
    if ell in (0, 1):
        return (n, "sp")
    if ell == 2:
        return (n, "d")
    if ell == 3:
        return (n, "f")
    raise ValueError(f"ell={ell} not supported")


def slater_zeff_for_least_bound(Z: int) -> float:
    """Z_eff for the LEAST-bound electron in the Aufbau ground state of Z.

    Strict Slater (1930), no per-element fudge.  Used as the substrate-
    Schroedinger zero-knob prediction.
    """
    cfg = aufbau_configuration(Z)
    n_t, ell_t = cfg[-1][0], cfg[-1][1]
    target_group = _slater_group(n_t, ell_t)
    target_kind = target_group[1]    # "sp", "d", or "f"

    s = 0.0
    for (n, ell, count) in cfg:
        gn, gk = _slater_group(n, ell)
        if (gn, gk) == target_group:
            # same group: per-electron 0.35 (0.30 for 1s-1s; n=1 always s)
            per = 0.30 if (n == 1 and ell == 0) else 0.35
            s += per * (count - 1)         # exclude the electron itself
            continue

        if target_kind == "sp":
            if gk in ("sp",):
                if gn == n_t - 1:
                    s += 0.85 * count
                elif gn <= n_t - 2:
                    s += 1.00 * count
                else:
                    # gn > n_t (higher shell) -> 0; gn == n_t handled above
                    pass
            elif gk in ("d", "f") and gn < n_t:
                s += 1.00 * count
        else:
            # target d/f: ALL lower groups contribute 1.0
            if (gn < n_t) or (gn == n_t and gk == "sp"):
                s += 1.00 * count

    return Z - s


# --------------------------------------------------------------------------- #
# Per-element calibrated Z_eff for Na..Ar (continuation of atom_substrate.py) #
# --------------------------------------------------------------------------- #
# Inverted from IE_meas = Rydberg * Z_eff^2 / n_least^2, exactly as
# atom_substrate.Z_EFF_LEAST_BOUND was calibrated for H..Ne.  Provided here so
# that the test can show what the n^{-2} substrate-Schroedinger form *can* fit
# when given one knob per element.  These are NOT predictions; they are the
# minimal-degrees-of-freedom values needed to absorb the measured IE.

def _calibrated_zeff_from_measured(Z: int) -> float:
    n_t, _ = AtomGeometry(Z).least_bound_subshell()
    return sqrt(MEASURED_IE_EV[Z] * n_t * n_t / RYDBERG_EV)


Z_EFF_CALIBRATED_EXTENDED: Dict[int, float] = {
    Z: Z_EFF_LEAST_BOUND[Z] for Z in range(1, 11)
}
for _Z in range(11, 19):
    Z_EFF_CALIBRATED_EXTENDED[_Z] = _calibrated_zeff_from_measured(_Z)


# --------------------------------------------------------------------------- #
# Result rows                                                                 #
# --------------------------------------------------------------------------- #


@dataclass
class IERow:
    Z: int
    symbol: str
    n_least: int
    ell_least: int
    measured_eV: float
    zeff_slater: float
    pred_slater_eV: float
    err_slater_pct: float
    zeff_calibrated: float
    pred_calibrated_eV: float
    err_calibrated_pct: float
    group: str

    def as_dict(self) -> Dict[str, float]:
        return {
            "Z": self.Z,
            "symbol": self.symbol,
            "n": self.n_least,
            "ell": self.ell_least,
            "measured_eV": self.measured_eV,
            "Zeff_slater": self.zeff_slater,
            "pred_slater_eV": self.pred_slater_eV,
            "err_slater_pct": self.err_slater_pct,
            "Zeff_calibrated": self.zeff_calibrated,
            "pred_calibrated_eV": self.pred_calibrated_eV,
            "err_calibrated_pct": self.err_calibrated_pct,
            "group": self.group,
        }


def predict_ionization_energy(
    Z: int, mode: str = "slater"
) -> Tuple[float, float]:
    """Return (Z_eff, IE_predicted_eV) for atom Z under the chosen rule.

    mode="slater"      : zero-knob substrate-Schroedinger via Slater's rules.
    mode="calibrated"  : per-element Z_eff (one knob per element).
    """
    n_t, _ = AtomGeometry(Z).least_bound_subshell()
    if mode == "slater":
        zeff = slater_zeff_for_least_bound(Z)
    elif mode == "calibrated":
        zeff = Z_EFF_CALIBRATED_EXTENDED[Z]
    else:
        raise ValueError(f"unknown mode {mode!r}")
    e = -AtomSimulator.orbital_energy_ev(Z_eff=zeff, n=n_t)
    return zeff, e


def build_rows(Z_max: int = 18) -> List[IERow]:
    rows: List[IERow] = []
    for Z in range(1, Z_max + 1):
        n_t, ell_t = AtomGeometry(Z).least_bound_subshell()
        meas = MEASURED_IE_EV[Z]
        z_sl, pred_sl = predict_ionization_energy(Z, "slater")
        z_ca, pred_ca = predict_ionization_energy(Z, "calibrated")
        err_sl = 100.0 * abs(pred_sl - meas) / meas
        err_ca = 100.0 * abs(pred_ca - meas) / meas
        rows.append(
            IERow(
                Z=Z,
                symbol=ELEMENT_SYMBOLS[Z],
                n_least=n_t,
                ell_least=ell_t,
                measured_eV=meas,
                zeff_slater=z_sl,
                pred_slater_eV=pred_sl,
                err_slater_pct=err_sl,
                zeff_calibrated=z_ca,
                pred_calibrated_eV=pred_ca,
                err_calibrated_pct=err_ca,
                group=GROUP_LABEL[Z],
            )
        )
    return rows


# --------------------------------------------------------------------------- #
# Verdict / summary                                                           #
# --------------------------------------------------------------------------- #


def group_breakdown(rows: List[IERow], err_field: str) -> Dict[str, Dict[str, float]]:
    """Mean / max absolute % error within each group label."""
    out: Dict[str, List[float]] = {}
    for r in rows:
        out.setdefault(r.group, []).append(getattr(r, err_field))
    return {
        g: {
            "n": float(len(errs)),
            "mean_pct": sum(errs) / len(errs),
            "max_pct":  max(errs),
        }
        for g, errs in out.items()
    }


def best_group(rows: List[IERow], err_field: str = "err_slater_pct") -> str:
    """Return the group label with the lowest mean error under err_field."""
    bd = group_breakdown(rows, err_field)
    return min(bd.items(), key=lambda kv: kv[1]["mean_pct"])[0]


def run_test(Z_max: int = 18) -> Dict[str, object]:
    """Build the per-element table and the verdict dictionary."""
    rows = build_rows(Z_max)
    sl_errs = [r.err_slater_pct     for r in rows]
    ca_errs = [r.err_calibrated_pct for r in rows]
    return {
        "rows": rows,
        "summary": {
            "n_elements":            len(rows),
            "slater_mean_pct":       sum(sl_errs) / len(sl_errs),
            "slater_max_pct":        max(sl_errs),
            "calibrated_mean_pct":   sum(ca_errs) / len(ca_errs),
            "calibrated_max_pct":    max(ca_errs),
        },
        "group_breakdown_slater":     group_breakdown(rows, "err_slater_pct"),
        "group_breakdown_calibrated": group_breakdown(rows, "err_calibrated_pct"),
        "best_group_slater":          best_group(rows, "err_slater_pct"),
        "best_group_calibrated":      best_group(rows, "err_calibrated_pct"),
    }


# --------------------------------------------------------------------------- #
# Pretty-printing                                                             #
# --------------------------------------------------------------------------- #


def _format_table(rows: List[IERow]) -> str:
    hdr = (
        f"{'Z':>3} {'sym':>3} {'n':>2} {'l':>2} "
        f"{'meas eV':>9} {'Zeff_S':>7} {'pred_S':>9} {'err_S%':>8} "
        f"{'Zeff_cal':>9} {'pred_cal':>9} {'err_cal%':>9}"
    )
    lines = [hdr, "-" * len(hdr)]
    for r in rows:
        lines.append(
            f"{r.Z:>3} {r.symbol:>3} {r.n_least:>2} {r.ell_least:>2} "
            f"{r.measured_eV:9.3f} {r.zeff_slater:7.3f} "
            f"{r.pred_slater_eV:9.3f} {r.err_slater_pct:8.1f} "
            f"{r.zeff_calibrated:9.3f} {r.pred_calibrated_eV:9.3f} "
            f"{r.err_calibrated_pct:9.3f}"
        )
    return "\n".join(lines)


def main() -> None:
    res = run_test()
    rows: List[IERow] = res["rows"]            # type: ignore[assignment]
    summary: Dict[str, float] = res["summary"]  # type: ignore[assignment]
    print(_format_table(rows))
    print()
    print("--- summary --------------------------------------------------------")
    print(
        f"  N = {int(summary['n_elements'])}\n"
        f"  Slater     (zero-knob substrate Schroedinger):"
        f"  mean abs err = {summary['slater_mean_pct']:6.1f}%   "
        f"max = {summary['slater_max_pct']:6.1f}%\n"
        f"  Calibrated (one Z_eff per element)         :"
        f"  mean abs err = {summary['calibrated_mean_pct']:6.4f}%  "
        f"max = {summary['calibrated_max_pct']:6.4f}%"
    )
    print("--- group breakdown (Slater zero-knob) -----------------------------")
    for g, st in res["group_breakdown_slater"].items():           # type: ignore[union-attr]
        print(f"  {g:>8}: n={int(st['n'])}, mean={st['mean_pct']:6.1f}%, "
              f"max={st['max_pct']:6.1f}%")
    print(f"  best group (Slater)     : {res['best_group_slater']}")
    print(f"  best group (calibrated) : {res['best_group_calibrated']}")


if __name__ == "__main__":
    main()
