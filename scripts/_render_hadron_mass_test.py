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
    """Produce 122_hadron_mass_test.png."""
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
    pred = np.array([r.pred_mev for r in ordered])
    pdg = np.array([r.pdg_mev for r in ordered])
    rels = np.array([100.0 * r.rel_err for r in ordered])
    bar_colours = [FAMILY_COLOUR[r.family] for r in ordered]

    # ------------------------------------------------------------------
    # Figure: 2 rows x 1 col (predicted-vs-PDG bars + residual scatter)
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.4, 1.0], hspace=0.35)

    # ---- Panel A: predicted vs PDG, log-y, side-by-side bars ----
    ax_top = fig.add_subplot(gs[0, 0])
    x = np.arange(len(names))
    w = 0.40
    ax_top.bar(
        x - w / 2.0, pdg, width=w,
        color="lightgray", edgecolor="black", linewidth=0.6,
        label="PDG 2024",
    )
    ax_top.bar(
        x + w / 2.0, pred, width=w,
        color=bar_colours, edgecolor="black", linewidth=0.6,
        label="substrate K_4 cell-stacking",
    )
    # Residual % labels above each pair.
    y_top = max(pdg.max(), pred.max())
    for i, r in enumerate(ordered):
        col = "tab:red" if abs(r.rel_err) > 0.10 else "black"
        ax_top.text(
            x[i], max(pdg[i], pred[i]) * 1.10,
            f"{100.0 * r.rel_err:+.1f}%",
            ha="center", va="bottom", fontsize=7,
            color=col, rotation=0,
        )
    ax_top.set_yscale("log")
    ax_top.set_xticks(x)
    ax_top.set_xticklabels(names, rotation=55, ha="right", fontsize=9)
    ax_top.set_ylabel("mass [MeV, log scale]", fontsize=11)
    ax_top.set_ylim(80.0, y_top * 4.0)
    ax_top.set_title(
        f"Substrate hadron mass predictions vs PDG 2024  "
        f"(n={rpt.n_total},  overall mean|Δ|={100.0 * rpt.mean_abs_rel:.2f}%,  "
        f"Λ_QCD = 200 MeV)",
        fontsize=12,
    )
    # Family colour legend (dummy patches).
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=FAMILY_COLOUR[f]) for f in family_order
    ]
    handles.append(plt.Rectangle((0, 0), 1, 1, color="lightgray", ec="black"))
    labels = [FAMILY_LABEL[f] for f in family_order] + ["PDG 2024 reference"]
    ax_top.legend(handles, labels, loc="upper left", fontsize=8, ncol=2,
                  framealpha=0.92)
    ax_top.grid(True, alpha=0.3, axis="y", which="both")

    # ---- Panel B: residual scatter by family + mean lines ----
    ax_bot = fig.add_subplot(gs[1, 0])
    for f in family_order:
        members = by_family[f]
        if not members:
            continue
        idxs = [names.index(r.name) for r in members]
        rs = [100.0 * r.rel_err for r in members]
        ax_bot.scatter(
            idxs, rs, s=80, c=FAMILY_COLOUR[f],
            edgecolor="black", linewidth=0.8, zorder=3,
            label=f"{FAMILY_LABEL[f]} (n={len(members)})",
        )
        # Family mean horizontal line spanning that family's x-range.
        if len(idxs) >= 1:
            mean_abs = 100.0 * sum(abs(r.rel_err) for r in members) / len(members)
            x0, x1 = min(idxs) - 0.5, max(idxs) + 0.5
            ax_bot.hlines(
                +mean_abs, x0, x1, colors=FAMILY_COLOUR[f],
                linestyles="dashed", linewidth=1.4, alpha=0.75,
            )
            ax_bot.hlines(
                -mean_abs, x0, x1, colors=FAMILY_COLOUR[f],
                linestyles="dashed", linewidth=1.4, alpha=0.75,
            )
    ax_bot.axhline(0.0, color="black", linewidth=0.8)
    ax_bot.axhspan(-1.0, 1.0, color="gray", alpha=0.10)
    ax_bot.text(
        len(names) - 0.5, 1.5, "  ±1% band",
        ha="right", va="bottom", fontsize=8, color="gray",
    )
    ax_bot.set_xticks(np.arange(len(names)))
    ax_bot.set_xticklabels(names, rotation=55, ha="right", fontsize=9)
    ax_bot.set_ylabel("residual  (B3 − PDG) / PDG  [%]", fontsize=11)
    ax_bot.set_title(
        "Per-hadron residuals coloured by family   "
        "(dashed = ±mean|Δ| within family)",
        fontsize=11,
    )
    ax_bot.legend(loc="lower left", fontsize=8, framealpha=0.92, ncol=2)
    ax_bot.grid(True, alpha=0.3)
    ax_bot.set_ylim(-80.0, 30.0)

    # Family-stats annotation box.
    fs_lines = ["Per-family mean |Δ|:"]
    for fs in rpt.family_stats():
        fs_lines.append(
            f"  {fs.family:<9s} n={fs.n}  "
            f"mean={100.0 * fs.mean_abs_rel:5.2f}%  "
            f"max={100.0 * fs.max_abs_rel:5.2f}% ({fs.worst})"
        )
    fs_lines.append("")
    fs_lines.append(
        f"OVERALL n={rpt.n_total}  "
        f"mean={100.0 * rpt.mean_abs_rel:.2f}%  "
        f"worst={rpt.worst_name}"
    )
    fs_lines.append("")
    fs_lines.append("Honest verdict:")
    fs_lines.append("  - p, n, Δ at sub-1%  (passes)")
    fs_lines.append("  - octet hyperons: 2-14%  (Ξ drift)")
    fs_lines.append("  - light PS: π OK; η, K break")
    fs_lines.append("    (SU(3) singlet-octet mixing)")
    fs_lines.append("  - heavy quarkonia: 36-66% low")
    fs_lines.append("    (no Coulomb binding in formula)")
    ax_bot.text(
        1.005, 1.0, "\n".join(fs_lines),
        transform=ax_bot.transAxes, fontsize=7.5,
        family="monospace", va="top", ha="left",
        bbox=dict(facecolor="white", edgecolor="black",
                  linewidth=0.6, boxstyle="round,pad=0.4"),
    )

    fig.suptitle(
        "Hadron Mass Test (122) — substrate K_4 cell-stacking vs PDG 2024",
        fontsize=14, weight="bold",
    )
    return [_save(fig, "122_hadron_mass_test.png")]


if __name__ == "__main__":
    paths = render_hadron_mass_test()
    for p in paths:
        print(p)
