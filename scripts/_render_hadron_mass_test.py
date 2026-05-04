"""Renderer for the substrate-vs-PDG-2024 hadron-mass test.

Produces:
    visuals/122_hadron_mass_test.png
        Two-panel diagnostic: (top) predicted vs PDG bar chart with
        residual labels; (bottom) per-family residual scatter coloured by
        family, with mean|Δ| reference lines.

Run standalone:
    python scripts/_render_hadron_mass_test.py
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

VISUALS_DIR = os.path.join(ROOT, "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)


def _save(fig, name: str) -> str:
    path = os.path.join(VISUALS_DIR, name)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


# Stable per-family colour map.
FAMILY_COLOUR = {
    "octet":   "#1f77b4",  # blue
    "decuplet": "#2ca02c",  # green
    "light_ps": "#d62728",  # red
    "light_v":  "#ff7f0e",  # orange
    "heavy":    "#9467bd",  # purple
}

FAMILY_LABEL = {
    "octet":   "spin-1/2 octet baryons",
    "decuplet": "spin-3/2 decuplet baryons",
    "light_ps": "light pseudoscalar mesons",
    "light_v":  "light vector mesons",
    "heavy":    "heavy quarkonia (cc̄, bb̄)",
}


def render_hadron_mass_test() -> list[str]:
    """Produce 122_hadron_mass_test.png.

    Three-panel diagnostic:
      A. Bare / Cornell+chiral / PDG mass bar comparison (log-y).
      B. Per-hadron residual scatter, both bare and corrected overlaid.
      C. Per-family bare-vs-corrected mean|Δ| paired bar chart.
    """
    from src.stiff_medium.hadron_mass_test import run_hadron_mass_test

    rpt = run_hadron_mass_test()
    residuals = rpt.residuals

    # Sort by family then by PDG mass for a clean reading order.
    family_order = ("octet", "decuplet", "light_ps", "light_v", "heavy")
    by_family = {f: [] for f in family_order}
    for r in residuals:
        by_family[r.family].append(r)
    for f in family_order:
        by_family[f].sort(key=lambda r: r.pdg_mev)

    ordered = [r for f in family_order for r in by_family[f]]
    names = [r.name for r in ordered]
    pred_bare = np.array([r.pred_mev for r in ordered])
    pred_corr = np.array([
        r.pred_corrected_mev if r.pred_corrected_mev is not None else r.pred_mev
        for r in ordered
    ])
    pdg = np.array([r.pdg_mev for r in ordered])
    rel_bare = np.array([100.0 * r.rel_err for r in ordered])
    rel_corr = np.array([
        100.0 * (r.rel_err_corrected if r.rel_err_corrected is not None else r.rel_err)
        for r in ordered
    ])
    bar_colours = [FAMILY_COLOUR[r.family] for r in ordered]

    # ------------------------------------------------------------------
    # Figure: 3 rows x 1 col
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(17, 13))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.4, 1.0, 0.7], hspace=0.42)

    # ---- Panel A: bare / corrected / PDG triple-bar (log-y) ----
    ax_top = fig.add_subplot(gs[0, 0])
    x = np.arange(len(names))
    w = 0.27
    ax_top.bar(
        x - w, pdg, width=w,
        color="lightgray", edgecolor="black", linewidth=0.5,
        label="PDG 2024",
    )
    ax_top.bar(
        x, pred_bare, width=w,
        color=bar_colours, edgecolor="black", linewidth=0.5,
        alpha=0.55,
        label="B3 bare (cell-stacking only)",
    )
    ax_top.bar(
        x + w, pred_corr, width=w,
        color=bar_colours, edgecolor="black", linewidth=1.0,
        hatch="///", label="B3 + Cornell + chiral",
    )
    y_top = max(pdg.max(), pred_bare.max(), pred_corr.max())
    # Residual % labels (corrected) above each triple
    for i, r in enumerate(ordered):
        rel = r.rel_err_corrected if r.rel_err_corrected is not None else r.rel_err
        col = "tab:red" if abs(rel) > 0.10 else "tab:green" if abs(rel) < 0.05 else "black"
        ax_top.text(
            x[i], max(pdg[i], pred_corr[i]) * 1.12,
            f"{100.0 * rel:+.1f}%",
            ha="center", va="bottom", fontsize=7,
            color=col, weight="bold",
        )
    ax_top.set_yscale("log")
    ax_top.set_xticks(x)
    ax_top.set_xticklabels(names, rotation=55, ha="right", fontsize=9)
    ax_top.set_ylabel("mass [MeV, log scale]", fontsize=11)
    ax_top.set_ylim(80.0, y_top * 4.5)
    ax_top.set_title(
        f"Substrate hadron mass predictions vs PDG 2024  "
        f"(bare mean|Δ|={100.0 * rpt.mean_abs_rel:.2f}%, "
        f"corrected mean|Δ|={100.0 * rpt.mean_abs_rel_corrected:.2f}%, "
        f"Λ_QCD = 200 MeV, σ = 9/2 · Λ² = 0.18 GeV²)",
        fontsize=12,
    )
    handles = [
        plt.Rectangle((0, 0), 1, 1, color="lightgray", ec="black"),
        plt.Rectangle((0, 0), 1, 1, color="gray", ec="black", alpha=0.55),
        plt.Rectangle((0, 0), 1, 1, color="gray", ec="black", hatch="///"),
    ]
    labels = ["PDG 2024", "B3 bare", "B3 + Cornell + chiral"]
    ax_top.legend(handles, labels, loc="upper left", fontsize=9,
                  framealpha=0.92)
    ax_top.grid(True, alpha=0.3, axis="y", which="both")

    # ---- Panel B: residual scatter (bare vs corrected, overlaid) ----
    ax_mid = fig.add_subplot(gs[1, 0])
    for f in family_order:
        members = by_family[f]
        if not members:
            continue
        idxs = [names.index(r.name) for r in members]
        rs_bare = [100.0 * r.rel_err for r in members]
        rs_corr = [
            100.0 * (r.rel_err_corrected if r.rel_err_corrected is not None else r.rel_err)
            for r in members
        ]
        # Bare marker (open circle)
        ax_mid.scatter(
            idxs, rs_bare, s=70, facecolors="white", edgecolors=FAMILY_COLOUR[f],
            linewidth=1.6, zorder=3,
            label=f"{FAMILY_LABEL[f]} bare",
        )
        # Corrected marker (filled circle)
        ax_mid.scatter(
            idxs, rs_corr, s=80, c=FAMILY_COLOUR[f],
            edgecolor="black", linewidth=0.8, zorder=4,
            label=f"{FAMILY_LABEL[f]} corrected",
        )
        # Connecting arrows for those that move
        for i, m in enumerate(members):
            if abs(rs_bare[i] - rs_corr[i]) > 0.1:
                ax_mid.annotate(
                    "", xy=(idxs[i], rs_corr[i]), xytext=(idxs[i], rs_bare[i]),
                    arrowprops=dict(arrowstyle="->", color=FAMILY_COLOUR[f],
                                    lw=0.8, alpha=0.6),
                )
    ax_mid.axhline(0.0, color="black", linewidth=0.8)
    ax_mid.axhspan(-5.0, 5.0, color="green", alpha=0.10, label="±5% band")
    ax_mid.axhspan(-1.0, 1.0, color="gray", alpha=0.20)
    ax_mid.set_xticks(np.arange(len(names)))
    ax_mid.set_xticklabels(names, rotation=55, ha="right", fontsize=9)
    ax_mid.set_ylabel("residual  (B3 − PDG) / PDG  [%]", fontsize=11)
    ax_mid.set_title(
        "Per-hadron residuals: bare (open) → corrected (filled), arrows show shift",
        fontsize=11,
    )
    ax_mid.legend(loc="lower left", fontsize=7, framealpha=0.92, ncol=3)
    ax_mid.grid(True, alpha=0.3)
    ax_mid.set_ylim(-80.0, 35.0)

    # ---- Panel C: per-family mean|Δ| bare vs corrected ----
    ax_bot = fig.add_subplot(gs[2, 0])
    fs_bare = {f.family: f for f in rpt.family_stats(corrected=False)}
    fs_corr = {f.family: f for f in rpt.family_stats(corrected=True)}
    fams = list(family_order)
    fx = np.arange(len(fams))
    bw = 0.4
    bare_vals = [100.0 * fs_bare[f].mean_abs_rel for f in fams]
    corr_vals = [100.0 * fs_corr[f].mean_abs_rel for f in fams]
    ax_bot.bar(
        fx - bw/2.0, bare_vals, width=bw,
        color=[FAMILY_COLOUR[f] for f in fams], alpha=0.55,
        edgecolor="black", linewidth=0.6,
        label="bare",
    )
    ax_bot.bar(
        fx + bw/2.0, corr_vals, width=bw,
        color=[FAMILY_COLOUR[f] for f in fams],
        edgecolor="black", linewidth=1.0, hatch="///",
        label="Cornell + chiral",
    )
    for i, f in enumerate(fams):
        ax_bot.text(
            fx[i] - bw/2.0, bare_vals[i] + 0.6,
            f"{bare_vals[i]:.1f}%", ha="center", va="bottom",
            fontsize=8, color="black",
        )
        ax_bot.text(
            fx[i] + bw/2.0, corr_vals[i] + 0.6,
            f"{corr_vals[i]:.1f}%", ha="center", va="bottom",
            fontsize=8, color="darkgreen", weight="bold",
        )
    ax_bot.axhline(5.0, color="green", linestyle="--", linewidth=0.9,
                   label="5% target")
    ax_bot.set_xticks(fx)
    ax_bot.set_xticklabels([FAMILY_LABEL[f] for f in fams], fontsize=9)
    ax_bot.set_ylabel("family mean |Δ|  [%]", fontsize=11)
    ax_bot.set_title(
        "Per-family mean |Δ|: bare cell-stacking vs Cornell + chiral correction",
        fontsize=11,
    )
    ax_bot.legend(loc="upper right", fontsize=9, framealpha=0.92)
    ax_bot.grid(True, alpha=0.3, axis="y")
    ax_bot.set_ylim(0.0, max(bare_vals) * 1.20)

    # Annotation box (right of panel B): summary of derivable vs empirical
    info_lines = [
        "Cornell + chiral extension",
        "─" * 30,
        "Substrate-DERIVED:",
        "  σ = (K_pair·K_rank − 1)/K_pair · Λ²",
        "    = 9/2 · 0.04 = 0.18 GeV² ✓",
        "  GMO m²_η₈ = (4 m²_K − m²_π)/3",
        "  (T_s−T_u)/(2T_u) = 3.57",
        "",
        "EMPIRICAL inputs (not derived):",
        "  α_s(m_c) = 0.30, α_s(m_b) = 0.22",
        "  m_c = 1.32 GeV, m_b = 4.50 GeV",
        "  χ_chiral = 3.5  (kaon m²)",
        "  m_η' = 957.78 MeV (η₁ anchor)",
        "  θ_P = −11°  (mixing angle)",
        "",
        f"Heavy: 51.2% → {100.0*fs_corr['heavy'].mean_abs_rel:.2f}%",
        f"Light PS: 16.3% → {100.0*fs_corr['light_ps'].mean_abs_rel:.2f}%",
        f"OVERALL: {100.0*rpt.mean_abs_rel:.2f}% → {100.0*rpt.mean_abs_rel_corrected:.2f}%",
    ]
    ax_mid.text(
        1.005, 1.0, "\n".join(info_lines),
        transform=ax_mid.transAxes, fontsize=7.0,
        family="monospace", va="top", ha="left",
        bbox=dict(facecolor="white", edgecolor="black",
                  linewidth=0.6, boxstyle="round,pad=0.4"),
    )

    fig.suptitle(
        "Hadron Mass Test (122) — substrate cell-stacking, with and without Cornell + chiral correction",
        fontsize=14, weight="bold",
    )
    return [_save(fig, "122_hadron_mass_test.png")]


if __name__ == "__main__":
    paths = render_hadron_mass_test()
    for p in paths:
        print(p)
