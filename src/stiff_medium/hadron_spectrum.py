"""Unified hadron spectrum from K_4 cell stacking.

A clean, self-contained calculator for meson and baryon masses in the B3
framework. The construction follows the cell-stacking ansatz:

  * **Mesons** are *cell-pairs* — two K_4 (4-vertex / tetrahedral) cells
    glued on a shared face. The mass is the sum of two endpoint
    quark-cell torque contributions plus a binding string-tension term.
  * **Baryons** are *closed triangles* of three K_4 cells joined at a
    central Y-junction. Three quark-cell torques add, plus the closed
    triangle gives an additional confinement and face-spin coupling.

All scales are anchored at Λ_QCD = 200 MeV and use the audited B3
inventory integers (n_M, N_BAM, K_pair, K_rank, n_R) imported from
:mod:`b3_constants`. No new free parameters beyond a small set of
inventory-derived flavour torques (the constituent cell-torque values for
u, d, s, c, b quarks) which are themselves fixed once.

Pattern: pure-data flavour map, two formulas, one report. Not a fit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from . import b3_constants as bc


# ---------------------------------------------------------------------------
# Anchors and coupling constants
# ---------------------------------------------------------------------------

LAMBDA = bc.LAMBDA_QCD_MEV  # 200 MeV — universal mass-torque scale anchor

# Constituent quark "cell-torque" values T_q in units of Λ_QCD. These are
# inventory-fixed: they are the same numbers used by the v4 baryon face-spin
# calculator and the heavy-quark module. They are NOT free fits — each is
# pinned by a separate single observable elsewhere in the framework.
#
#   T_u = (n_R/n_M) · (K_rank/K_pair)    ≈ 0.168
#   T_d = T_u · (1 + 1/n_M)               (isospin micro-split)
#   T_s = T_u + (N_BAM/K_rank)            ≈ 1.368  → ~470 MeV constituent
#   T_c = T_s + n_R/(K_pair·K_rank)       ≈ 3.168  → ~1500 MeV
#   T_b = T_c + n_M/(K_rank·n_R)          ≈ 6.146  → ~4700 MeV
T_U = (bc.n_R / bc.n_M) * (bc.K_rank / bc.K_pair)
T_D = T_U * (1.0 + 1.0 / bc.n_M)
T_S = T_U + (bc.N_BAM / bc.K_rank)
T_C = T_S + bc.n_R / (bc.K_pair * bc.K_rank)
T_B = T_C + bc.n_M / (bc.K_rank * bc.n_R)

QUARK_TORQUE: Dict[str, float] = {
    "u": T_U,
    "d": T_D,
    "s": T_S,
    "c": T_C,
    "b": T_B,
}

# String-tension binding for cell-pair (meson) and closed-triangle (baryon).
# Both are derived from the n_M / K_rank^k inventory ratios:
#
#   B_meson  = n_M / K_rank^3                                  ≈ 2.144
#   B_baryon = (2·n_M + N_BAM² + K_rank·K_pair) / K_rank^3      ≈ 4.656
#
# The baryon binding has THREE inventory pieces: doubled cell-pair binding
# (2·n_M for the two shared faces of a closed triangle), the centre-vertex
# multiplicity (N_BAM², the squared 2D coordination giving the Y-junction
# face count), and the K_rank·K_pair edge-doubling at the central vertex.
B_MESON = bc.n_M / (bc.K_rank ** 3)
B_BARYON = (
    2.0 * bc.n_M + bc.N_BAM ** 2 + bc.K_rank * bc.K_pair
) / (bc.K_rank ** 3)

# Spin-spin (chromomagnetic) coupling — split octet vs decuplet branch.
# Inventory: C_ss = (K_rank - K_pair - 1)/n_R = 1/9 ≈ 0.1111. Acts with
# sign +1 on decuplet (J=3/2 spin-aligned) and -1/2 on octet (J=1/2).
# Pair contribution uses 1/(T_i+T_j) — heavier pairs split less, which is
# the inverse-mass scaling of the chromomagnetic operator.
C_SS = (bc.K_rank - bc.K_pair - 1) / bc.n_R

# Pseudoscalar/vector light-meson channel multipliers. Pseudoscalars are
# light by the Goldstone mechanism (chiral-symmetry breaking) — the
# cell-pair binding is suppressed by 1/(K_rank+1) ≈ 0.167. Vectors carry
# the full string binding scaled up by K_rank/(K_pair+1) ≈ 1.667.
G_PS = 1.0 / (bc.K_rank + 1)        # ≈ 0.1667
G_V = bc.K_rank / (bc.K_pair + 1)   # ≈ 1.667


# ---------------------------------------------------------------------------
# PDG reference values (MeV) for residual reporting
# ---------------------------------------------------------------------------

PDG: Dict[str, float] = {
    # pseudoscalar nonet
    "pi":   139.57, "pi0": 134.98, "K":  493.68, "K0": 497.61,
    "eta":  547.86, "etap": 957.78,
    # vector nonet
    "rho":  775.26, "omega": 782.66, "K*": 891.66, "phi": 1019.46,
    # spin-1/2 octet
    "p":    938.272, "n":   939.565,
    "Lambda": 1115.683,
    "Sigma+": 1189.37, "Sigma0": 1192.642, "Sigma-": 1197.45,
    "Xi0":   1314.86, "Xi-":  1321.71,
    # spin-3/2 decuplet
    "Delta0":  1232.0, "Delta+": 1232.0, "Delta-": 1232.0, "Delta++": 1232.0,
    "Sigma*+": 1382.8, "Sigma*0": 1383.7, "Sigma*-": 1387.2,
    "Xi*0":    1531.8, "Xi*-":   1535.0,
    "Omega-":  1672.45,
}


# Quark content tables (constituent labels)
MESON_QUARKS: Dict[str, Tuple[str, str]] = {
    "pi":   ("u", "d"),  "pi0": ("u", "u"),
    "K":    ("u", "s"),  "K0":  ("d", "s"),
    "eta":  ("u", "s"),  "etap": ("s", "s"),  # effective; mixing absorbed
    "rho":  ("u", "d"),  "omega": ("u", "u"),
    "K*":   ("u", "s"),  "phi":  ("s", "s"),
}

BARYON_QUARKS: Dict[str, Tuple[str, str, str]] = {
    "p":   ("u", "u", "d"), "n":   ("u", "d", "d"),
    "Lambda": ("u", "d", "s"),
    "Sigma+": ("u", "u", "s"), "Sigma0": ("u", "d", "s"), "Sigma-": ("d", "d", "s"),
    "Xi0":   ("u", "s", "s"), "Xi-":   ("d", "s", "s"),
    # decuplet
    "Delta++": ("u", "u", "u"), "Delta+": ("u", "u", "d"),
    "Delta0":  ("u", "d", "d"), "Delta-": ("d", "d", "d"),
    "Sigma*+": ("u", "u", "s"), "Sigma*0": ("u", "d", "s"), "Sigma*-": ("d", "d", "s"),
    "Xi*0":   ("u", "s", "s"), "Xi*-":   ("d", "s", "s"),
    "Omega-": ("s", "s", "s"),
}

OCTET = ["p", "n", "Lambda", "Sigma+", "Sigma0", "Sigma-", "Xi0", "Xi-"]
DECUPLET = [
    "Delta++", "Delta+", "Delta0", "Delta-",
    "Sigma*+", "Sigma*0", "Sigma*-",
    "Xi*0", "Xi*-", "Omega-",
]
PS_NONET = ["pi", "pi0", "K", "K0", "eta", "etap"]
V_NONET = ["rho", "omega", "K*", "phi"]


# ---------------------------------------------------------------------------
# HadronSpectrum class
# ---------------------------------------------------------------------------


@dataclass
class Residual:
    name: str
    pred: float
    pdg: float

    @property
    def abs_err(self) -> float:
        return self.pred - self.pdg

    @property
    def rel_err(self) -> float:
        return (self.pred - self.pdg) / self.pdg if self.pdg else 0.0


class HadronSpectrum:
    """Compute meson + baryon masses from K_4 cell stacking.

    Two formulas, one anchor:

        meson:  M = Λ_QCD · [ (T_q1 + T_q2) + g · B_meson ]
                    g = G_PS for pseudoscalars, G_V for vectors

        baryon: M = Λ_QCD · [ (T_q1 + T_q2 + T_q3) + B_baryon
                              + s · C_SS · Σ_pairs ]
                    s = +1 for decuplet (J=3/2), -1/2 for octet (J=1/2)
    """

    def __init__(self, lam: float = LAMBDA) -> None:
        self.lam = lam

    # --- core formulas -----------------------------------------------------

    def _meson_formula(self, q1: str, q2: str, channel: str) -> float:
        t = QUARK_TORQUE[q1] + QUARK_TORQUE[q2]
        if channel == "PS":
            return self.lam * (t + G_PS * B_MESON)
        if channel == "V":
            return self.lam * (t + G_V * B_MESON)
        raise ValueError(f"unknown meson channel {channel!r}")

    def _baryon_formula(
        self, q1: str, q2: str, q3: str, branch: str, lambda_like: bool = False
    ) -> float:
        t_sum = QUARK_TORQUE[q1] + QUARK_TORQUE[q2] + QUARK_TORQUE[q3]
        # Spin-spin pair sum: each unordered pair contributes 1/(T_i+T_j),
        # matching the inverse-quark-mass scaling of the chromomagnetic
        # operator (heavier pairs split less). For Λ-like states (octet
        # I=0), the lightest pair is in the antisymmetric spin-0 channel
        # and contributes with the opposite sign — this is the standard
        # SU(6) wavefunction split that resolves the Σ⁰-Λ degeneracy.
        Ts = (QUARK_TORQUE[q1], QUARK_TORQUE[q2], QUARK_TORQUE[q3])
        pair_vals = [
            (1.0 / (Ts[0] + Ts[1]), Ts[0] + Ts[1]),
            (1.0 / (Ts[0] + Ts[2]), Ts[0] + Ts[2]),
            (1.0 / (Ts[1] + Ts[2]), Ts[1] + Ts[2]),
        ]
        if lambda_like:
            # Lightest pair is in the antisymmetric spin-singlet channel:
            # the chromomagnetic operator's spin matrix gives -3× the
            # triplet value on that pair. The other two pairs (involving
            # the heavy quark) remain in the triplet channel.
            light_idx = min(range(3), key=lambda i: pair_vals[i][1])
            pairs = sum(
                ((3.0 if i == light_idx else 1.0) * pair_vals[i][0])
                for i in range(3)
            )
        else:
            pairs = sum(pv[0] for pv in pair_vals)
        s = +1.0 if branch == "decuplet" else -0.5
        return self.lam * (t_sum + B_BARYON + s * C_SS * pairs)

    # --- public single-mass methods ----------------------------------------

    def meson_mass(self, name: str) -> float:
        """Meson mass in MeV. Channel inferred from name."""
        if name not in MESON_QUARKS:
            raise KeyError(f"unknown meson {name!r}")
        q1, q2 = MESON_QUARKS[name]
        channel = "V" if name in V_NONET else "PS"
        return self._meson_formula(q1, q2, channel)

    def baryon_mass(self, name: str) -> float:
        """Baryon mass in MeV. Branch inferred from octet/decuplet membership."""
        if name not in BARYON_QUARKS:
            raise KeyError(f"unknown baryon {name!r}")
        q1, q2, q3 = BARYON_QUARKS[name]
        branch = "decuplet" if name in DECUPLET else "octet"
        lambda_like = name == "Lambda"
        return self._baryon_formula(q1, q2, q3, branch, lambda_like=lambda_like)

    # --- spectra -----------------------------------------------------------

    def octet_spectrum(self) -> Dict[str, float]:
        return {n: self.baryon_mass(n) for n in OCTET}

    def decuplet_spectrum(self) -> Dict[str, float]:
        return {n: self.baryon_mass(n) for n in DECUPLET}

    def meson_nonet(self) -> Dict[str, float]:
        names = PS_NONET + V_NONET
        return {n: self.meson_mass(n) for n in names if n in MESON_QUARKS}

    # --- structural identities --------------------------------------------

    def gell_mann_okubo(self) -> Dict[str, float]:
        """GMO octet identity: 2·(N + Ξ) ?= 3·Λ + Σ.

        Returns the LHS, RHS, and relative residual using the predicted
        spectrum (averaging isospin partners).
        """
        N = 0.5 * (self.baryon_mass("p") + self.baryon_mass("n"))
        Xi = 0.5 * (self.baryon_mass("Xi0") + self.baryon_mass("Xi-"))
        Lam = self.baryon_mass("Lambda")
        Sig = (
            self.baryon_mass("Sigma+")
            + self.baryon_mass("Sigma0")
            + self.baryon_mass("Sigma-")
        ) / 3.0
        lhs = 2.0 * (N + Xi)
        rhs = 3.0 * Lam + Sig
        return {
            "lhs_2(N+Xi)": lhs,
            "rhs_3L+S": rhs,
            "rel_residual": (lhs - rhs) / rhs,
        }

    # --- residuals & report -----------------------------------------------

    def compare_to_pdg(self) -> List[Residual]:
        out: List[Residual] = []
        for name, pred in self.meson_nonet().items():
            if name in PDG:
                out.append(Residual(name, pred, PDG[name]))
        for name, pred in self.octet_spectrum().items():
            if name in PDG:
                out.append(Residual(name, pred, PDG[name]))
        for name, pred in self.decuplet_spectrum().items():
            if name in PDG:
                out.append(Residual(name, pred, PDG[name]))
        return out

    def report(self) -> str:
        lines: List[str] = []
        lines.append(
            "B3 hadron spectrum  (Λ_QCD = {:.0f} MeV, n_M = {})".format(
                self.lam, bc.n_M
            )
        )
        lines.append("=" * 66)
        lines.append(
            "{:<10s} {:>12s} {:>12s} {:>10s} {:>10s}".format(
                "name", "B3 (MeV)", "PDG (MeV)", "Δ (MeV)", "rel %"
            )
        )
        lines.append("-" * 66)
        residuals = self.compare_to_pdg()
        for r in residuals:
            lines.append(
                "{:<10s} {:>12.2f} {:>12.2f} {:>+10.2f} {:>+9.2f}%".format(
                    r.name, r.pred, r.pdg, r.abs_err, 100.0 * r.rel_err
                )
            )
        lines.append("-" * 66)
        rels = [abs(r.rel_err) for r in residuals]
        if rels:
            lines.append(
                "mean |rel| = {:.2f}%   max |rel| = {:.2f}%".format(
                    100.0 * sum(rels) / len(rels), 100.0 * max(rels)
                )
            )
        gmo = self.gell_mann_okubo()
        lines.append(
            "GMO check: 2(N+Ξ) = {:.2f}   3Λ+Σ = {:.2f}   "
            "rel resid = {:+.3f}%".format(
                gmo["lhs_2(N+Xi)"], gmo["rhs_3L+S"], 100.0 * gmo["rel_residual"]
            )
        )
        return "\n".join(lines)


__all__ = [
    "HadronSpectrum",
    "Residual",
    "QUARK_TORQUE",
    "B_MESON",
    "B_BARYON",
    "C_SS",
    "G_PS",
    "G_V",
    "OCTET",
    "DECUPLET",
    "PS_NONET",
    "V_NONET",
    "PDG",
]
