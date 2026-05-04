"""Debye-temperature predictions vs measured Θ_D for 14 elemental solids.

Tests the substrate phonon-dispersion picture by checking whether the
substrate-derived sound speed c_s = sqrt(K/ρ) -- when fed into the standard
Debye formula

    Θ_D = (ℏ / k_B) · c_s · (6 π² n)^(1/3)

reproduces measured Debye temperatures across a benchmark set of solids
spanning ~14× in Θ_D (Pb 105 K -> diamond 2230 K).

WHAT THE TEST IS ACTUALLY MEASURING
-----------------------------------
The substrate Lagrangian L = (ρ/2)(∂_t φ)² - (K/2)(∇φ)² gives
c_s = sqrt(K/ρ) at long wavelength (`PhononDispersion.sound_speed`). The
Debye temperature follows by counting modes up to the Brillouin-zone radius
k_D = (6 π² n)^(1/3) and identifying ω_D = c_s · k_D.

For each material we use:
  * the Debye-averaged sound speed from elastic constants
        c_s = ((1/c_L³ + 2/c_T³) / 3)^(-1/3)
    where c_L = sqrt((B + 4G/3)/ρ) is the longitudinal speed,
          c_T = sqrt(G/ρ)           is the transverse speed,
    with bulk modulus B and shear modulus G from CRC Handbook (90th ed.).
  * the atomic number density n = N_A · ρ_mass / M_molar.

Comparing predicted Θ_D against measured Θ_D is a SHARP test of the
Lagrangian's elastic structure: it asks whether the long-wavelength
acoustic dispersion ω(k) = c_s · k -- which is forced by the substrate
kinetic and gradient terms -- correctly predicts the high-frequency
zone-boundary cutoff that controls the heat capacity.

HONEST CAVEAT
-------------
Per material we use the EXPERIMENTAL bulk and shear moduli to compute c_s,
not a substrate-derived (B, G) -- so the test is on the structure of the
formula (Debye averaging + zone-boundary scaling), NOT on a parameter-free
prediction of the moduli themselves. A failure here would still falsify
the substrate Lagrangian's kinematic content; a success means only that
the kinematic content is consistent with measured elasticity, not that
the moduli are derived. This is the same calibration used by Ashcroft &
Mermin Chapter 23.

The 14 materials cover FCC (Cu, Al, Au, Ag, Ni, Pb), BCC (Fe, W),
diamond cubic (C, Si, Ge), HCP (Be, Mg), and tetragonal (Sn) lattices.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


# --------------------------------------------------------------------------- #
# Physical constants (SI)                                                     #
# --------------------------------------------------------------------------- #

HBAR: float = 1.054571817e-34   # J·s
KB: float = 1.380649e-23        # J/K
N_A: float = 6.02214076e23      # 1/mol


# --------------------------------------------------------------------------- #
# Material database                                                           #
# --------------------------------------------------------------------------- #
#
# All numbers are CRC Handbook of Chemistry and Physics (90th ed., 2009-2010)
# unless noted otherwise. Values picked to match the Θ_D reference values in
# Ashcroft & Mermin Table 23.2 (column 2: low-temperature heat-capacity Θ_D).
#
# Fields per material:
#   M_molar    : molar mass in kg/mol
#   rho_mass   : mass density at room temperature in kg/m³
#   B_GPa      : isothermal bulk modulus, GPa
#   G_GPa      : shear (Voigt-Reuss-Hill) modulus, GPa
#   theta_D_K  : measured Debye temperature, K (Ashcroft-Mermin / Kittel)
#   lattice    : crystal structure label (informational only)
#
# Where multiple polymorphs exist (Sn: white = β-Sn at RT; C: diamond) we
# pick the room-temperature stable phase consistent with the Θ_D quoted in
# the standard tables.

@dataclass(frozen=True)
class Material:
    name: str
    M_molar: float       # kg/mol
    rho_mass: float      # kg/m³
    B_GPa: float
    G_GPa: float
    theta_D_K: float     # measured
    lattice: str

    @property
    def n_atoms_per_m3(self) -> float:
        """Atomic number density: N_A · ρ / M."""
        return N_A * self.rho_mass / self.M_molar


MATERIALS: Dict[str, Material] = {
    # FCC metals
    "Copper":     Material("Copper",     0.06355,  8960.0, 140.0,  48.0,  343.0, "FCC"),
    "Aluminum":   Material("Aluminum",   0.02698,  2700.0,  76.0,  26.0,  428.0, "FCC"),
    "Gold":       Material("Gold",       0.19697, 19300.0, 180.0,  27.0,  165.0, "FCC"),
    "Silver":     Material("Silver",     0.10787, 10490.0, 100.0,  30.0,  225.0, "FCC"),
    "Nickel":     Material("Nickel",     0.05869,  8908.0, 180.0,  76.0,  450.0, "FCC"),
    "Lead":       Material("Lead",       0.20720, 11340.0,  46.0,   5.6,  105.0, "FCC"),

    # BCC metals
    "Iron":       Material("Iron",       0.05585,  7874.0, 170.0,  82.0,  470.0, "BCC"),
    "Tungsten":   Material("Tungsten",   0.18384, 19250.0, 310.0, 161.0,  400.0, "BCC"),

    # Diamond-cubic covalent
    "Diamond":    Material("Diamond",    0.01201,  3515.0, 442.0, 478.0, 2230.0, "diamond"),
    "Silicon":    Material("Silicon",    0.02809,  2329.0,  98.0,  66.0,  645.0, "diamond"),
    "Germanium":  Material("Germanium",  0.07264,  5323.0,  75.0,  55.0,  374.0, "diamond"),

    # HCP metals
    "Beryllium":  Material("Beryllium",  0.00901,  1850.0, 130.0, 132.0, 1440.0, "HCP"),
    "Magnesium":  Material("Magnesium",  0.02431,  1738.0,  45.0,  17.0,  400.0, "HCP"),

    # White tin (β-Sn, body-centered tetragonal, room-temperature stable)
    "Tin":        Material("Tin",        0.11871,  7287.0,  58.0,  18.0,  200.0, "tetragonal"),
}


# --------------------------------------------------------------------------- #
# Sound-speed extraction                                                      #
# --------------------------------------------------------------------------- #


def longitudinal_speed(B_GPa: float, G_GPa: float, rho: float) -> float:
    """c_L = sqrt((B + 4G/3) / ρ).  Inputs in GPa, kg/m³.  Output m/s."""
    M = (B_GPa + (4.0 / 3.0) * G_GPa) * 1.0e9     # Pa
    return math.sqrt(M / rho)


def transverse_speed(G_GPa: float, rho: float) -> float:
    """c_T = sqrt(G / ρ).  Inputs in GPa, kg/m³.  Output m/s."""
    return math.sqrt(G_GPa * 1.0e9 / rho)


def debye_average_speed(c_L: float, c_T: float) -> float:
    """Debye-averaged sound speed: 3/c_s³ = 1/c_L³ + 2/c_T³."""
    return (3.0 / (1.0 / c_L ** 3 + 2.0 / c_T ** 3)) ** (1.0 / 3.0)


def material_sound_speeds(mat: Material) -> Tuple[float, float, float]:
    """Return (c_L, c_T, c_Debye) for a material in m/s."""
    c_L = longitudinal_speed(mat.B_GPa, mat.G_GPa, mat.rho_mass)
    c_T = transverse_speed(mat.G_GPa, mat.rho_mass)
    c_D = debye_average_speed(c_L, c_T)
    return c_L, c_T, c_D


# --------------------------------------------------------------------------- #
# Debye-temperature prediction                                                #
# --------------------------------------------------------------------------- #


def debye_temperature(c_s: float, n_atoms_per_m3: float) -> float:
    """Standard Debye formula Θ_D = (ℏ/k_B) · c_s · (6 π² n)^(1/3)."""
    omega_D = c_s * (6.0 * math.pi ** 2 * n_atoms_per_m3) ** (1.0 / 3.0)
    return HBAR * omega_D / KB


def predict_theta_D(mat: Material) -> Dict[str, float]:
    """Run the substrate-Lagrangian Debye prediction for one material."""
    c_L, c_T, c_D = material_sound_speeds(mat)
    n = mat.n_atoms_per_m3
    theta_pred = debye_temperature(c_D, n)
    theta_meas = mat.theta_D_K
    rel_err = (theta_pred - theta_meas) / theta_meas
    return {
        "name":       mat.name,
        "lattice":    mat.lattice,
        "rho_mass":   mat.rho_mass,
        "B_GPa":      mat.B_GPa,
        "G_GPa":      mat.G_GPa,
        "n_atoms":    n,
        "c_L":        c_L,
        "c_T":        c_T,
        "c_Debye":    c_D,
        "theta_pred": theta_pred,
        "theta_meas": theta_meas,
        "rel_err":    rel_err,
    }


def run_test() -> Dict[str, object]:
    """Compute predictions for every material; return rows + summary stats."""
    rows: Dict[str, Dict[str, float]] = {}
    pred_arr: List[float] = []
    meas_arr: List[float] = []
    for name, mat in MATERIALS.items():
        row = predict_theta_D(mat)
        rows[name] = row
        pred_arr.append(row["theta_pred"])
        meas_arr.append(row["theta_meas"])

    pred = np.asarray(pred_arr)
    meas = np.asarray(meas_arr)
    rel = (pred - meas) / meas

    # Pearson correlation
    pm = pred - pred.mean()
    mm = meas - meas.mean()
    denom = math.sqrt(float((pm * pm).sum()) * float((mm * mm).sum()))
    pearson_r = float((pm * mm).sum()) / denom if denom > 0.0 else float("nan")

    # Log-space (geometric) Pearson, since Θ_D varies over 14×
    lp = np.log(pred)
    lm = np.log(meas)
    lpm = lp - lp.mean()
    lmm = lm - lm.mean()
    ldenom = math.sqrt(float((lpm * lpm).sum()) * float((lmm * lmm).sum()))
    pearson_log_r = (
        float((lpm * lmm).sum()) / ldenom if ldenom > 0.0 else float("nan")
    )

    # Linear regression in log-log space (slope of log(pred) vs log(meas))
    slope, intercept = np.polyfit(lm, lp, 1)

    # Per-material agreement classes
    materials_within_5pct = sum(1 for r in rel if abs(r) <= 0.05)
    materials_within_10pct = sum(1 for r in rel if abs(r) <= 0.10)
    materials_within_20pct = sum(1 for r in rel if abs(r) <= 0.20)

    summary = {
        "n_materials":            len(rows),
        "mean_rel_err":           float(rel.mean()),
        "mean_abs_rel_err":       float(np.abs(rel).mean()),
        "median_abs_rel_err":     float(np.median(np.abs(rel))),
        "max_abs_rel_err":        float(np.abs(rel).max()),
        "max_rel_err_material":   list(rows.keys())[int(np.argmax(np.abs(rel)))],
        "rms_rel_err":            float(np.sqrt((rel * rel).mean())),
        "pearson_r":              pearson_r,
        "pearson_log_r":          pearson_log_r,
        "loglog_slope":           float(slope),
        "loglog_intercept":       float(intercept),
        "within_5pct":            materials_within_5pct,
        "within_10pct":           materials_within_10pct,
        "within_20pct":           materials_within_20pct,
    }
    return {"rows": rows, "summary": summary}


# --------------------------------------------------------------------------- #
# Visual rendering                                                            #
# --------------------------------------------------------------------------- #


def render_debye_test(out_path: str | None = None) -> str:
    """Render visuals/124_debye_test.png: predicted vs measured Θ_D scatter
    plus per-material residual bar chart."""
    import matplotlib.pyplot as plt
    from pathlib import Path

    if out_path is None:
        out_path = str(
            Path(__file__).resolve().parents[2]
            / "visuals" / "124_debye_test.png"
        )

    res = run_test()
    rows = res["rows"]
    summary = res["summary"]

    names = list(rows.keys())
    pred = np.array([rows[n]["theta_pred"] for n in names])
    meas = np.array([rows[n]["theta_meas"] for n in names])
    rel = (pred - meas) / meas
    lattice = [rows[n]["lattice"] for n in names]
    lattice_set = sorted(set(lattice))
    palette = {
        "FCC":         "#1f77b4",
        "BCC":         "#d62728",
        "diamond":     "#2ca02c",
        "HCP":         "#ff7f0e",
        "tetragonal":  "#9467bd",
    }
    colors = [palette.get(L, "#7f7f7f") for L in lattice]

    fig, (ax_sc, ax_bar) = plt.subplots(
        1, 2, figsize=(15.5, 7.0), gridspec_kw={"width_ratios": [1.1, 1.4]}
    )

    # ---------- left: predicted vs measured (log-log) ----------
    for L in lattice_set:
        idx = [i for i, l in enumerate(lattice) if l == L]
        ax_sc.loglog(
            meas[idx], pred[idx], "o", markersize=10,
            color=palette.get(L, "#7f7f7f"), label=f"{L}",
            markeredgecolor="black", markeredgewidth=0.5,
        )
    lim = [50.0, 3000.0]
    ax_sc.plot(lim, lim, "k--", alpha=0.7, label="y = x (perfect)")
    ax_sc.plot(lim, [v * 1.1 for v in lim], "k:", alpha=0.4, label="±10%")
    ax_sc.plot(lim, [v / 1.1 for v in lim], "k:", alpha=0.4)
    for n, m, p in zip(names, meas, pred):
        ax_sc.annotate(
            n, (m, p), xytext=(5, 4), textcoords="offset points", fontsize=8
        )
    ax_sc.set_xlim(lim)
    ax_sc.set_ylim(lim)
    ax_sc.set_xlabel(r"measured $\Theta_D$ [K]  (Ashcroft-Mermin / Kittel)")
    ax_sc.set_ylabel(r"substrate-predicted $\Theta_D$ [K]")
    ax_sc.set_aspect("equal", "box")
    ax_sc.set_title(
        "Substrate-Lagrangian Debye-temperature prediction\n"
        f"mean |rel err| = {summary['mean_abs_rel_err']:.1%}, "
        f"log-log slope = {summary['loglog_slope']:.3f}, "
        f"r(log) = {summary['pearson_log_r']:.4f}"
    )
    ax_sc.legend(loc="upper left", fontsize=9)
    ax_sc.grid(True, which="both", alpha=0.3)

    # ---------- right: per-material residual bar chart ----------
    order = np.argsort(rel)
    names_o = [names[i] for i in order]
    rel_o = rel[order]
    colors_o = [colors[i] for i in order]
    y = np.arange(len(names_o))
    ax_bar.barh(y, rel_o * 100.0, color=colors_o, edgecolor="black", linewidth=0.4)
    ax_bar.axvline(0.0, color="black", linewidth=1.2)
    ax_bar.axvline(5.0, color="grey", linestyle=":", linewidth=0.8)
    ax_bar.axvline(-5.0, color="grey", linestyle=":", linewidth=0.8)
    ax_bar.axvline(10.0, color="grey", linestyle="--", linewidth=0.8)
    ax_bar.axvline(-10.0, color="grey", linestyle="--", linewidth=0.8)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(names_o, fontsize=10)
    ax_bar.set_xlabel(r"$(\Theta_D^{\rm pred}/\Theta_D^{\rm meas} - 1)$ [%]")
    ax_bar.set_title(
        "Per-material residual\n"
        f"{summary['within_5pct']}/{summary['n_materials']} within 5%, "
        f"{summary['within_10pct']}/{summary['n_materials']} within 10%, "
        f"{summary['within_20pct']}/{summary['n_materials']} within 20%"
    )
    ax_bar.grid(True, axis="x", alpha=0.3)
    # Worst-case annotation
    worst = summary["max_rel_err_material"]
    ax_bar.text(
        0.98, 0.02,
        f"worst residual: {worst}  ({summary['max_abs_rel_err']:+.1%})",
        transform=ax_bar.transAxes, ha="right", va="bottom", fontsize=9,
        bbox=dict(facecolor="white", edgecolor="grey", alpha=0.8),
    )

    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


# --------------------------------------------------------------------------- #
# CLI entrypoint                                                              #
# --------------------------------------------------------------------------- #


def main() -> None:
    res = run_test()
    rows = res["rows"]
    summary = res["summary"]

    print("Substrate phonon Debye-temperature test (14 materials)")
    print("=" * 88)
    print(
        f"{'Material':<12}{'lat.':<6}{'c_L (m/s)':>10}{'c_T (m/s)':>10}"
        f"{'c_D (m/s)':>10}{'Θ_pred [K]':>13}{'Θ_meas [K]':>13}{'rel err':>10}"
    )
    for name, row in rows.items():
        print(
            f"{name:<12}{row['lattice']:<6}"
            f"{row['c_L']:>10.0f}{row['c_T']:>10.0f}{row['c_Debye']:>10.0f}"
            f"{row['theta_pred']:>13.1f}{row['theta_meas']:>13.1f}"
            f"{row['rel_err']:>+10.2%}"
        )

    print()
    print("Summary")
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k:<24} {v:+.5f}")
        else:
            print(f"  {k:<24} {v}")


if __name__ == "__main__":
    main()
