"""Render visuals/130_atomic_transitions.png — substrate vs NIST atomic spectra.

Two-panel figure summarising the multi-element substrate-vs-NIST atomic
transition test.  Top panel: bar chart of substrate predicted vs NIST
wavelength per transition, coloured by family.  Bottom panel: per-family
mean / max |relative error| with the transition-metal failure mode
highlighted.

Run standalone:
    python scripts/_render_atomic_transitions_test.py
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
sys.path.insert(0, os.path.join(ROOT, "src"))

VISUALS_DIR = os.path.join(ROOT, "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)


# Stable per-family colour map.
FAMILY_COLOUR = {
    "hydrogen":         "#1f77b4",  # blue
    "He":               "#2ca02c",  # green
    "alkali":           "#d62728",  # red
    "alkaline_earth":   "#9467bd",  # purple
    "transition_metal": "#ff7f0e",  # orange
}

FAMILY_LABEL = {
    "hydrogen":         "H I (Bohr + reduced mass)",
    "He":               "He I (1snℓ Z_eff=26/25)",
    "alkali":           "Li/Na/K I (quantum defect)",
    "alkaline_earth":   "Mg/Ca I & Ca II (defects + s/t)",
    "transition_metal": "Fe I (d-electron — fails)",
}


def render_atomic_transitions_test() -> str:
    """Render visuals/130_atomic_transitions.png."""
    from stiff_medium.atomic_transitions_test import (
        family_summary,
        run_atomic_transitions_test,
    )

    rows = run_atomic_transitions_test()
    family_order = ("hydrogen", "He", "alkali", "alkaline_earth", "transition_metal")
    by_family = {f: [] for f in family_order}
    for r in rows:
        by_family[r.family].append(r)
    for f in family_order:
        by_family[f].sort(key=lambda r: r.nist_nm)

    ordered = [r for f in family_order for r in by_family[f]]
    labels = [r.label for r in ordered]
    nist = np.array([r.nist_nm for r in ordered])
    pred = np.array([r.pred_nm for r in ordered])
    rel = np.array([r.rel_err_pct for r in ordered])
    abs_rel = np.array([r.abs_rel_err_pct for r in ordered])
    colours = [FAMILY_COLOUR[r.family] for r in ordered]

    fig = plt.figure(figsize=(17, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.4, 1.0, 0.7], hspace=0.55)

    # ------------------------------------------------------------------
    # Panel A: predicted vs NIST wavelength (log-y)
    # ------------------------------------------------------------------
    ax_top = fig.add_subplot(gs[0, 0])
    x = np.arange(len(labels))
    w = 0.4
    ax_top.bar(
        x - w / 2, nist, width=w, color="#bbbbbb", edgecolor="black",
        label="NIST (vacuum/air)", zorder=2,
    )
    ax_top.bar(
        x + w / 2, pred, width=w, color=colours, edgecolor="black",
        label="substrate prediction", zorder=2,
    )
    ax_top.set_yscale("log")
    ax_top.set_ylabel("wavelength (nm)  [log]")
    ax_top.set_title(
        "Substrate atomic transitions vs NIST Atomic Spectra Database  "
        "(25 transitions, 8 elements, K_rank=5 + quantum defects)"
    )
    ax_top.set_xticks(x)
    ax_top.set_xticklabels([lbl[:22] for lbl in labels], rotation=70, ha="right", fontsize=8)
    # Family-coloured legend handles
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=FAMILY_COLOUR[f], label=FAMILY_LABEL[f]) for f in family_order]
    handles.append(Patch(facecolor="#bbbbbb", label="NIST reference"))
    ax_top.legend(handles=handles, loc="upper left", fontsize=8, ncol=2)
    ax_top.grid(True, axis="y", which="major", linestyle="--", alpha=0.4)
    ax_top.set_axisbelow(True)

    # ------------------------------------------------------------------
    # Panel B: per-transition |relative error| (log-y)
    # ------------------------------------------------------------------
    ax_mid = fig.add_subplot(gs[1, 0])
    eps = 0.001  # log axis floor
    ax_mid.bar(
        x, np.maximum(abs_rel, eps), color=colours, edgecolor="black", zorder=2,
    )
    ax_mid.set_yscale("log")
    ax_mid.set_ylabel("|relative error| (%)  [log]")
    ax_mid.set_xticks(x)
    ax_mid.set_xticklabels([lbl[:22] for lbl in labels], rotation=70, ha="right", fontsize=8)
    ax_mid.axhline(1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.6,
                   label="1% reference")
    ax_mid.axhline(5.0, color="grey", linestyle=":", linewidth=1.0, alpha=0.6,
                   label="5% reference")
    ax_mid.legend(loc="upper left", fontsize=8)
    ax_mid.grid(True, axis="y", which="both", linestyle="--", alpha=0.3)
    ax_mid.set_axisbelow(True)
    n_below_1 = int(np.sum(abs_rel < 1.0))
    n_below_5 = int(np.sum(abs_rel < 5.0))
    ax_mid.set_title(
        f"Per-transition |rel err|  —  {n_below_1}/{len(rows)} <1%, "
        f"{n_below_5}/{len(rows)} <5%, max = {abs_rel.max():.1f}% (Fe I, d-electron)"
    )

    # ------------------------------------------------------------------
    # Panel C: per-family mean / median / max |rel err|
    # ------------------------------------------------------------------
    ax_bot = fig.add_subplot(gs[2, 0])
    summary = family_summary(rows)
    fams = list(family_order)
    means = np.array([summary[f]["mean"] for f in fams])
    medians = np.array([summary[f]["median"] for f in fams])
    maxs = np.array([summary[f]["max"] for f in fams])
    ns = np.array([int(summary[f]["n"]) for f in fams])

    xf = np.arange(len(fams))
    wf = 0.27
    ax_bot.bar(xf - wf, means, width=wf, label="mean", color="#1f77b4", edgecolor="black")
    ax_bot.bar(xf,      medians, width=wf, label="median", color="#2ca02c", edgecolor="black")
    ax_bot.bar(xf + wf, maxs, width=wf, label="max", color="#d62728", edgecolor="black")
    ax_bot.set_yscale("log")
    ax_bot.set_xticks(xf)
    ax_bot.set_xticklabels(
        [f"{FAMILY_LABEL[f]}\n(n={ns[i]})" for i, f in enumerate(fams)],
        fontsize=8, rotation=15, ha="right",
    )
    ax_bot.set_ylabel("|rel err| %  [log]")
    ax_bot.axhline(1.0, color="black", linestyle="--", linewidth=1.0, alpha=0.6)
    ax_bot.axhline(5.0, color="grey", linestyle=":", linewidth=1.0, alpha=0.6)
    ax_bot.legend(loc="upper left", fontsize=8)
    ax_bot.set_axisbelow(True)
    ax_bot.grid(True, axis="y", which="both", linestyle="--", alpha=0.3)
    ax_bot.set_title(
        "Per-family error: substrate K_rank model excellent for s/p valence (≤2.1%); "
        "fails for transition-metal d-electrons (≥670%)"
    )
    # annotate value labels at top of max bars
    for i, m in enumerate(maxs):
        ax_bot.text(xf[i] + wf, m * 1.4, f"{m:.2f}%", ha="center", fontsize=7)

    fig.suptitle(
        "B3 substrate atomic transitions — NIST sweep across periodic table",
        fontsize=13, y=0.995,
    )

    out_path = os.path.join(VISUALS_DIR, "130_atomic_transitions.png")
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    path = render_atomic_transitions_test()
    print(f"wrote: {path}")
