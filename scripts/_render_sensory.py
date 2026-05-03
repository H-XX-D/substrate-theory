"""Renderer for the sensory-transduction GEOMETRY+SIM+VIZ pair.

Produces:
    visuals/108_phototransduction.png  (rhodopsin photoisomerization + cascade)
    visuals/109_hearing_cochlea.png    (cochlea tonotopy + MET channel + WF)

Run standalone:
    python scripts/_render_sensory.py
or import render_sensory() from render_all_visuals.py.
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


def render_sensory() -> list[str]:
    """Produce 108_phototransduction.png and 109_hearing_cochlea.png."""
    from src.stiff_medium.sensory_substrate import (
        F_APEX_HZ,
        F_BASE_HZ,
        N_DISTINGUISHABLE_ODORS,
        N_OLFACTORY_RECEPTORS,
        PHOTON_TO_CHANNEL_GAIN,
        PDE_GAIN,
        RHODOPSIN_ISOMERIZATION_FS,
        RHODOPSIN_LAMBDA_MAX_NM,
        SINGLE_PHOTON_THRESHOLD,
        TRANSDUCIN_GAIN,
        SensoryGeometry,
        SensorySimulator,
        cochlear_position_at_frequency,
    )
    out: list[str] = []

    geom = SensoryGeometry()
    sim = SensorySimulator(geometry=geom)

    # ------------------------------------------------------------------
    # 108_phototransduction.png — rhodopsin photoisomerization + cascade
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0],
                          width_ratios=[1.2, 1.2, 1.0],
                          hspace=0.45, wspace=0.4)

    # Panel A: 11-cis -> all-trans isomerization (~200 fs)
    ax_iso = fig.add_subplot(gs[0, 0])
    t_fs = np.linspace(0.0, 1500.0, 400)
    iso = sim.photoisomerize(t_fs)
    ax_iso.plot(iso["t_fs"], iso["cis_pop"], color="tab:purple",
                linewidth=2.2, label="11-cis retinal")
    ax_iso.plot(iso["t_fs"], iso["trans_pop"], color="tab:orange",
                linewidth=2.2, label="all-trans retinal")
    ax_iso.axvline(RHODOPSIN_ISOMERIZATION_FS, color="black", linestyle="--",
                   linewidth=1.0,
                   label=f"tau = {RHODOPSIN_ISOMERIZATION_FS:.0f} fs")
    ax_iso.set_xlabel("time after photon absorption [fs]", fontsize=10)
    ax_iso.set_ylabel("population fraction", fontsize=10)
    ax_iso.set_title(
        "Rhodopsin 11-cis -> all-trans photoisomerization\n"
        "(Schoenlein 1991: ~200 fs, fastest known biological reaction)",
        fontsize=10,
    )
    ax_iso.legend(loc="center right", fontsize=9)
    ax_iso.grid(True, alpha=0.3)
    ax_iso.set_ylim(-0.02, 1.02)

    # Panel B: cascade gain bar chart
    ax_cas = fig.add_subplot(gs[0, 1])
    cas = sim.phototransduction_cascade(n_photons=1)
    stages = ["1 photon\n(absorbed)", "1 R*\n(metarhodopsin II)",
              f"~{int(TRANSDUCIN_GAIN)}\nG_t (transducin)",
              f"~{int(TRANSDUCIN_GAIN * PDE_GAIN):.0e}\ncGMP hydrolyzed",
              f"~{int(PHOTON_TO_CHANNEL_GAIN):.0e}\nCNG channels closed"]
    counts = [1.0, cas["n_R_star"], cas["n_transducin"],
              cas["n_cGMP_hydrolyzed"], cas["n_channels_closed"]]
    colors = ["#4daf4a", "#377eb8", "#ff7f00", "#984ea3", "#e41a1c"]
    bars = ax_cas.bar(range(len(stages)), counts, color=colors,
                      edgecolor="black", linewidth=0.8)
    ax_cas.set_yscale("log")
    ax_cas.set_xticks(range(len(stages)))
    ax_cas.set_xticklabels(stages, fontsize=8)
    ax_cas.set_ylabel("molecules / channels (log scale)", fontsize=10)
    ax_cas.set_title(
        "Phototransduction cascade gain ~ 10^6\n"
        "(Pugh-Lamb 1993: 1 photon -> ~10^6 closed CNG channels)",
        fontsize=10,
    )
    ax_cas.grid(True, alpha=0.3, axis="y", which="both")
    for bar, c in zip(bars, counts):
        ax_cas.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() * 1.5,
                    f"{c:.1e}", ha="center", fontsize=8)

    # Panel C: rod outer-segment cartoon
    ax_rod = fig.add_subplot(gs[0, 2])
    ax_rod.set_aspect("equal")
    for i in range(20):
        ax_rod.add_patch(plt.Rectangle((0.1, 0.05 + i * 0.04), 0.8, 0.025,
                                        facecolor="#fdd0a2",
                                        edgecolor="#a63603", linewidth=0.5))
    ax_rod.add_patch(plt.Rectangle((0.25, 0.85), 0.5, 0.05,
                                    facecolor="#a1d99b",
                                    edgecolor="#006d2c", linewidth=0.8))
    ax_rod.add_patch(plt.Circle((0.5, 0.95), 0.04,
                                 facecolor="#3182bd",
                                 edgecolor="black", linewidth=0.8))
    ax_rod.text(0.5, 0.5, "ROD\nOUTER\nSEGMENT\n~10^9 rhodopsin /\n~1000 discs",
                ha="center", va="center", fontsize=9, weight="bold")
    ax_rod.text(1.05, 0.5, "OUT", ha="left", va="center", fontsize=9,
                color="#a63603")
    ax_rod.text(0.5, 0.87, "inner segment", ha="center", va="center",
                fontsize=8)
    ax_rod.text(0.5, 0.985, "synapse", ha="center", va="center", fontsize=8)
    ax_rod.set_xlim(-0.05, 1.4)
    ax_rod.set_ylim(0.0, 1.05)
    ax_rod.axis("off")
    ax_rod.set_title("Rod photoreceptor architecture\n"
                     f"~{int(geom.rod_count):.0e} rods (vs ~6e6 cones)",
                     fontsize=10)

    # Panel D: photon energy vs wavelength
    ax_E = fig.add_subplot(gs[1, 0])
    wavelengths = np.linspace(350.0, 750.0, 200)
    E_eV = (6.626e-34 * 3.0e8 / (wavelengths * 1.0e-9)) / 1.602e-19
    ax_E.plot(wavelengths, E_eV, color="black", linewidth=2.0)
    ax_E.axvline(RHODOPSIN_LAMBDA_MAX_NM, color="tab:green",
                 linestyle="--", linewidth=1.5,
                 label=f"rhodopsin lambda_max = {RHODOPSIN_LAMBDA_MAX_NM:.0f} nm")
    visible = np.linspace(400.0, 700.0, 200)
    visible_color = plt.cm.nipy_spectral(np.linspace(0.0, 0.85, len(visible)))
    for i in range(len(visible) - 1):
        ax_E.axvspan(visible[i], visible[i + 1], color=visible_color[i],
                     alpha=0.15)
    ax_E.set_xlabel("wavelength [nm]", fontsize=10)
    ax_E.set_ylabel("photon energy [eV]", fontsize=10)
    ax_E.set_title("Single photon E = hc/lambda  (visible: ~1.8 - 3.1 eV)",
                   fontsize=10)
    ax_E.legend(loc="upper right", fontsize=9)
    ax_E.grid(True, alpha=0.3)
    ax_E.set_xlim(350.0, 750.0)

    # Panel E: signal vs noise (single-photon detectability)
    ax_snr = fig.add_subplot(gs[1, 1])
    n_photons = np.arange(0, 11)
    signal = PHOTON_TO_CHANNEL_GAIN * n_photons
    ax_snr.semilogy(n_photons, np.maximum(signal, 1.0), "o-",
                    color="tab:red", linewidth=1.8, markersize=8,
                    label=f"signal = {PHOTON_TO_CHANNEL_GAIN:.0e} per photon")
    ax_snr.axhline(1.0e4, color="gray", linestyle="--", linewidth=1.2,
                   label="thermal-isomerization noise floor")
    ax_snr.axvline(SINGLE_PHOTON_THRESHOLD - 0.5, color="black",
                   linestyle=":", linewidth=1.0)
    ax_snr.fill_betweenx([1.0, 1.0e8], -0.5,
                          SINGLE_PHOTON_THRESHOLD - 0.5,
                          color="gray", alpha=0.2,
                          label="below threshold")
    ax_snr.set_xlabel("absorbed photons", fontsize=10)
    ax_snr.set_ylabel("downstream signal (channels closed)", fontsize=10)
    ax_snr.set_title(
        "Single-photon detection (Hecht-Shlaer-Pirenne 1942)\n"
        "1 photon -> 10^6 channels >> noise floor",
        fontsize=10,
    )
    ax_snr.legend(loc="lower right", fontsize=8)
    ax_snr.grid(True, alpha=0.3, which="both")
    ax_snr.set_xlim(-0.5, 10.5)
    ax_snr.set_ylim(1.0, 1.0e8)

    # Panel F: substrate annotation
    ax_anno = fig.add_subplot(gs[1, 2])
    ax_anno.axis("off")
    txt = (
        "Substrate (B3) view\n"
        "===================\n\n"
        "1.  Rhodopsin = saturation-\n"
        "    gated substrate cell.\n\n"
        "2.  Photon = transient strain\n"
        "    pulse (sigma -> 1/2 release\n"
        "    of one cell).\n\n"
        "3.  G_t / PDE = strain-\n"
        "    amplifier network: each\n"
        "    activation triggers ~500\n"
        "    downstream cells.\n\n"
        "4.  Total gain = product of\n"
        "    cascade fan-outs:\n"
        "    1 x 500 x 1000 = 5e5\n"
        "    (~10^6 measured).\n\n"
        "5.  Action potential = the\n"
        "    cumulative torque T on\n"
        "    the post-synaptic\n"
        "    substrate.\n"
    )
    ax_anno.text(0.0, 1.0, txt, fontsize=8, family="monospace",
                 va="top", ha="left", transform=ax_anno.transAxes)

    fig.suptitle(
        "Phototransduction (108) — rhodopsin photo-cascade & single-photon "
        "detection\nrhodopsin (vision) -> 200 fs isomerization -> ~10^6 amplification",
        fontsize=13,
    )
    fig.tight_layout()
    out.append(_save(fig, "108_phototransduction.png"))

    # ------------------------------------------------------------------
    # 109_hearing_cochlea.png
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0],
                          width_ratios=[1.2, 1.2, 1.0],
                          hspace=0.45, wspace=0.4)

    # Panel A: tonotopic map
    ax_map = fig.add_subplot(gs[0, 0])
    tono = sim.tonotopic_map(n_points=400)
    ax_map.semilogy(tono["x_mm"], tono["f_hz"], color="tab:blue",
                    linewidth=2.2, label="f(x) = 20 Hz x 1000^(x/L)")
    for f_target in (100.0, 500.0, 1000.0, 4000.0, 10000.0):
        x_t = cochlear_position_at_frequency(f_target)
        ax_map.scatter([x_t], [f_target], s=50, c="tab:red", zorder=5)
        ax_map.annotate(f"{int(f_target)} Hz", (x_t, f_target),
                        textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax_map.set_xlabel("distance from apex [mm]   (apex 0 mm -> base 35 mm)",
                      fontsize=10)
    ax_map.set_ylabel("characteristic frequency [Hz, log]", fontsize=10)
    ax_map.set_title(
        "Cochlear tonotopic map (von Bekesy 1928 place principle)\n"
        f"apex {F_APEX_HZ:.0f} Hz <- {geom.cochlea_length_mm:.0f} mm -> "
        f"base {F_BASE_HZ/1000:.0f} kHz",
        fontsize=10,
    )
    ax_map.grid(True, alpha=0.3, which="both")
    ax_map.legend(loc="lower right", fontsize=9)

    # Panel B: traveling-wave envelopes
    ax_wave = fig.add_subplot(gs[0, 1])
    f_drives = [200.0, 1000.0, 4000.0, 10000.0]
    drive_colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(f_drives)))
    for f_d, c in zip(f_drives, drive_colors):
        wave = sim.cochlear_traveling_wave(f_drive_hz=f_d, n_points=400)
        ax_wave.plot(wave["x_mm"], wave["envelope"], color=c, linewidth=2.0,
                     label=f"{int(f_d)} Hz drive")
    ax_wave.set_xlabel("distance from apex [mm]", fontsize=10)
    ax_wave.set_ylabel("BM displacement envelope [arb]", fontsize=10)
    ax_wave.set_title(
        "Basilar-membrane traveling waves (place principle)\n"
        "high-frequency tones peak at the base, low-frequency at the apex",
        fontsize=10,
    )
    ax_wave.legend(loc="upper left", fontsize=8)
    ax_wave.grid(True, alpha=0.3)
    ax_wave.set_xlim(0.0, geom.cochlea_length_mm)

    # Panel C: hair-cell + tip-link cartoon
    ax_hc = fig.add_subplot(gs[0, 2])
    ax_hc.set_aspect("equal")
    ax_hc.add_patch(plt.Rectangle((0.25, 0.05), 0.5, 0.5,
                                   facecolor="#fee0d2",
                                   edgecolor="#a50f15", linewidth=1.0))
    base_x = np.linspace(0.27, 0.73, 7)
    for i, bx in enumerate(base_x):
        h = 0.10 + 0.04 * i
        ax_hc.plot([bx, bx], [0.55, 0.55 + h], color="#08519c", linewidth=2.2)
    for i in range(len(base_x) - 1):
        bx0 = base_x[i]
        bx1 = base_x[i + 1]
        h0 = 0.55 + 0.10 + 0.04 * i
        h1 = 0.55 + 0.10 + 0.04 * (i + 1)
        ax_hc.plot([bx0, bx1], [h0, h1 - 0.005], color="black",
                   linewidth=0.8, linestyle="--")
    for i, bx in enumerate(base_x):
        h = 0.55 + 0.10 + 0.04 * i
        ax_hc.scatter([bx], [h], s=30, c="red", zorder=5)
    ax_hc.text(0.5, 0.30, "HAIR CELL\nbody", ha="center", va="center",
               fontsize=9, weight="bold")
    ax_hc.text(0.5, 0.95, "stereocilia + tip links\n(MET channels at tips)",
               ha="center", va="top", fontsize=8)
    ax_hc.set_xlim(0.0, 1.0)
    ax_hc.set_ylim(0.0, 1.0)
    ax_hc.axis("off")
    ax_hc.set_title("Inner hair cell (Hudspeth-Corey 1989)\n"
                    f"{geom.inner_hair_cells} IHCs + "
                    f"{geom.outer_hair_cells} OHCs",
                    fontsize=10)

    # Panel D: MET-channel current vs displacement
    ax_met = fig.add_subplot(gs[1, 0])
    dx_pm = np.linspace(-2.0, 6.0, 400)
    dx_m = dx_pm * 1.0e-12
    I_met = sim.met_current(dx_m)
    ax_met.plot(dx_pm, I_met, color="tab:red", linewidth=2.2,
                label="I_MET(dx)")
    ax_met.axvline(1.0, color="black", linestyle="--", linewidth=1.0,
                   label="threshold ~ 1 pm")
    ax_met.axhline(50.0, color="gray", linestyle=":", linewidth=0.8,
                   label="half-activation 50 pA")
    ax_met.fill_between(dx_pm, 0, I_met, where=(dx_pm >= 1.0),
                        color="orange", alpha=0.2)
    ax_met.set_xlabel("stereocilia tip displacement [pm = 10^-12 m]",
                      fontsize=10)
    ax_met.set_ylabel("MET current [pA]", fontsize=10)
    ax_met.set_title(
        "MET channel: sub-picometer mechano-transduction\n"
        "(half-activation at 1 pm, the diameter of a single H atom!)",
        fontsize=10,
    )
    ax_met.legend(loc="lower right", fontsize=9)
    ax_met.grid(True, alpha=0.3)
    ax_met.set_xlim(-2.0, 6.0)
    ax_met.set_ylim(-2.0, 110.0)

    # Panel E: Weber-Fechner across modalities
    ax_wf = fig.add_subplot(gs[1, 1])
    for modality, color in zip(("vision", "hearing", "smell"),
                                ("tab:green", "tab:blue", "tab:purple")):
        out_wf = sim.weber_fechner_curve(modality,
                                          I_min=1.0, I_max=1.0e6,
                                          n_points=200)
        k_w = out_wf["weber_k"]
        ax_wf.semilogx(out_wf["I"], out_wf["psi_norm"], color=color,
                        linewidth=2.0, label=f"{modality}  k_w={k_w:.2f}")
    ax_wf.set_xlabel("physical intensity I [arb, log]", fontsize=10)
    ax_wf.set_ylabel("perceived intensity psi (normalized)", fontsize=10)
    ax_wf.set_title(
        "Weber-Fechner law: psi = k log(I/I_0)\n"
        "logarithmic perception across vision, hearing, smell",
        fontsize=10,
    )
    ax_wf.legend(loc="lower right", fontsize=9)
    ax_wf.grid(True, alpha=0.3, which="both")

    # Panel F: olfactory combinatorial-coding heatmap
    ax_olf = fig.add_subplot(gs[1, 2])
    olf_R = geom.make_receptor_response_matrix(n_odorants=64,
                                                sparsity=0.03, seed=2)
    ax_olf.imshow(olf_R[:60, :40], aspect="auto", cmap="hot",
                  interpolation="nearest")
    ax_olf.set_xlabel("odorant index", fontsize=9)
    ax_olf.set_ylabel("OR receptor index", fontsize=9)
    ax_olf.set_title(
        f"Olfaction: ~{N_OLFACTORY_RECEPTORS} ORs encode "
        f"~{N_DISTINGUISHABLE_ODORS:.0e} odors\n"
        f"combinatorial sparse code (~3% per odorant)",
        fontsize=9,
    )

    fig.suptitle(
        "Hearing + Smell (109) — cochlear traveling wave + MET channel + "
        "Weber-Fechner\n20 Hz apex -> 20 kHz base; 1 pm tip-link threshold; "
        "log-perception across all senses",
        fontsize=13,
    )
    fig.tight_layout()
    out.append(_save(fig, "109_hearing_cochlea.png"))

    return out


if __name__ == "__main__":
    paths = render_sensory()
    for p in paths:
        print(p)
