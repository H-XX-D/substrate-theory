"""Generate visuals/134_sound_velocity.png.

Three-panel figure summarising the substrate sound-velocity test across
15 materials (water through diamond, ~12× span in c_L):

  (top-left)  scatter c_L_pred vs c_L_meas in log-log; substrate prediction
              with substrate-derived (B, G) marked in solid blue, fall-back
              measured-(B, G) materials in open orange. Diagonal y=x and
              ±25% bands shown.
  (top-right) scatter c_L_kinematic (measured B, G + substrate wave eq)
              vs c_L_meas — the "wave-equation only" check, which lands on
              y=x to ~1-2%.
  (bottom)    bar chart of relative error per material (substrate prediction
              and kinematic check side by side), sorted by c_L_meas.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.stiff_medium.sound_velocity_test import MATERIALS, run_test


OUT_PATH = Path(__file__).resolve().parents[1] / "visuals" / "134_sound_velocity.png"


def main() -> None:
    res = run_test()
    rows = res["rows"]
    summary = res["summary"]
    summary_sub = res["summary_substrate_BG"]
    summary_kin = res["summary_kinematic"]

    # Sort materials by measured c_L (low -> high) for the bar chart
    items = sorted(rows.items(), key=lambda kv: kv[1]["c_L_meas"])
    names      = [name for name, _ in items]
    c_pred     = np.array([row["c_L_pred"]            for _, row in items])
    c_kin      = np.array([row["c_L_measured_moduli"] for _, row in items])
    c_meas     = np.array([row["c_L_meas"]            for _, row in items])
    used_sub   = np.array([row["used_substrate_BG"]   for _, row in items])
    rel_pred   = (c_pred - c_meas) / c_meas
    rel_kin    = (c_kin  - c_meas) / c_meas

    fig = plt.figure(figsize=(14.0, 10.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.85],
                          hspace=0.32, wspace=0.28)

    # ---------------- top-left: substrate prediction scatter ---------------- #
    ax_sub = fig.add_subplot(gs[0, 0])
    sub_mask = used_sub
    ax_sub.loglog(
        c_meas[sub_mask], c_pred[sub_mask], "o",
        color="#1f77b4", markersize=10, label="substrate-derived (B, G)",
    )
    ax_sub.loglog(
        c_meas[~sub_mask], c_pred[~sub_mask], "s",
        color="#ff7f0e", markersize=9, mfc="none", mew=1.6,
        label="measured (B, G) fallback",
    )
    lim = [min(c_meas.min(), c_pred.min()) * 0.7,
           max(c_meas.max(), c_pred.max()) * 1.4]
    ax_sub.plot(lim, lim, "k--", alpha=0.55, label="y = x")
    ax_sub.fill_between(lim, [0.75 * v for v in lim], [1.25 * v for v in lim],
                        color="grey", alpha=0.10, label=r"±25% band")
    for nm, x, y in zip(names, c_meas, c_pred):
        ax_sub.annotate(
            nm, (x, y), textcoords="offset points", xytext=(5, 5),
            fontsize=7, color="#444",
        )
    ax_sub.set_xlim(lim)
    ax_sub.set_ylim(lim)
    ax_sub.set_aspect("equal", "box")
    ax_sub.set_xlabel(r"measured $c_L$  [m/s]")
    ax_sub.set_ylabel(r"substrate-predicted $c_L$  [m/s]")
    ax_sub.set_title(
        "Substrate prediction: K_4 (B, G) into substrate wave equation\n"
        f"15 materials, log-log Pearson r = {summary['loglog_pearson']:.3f}, "
        f"mean |err| = {summary['mean_abs_rel_err']:.1%}"
    )
    ax_sub.legend(loc="upper left", fontsize=8)
    ax_sub.grid(True, which="both", alpha=0.3)

    # ---------------- top-right: kinematic-only scatter --------------------- #
    ax_kin = fig.add_subplot(gs[0, 1])
    ax_kin.loglog(c_meas, c_kin, "o", color="#2ca02c", markersize=10,
                  label="substrate wave eq, measured (B, G)")
    lim_k = [min(c_meas.min(), c_kin.min()) * 0.7,
             max(c_meas.max(), c_kin.max()) * 1.4]
    ax_kin.plot(lim_k, lim_k, "k--", alpha=0.55, label="y = x")
    ax_kin.fill_between(lim_k, [0.95 * v for v in lim_k], [1.05 * v for v in lim_k],
                        color="grey", alpha=0.12, label=r"±5% band")
    for nm, x, y in zip(names, c_meas, c_kin):
        ax_kin.annotate(
            nm, (x, y), textcoords="offset points", xytext=(5, 5),
            fontsize=7, color="#444",
        )
    ax_kin.set_xlim(lim_k)
    ax_kin.set_ylim(lim_k)
    ax_kin.set_aspect("equal", "box")
    ax_kin.set_xlabel(r"measured $c_L$  [m/s]")
    ax_kin.set_ylabel(r"kinematic-only $c_L$  [m/s]")
    ax_kin.set_title(
        "Kinematic-only: substrate wave equation with MEASURED (B, G)\n"
        f"log-log Pearson r = {summary_kin['loglog_pearson']:.4f}, "
        f"mean |err| = {summary_kin['mean_abs_rel_err']:.2%}"
    )
    ax_kin.legend(loc="upper left", fontsize=8)
    ax_kin.grid(True, which="both", alpha=0.3)

    # ---------------- bottom: per-material relative-error bars --------------- #
    ax_bar = fig.add_subplot(gs[1, :])
    x = np.arange(len(names))
    w = 0.40
    bars_pred = ax_bar.bar(
        x - w / 2, rel_pred * 100.0, w,
        color=["#1f77b4" if u else "#ff7f0e" for u in used_sub],
        edgecolor="black", linewidth=0.4,
        label="substrate (B, G) prediction",
    )
    bars_kin = ax_bar.bar(
        x + w / 2, rel_kin * 100.0, w,
        color="#2ca02c", alpha=0.85, edgecolor="black", linewidth=0.4,
        label="kinematic-only (measured B, G)",
    )
    ax_bar.axhline(0.0, color="black", linewidth=0.8)
    ax_bar.axhline(+10.0, color="grey", linestyle=":", alpha=0.7)
    ax_bar.axhline(-10.0, color="grey", linestyle=":", alpha=0.7)
    ax_bar.axhline(+25.0, color="grey", linestyle="--", alpha=0.5)
    ax_bar.axhline(-25.0, color="grey", linestyle="--", alpha=0.5)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax_bar.set_ylabel("relative error  (c_pred − c_meas) / c_meas  [%]")
    ax_bar.set_title(
        "Per-material relative error (sorted by measured c_L)\n"
        "Blue = substrate-predicted (B, G); Orange = measured-(B, G) fallback; "
        "Green = kinematic-only check"
    )
    ax_bar.legend(loc="lower left", fontsize=9)
    ax_bar.grid(True, axis="y", alpha=0.3)

    # ---------------- footer with summary stats ----------------------------- #
    txt = (
        f"All 15 materials: mean |err| = {summary['mean_abs_rel_err']:.1%}, "
        f"median |err| = {summary['median_abs_rel_err']:.1%}, "
        f"{summary['within_25pct']}/15 within 25%, "
        f"all within {summary['max_abs_rel_err']*100:.0f}% (max).   "
        f"Substrate-only subset (n={summary_sub['n_materials_substrate_BG']}): "
        f"mean |err| = {summary_sub['mean_abs_rel_err']:.1%}, "
        f"log-log r = {summary_sub['loglog_pearson']:.3f}.   "
        f"Kinematic check: mean |err| = {summary_kin['mean_abs_rel_err']:.2%}, "
        f"log-log r = {summary_kin['loglog_pearson']:.4f}."
    )
    fig.text(0.5, 0.005, txt, ha="center", va="bottom", fontsize=9,
             color="#222", wrap=True)

    fig.suptitle(
        r"Substrate sound velocity:  $c_L = \sqrt{(B + 4G/3)/\rho}$  vs measured P-wave speeds (15 materials)",
        fontsize=13.5, y=0.995,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
