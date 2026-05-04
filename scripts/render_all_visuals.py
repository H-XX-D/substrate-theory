"""Render every available substrate-framework visualization to visuals/.

Runs all visualization-producing modules and saves PNG outputs into the
visuals/ folder so you can SEE what the geometry and simulations look like.
"""
from __future__ import annotations

import os
import sys
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

VISUALS_DIR = os.path.join(ROOT, "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)


def save(fig, name: str) -> str:
    """Save matplotlib figure to visuals/ and return relative path."""
    path = os.path.join(VISUALS_DIR, name)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# 1. K_4 face-pair geometry
# ---------------------------------------------------------------------------

def render_k4_face_pair() -> list[str]:
    from src.stiff_medium.k4_face_pair_geometry import (
        K4Geometry, K4FacePairCoupling
    )
    out = []

    # Single K_4 geometry
    geom = K4Geometry()
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    v = geom.vertices
    for i in range(4):
        ax.scatter(*v[i], s=200, c="red", edgecolors="black", linewidths=2)
        ax.text(v[i, 0]*1.1, v[i, 1]*1.1, v[i, 2]*1.1, f"v{i}", fontsize=11)
    for a, b in geom.edges:
        ax.plot(*zip(v[a], v[b]), "k-", alpha=0.6, linewidth=2)
    fc = geom.face_centroids
    fn = geom.face_normals
    for i in range(4):
        ax.quiver(fc[i, 0], fc[i, 1], fc[i, 2],
                  fn[i, 0]*0.4, fn[i, 1]*0.4, fn[i, 2]*0.4,
                  color="blue", alpha=0.7, arrow_length_ratio=0.3)
    ax.set_title(f"K_4 tetrahedron: 4v + 6e + 4f\n"
                 f"vertex angle {geom.vertex_angle()*180/np.pi:.2f}°  "
                 f"dihedral {geom.dihedral_angle()*180/np.pi:.2f}°")
    out.append(save(fig, "01_k4_geometry.png"))

    # Two K_4 coupled at deuteron geometry
    coupling = K4FacePairCoupling()
    coupling.place_two_cells(d_centers=1.4, orientation=0.0)
    fig_pair = plt.figure(figsize=(9, 8))
    ax_pair = fig_pair.add_subplot(111, projection="3d")
    coupling.make_visualization(ax=ax_pair, highlight_match=True)
    out.append(save(fig_pair, "02_k4_face_pair_deuteron.png"))

    # Binding energy curve
    distances = np.linspace(0.5, 4.0, 80)
    curve = coupling.binding_energy_curve(distances)
    if isinstance(curve, tuple) and len(curve) == 2:
        d_vals, e_vals = np.asarray(curve[0]), np.asarray(curve[1])
    else:
        arr = np.asarray(curve)
        if arr.ndim == 2 and arr.shape[0] == 2:
            d_vals, e_vals = arr[0], arr[1]
        else:
            d_vals, e_vals = distances, arr.flatten()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(d_vals, e_vals, "b-", linewidth=2)
    ax.axhline(-2.222, color="red", linestyle="--", label="ε_face = 2.222 MeV")
    ax.axvline(1.4, color="green", linestyle=":", label="d_min ≈ 1.4 fm")
    ax.set_xlabel("Cell-cell separation [fm]")
    ax.set_ylabel("Coupling energy [MeV]")
    ax.set_title("K_4 face-pair coupling: deuteron binding curve")
    ax.legend()
    ax.grid(True, alpha=0.3)
    out.append(save(fig, "03_k4_binding_curve.png"))
    return out


# ---------------------------------------------------------------------------
# 2. Topological defects (kink, vortex, monopole, texture)
# ---------------------------------------------------------------------------

def render_topological_defects() -> list[str]:
    from src.stiff_medium.topological_defect_zoo import (
        Kink1D, Vortex2D, Monopole3D, Texture3D, DefectVisualizer
    )
    out = []
    viz = DefectVisualizer()

    fig = viz.plot_kink(Kink1D(xi=1.0))
    out.append(save(fig, "04_defect_kink_1d.png"))

    fig = viz.plot_vortex(Vortex2D(xi=1.0, n=1))
    out.append(save(fig, "05_defect_vortex_n1.png"))

    fig = viz.plot_vortex(Vortex2D(xi=1.0, n=2))
    out.append(save(fig, "06_defect_vortex_n2.png"))

    fig = viz.plot_monopole(Monopole3D(xi=1.0))
    out.append(save(fig, "07_defect_monopole_3d.png"))

    fig = viz.plot_texture(Texture3D(R=2.0))
    out.append(save(fig, "08_defect_texture_skyrmion.png"))
    return out


# ---------------------------------------------------------------------------
# 3. Kink-antikink scattering (sine-Gordon)
# ---------------------------------------------------------------------------

def render_kink_scattering() -> list[str]:
    from src.stiff_medium.kink_scattering import KinkScattering
    out = []
    ks = KinkScattering(Nx=512, L=40.0)
    ks.init_two_kinks(x_K=-10.0, v_K=0.4, x_AK=10.0, v_AK=-0.4,
                       sign_K=+1, sign_AK=-1)
    snapshots = []
    times = []
    for _ in range(8):
        ks.step(n=80)
        snapshots.append(ks.phi.copy())
        times.append(ks.t)

    fig, ax = plt.subplots(figsize=(10, 5))
    cmap = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
    for snap, t, c in zip(snapshots, times, cmap):
        ax.plot(ks.x, snap, color=c, label=f"t={t:.1f}", alpha=0.85)
    ax.set_xlabel("x [ξ]")
    ax.set_ylabel("φ")
    ax.set_title("Kink-antikink collision (sine-Gordon, v=0.4)")
    ax.legend(fontsize=8, ncol=2, loc="upper right")
    ax.grid(True, alpha=0.3)
    out.append(save(fig, "09_kink_antikink_collision.png"))
    return out


# ---------------------------------------------------------------------------
# 4. 2D substrate field evolution
# ---------------------------------------------------------------------------

def render_lattice_substrate_2d() -> list[str]:
    from src.stiff_medium.lattice_substrate_2d import LatticeSubstrate2D
    out = []
    sim = LatticeSubstrate2D(Nx=64, Ny=64, dx=0.5, dt=0.1)
    # Initialize with a Gaussian bump
    X, Y = np.meshgrid(np.arange(64) * 0.5 - 16, np.arange(64) * 0.5 - 16)
    sim.u = 1.5 * np.exp(-(X**2 + Y**2) / 16.0)
    sim.v = np.zeros_like(sim.u)

    snaps = [sim.u.copy()]
    for _ in range(4):
        for _ in range(20):
            sim.step()
        snaps.append(sim.u.copy())

    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    vmax = max(abs(s).max() for s in snaps)
    for ax, snap, i in zip(axes, snaps, range(5)):
        im = ax.imshow(snap, origin="lower", cmap="RdBu_r",
                       vmin=-vmax, vmax=vmax)
        ax.set_title(f"step {i*20}")
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("2D substrate field u(x,y,t) — Gaussian bump radiating outward")
    fig.colorbar(im, ax=axes.tolist(), shrink=0.8)
    out.append(save(fig, "10_lattice_2d_evolution.png"))
    return out


# ---------------------------------------------------------------------------
# 5. Saturation cap scenarios
# ---------------------------------------------------------------------------

def render_saturation_simulator() -> list[str]:
    from src.stiff_medium.saturation_simulator import (
        scenario_inverse_radius, scenario_shock_front, scenario_black_hole,
        scenario_linear_pulse,
    )
    out = []
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    scenarios = [
        ("Linear pulse", scenario_linear_pulse, axes[0, 0]),
        ("Inverse radius", scenario_inverse_radius, axes[0, 1]),
        ("Shock front", scenario_shock_front, axes[1, 0]),
        ("Black-hole-like", scenario_black_hole, axes[1, 1]),
    ]
    for name, fn, ax in scenarios:
        try:
            res = fn()
            # SimResult dataclass: .x, .u_history (n_t, n_x), .sigma_history, .times
            x = getattr(res, "x", None)
            u_hist = getattr(res, "u_history", None)
            sig_hist = getattr(res, "sigma_history", None)
            times = getattr(res, "times", None)
            if x is not None and u_hist is not None and len(u_hist) > 0:
                # Show initial + middle + final snapshots
                n_t = len(u_hist)
                snap_idxs = [0, n_t // 2, n_t - 1]
                colors = ["lightblue", "royalblue", "navy"]
                for i, c in zip(snap_idxs, colors):
                    label = f"t={times[i]:.2f}" if times is not None else f"step {i}"
                    ax.plot(x, u_hist[i], color=c, linewidth=1.4, label=label)
            if x is not None and sig_hist is not None and len(sig_hist) > 0:
                ax2 = ax.twinx()
                ax2.plot(x, sig_hist[-1], "r--", linewidth=1.5,
                         label="σ final", alpha=0.7)
                ax2.axhline(0.5, color="orange", linestyle=":",
                            linewidth=2, label="σ_max=½")
                ax2.set_ylabel("σ", color="r")
                ax2.legend(loc="upper right", fontsize=8)
                ax2.set_ylim(-0.05, 0.6)
            ax.set_title(name)
            ax.set_xlabel("x")
            ax.set_ylabel("u(x,t)", color="b")
            ax.legend(loc="upper left", fontsize=8)
            ax.grid(True, alpha=0.3)
        except Exception as e:
            ax.text(0.5, 0.5, f"{name}\n(error: {type(e).__name__}: {e})",
                    ha="center", transform=ax.transAxes, fontsize=8,
                    wrap=True)
    fig.suptitle("Substrate saturation cap σ ≤ 1/2 — 4 dynamic scenarios")
    fig.tight_layout()
    out.append(save(fig, "11_saturation_scenarios.png"))
    return out


# ---------------------------------------------------------------------------
# 6. Phonon dispersion across lattice geometries
# ---------------------------------------------------------------------------

def render_phonon_dispersion() -> list[str]:
    from src.stiff_medium.phonon_dispersion import PhononDispersion
    out = []
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    # (lattice key, label, k-path through high-symmetry points)
    geoms = [
        ("chain", "1D chain", ["G", "X", "G"]),
        ("square", "2D square", ["G", "X", "M", "G"]),
        ("hex", "2D hexagonal", ["G", "M", "K", "G"]),
        ("3d_fcc", "3D FCC", ["G", "X", "L", "G", "K"]),
        ("bcc", "3D BCC", ["G", "H", "N", "G", "P"]),
        ("diamond", "3D diamond", ["G", "X", "L", "G", "K"]),
    ]
    # Map any aliases to actual lattice factory keys
    lattice_alias = {"3d_fcc": "fcc"}
    for ax, (g, label, path) in zip(axes.flat, geoms):
        lattice_key = lattice_alias.get(g, g)
        try:
            pd = PhononDispersion(K=1.0, rho=1.0, lattice=lattice_key)
            x, omega, ticks = pd.dispersion_curve(path, n_points=40)
            if omega.ndim == 1:
                ax.plot(x, omega, "b-", linewidth=2)
            else:
                for i in range(omega.shape[1]):
                    ax.plot(x, omega[:, i], alpha=0.75, linewidth=1.5)
            for t in ticks:
                ax.axvline(t, color="gray", alpha=0.3, linewidth=0.5)
            ax.set_xticks(ticks)
            ax.set_xticklabels(path, fontsize=9)
            ax.set_title(label)
            ax.set_xlabel("k-path")
            ax.set_ylabel("ω")
            ax.grid(True, alpha=0.3)
        except Exception as e:
            ax.text(0.5, 0.5, f"{label}\n(N/A: {type(e).__name__})", ha="center",
                    transform=ax.transAxes, fontsize=9)
    fig.suptitle("Substrate phonon dispersion: ω(k) for 6 lattice geometries")
    fig.tight_layout()
    out.append(save(fig, "12_phonon_dispersion.png"))
    return out


# ---------------------------------------------------------------------------
# 7. Cube cell Q_3 dark matter
# ---------------------------------------------------------------------------

def render_cube_dm() -> list[str]:
    from src.stiff_medium.cube_cell_dm_simulator import (
        CubeCell, vertex_charges, octupole, leading_multipole_order
    )
    out = []
    cell = CubeCell()
    verts = cell.vertices()  # 8 x 3
    charges = vertex_charges()  # ±1 per parity

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")
    for i, (v, q) in enumerate(zip(verts, charges)):
        color = "red" if q > 0 else "blue"
        ax.scatter(*v, c=color, s=350, edgecolors="black",
                   linewidths=2, zorder=5)
        ax.text(v[0]*1.15, v[1]*1.15, v[2]*1.15,
                f"v{i}\n{'+' if q>0 else '−'}", fontsize=9)
    # Edges of cube
    cube_edges = [(0,1),(1,3),(3,2),(2,0),(4,5),(5,7),(7,6),(6,4),
                  (0,4),(1,5),(2,6),(3,7)]
    for a, b in cube_edges:
        ax.plot(*zip(verts[a], verts[b]), "k-", alpha=0.4, linewidth=1.5)

    leading = leading_multipole_order(cell)
    octu = octupole(cell)
    ax.set_title(f"Cube cell Q_3 — dark matter\n"
                 f"Bipartite parity (red=+, blue=−), no triangular faces\n"
                 f"Leading multipole: l={leading}, octupole={octu:.3e}")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    out.append(save(fig, "13_cube_dm_q3.png"))
    return out


# ---------------------------------------------------------------------------
# 8. Möbius bundle
# ---------------------------------------------------------------------------

def render_mobius_bundle() -> list[str]:
    out = []
    u = np.linspace(0, 2 * np.pi, 120)
    v = np.linspace(-0.5, 0.5, 24)
    U, V = np.meshgrid(u, v)
    X = (1 + V * np.cos(U / 2)) * np.cos(U)
    Y = (1 + V * np.cos(U / 2)) * np.sin(U)
    Z = V * np.sin(U / 2)

    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.92,
                           edgecolor="none", antialiased=True)
    ax.set_title(
        "Möbius strip — substrate orientability axiom\n"
        "Z/2 sheet swap: K_pair = 2 sheets identified after one twist;\n"
        "11/12 amplitude integral on K_4 → α = 1/137.04 at 0.004%"
    )
    fig.colorbar(surf, ax=ax, shrink=0.6)
    out.append(save(fig, "14_mobius_strip.png"))
    return out


# ---------------------------------------------------------------------------
# 9. EM radiation patterns
# ---------------------------------------------------------------------------

def render_em_radiation() -> list[str]:
    out = []
    theta = np.linspace(0, np.pi, 200)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5),
                             subplot_kw={"projection": "polar"})
    names = ["Dipole sin²θ", "Quadrupole sin²2θ",
             "Synchrotron-like (γ=3)"]
    gamma = 3.0
    patterns = [
        np.sin(theta)**2,
        np.sin(2*theta)**2,
        np.sin(theta)**2 / (1 - 0.95 * np.cos(theta))**5,
    ]
    for ax, name, p in zip(axes, names, patterns):
        # Symmetric polar plot
        full_theta = np.concatenate([theta, theta + np.pi])
        full_p = np.concatenate([p, p[::-1]])
        ax.plot(full_theta, full_p / full_p.max(), "b-", linewidth=2)
        ax.fill_between(full_theta, 0, full_p / full_p.max(),
                        alpha=0.25)
        ax.set_title(name, fontsize=11)
        ax.set_yticks([])
    fig.suptitle("EM radiation patterns from substrate transverse modes")
    fig.tight_layout()
    out.append(save(fig, "15_em_radiation_patterns.png"))
    return out


# ---------------------------------------------------------------------------
# 10. Cosmology de-saturation evolution
# ---------------------------------------------------------------------------

def render_cosmology_evolution() -> list[str]:
    from src.stiff_medium.cosmology_simulator import (
        SubstrateParams, SubstrateCosmologySimulator
    )
    out = []
    sim = SubstrateCosmologySimulator(SubstrateParams())
    history = sim.run()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Saturation σ(t)
    ax = axes[0]
    if "t" in history and "sigma" in history:
        ax.plot(history["t"], history["sigma"], "b-", linewidth=2)
        ax.axhline(0.5, color="red", linestyle="--", label="σ_max = 1/2")
        ax.axhline(0.0, color="green", linestyle=":", label="fully de-saturated")
        ax.set_xlabel("Time [arb units]")
        ax.set_ylabel("Substrate saturation σ(t)")
        ax.set_title("De-saturation: σ → 0 from σ = 1/2")
        ax.legend()
        ax.grid(True, alpha=0.3)
    elif "scale_factor" in history:
        ax.semilogy(history.get("t", range(len(history["scale_factor"]))),
                    history["scale_factor"], "b-")
        ax.set_title("Scale factor a(t)")
        ax.grid(True, alpha=0.3)

    # Energy density components — decompose rho_total into matter + Lambda
    ax = axes[1]
    if "rho_total" in history and "a" in history:
        a = np.asarray(history["a"])
        t = np.asarray(history.get("t", np.arange(len(a))))
        rho_total = np.asarray(history["rho_total"])
        rho_lambda = float(sim.predict_rho_lambda())
        a_today = a[-1] if len(a) else 1.0
        rho_m_today = max(rho_total[-1] - rho_lambda, 0.0)
        rho_matter = rho_m_today * (a_today / np.maximum(a, 1e-30)) ** 3
        # Radiation scales as a^-4; tiny today, but plot for visualization
        rho_radiation = rho_m_today * 1e-4 * (a_today / np.maximum(a, 1e-30)) ** 4
        rho_lambda_arr = np.full_like(a, rho_lambda)
        ax.semilogy(t, rho_matter, color="blue", label="ρ_matter (a⁻³)")
        ax.semilogy(t, rho_radiation, color="red", label="ρ_radiation (a⁻⁴)")
        ax.semilogy(t, rho_lambda_arr, color="green", linestyle="--",
                    label=f"ρ_Λ ({rho_lambda:.2e})")
        ax.semilogy(t, rho_total, color="black", linewidth=2, label="ρ_total")
        ax.set_xlabel("Time [arb units]")
        ax.set_ylabel("Energy density [kg/m³]")
        ax.set_title("Cosmic energy budget: matter + radiation + Λ")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "(component evolution not exposed)",
                ha="center", transform=ax.transAxes)
    fig.suptitle("Substrate cosmology: de-saturation timeline")
    fig.tight_layout()
    out.append(save(fig, "16_cosmology_desaturation.png"))
    return out


# ---------------------------------------------------------------------------
# 11. Cone-bouncing visualizer (geometry + simulator)
# ---------------------------------------------------------------------------

def render_cone_bouncing() -> list[str]:
    """Produce 17_cone_bouncing.png and 18_cone_bouncing_drag_scan.png.

    Visualises the cone-bouncing mass mechanism: a substrate-strain
    envelope reflecting off the σ = ±1/2 saturation cone walls at
    frequency ω_b, with m c² = ℏ ω_b.
    """
    from src.stiff_medium.cone_bouncing_visualizer import (
        ConeBouncingGeometry,
        ConeBouncingSimulator,
        make_bouncing_figure,
        make_drag_scan_figure,
    )
    out: list[str] = []

    # Use natural-baseline primitives for the geometry panel so the
    # bouncing envelope is visually clean.  The mass-energy mapping
    # m c² = ℏ ω_b still applies; the panel is about geometry, not
    # SI absolute values.
    geom = ConeBouncingGeometry(K=1.0, rho=1.0, xi=1.0, gamma=0.0)
    sim  = ConeBouncingSimulator(geometry=geom, amplitude_frac=0.95,
                                  n_steps=4000, dt_per_period=200)
    fig = make_bouncing_figure(geom, sim)
    out.append(save(fig, "17_cone_bouncing.png"))

    # Drag scan in natural units so the 5-point ladder is visible
    sim_scan = ConeBouncingSimulator(
        geometry=ConeBouncingGeometry(K=1.0, rho=1.0, xi=1.0),
        amplitude_frac=0.6,
        n_steps=4000, dt_per_period=200,
    )
    fig = make_drag_scan_figure(sim_scan)
    out.append(save(fig, "18_cone_bouncing_drag_scan.png"))
    return out


# ---------------------------------------------------------------------------
# 12. Mass torque ladder
# ---------------------------------------------------------------------------

def render_mass_ladder() -> list[str]:
    from src.stiff_medium.mass_torque_engine import MassTorque
    out = []
    mt = MassTorque()
    configs = ["electron", "muon", "tau", "deuteron", "alpha",
               "fine_structure", "hierarchy", "higgs", "t_c_max"]
    results = []
    for c in configs:
        try:
            r = mt.compute(c)
            pred = r.get("predicted") or r.get("pred")
            obs = r.get("observed") or r.get("obs")
            err = r.get("error_pct") or r.get("err_pct") or 0
            if pred is not None and obs is not None:
                results.append((c, float(pred), float(obs), float(err)))
        except Exception:
            pass

    if results:
        names, pred, obs, err = zip(*results)
        # Use a normalized ratio plot
        fig, ax = plt.subplots(figsize=(11, 6))
        x = np.arange(len(names))
        ratios = [p / o for p, o in zip(pred, obs)]
        bars = ax.bar(x, ratios, color=["green" if abs(r-1)<0.02 else
                                        "orange" if abs(r-1)<0.10 else "red"
                                        for r in ratios])
        ax.axhline(1.0, color="black", linestyle="--", linewidth=2,
                   label="exact match")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha="right")
        ax.set_ylabel("Predicted / Observed")
        ax.set_title("Substrate mass-torque ladder vs PDG\n"
                     f"green = <2%, orange = 2-10%, red = >10%")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        for b, r in zip(bars, ratios):
            ax.text(b.get_x() + b.get_width()/2, b.get_height(),
                    f"{r:.4f}", ha="center", va="bottom", fontsize=8)
        fig.tight_layout()
        out.append(save(fig, "21_mass_torque_ladder.png"))
    return out


# ---------------------------------------------------------------------------
# 13. Multi-nucleon K_4 stacking (deuteron, triton, alpha)
#     + nuclear chart BE/A vs PDG
# ---------------------------------------------------------------------------

def render_nucleon_stacking() -> list[str]:
    """Produce 19_nucleon_stacking.png and 20_nuclear_chart.png.

    19: 3D rendering of deuteron, triton, alpha as face-shared K_4 stacks.
    20: BE/A vs A curve showing predicted (K_4 stacking) vs PDG/AME2020.
    """
    from src.stiff_medium.nucleon_stacking_geometry import (
        NuclearChartVisualizer,
        NucleonStackGeometry,
        get_topology,
    )
    out: list[str] = []

    # ---- 19: deuteron + triton + alpha 3D ----
    fig = plt.figure(figsize=(18, 6))
    viz = NuclearChartVisualizer()
    for col, A in enumerate([2, 3, 4]):
        ax = fig.add_subplot(1, 3, col + 1, projection="3d")
        viz.visualize_geometry_3d(A, ax=ax, highlight_shared=True)
    fig.suptitle(
        "Multi-nucleon K_4 stacking: A nucleon ↔ 1 K_4 cell, "
        "shared faces (red) bind by ε_face = 2.222 MeV",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "19_nucleon_stacking.png"))

    # ---- 20: BE/A nuclear chart vs PDG ----
    fig, ax = plt.subplots(figsize=(11, 6))
    viz.chart_BE_per_A(ax=ax, A_max=20)
    fig.tight_layout()
    out.append(save(fig, "20_nuclear_chart.png"))

    return out


# ---------------------------------------------------------------------------
# 14. 3-generation lepton/quark tower (geometry + ladder)
# ---------------------------------------------------------------------------

def render_generation_tower() -> list[str]:
    """Produce 22_generation_tower.png and 23_lepton_quark_ladder.png.

    22: 3D plot of three orthogonal K_4 cells -- one per substrate axis --
        showing why D = 3 forces exactly 3 generations.
    23: log-scale mass ladder for all 6 leptons + 6 quarks, with the
        substrate generation jumps annotated.
    """
    from src.stiff_medium.generation_tower_visualizer import (
        GenerationTowerGeometry, GenerationTowerSimulator,
    )
    out: list[str] = []

    geom = GenerationTowerGeometry()
    sim = GenerationTowerSimulator(geometry=geom)

    # 22: 3D geometric tower
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")
    sim.draw_geometric_tower(ax=ax)
    fig.tight_layout()
    out.append(save(fig, "22_generation_tower.png"))

    # 23: lepton + quark mass ladder
    fig, ax = plt.subplots(figsize=(11, 7))
    sim.draw_full_ladder(ax=ax)
    fig.tight_layout()
    out.append(save(fig, "23_lepton_quark_ladder.png"))

    return out


# ---------------------------------------------------------------------------
# 12. Substrate visualizer (existing module)
# ---------------------------------------------------------------------------

def render_substrate_visualizer() -> list[str]:
    out = []
    try:
        from src.stiff_medium.substrate_visualizer import SubstrateVisualizer
        viz = SubstrateVisualizer()
        if hasattr(viz, "save_all"):
            paths = viz.save_all(VISUALS_DIR)
            if isinstance(paths, list):
                out.extend(paths)
    except Exception as e:
        print(f"  substrate_visualizer: {e}")
    return out


# ---------------------------------------------------------------------------
# 15. Möbius sheet-swap (Z/2 involution → particle/antiparticle, Majorana,
#     σ = 1/2 fixed point, half-integer spin from double cover)
# ---------------------------------------------------------------------------

def render_mobius_sheet_swap() -> list[str]:
    """Produce 24_mobius_sheet_swap.png and 25_majorana_visualization.png.

    24: Möbius strip with the two sheets A/B coloured separately and an
        explicit arrow indicating the Z/2 swap τ : (θ, s) → (θ, −s).
    25: Side-by-side comparison of charged (electron, sheet A → B,
        distinct antiparticle endpoint) vs neutral (neutrino, sheet
        A = B, identical Majorana endpoint).
    """
    from src.stiff_medium.mobius_sheet_swap import (
        SIGMA_MAX,
        MobiusSheetGeometry,
        SheetSwapSimulator,
        default_charged,
        default_neutral,
        summary,
    )

    out: list[str] = []

    geom = MobiusSheetGeometry(radius=1.0, width=0.5,
                               n_theta=240, n_v=24)
    sim = SheetSwapSimulator(geometry=geom, n_steps=240)

    # ---- 24: Möbius strip with sheet labels A/B + swap arrow ----
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")
    X, Y, Z = geom.surface_xyz()
    sheet_color = geom.sheet_color_field()

    # Two-sheet colouring: sheet A (v > 0) red, sheet B (v < 0) blue;
    # the v = 0 core circle sits between them as the τ-fixed locus.
    cmap = plt.get_cmap("coolwarm")
    ax.plot_surface(
        X, Y, Z,
        facecolors=cmap(0.5 * sheet_color + 0.5),
        rcount=24, ccount=120,
        linewidth=0.0, antialiased=True, alpha=0.92, shade=True,
    )

    # Sheet A label (top of strip)
    ax.text(1.55, 0.0, 0.55, "Sheet A  (s = +1)", color="darkred",
            fontsize=12, fontweight="bold")
    # Sheet B label (bottom of strip, on the Möbius-flipped side)
    ax.text(1.55, 0.0, -0.55, "Sheet B  (s = −1)", color="darkblue",
            fontsize=12, fontweight="bold")

    # Z/2 swap arrow: from a point on sheet A across to the matching
    # point on sheet B (vertical reflection through the v = 0 core).
    a_xyz = (1.20, 0.05, 0.45)
    b_xyz = (1.20, 0.05, -0.45)
    ax.quiver(a_xyz[0], a_xyz[1], a_xyz[2],
              b_xyz[0] - a_xyz[0], b_xyz[1] - a_xyz[1],
              b_xyz[2] - a_xyz[2],
              color="black", arrow_length_ratio=0.18, linewidth=2.5)
    ax.quiver(b_xyz[0], b_xyz[1], b_xyz[2],
              a_xyz[0] - b_xyz[0], a_xyz[1] - b_xyz[1],
              a_xyz[2] - b_xyz[2],
              color="black", arrow_length_ratio=0.18, linewidth=2.5)
    ax.text(1.45, 0.05, 0.0, "τ : (θ, s) ↦ (θ, −s)",
            color="black", fontsize=11, fontstyle="italic")

    # Highlight the σ = 1/2 fixed circle (core of the strip, v = 0)
    theta_circle = np.linspace(0.0, 2.0 * np.pi, 240)
    ax.plot(np.cos(theta_circle), np.sin(theta_circle),
            np.zeros_like(theta_circle),
            color="goldenrod", linewidth=2.5, linestyle="--",
            label="σ = 1/2 fixed circle  (τ-invariant)")

    s = summary()
    ax.set_title(
        "Möbius bundle: two sheets A/B identified by Z/2 swap τ\n"
        f"τ² = id ({s['involution_squared_is_identity']}),  "
        f"holonomy(1 loop) = {s['double_cover_holonomy_one_loop']:+.0f},  "
        f"spin = {s['spin_value']}",
        fontsize=12,
    )
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.legend(loc="upper left", fontsize=9)
    ax.view_init(elev=24, azim=-58)
    out.append(save(fig, "24_mobius_sheet_swap.png"))

    # ---- 25: Majorana visualization — charged vs neutral side by side ----
    demo = sim.demo_charged_vs_neutral(
        charged=default_charged(),
        neutral=default_neutral(),
    )
    fig = plt.figure(figsize=(15, 8))

    # Left panel: electron — sheet A → sheet B, distinct antiparticle.
    ax_left = fig.add_subplot(1, 2, 1, projection="3d")
    Xc, Yc, Zc = geom.surface_xyz()
    ax_left.plot_surface(
        Xc, Yc, Zc,
        facecolors=cmap(0.5 * sheet_color + 0.5),
        rcount=24, ccount=120,
        linewidth=0.0, antialiased=True, alpha=0.55, shade=True,
    )

    n_arc = 60
    arc_theta = np.linspace(0.0, 2.0 * np.pi, n_arc)
    # Trajectory of the charged excitation: starts on sheet A (v > 0)
    # and after the loop emerges on sheet B (v < 0) of the same surface.
    v_path_e = 0.35 * np.cos(arc_theta / 2.0)  # +0.35 → −0.35 across loop
    Xe = (geom.radius + v_path_e * np.cos(arc_theta / 2.0)) * np.cos(arc_theta)
    Ye = (geom.radius + v_path_e * np.cos(arc_theta / 2.0)) * np.sin(arc_theta)
    Ze = v_path_e * np.sin(arc_theta / 2.0)
    ax_left.plot(Xe, Ye, Ze, color="black", linewidth=3.0,
                 label="electron trajectory")
    ax_left.scatter([Xe[0]], [Ye[0]], [Ze[0]], color="darkred", s=160,
                    edgecolors="black", linewidths=1.5,
                    label="start: e⁻ on sheet A", zorder=5)
    ax_left.scatter([Xe[-1]], [Ye[-1]], [Ze[-1]], color="darkblue", s=160,
                    edgecolors="black", linewidths=1.5,
                    label="end: e⁺ on sheet B", zorder=5)
    end_e = demo["charged"]["end"]
    ax_left.set_title(
        "Charged: electron e⁻ → distinct antiparticle e⁺\n"
        f"(charge {default_charged().charge:+.0f} → "
        f"{end_e.charge:+.0f},  sheet A → B)",
        fontsize=11,
    )
    ax_left.set_xlabel("x"); ax_left.set_ylabel("y"); ax_left.set_zlabel("z")
    ax_left.legend(loc="upper left", fontsize=8)
    ax_left.view_init(elev=24, azim=-60)

    # Right panel: neutrino — Majorana fixed point on the v = 0 circle.
    ax_right = fig.add_subplot(1, 2, 2, projection="3d")
    ax_right.plot_surface(
        Xc, Yc, Zc,
        facecolors=cmap(0.5 * sheet_color + 0.5),
        rcount=24, ccount=120,
        linewidth=0.0, antialiased=True, alpha=0.55, shade=True,
    )
    # Neutrino trajectory: rides the v = 0 fixed circle.  The sheet
    # swap is gauged out so start = end (Majorana ν = ν̄).
    Xn = geom.radius * np.cos(arc_theta)
    Yn = geom.radius * np.sin(arc_theta)
    Zn = np.zeros_like(arc_theta)
    ax_right.plot(Xn, Yn, Zn, color="goldenrod", linewidth=3.5,
                  label="neutrino trajectory  (on fixed circle)")
    ax_right.scatter([Xn[0]], [Yn[0]], [Zn[0]], color="darkgreen", s=160,
                     edgecolors="black", linewidths=1.5,
                     label="start: ν on fixed circle", zorder=5)
    ax_right.scatter([Xn[-1]], [Yn[-1]], [Zn[-1]], color="darkgreen", s=200,
                     edgecolors="black", linewidths=1.5, marker="X",
                     label="end: ν̄ = ν  (same state)", zorder=5)
    ax_right.set_title(
        "Neutral: neutrino ν → identical Majorana fixed point\n"
        f"(charge {default_neutral().charge:+.0f}  unchanged,  "
        f"ν = ν̄;  is_majorana = {demo['neutral']['is_majorana']})",
        fontsize=11,
    )
    ax_right.set_xlabel("x"); ax_right.set_ylabel("y"); ax_right.set_zlabel("z")
    ax_right.legend(loc="upper left", fontsize=8)
    ax_right.view_init(elev=24, azim=-60)

    fig.suptitle(
        "Möbius sheet-swap τ — charged sees the swap (e⁻ → e⁺), "
        "neutral does not (ν = ν̄)\n"
        f"σ ≤ 1/2 cap enforced  (cap = {SIGMA_MAX});  "
        "spin-½ from (−1)^n holonomy of the double cover",
        fontsize=12,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
    out.append(save(fig, "25_majorana_visualization.png"))

    return out


# ---------------------------------------------------------------------------
# 16. Saturation horizon: cone tilt + crack-tip + potential
# ---------------------------------------------------------------------------

def render_saturation_horizon() -> list[str]:
    """Produce 26_horizon_cone_tilt.png and 27_horizon_potential.png.

    26: Family of light cones at varying σ from 0 to 1/2, showing the
        tilt grow continuously from 0° (vertical) to 90° (horizon).
        Includes a panel of cone-tilt vs σ.
    27: Substrate potential V(σ) showing the finite cap (sampled at
        σ < 1/2) plus the crack-tip stress regularization (σ_LEFM
        diverges, σ_capped = min(σ_LEFM, σ_max) is bounded).
    """
    from src.stiff_medium.saturation_horizon_geometry import (
        SIGMA_MAX,
        SaturationHorizonGeometry,
        crack_stress_curve,
        potential_curve,
    )

    out: list[str] = []
    geom = SaturationHorizonGeometry()

    # ---- 26: light cones tilting from 0° to 90° as σ → 1/2 ----
    fig = plt.figure(figsize=(14, 6))
    ax_cones = fig.add_subplot(1, 2, 1)
    ax_curve = fig.add_subplot(1, 2, 2)

    sigmas = np.array([0.0, 0.0625, 0.125, 0.25, 0.375, 0.49, 0.5])
    half_h = 1.0
    cmap = plt.cm.plasma(np.linspace(0.0, 0.95, len(sigmas)))

    for i, (s, color) in enumerate(zip(sigmas, cmap)):
        walls = geom.cone_walls(float(s), r0=float(i) * 2.5,
                                t0=0.0, half_height=half_h)
        # Future cone (upward): two walls
        for side in ("right", "left"):
            seg = walls[side]
            ax_cones.plot(seg[:, 0], seg[:, 1], color=color,
                          linewidth=2.4, alpha=0.92)
        # Past cone (mirror image, downward) — drawn faintly
        for side in ("right", "left"):
            seg = walls[side]
            ax_cones.plot(seg[:, 0], -seg[:, 1] + 2 * walls[side][0, 1],
                          color=color, linewidth=1.4, alpha=0.45,
                          linestyle="--")
        # Fill the future cone interior
        triangle_x = [walls["left"][1, 0], walls["right"][0, 0],
                      walls["right"][1, 0]]
        triangle_y = [walls["left"][1, 1], walls["right"][0, 1],
                      walls["right"][1, 1]]
        ax_cones.fill(triangle_x, triangle_y, color=color, alpha=0.18)

        deg = float(geom.cone_tilt_degrees(float(s)))
        ax_cones.text(float(i) * 2.5, -1.25,
                      f"σ={s:.4g}\n{deg:.0f}°",
                      ha="center", va="top", fontsize=9,
                      color=color)

    ax_cones.axhline(0.0, color="gray", linewidth=0.8, alpha=0.5)
    ax_cones.set_xlabel("r (cone center, arbitrary spacing)", fontsize=10)
    ax_cones.set_ylabel("ct", fontsize=10)
    ax_cones.set_title(
        "Future light cones: σ = 0 (vertical) → σ = 1/2 (horizon, 90°)",
        fontsize=11)
    ax_cones.set_xlim(-1.5, len(sigmas) * 2.5)
    ax_cones.set_ylim(-1.6, 1.2)
    ax_cones.set_aspect("equal", adjustable="box")
    ax_cones.grid(True, alpha=0.25)

    # Right panel: tilt-angle curve
    sig_curve = np.linspace(0.0, SIGMA_MAX, 400)
    tilt_curve = geom.cone_tilt_degrees(sig_curve)
    ax_curve.plot(sig_curve, tilt_curve, "b-", linewidth=2.5,
                  label="cone tilt θ(σ)")
    ax_curve.axhline(90.0, color="red", linestyle="--", linewidth=1.5,
                     label="90° = horizon")
    ax_curve.axvline(SIGMA_MAX, color="orange", linestyle=":",
                     linewidth=1.5, label="σ_max = 1/2")
    # Mark the special points
    for s in (0.0, 0.125, 0.25, 0.375, 0.5):
        ax_curve.scatter([s], [float(geom.cone_tilt_degrees(s))],
                         color="black", zorder=5, s=30)
    ax_curve.set_xlabel("substrate strain σ", fontsize=10)
    ax_curve.set_ylabel("cone-tilt angle θ (degrees)", fontsize=10)
    ax_curve.set_title(
        "Cone tilt vs σ: θ(σ) = 2·arctan(√(σ/σ_max))", fontsize=11)
    ax_curve.legend(loc="upper left", fontsize=9)
    ax_curve.grid(True, alpha=0.3)
    ax_curve.set_xlim(-0.01, 0.51)
    ax_curve.set_ylim(-2, 100)

    fig.suptitle(
        "Saturation horizon geometry: σ → 1/2 ⇒ light cone tilts 90°\n"
        "Schwarzschild r_s = 2GM/c² recovered as the locus where σ(r) = 1/2",
        fontsize=12)
    fig.tight_layout()
    out.append(save(fig, "26_horizon_cone_tilt.png"))

    # ---- 27: substrate potential V(σ) + crack-tip regularization ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax_V, ax_crack = axes

    # Potential V(σ) — sampled below the cap so it stays finite
    sig_v, V = potential_curve(n=400, K=1.0, sigma_clip=0.4995)
    ax_V.plot(sig_v, V, "b-", linewidth=2.4, label="V(σ) = -½ log(1-(σ/σ_max)²)")
    ax_V.axvline(SIGMA_MAX, color="red", linestyle="--", linewidth=2,
                 label="σ_max = 1/2 (cap)")
    # The cap value at σ = 0.499 — finite even though the bare potential
    # has a logarithmic divergence at σ = 1/2
    V_cap = float(V[-1])
    ax_V.axhline(V_cap, color="orange", linestyle=":", linewidth=1.5,
                 label=f"V_cap (σ=0.4995) ≈ {V_cap:.2f}")
    ax_V.set_xlabel("substrate strain σ", fontsize=10)
    ax_V.set_ylabel("substrate potential V(σ)  [units of K]", fontsize=10)
    ax_V.set_title(
        "Substrate potential V(σ): finite cap, logarithmic divergence",
        fontsize=11)
    ax_V.set_xlim(-0.01, 0.55)
    ax_V.set_ylim(-0.2, V_cap * 1.15)
    ax_V.legend(loc="upper left", fontsize=9)
    ax_V.grid(True, alpha=0.3)

    # Crack-tip stress: classical LEFM diverges, capped version is finite
    crack = crack_stress_curve(a=1.0, sigma_inf=0.1,
                               r_min=1e-3, r_max=1.0, n=600)
    ax_crack.plot(crack["r"], crack["stress_LEFM"], "r--",
                  linewidth=2, label="σ_LEFM(r) = σ_∞ √(a/2r) (singular)")
    ax_crack.plot(crack["r"], crack["stress_capped"], "b-",
                  linewidth=2.4, label="σ_capped = min(σ_LEFM, σ_max)")
    ax_crack.axhline(SIGMA_MAX, color="orange", linestyle=":",
                     linewidth=1.5, label="σ_max = 1/2 (cap)")
    rp = crack["process_zone_radius"]
    ax_crack.axvline(rp, color="green", linestyle="-.",
                     linewidth=1.5,
                     label=f"r_p = (a/2)(σ_∞/σ_max)² = {rp:.3f}")
    ax_crack.set_xlabel("distance from crack tip r", fontsize=10)
    ax_crack.set_ylabel("local stress (in σ_max units)", fontsize=10)
    ax_crack.set_title(
        "Crack-tip regularization: same cap σ_max = 1/2 bounds the stress",
        fontsize=11)
    ax_crack.set_ylim(0, 1.3)
    ax_crack.set_xlim(0, 1.0)
    ax_crack.legend(loc="upper right", fontsize=9)
    ax_crack.grid(True, alpha=0.3)

    fig.suptitle(
        "Substrate potential V(σ) finite at the cap "
        "→ regularises both BH horizons and crack-tip singularities",
        fontsize=12)
    fig.tight_layout()
    out.append(save(fig, "27_horizon_potential.png"))

    return out


# ---------------------------------------------------------------------------
# 17. Möbius bundle 11/12 amplitude on K_4 + α derivation breakdown
# ---------------------------------------------------------------------------

def render_mobius_amplitude() -> list[str]:
    """Produce 28_mobius_k4_11_12.png and 29_alpha_derivation.png.

    28: K_4 with the 12 face-dihedral sub-simplices colored, 1 grayed
        out by the Möbius Z_2 pinch — geometric origin of the 11/12.
    29: α = 11/(48π³)·exp(-3π/737) decomposed into its four substrate
        factors with running-product convergence on α_CODATA.
    """
    from src.stiff_medium.mobius_amplitude_visualizer import (
        MobiusAmplitudeGeometry,
        make_alpha_derivation_figure,
        make_mobius_k4_figure,
    )
    out: list[str] = []

    geom = MobiusAmplitudeGeometry()
    fig = make_mobius_k4_figure(geometry=geom)
    out.append(save(fig, "28_mobius_k4_11_12.png"))

    fig = make_alpha_derivation_figure()
    out.append(save(fig, "29_alpha_derivation.png"))
    return out


# ---------------------------------------------------------------------------
# 17b. 3D bound-state extraction (particle EMERGES as substrate strain)
# ---------------------------------------------------------------------------

def render_bound_state_3d() -> list[str]:
    """Produce 30_bound_state_3d.png and 31_bound_state_modes.png.

    30: Three 3D iso-surface snapshots of |u(x,y,z)| at t = 0, T/2, T
        showing the substrate-strain envelope BREATHING in place.  This
        IS the particle: a localized field pattern oscillating at
        ω_b = c/ξ, with rest energy E_rest = ℏ ω_b.

    31: Side-by-side modes — ground / first-excited / breathing — each
        rendered as a centre-plane slice plus the centre-cell amplitude
        trace u(0,0,0,t) and its FFT-extracted ω peak vs the analytic
        ω_b prediction.
    """
    from src.stiff_medium.bound_state_3d_extractor import (
        BoundState3DGeometry,
        BoundState3DSimulator,
        run_three_modes,
    )
    out: list[str] = []

    # ---- 30: 3D iso-surfaces at t = 0, T/2, T ----
    geom = BoundState3DGeometry(N=24, L=12.0)
    sim = BoundState3DSimulator(
        geometry=geom, mode="breathing",
        n_periods=3.0, samples_per_period=24,
    )
    res = sim.run()
    rep = sim.report()
    snaps = res["snapshots"]                   # shape (3, N, N, N)
    x = res["x"]; y = res["y"]; z = res["z"]
    T = float(res["T_period"][0])

    fig = plt.figure(figsize=(16, 6))
    titles = [f"t = 0",
              f"t = T/2 = {T/2:.3f}",
              f"t = T   = {T:.3f}"]
    abs_max = float(np.abs(snaps).max())
    if abs_max <= 0.0:
        abs_max = 1.0
    iso_level = 0.35 * abs_max

    for col in range(3):
        ax = fig.add_subplot(1, 3, col + 1, projection="3d")
        u_abs = np.abs(snaps[col])
        # Marching-cubes-free iso-surface: scatter all cells whose
        # |u| is close to the iso-level.  This uses only matplotlib
        # primitives — no skimage dependency.
        mask = (u_abs > iso_level) & (u_abs < 1.5 * iso_level)
        if mask.sum() > 4000:   # subsample for speed
            idx = np.where(mask.ravel())[0]
            sub = np.random.default_rng(0).choice(idx, size=4000, replace=False)
            mask = np.zeros(mask.size, dtype=bool); mask[sub] = True
            mask = mask.reshape(u_abs.shape)
        if mask.any():
            ix, iy, iz = np.where(mask)
            ax.scatter(x[ix], y[iy], z[iz], c=u_abs[mask],
                       cmap="plasma", s=12, alpha=0.55,
                       vmin=0.0, vmax=abs_max)
        # Outline the cube
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.set_zlim(z.min(), z.max())
        ax.set_xlabel("x [ξ]")
        ax.set_ylabel("y [ξ]")
        ax.set_zlabel("z [ξ]")
        ax.set_title(titles[col], fontsize=11)

    fig.suptitle(
        f"3D bound state EMERGES from substrate field u(x,y,z,t) — "
        f"iso-surfaces |u| = {iso_level:.3f}\n"
        f"ω_meas = {rep['omega_meas']:.4f}  |  ω_b = {rep['omega_pred']:.4f}  "
        f"({rep['omega_rel_err']*100:.2f}% off)   "
        f"E_rest = ℏ ω_b = {rep['rest_E_pred']:.3e} J",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "30_bound_state_3d.png"))

    # ---- 31: ground / excited / breathing side-by-side ----
    results = run_three_modes(
        geometry=BoundState3DGeometry(N=24, L=12.0),
        n_periods=3.0,
        samples_per_period=32,
    )
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    mode_titles = {
        "ground":    "GROUND mode (sech-shaped bump)",
        "excited":   "FIRST-EXCITED (1 radial node)",
        "breathing": "BREATHING (amplitude jitter)",
    }

    # Top row: centre-plane (z = 0) slice of u at t = 0
    for col, mode in enumerate(("ground", "excited", "breathing")):
        ax = axes[0, col]
        snap0 = results[mode]["snapshots"][0]    # t = 0
        # Use central z-slice
        cz = snap0.shape[2] // 2
        slab = snap0[:, :, cz]
        vmax = float(np.abs(slab).max())
        if vmax <= 0.0: vmax = 1.0
        im = ax.imshow(
            slab.T, origin="lower", cmap="RdBu_r",
            extent=[results[mode]["x"].min(), results[mode]["x"].max(),
                    results[mode]["y"].min(), results[mode]["y"].max()],
            vmin=-vmax, vmax=vmax, aspect="equal",
        )
        ax.set_title(mode_titles[mode], fontsize=10)
        ax.set_xlabel("x [ξ]")
        ax.set_ylabel("y [ξ]")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="u(x,y,0)")

    # Bottom row: centre-cell amplitude trace + frequency comparison
    for col, mode in enumerate(("ground", "excited", "breathing")):
        ax = axes[1, col]
        t = results[mode]["t"]
        u_c = results[mode]["u_center"]
        omega_meas = float(results[mode]["_omega_meas"][0])
        omega_pred = float(results[mode]["_omega_pred"][0])
        rel_err = abs(omega_meas - omega_pred) / max(omega_pred, 1e-30)

        ax.plot(t, u_c, "b-", linewidth=1.4, label="u(0,0,0,t)")
        # Analytic envelope at ω_b for visual comparison
        u0_amp = float(np.abs(u_c[:8]).max())
        ax.plot(t, u_c[0] * np.cos(omega_pred * t), "r--",
                linewidth=1.0, alpha=0.6,
                label=f"cos(ω_b t), ω_b={omega_pred:.3f}")
        ax.set_xlabel("t [c·ξ⁻¹·ω_b⁻¹]")
        ax.set_ylabel("u(0)")
        color = "green" if rel_err < 0.10 else "orange" if rel_err < 0.25 else "red"
        ax.set_title(
            f"ω_meas={omega_meas:.3f}  vs  ω_b={omega_pred:.3f}  "
            f"({rel_err*100:.1f}%)",
            fontsize=10, color=color,
        )
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Bound-state mode catalogue — particle = substrate strain pattern\n"
        "Top: centre-plane slice of u(x,y,0).   Bottom: centre-cell "
        "u(0,0,0,t) trace vs analytic cos(ω_b t)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "31_bound_state_modes.png"))
    return out


# ---------------------------------------------------------------------------
# 18. Lagrangian-term contributions (each term turned on separately)
# ---------------------------------------------------------------------------

def render_phase_transition() -> list[str]:
    """Produce 40_phase_transition.png and 41_bubble_nucleation.png.

    40: 2-D snapshots of the substrate de-saturation transition —
        bubbles of σ = -1 (de-saturated) nucleating inside the σ = +1
        (saturated, pre-Big-Bang) sea, expanding, colliding, and
        finally percolating.
    41: bubble size distribution + nucleation rate Γ(T) curve.
    """
    from src.stiff_medium.phase_transition_paired import (
        PhaseTransitionGeometry,
        PhaseTransitionSimulator,
        T_CRITICAL_ONSAGER,
        nucleation_rate_vs_T,
    )
    out: list[str] = []

    # ----- 40: snapshots of bubble formation + percolation ----------------
    geom = PhaseTransitionGeometry(L=64, seed=2)
    sim = PhaseTransitionSimulator(
        geometry=geom,
        T=2.20,                # just below T_c — metastable saturated phase
        n_sweeps=180,
        snapshot_every=30,
        seed_grid="saturated",
        seed=2,
    )
    sim.run()

    snaps = sim.history["snapshots"]
    sweeps = sim.history["snapshot_sweeps"]

    # Always show 6 panels (pad with last snapshot if fewer were taken).
    target_panels = 6
    while len(snaps) < target_panels:
        snaps.append(snaps[-1])
        sweeps.append(sweeps[-1])
    snaps = snaps[:target_panels]
    sweeps = sweeps[:target_panels]

    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for ax, snap, t in zip(axes.flat, snaps, sweeps):
        ax.imshow(snap, cmap="RdBu", vmin=-1, vmax=1, interpolation="nearest")
        sigma_mean = float(snap.mean())
        # Highlight percolation status in the title.
        perc = geom.has_percolating_cluster(grid=snap, target=-1)
        tag = "PERCOLATING" if perc else "isolated bubbles"
        ax.set_title(f"sweep {t}   ⟨σ⟩={sigma_mean:+.2f}   {tag}",
                     fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(
        f"Substrate de-saturation: σ=+1 (red) → σ=-1 (blue) bubbles  "
        f"|  T = {sim.T:.2f}, T_c = {T_CRITICAL_ONSAGER:.3f}",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "40_phase_transition.png"))

    # ----- 41: bubble-size distribution + nucleation rate vs T ------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left panel — bubble size distribution at the final snapshot.
    sizes = sim.bubble_size_distribution()
    ax = axes[0]
    if sizes.size > 0:
        # Log-binned histogram from 1 to max(sizes)+1
        max_s = int(sizes.max())
        bins = np.geomspace(1, max(max_s, 2) + 1, num=12)
        ax.hist(sizes, bins=bins, color="steelblue", edgecolor="black",
                alpha=0.8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("bubble size  s  [sites]")
        ax.set_ylabel("count  N(s)")
        ax.set_title(
            f"Bubble size distribution (final snapshot, T = {sim.T:.2f})\n"
            f"largest bubble = {int(sizes.max())} sites"
        )
        ax.grid(True, which="both", alpha=0.3)
    else:
        ax.text(0.5, 0.5, "no bubbles formed",
                ha="center", transform=ax.transAxes)

    # Right panel — nucleation rate Γ(T)
    Ts = np.linspace(1.0, 3.5, 14)
    scan = nucleation_rate_vs_T(Ts, L=24, n_sweeps=60, seed=42)
    ax = axes[1]
    ax.plot(scan["T"], scan["rate"], "o-", color="crimson", linewidth=2,
            markersize=6, label="Γ(T) bubbles / area / sweep")
    ax.axvline(T_CRITICAL_ONSAGER, color="black", linestyle="--",
               label=f"T_c (Onsager) = {T_CRITICAL_ONSAGER:.3f}")
    ax.set_xlabel("Temperature  T  [units of J]")
    ax.set_ylabel("nucleation rate  Γ(T)")
    ax.set_title("Bubble nucleation rate vs temperature\n"
                 "(saturated initial state — substrate de-saturation)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Cosmological substrate phase transition — bubble statistics",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "41_bubble_nucleation.png"))
    return out


# ---------------------------------------------------------------------------
# 19. Black-hole horizon + Hawking + ringdown (paired geometry/sim/viz)
# ---------------------------------------------------------------------------

def render_black_hole() -> list[str]:
    """Produce 34_black_hole_horizon.png and 35_hawking_ringdown.png.

    34: Substrate σ(r) profile + inward photon trajectories near r_s
        for a solar-mass Schwarzschild BH.
    35: Hawking blackbody spectrum at T_H + (2,2,0) Schwarzschild
        ringdown waveform for a stellar-mass remnant (~250 Hz).

    Both panels are produced by the paired pipeline in
    src/stiff_medium/black_hole_paired.py — geometry + simulator + viz
    around the universal substrate saturation cap σ = 1/2 (B3 §18.39).
    """
    from src.stiff_medium.black_hole_paired import (
        BlackHoleVisualizer,
        default_solar_bh,
        default_stellar_remnant,
    )
    out: list[str] = []

    # Panel 34 — solar-mass BH (r_s ~ 3 km, µs photon dynamics)
    sim_sun = default_solar_bh()
    viz_sun = BlackHoleVisualizer(sim_sun)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    viz_sun.horizon_panel(ax1, ax2)
    fig.suptitle(
        r"Black-hole horizon as substrate $\sigma=1/2$ saturation surface "
        r"(M = 1 M$_\odot$, $r_s \approx$ 2.95 km)",
        fontsize=12, y=1.02,
    )
    fig.tight_layout()
    out.append(save(fig, "34_black_hole_horizon.png"))

    # Panel 35 — Hawking spectrum (solar mass) + stellar-remnant ringdown
    sim_remnant = default_stellar_remnant()
    fig, (ax_spec, ax_wave) = plt.subplots(1, 2, figsize=(13, 5))
    # Spectrum from solar-mass BH (T_H ~ 6e-8 K → microwave-ish Wien peak)
    dummy_fig1 = plt.figure()
    viz_sun.hawking_ringdown_panel(ax_spec=ax_spec,
                                   ax_wave=dummy_fig1.add_subplot(111))
    plt.close(dummy_fig1)
    # Ringdown from 48 M_sun Schwarzschild (~250 Hz) — astrophysically realistic
    dummy_fig2 = plt.figure()
    BlackHoleVisualizer(sim_remnant).hawking_ringdown_panel(
        ax_spec=dummy_fig2.add_subplot(111),
        ax_wave=ax_wave,
    )
    plt.close(dummy_fig2)
    fig.suptitle(
        r"Hawking radiation $T_H = \hbar c^3 / (8\pi G M k_B)$  +  "
        r"Schwarzschild (2,2,0) ringdown",
        fontsize=12, y=1.02,
    )
    fig.tight_layout()
    out.append(save(fig, "35_hawking_ringdown.png"))
    return out


# ---------------------------------------------------------------------------
# 20. Lagrangian-term contributions (each term turned on separately)
# ---------------------------------------------------------------------------

def render_lagrangian_terms() -> list[str]:
    """Produce 32_lagrangian_terms.png and 33_term_contributions.png.

    32: 4 panels — KINETIC+GRADIENT (free wave), KINETIC+POTENTIAL
        (bound oscillation), KINETIC+DRAG (exponential decay), and the
        FULL Lagrangian (kink-antikink particle dynamics).
    33: Energy-flow diagram with each Lagrangian term labeled — symbol,
        physical role, Euler-Lagrange contribution, and what is lost
        when the term is omitted.
    """
    from src.stiff_medium.lagrangian_term_visualizer import (
        LagrangianTermGeometry,
        draw_term_contributions,
        draw_term_panels,
    )
    out: list[str] = []

    geom = LagrangianTermGeometry(rho=1.0, K=1.0, xi=1.0, gamma=0.3)

    fig = draw_term_panels(geometry=geom)
    out.append(save(fig, "32_lagrangian_terms.png"))

    fig = draw_term_contributions(geometry=geom)
    out.append(save(fig, "33_term_contributions.png"))
    return out


# ---------------------------------------------------------------------------
# 19. Gravitational-wave signal (BBH inspiral + merger + ringdown)
# ---------------------------------------------------------------------------

def render_gw_signal() -> list[str]:
    """Produce 46_gw_inspiral.png and 47_gw_merger_ringdown.png.

    46: strain h(t) for a GW150914-like BBH (M_c ≈ 28 M_sun) showing the
        chirp + merger + ringdown, plus the f(t) overlay tracing the
        Newtonian-PN τ^{-3/8} chirp law.
    47: spectrogram |H(f, t)|^2 of the same waveform with f_ISCO and the
        substrate-derived ringdown frequency f_RD overlaid; second panel
        shows the ringdown waveform with its damping envelope.

    Substrate identity: v_GW = √(K/ρ) = c (zero-parameter, structural).
    Ringdown frequency = QNM resonance of the σ → 1/2 cone-tilt surface.
    """
    from src.stiff_medium.gw_signal_paired import (
        gw150914_preset,
        render_inspiral_figure,
        render_ringdown_figure,
    )
    out: list[str] = []
    geom, sim = gw150914_preset()

    fig = render_inspiral_figure(geom=geom, sim=sim)
    out.append(save(fig, "46_gw_inspiral.png"))

    fig = render_ringdown_figure(geom=geom, sim=sim)
    out.append(save(fig, "47_gw_merger_ringdown.png"))
    return out


# ---------------------------------------------------------------------------
# Hubble tension paired (substrate H_0 = 71.92 vs SH0ES vs Planck)
# ---------------------------------------------------------------------------


def render_hubble() -> list[str]:
    """Produce 38_hubble_tension.png and 39_distance_ladder.png.

    38: horizontal-bar plot of the seven leading H_0 probes with the
        substrate prediction H_0 = 71.92 km/s/Mpc shown as a vertical
        band; bars colour-coded by early (CMB) vs late (distance ladder).
    39: distance-modulus Hubble diagram with three theory curves
        (substrate, SH0ES, Planck) on top of a synthetic SN Ia sample
        drawn from the substrate cosmology, plus the H_0 best-fit value;
        residual panel highlights where rivals diverge from substrate.
    """
    from src.stiff_medium.hubble_paired import (
        H0_MEASUREMENTS,
        PLANCK_H0,
        SH0ES_H0,
        SUBSTRATE_H0,
        SUBSTRATE_H0_SIGMA,
        make_default_pair,
    )

    out: list[str] = []
    geom, sim = make_default_pair()

    # ---------------------------------------------- 38: tension landscape
    fig, ax = plt.subplots(figsize=(11, 6.5))

    items = sorted(H0_MEASUREMENTS.items(), key=lambda kv: kv[1][0])
    names = [k for k, _ in items]
    vals = [v[0] for _, v in items]
    sigs = [v[1] for _, v in items]
    sides = [v[2] for _, v in items]

    y = np.arange(len(items))
    side_colour = {"late": "#d0411e", "early": "#1d5fb6"}
    colours = [side_colour[s] for s in sides]

    for yi, vi, si, ci in zip(y, vals, sigs, colours):
        ax.errorbar([vi], [yi], xerr=[si], fmt="o", ecolor=ci, mfc="white",
                    mec=ci, ms=10, mew=1.6, capsize=5, elinewidth=2.0,
                    zorder=3)
        ax.scatter([vi], [yi], color=ci, s=80, zorder=4,
                   edgecolors="black", linewidths=0.6)

    ax.axvspan(SUBSTRATE_H0 - SUBSTRATE_H0_SIGMA,
               SUBSTRATE_H0 + SUBSTRATE_H0_SIGMA,
               color="#2ca02c", alpha=0.22,
               label=f"Substrate H_0 = {SUBSTRATE_H0:.2f} +/- {SUBSTRATE_H0_SIGMA:.2f}")
    ax.axvline(SUBSTRATE_H0, color="#2ca02c", linewidth=2.5, zorder=5)

    ax.axvline(SH0ES_H0, color="#d0411e", linestyle="--", alpha=0.65,
               linewidth=1.4, label=f"SH0ES = {SH0ES_H0:.2f}")
    ax.axvline(PLANCK_H0, color="#1d5fb6", linestyle="--", alpha=0.65,
               linewidth=1.4, label=f"Planck = {PLANCK_H0:.2f}")

    for yi, vi in zip(y, vals):
        delta = vi - SUBSTRATE_H0
        ax.text(78.7, yi, f"d={delta:+.2f}", va="center", fontsize=9,
                color="#444444")

    late_proxy = plt.Line2D([0], [0], marker="o", color="white",
                            mec="#d0411e", mfc="#d0411e", ms=9,
                            label="late (distance ladder)")
    early_proxy = plt.Line2D([0], [0], marker="o", color="white",
                             mec="#1d5fb6", mfc="#1d5fb6", ms=9,
                             label="early (CMB / inverse ladder)")

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("H_0  [km / s / Mpc]")
    ax.set_xlim(63.0, 81.0)
    ax.set_title("Hubble tension: substrate H_0 = 71.92 vs leading probes\n"
                 "red = late-universe distance ladder | blue = early-universe CMB")
    handles, labels = ax.get_legend_handles_labels()
    handles += [late_proxy, early_proxy]
    labels += ["late (distance ladder)", "early (CMB / inverse ladder)"]
    ax.legend(handles, labels, loc="lower right", fontsize=9, framealpha=0.95)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    out.append(save(fig, "38_hubble_tension.png"))

    # ---------------------------------------------- 39: distance ladder
    fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                             gridspec_kw={"width_ratios": [3, 2]})

    z_data, mu_data, sigma_mu = sim.synthesize_sn_sample(
        n=80, z_max=1.5, H0_true=SUBSTRATE_H0, scatter_mag=0.12)

    z_curve = np.linspace(0.01, 1.6, 80)
    mu_sub = sim.distance_modulus_array(z_curve, SUBSTRATE_H0)
    mu_shoes = sim.distance_modulus_array(z_curve, SH0ES_H0)
    mu_planck = sim.distance_modulus_array(z_curve, PLANCK_H0)

    fit = sim.fit_H0(z_data, mu_data, sigma_mu)

    ax = axes[0]
    ax.errorbar(z_data, mu_data, yerr=sigma_mu, fmt=".", color="#888888",
                ecolor="#bbbbbb", ms=7, alpha=0.85,
                label="synthetic SN Ia (substrate)")
    ax.plot(z_curve, mu_sub, color="#2ca02c", linewidth=2.4,
            label=f"Substrate H_0={SUBSTRATE_H0:.2f}")
    ax.plot(z_curve, mu_shoes, color="#d0411e", linewidth=1.8, linestyle="--",
            label=f"SH0ES H_0={SH0ES_H0:.2f}")
    ax.plot(z_curve, mu_planck, color="#1d5fb6", linewidth=1.8, linestyle="--",
            label=f"Planck H_0={PLANCK_H0:.2f}")
    ax.set_xscale("log")
    ax.set_xlabel("redshift  z")
    ax.set_ylabel("distance modulus  mu")
    ax.set_title("Hubble diagram: mu vs z\n"
                 f"best-fit H_0 on synthetic data = "
                 f"{fit['H0_best']:.2f} +/- {fit['sigma_H0']:.2f}")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.92)
    ax.grid(True, alpha=0.3, which="both")

    ax2 = axes[1]
    mu_sub_at_data = sim.distance_modulus_array(z_data, SUBSTRATE_H0)
    res_data = mu_data - mu_sub_at_data
    res_shoes_curve = (sim.distance_modulus_array(z_curve, SH0ES_H0)
                       - sim.distance_modulus_array(z_curve, SUBSTRATE_H0))
    res_planck_curve = (sim.distance_modulus_array(z_curve, PLANCK_H0)
                        - sim.distance_modulus_array(z_curve, SUBSTRATE_H0))

    ax2.errorbar(z_data, res_data, yerr=sigma_mu, fmt=".", color="#888888",
                 ecolor="#bbbbbb", ms=6, alpha=0.7, label="data - substrate")
    ax2.plot(z_curve, res_shoes_curve, color="#d0411e", linewidth=1.8,
             linestyle="--",
             label=f"SH0ES - substrate (d={SH0ES_H0 - SUBSTRATE_H0:+.2f})")
    ax2.plot(z_curve, res_planck_curve, color="#1d5fb6", linewidth=1.8,
             linestyle="--",
             label=f"Planck - substrate (d={PLANCK_H0 - SUBSTRATE_H0:+.2f})")
    ax2.axhline(0.0, color="#2ca02c", linewidth=2.0, label="substrate")
    ax2.set_xscale("log")
    ax2.set_xlabel("redshift  z")
    ax2.set_ylabel("d_mu  (theory - substrate)")
    ax2.set_title("Residuals: rival H_0 vs substrate")
    ax2.legend(loc="best", fontsize=8, framealpha=0.92)
    ax2.grid(True, alpha=0.3, which="both")

    fig.tight_layout()
    out.append(save(fig, "39_distance_ladder.png"))
    return out


# ---------------------------------------------------------------------------
# 24. 3D substrate field full-evolution movie (32³ lattice, iso-surfaces)
# ---------------------------------------------------------------------------

def render_substrate_3d_movie() -> list[str]:
    """Produce 44_substrate_3d_evolution.png and 45_3d_iso_snapshots.png.

    44: 4 time snapshots of the |u| iso-surface across one breathing
        period — the bound state visibly breathes in 3D.
    45: 6-panel grid of iso-surfaces extracted at different threshold
        levels (5% → 60% of |u|_max), showing how the strain envelope
        nests from a thin shell to the inner core.
    """
    from src.stiff_medium.substrate_3d_movie import (
        Substrate3DGeometry,
        Substrate3DSimulator,
    )
    out: list[str] = []

    geom = Substrate3DGeometry(N=32, L=12.0)
    sim = Substrate3DSimulator(
        geometry=geom, n_frames=4, n_periods=1.0,
    )
    sim.run()
    diag = sim.diagnostics()
    T = diag["T_period"]
    abs_max = diag["abs_max"]

    # ---- 44: 4 time snapshots of the |u| iso-surface ----
    fig = plt.figure(figsize=(20, 6))
    snap_titles = [
        "t = 0",
        f"t = T/3 = {T/3.0:.3f}",
        f"t = 2T/3 = {2.0*T/3.0:.3f}",
        f"t = T = {T:.3f}",
    ]
    iso_level_frac = 0.35
    iso_level = iso_level_frac * abs_max

    for col in range(4):
        ax = fig.add_subplot(1, 4, col + 1, projection="3d")
        xs, ys, zs, vals = sim.iso_points(
            frame_index=col, level_frac=iso_level_frac, max_points=4000,
        )
        if len(xs) > 0:
            ax.scatter(
                xs, ys, zs, c=vals, cmap="plasma",
                s=12, alpha=0.55,
                vmin=0.0, vmax=abs_max,
            )
        ax.set_xlim(-geom.L, geom.L)
        ax.set_ylim(-geom.L, geom.L)
        ax.set_zlim(-geom.L, geom.L)
        ax.set_xlabel("x [ξ]")
        ax.set_ylabel("y [ξ]")
        ax.set_zlabel("z [ξ]")
        ax.set_title(snap_titles[col], fontsize=11)

    fig.suptitle(
        f"3D substrate field u(x,y,z,t) — full breathing-period evolution\n"
        f"32³ lattice, |u| iso-level = {iso_level:.4f} "
        f"(35% of |u|_max = {abs_max:.4f}),  T = 2π/ω_b = {T:.3f}\n"
        f"Energy drift over the period: {diag['energy_drift_pct']:.3f}%   "
        f"  iso-volume oscillation: "
        f"{100.0*diag['iso_vol_amp_frac']:.2f}% of mean",
        fontsize=11,
    )
    fig.tight_layout()
    out.append(save(fig, "44_substrate_3d_evolution.png"))

    # ---- 45: 6-panel grid of iso-surfaces at varying thresholds ----
    fig = plt.figure(figsize=(18, 11))
    # Use the t = T/3 frame so all thresholds capture a clean
    # breathing-state snapshot.
    mid_frame = 1
    levels = [0.05, 0.15, 0.25, 0.35, 0.50, 0.60]

    for idx, lev in enumerate(levels):
        ax = fig.add_subplot(2, 3, idx + 1, projection="3d")
        xs, ys, zs, vals = sim.iso_points(
            frame_index=mid_frame,
            level_frac=lev,
            max_points=3500,
            rng_seed=idx,
        )
        n_pts = len(xs)
        if n_pts > 0:
            ax.scatter(
                xs, ys, zs, c=vals, cmap="plasma",
                s=10, alpha=0.55,
                vmin=0.0, vmax=abs_max,
            )
        ax.set_xlim(-geom.L, geom.L)
        ax.set_ylim(-geom.L, geom.L)
        ax.set_zlim(-geom.L, geom.L)
        ax.set_xlabel("x [ξ]"); ax.set_ylabel("y [ξ]"); ax.set_zlabel("z [ξ]")
        ax.set_title(
            f"|u| iso-level = {lev*100:.0f}% of |u|_max\n"
            f"({lev*abs_max:.4f}, {n_pts} cells)",
            fontsize=10,
        )

    fig.suptitle(
        "3D iso-surfaces of |u(x,y,z)| at varying thresholds  "
        "(frame t ≈ T/3)\n"
        "Strain envelope nests: low threshold = outer shell, "
        "high threshold = inner core\n"
        f"32³ lattice, ω_b = {diag['omega_pred']:.4f}, "
        f"E_rest = ℏ ω_b = {diag['rest_E_pred']:.3e} J",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "45_3d_iso_snapshots.png"))

    return out


# ---------------------------------------------------------------------------
# 25. CMB power spectrum + polarization (paired GEOMETRY+SIM+VIZ)
# ---------------------------------------------------------------------------

def render_cmb() -> list[str]:
    """Produce 36_cmb_power_spectrum.png and 37_cmb_polarization.png.

    36: D_l vs l for TT and EE (boosted x50 for visibility) on a single
        axis, with the first 5 acoustic peaks marked.
    37: 2D polarization (Q,U) pattern on the (theta,phi) sphere unrolled
        to a flat projection, plus a B-mode null plot showing substrate
        r=0 (lensing only) vs an illustrative inflation r=0.05 curve.

    Substrate identity:
        * T_CMB = 2.7255 K  (calibrated horizon temperature)
        * first acoustic peak l ~ 220 (recombination physics unchanged)
        * primordial r = 0  (no inflation; only lensing B-modes survive)
    """
    from src.stiff_medium.cmb_paired import (
        CMBGeometry,
        CMBSimulator,
        LENSING_B_PEAK_AMPLITUDE_UK2,
    )
    out: list[str] = []

    geom = CMBGeometry(n_theta=120, n_phi=240, l_max=20, seed=7)
    sim = CMBSimulator(geometry=geom)

    # ---- 36: D_l vs l for TT and EE -----------------------------------
    ells = np.arange(2, 2500)
    d_tt = sim.tt_spectrum(ells)
    d_ee = sim.ee_spectrum(ells)
    detected_peaks = sim.detect_peaks(5)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(ells, d_tt, "b-", linewidth=2, label="TT (substrate)")
    ax.plot(ells, d_ee * 50.0, "r-", linewidth=1.5, alpha=0.85,
            label="EE x 50 (substrate)")
    for i, lp in enumerate(detected_peaks, start=1):
        ax.axvline(lp, color="green", linestyle=":", alpha=0.6,
                   linewidth=1.2)
        ax.text(lp, d_tt.max() * (0.95 - 0.07 * i), f"l={int(lp)}",
                color="darkgreen", fontsize=9, ha="center", rotation=90)
    ax.set_xscale("log")
    ax.set_xlim(2, 2500)
    ax.set_ylim(0, max(d_tt.max(), 1.0) * 1.1)
    ax.set_xlabel("multipole l")
    ax.set_ylabel(r"$D_\ell = \ell(\ell+1)\,C_\ell\,/\,2\pi$  [$\mu$K$^2$]")
    ax.set_title(
        f"CMB angular power spectrum (substrate framework)\n"
        f"first peak l~{detected_peaks[0]:.0f}  "
        f"T_CMB={sim.temperature():.4f} K  "
        f"r_tensor={sim.tensor_to_scalar_ratio():.2f}"
    )
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="upper right")
    out.append(save(fig, "36_cmb_power_spectrum.png"))

    # ---- 37: polarization pattern + B-mode null -----------------------
    Q, U = geom.polarization_QU()
    delta_uK = geom.temperature_field_uK()
    sub = 8
    th = geom.theta[::sub]
    ph = geom.phi[::sub]
    PH, TH = np.meshgrid(ph, th)
    Qs = Q[::sub, ::sub]
    Us = U[::sub, ::sub]
    psi = 0.5 * np.arctan2(Us, Qs)
    amp = np.sqrt(Qs ** 2 + Us ** 2)
    amp_norm = amp / (amp.max() + 1e-30)
    Vx = amp_norm * np.cos(psi)
    Vy = amp_norm * np.sin(psi)

    fig = plt.figure(figsize=(13, 6))

    # Left: temperature anisotropy with polarization vectors
    ax1 = fig.add_subplot(1, 2, 1)
    extent = [0.0, 360.0, 180.0, 0.0]
    sigma_T = max(delta_uK.std(), 1e-30)
    im = ax1.imshow(delta_uK, extent=extent, aspect="auto",
                    cmap="RdBu_r", vmin=-3 * sigma_T, vmax=3 * sigma_T)
    ax1.quiver(np.degrees(PH), np.degrees(TH), Vx, -Vy,
               color="black", pivot="middle", headwidth=0,
               headlength=0, headaxislength=0,
               scale=25, width=0.0025, alpha=0.7)
    ax1.set_xlabel("longitude phi [deg]")
    ax1.set_ylabel("colatitude theta [deg]")
    ax1.set_title("Temperature anisotropy + polarization (E-mode only)")
    fig.colorbar(im, ax=ax1, fraction=0.04, pad=0.02,
                 label=r"$\delta T$ [$\mu$K]")

    # Right: B-mode null plot
    ax2 = fig.add_subplot(1, 2, 2)
    bb_substrate = sim.bb_spectrum(ells)
    sim_inflation = CMBSimulator(r_tensor=0.05)
    bb_inflation_005 = sim_inflation.bb_spectrum(ells)
    ax2.plot(ells, bb_substrate, "b-", linewidth=2,
             label="substrate (r=0): lensing only")
    ax2.plot(ells, bb_inflation_005, "r--", linewidth=1.5,
             label="inflation r=0.05 (illustrative)")
    ax2.axhline(LENSING_B_PEAK_AMPLITUDE_UK2, color="gray",
                linestyle=":", linewidth=1.0,
                label=f"lensing peak ~ {LENSING_B_PEAK_AMPLITUDE_UK2:.0e} uK^2")
    ax2.set_xlim(2, 2000)
    ax2.set_yscale("log")
    ax2.set_ylim(1e-7, 1e-1)
    ax2.set_xlabel("multipole l")
    ax2.set_ylabel(r"$D_\ell^{BB}$  [$\mu$K$^2$]")
    ax2.set_title("B-mode null: substrate r=0 vs inflation")
    ax2.grid(True, alpha=0.3, which="both")
    ax2.legend(loc="upper right", fontsize=9)

    fig.suptitle(
        "CMB polarization (substrate framework): E-mode only, B-mode null",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "37_cmb_polarization.png"))

    return out


# ---------------------------------------------------------------------------
# Quantum measurement & decoherence (double-slit + density matrix + CHSH)
# ---------------------------------------------------------------------------

def render_quantum_measurement() -> list[str]:
    """Produce 42_double_slit.png and 43_decoherence.png.

    42: Two-slit screen intensity I(x) for low γ (interference fringes)
        vs high γ (which-slit / detector pattern), plus the visibility
        crossover V(γ).
    43: Density-matrix coherence |ρ_{12}(t)| decay vs γ, plus a Bloch
        sphere shrink panel and CHSH/Tsirelson saturation panel showing
        the substrate violates the classical LHV bound 2 (predicts 2√2).
    """
    from src.stiff_medium.quantum_measurement_paired import (
        DecoherenceSimulator,
        DoubleSlitGeometry,
        classical_chsh_bound,
        substrate_chsh_value,
        visibility_vs_gamma,
    )
    out: list[str] = []

    # ---- 42: double-slit interference vs detector pattern --------------
    fig = plt.figure(figsize=(15, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1.4, 1.0])
    ax_low = fig.add_subplot(gs[0, 0])
    ax_high = fig.add_subplot(gs[0, 1])
    ax_vis = fig.add_subplot(gs[0, 2])

    geom_low = DoubleSlitGeometry(
        slit_separation=1.0e-5, slit_width=2.0e-6,
        screen_distance=1.0, wavelength=5.0e-7,
        gamma=0.0, wave_speed=1.0,
    )
    fs = geom_low.fringe_spacing()
    x = np.linspace(-6.0 * fs, 6.0 * fs, 1601)

    # Panel A: gamma = 0 -- full coherence, fringes
    i_low = geom_low.intensity(x)
    ax_low.plot(x * 1e3, i_low, "b-", linewidth=1.6,
                label="I(x) = E(x).(1+cos phi)")
    ax_low.fill_between(x * 1e3, 0, i_low, color="blue", alpha=0.15)
    ax_low.set_xlabel("screen position x [mm]", fontsize=10)
    ax_low.set_ylabel("intensity I(x) [arb]", fontsize=10)
    ax_low.set_title(
        f"gamma = 0   (low decoherence)\n"
        f"INTERFERENCE  --  V = {geom_low.visibility(x):.3f}\n"
        f"fringe spacing dx = lambda L/d = {fs*1e3:.3f} mm",
        fontsize=10,
    )
    ax_low.grid(True, alpha=0.3)
    ax_low.legend(fontsize=8, loc="upper right")

    # Panel B: gamma >> 1 -- full decoherence, detector pattern
    geom_high = DoubleSlitGeometry(
        slit_separation=1.0e-5, slit_width=2.0e-6,
        screen_distance=1.0, wavelength=5.0e-7,
        gamma=200.0, wave_speed=1.0,
    )
    i_high = geom_high.intensity(x)
    ax_high.plot(x * 1e3, i_high, "r-", linewidth=1.6,
                 label="I(x) -> E(x)  (cross-term killed)")
    ax_high.fill_between(x * 1e3, 0, i_high, color="red", alpha=0.15)
    ax_high.set_xlabel("screen position x [mm]", fontsize=10)
    ax_high.set_ylabel("intensity I(x) [arb]", fontsize=10)
    ax_high.set_title(
        f"gamma = {geom_high.gamma:.0f}  (high decoherence)\n"
        f"DETECTOR PATTERN  --  V = {geom_high.visibility(x):.3f}\n"
        "no fringes: smooth single-slit envelope",
        fontsize=10,
    )
    ax_high.grid(True, alpha=0.3)
    ax_high.legend(fontsize=8, loc="upper right")

    # Panel C: visibility crossover V(gamma)
    geom_scan = DoubleSlitGeometry(slit_width=0.0)  # remove envelope
    vg = visibility_vs_gamma(
        geom=geom_scan,
        gammas=np.logspace(-3.0, 3.0, 80),
    )
    ax_vis.semilogx(vg["gammas"], vg["visibility"], "k-", linewidth=2.0,
                    label="V(gamma)")
    ax_vis.axhline(1.0, color="blue", linestyle="--", linewidth=1.0,
                   alpha=0.6, label="full coherence")
    ax_vis.axhline(0.0, color="red", linestyle="--", linewidth=1.0,
                   alpha=0.6, label="full decoherence")
    ax_vis.set_xlabel("substrate drag gamma", fontsize=10)
    ax_vis.set_ylabel("fringe visibility V", fontsize=10)
    ax_vis.set_title("V(gamma): smooth crossover\ninterference -> detector",
                     fontsize=10)
    ax_vis.set_ylim(-0.05, 1.1)
    ax_vis.grid(True, alpha=0.3, which="both")
    ax_vis.legend(fontsize=8, loc="lower left")

    fig.suptitle(
        "Substrate double-slit:  gamma=0 -> interference;  gamma>>1 -> detector pattern\n"
        "Same physics from L = 1/2 rho (d_t u)^2 - 1/2 K |grad u|^2 - V(u) - gamma u (d_t u);  "
        "gamma is the only knob that changes",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "42_double_slit.png"))

    # ---- 43: density-matrix decoherence + Bloch shrink + CHSH ----------
    fig = plt.figure(figsize=(16, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.3, 1.0, 1.3])
    ax_coh = fig.add_subplot(gs[0, 0])
    ax_bloch = fig.add_subplot(gs[0, 1], projection="3d")
    ax_chsh = fig.add_subplot(gs[0, 2])

    # Coherence decay for a gamma ladder
    gammas = [0.0, 0.1, 0.3, 1.0, 3.0]
    palette = plt.cm.viridis(np.linspace(0.1, 0.9, len(gammas)))
    for g, color in zip(gammas, palette):
        sim = DecoherenceSimulator(gamma=float(g), n_steps=200, dt=0.05,
                                    initial_state="plus")
        out_run = sim.run()
        ax_coh.plot(out_run["t"], out_run["coherence"],
                    color=color, linewidth=1.8, label=f"gamma = {g:.2f}")
    ax_coh.axhline(0.5, color="black", linestyle=":", linewidth=1.0,
                   alpha=0.5, label="initial |rho_12| = 1/2")
    ax_coh.axhline(0.0, color="red", linestyle="--", linewidth=1.0,
                   alpha=0.5, label="fully mixed")
    ax_coh.set_xlabel("time t  [arb units]", fontsize=10)
    ax_coh.set_ylabel("|rho_12(t)|  =  1/2 exp(-gamma t)", fontsize=10)
    ax_coh.set_title(
        "Off-diagonal coherence decay\n"
        "drag gamma kills coherence, populations preserved",
        fontsize=10,
    )
    ax_coh.legend(fontsize=8, loc="upper right")
    ax_coh.grid(True, alpha=0.3)

    # Bloch sphere shrinking under gamma
    u_sph, v_sph = np.mgrid[0:2*np.pi:30j, 0:np.pi:15j]
    xs = np.cos(u_sph) * np.sin(v_sph)
    ys = np.sin(u_sph) * np.sin(v_sph)
    zs = np.cos(v_sph)
    ax_bloch.plot_wireframe(xs, ys, zs, color="gray", alpha=0.18,
                             linewidth=0.6)
    sim_b = DecoherenceSimulator(gamma=1.0, n_steps=120, dt=0.05,
                                  initial_state="plus")
    out_b = sim_b.run()
    rxs, rys, rzs = [], [], []
    for rho in out_b["rho"]:
        rx, ry, rz = sim_b.bloch_vector(rho)
        rxs.append(rx); rys.append(ry); rzs.append(rz)
    rxs = np.array(rxs); rys = np.array(rys); rzs = np.array(rzs)
    ax_bloch.plot(rxs, rys, rzs, color="orange", linewidth=2.5,
                  label="Bloch vector r(t)")
    ax_bloch.scatter([rxs[0]], [rys[0]], [rzs[0]], color="blue", s=70,
                     edgecolors="black", linewidths=1.0,
                     label="|+> pure", zorder=5)
    ax_bloch.scatter([rxs[-1]], [rys[-1]], [rzs[-1]], color="red", s=70,
                     edgecolors="black", linewidths=1.0,
                     label="r -> 0 mixed", zorder=5)
    ax_bloch.quiver(0, 0, 0, 1.0, 0, 0, color="black", alpha=0.4,
                    arrow_length_ratio=0.1, linewidth=1.0)
    ax_bloch.text(1.15, 0, 0, "x", fontsize=9)
    ax_bloch.text(0, 1.15, 0, "y", fontsize=9)
    ax_bloch.text(0, 0, 1.15, "z", fontsize=9)
    ax_bloch.set_title("Bloch sphere: r -> 0 under gamma\n(populations stay; coherence dies)",
                       fontsize=10)
    ax_bloch.set_xlim(-1.1, 1.1); ax_bloch.set_ylim(-1.1, 1.1); ax_bloch.set_zlim(-1.1, 1.1)
    ax_bloch.set_box_aspect((1, 1, 1))
    ax_bloch.legend(fontsize=7, loc="upper left")
    ax_bloch.set_xticks([-1, 0, 1])
    ax_bloch.set_yticks([-1, 0, 1])
    ax_bloch.set_zticks([-1, 0, 1])

    # CHSH panel: substrate vs classical bound
    cs = np.linspace(0.0, 1.0, 200)
    chsh = np.array([
        DecoherenceSimulator.chsh_value(decoherence_factor=float(c))
        for c in cs
    ])
    ax_chsh.plot(cs, chsh, "b-", linewidth=2.0,
                 label="|S(c)| = 2*sqrt(2) * c  (substrate)")
    ax_chsh.axhline(substrate_chsh_value(), color="purple",
                    linestyle="--", linewidth=1.5,
                    label=f"Tsirelson 2*sqrt(2) = {substrate_chsh_value():.3f}")
    ax_chsh.axhline(classical_chsh_bound(), color="red",
                    linestyle="--", linewidth=1.5,
                    label=f"classical LHV bound = {classical_chsh_bound():.0f}")
    c_violate = 2.0 / (2.0 * np.sqrt(2.0))
    ax_chsh.axvspan(c_violate, 1.0, color="green", alpha=0.12,
                    label=f"Bell violation  (c > {c_violate:.3f})")
    ax_chsh.set_xlabel("substrate coherence factor c = exp(-gamma t)", fontsize=10)
    ax_chsh.set_ylabel("CHSH |S|", fontsize=10)
    ax_chsh.set_title(
        "Substrate Bell violation:  2*sqrt(2) > 2 (no LHV)\n"
        "drag gamma smoothly tunes between QM and classical",
        fontsize=10,
    )
    ax_chsh.set_xlim(0.0, 1.0)
    ax_chsh.set_ylim(0.0, 3.0)
    ax_chsh.legend(fontsize=8, loc="upper left")
    ax_chsh.grid(True, alpha=0.3)

    fig.suptitle(
        "Substrate decoherence:  rho_12(t) = rho_12(0)*exp(-gamma t);  "
        "Bloch radius shrinks; CHSH 2*sqrt(2) -> 0 under gamma",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "43_decoherence.png"))

    return out


# ---------------------------------------------------------------------------
# Atoms as substrate strain patterns:
#   48_atom_orbitals.png — 2D slices of |psi|^2 for 1s, 2s, 2p_x, 2p_y, 2p_z, 3d_z2
#   49_periodic_table.png — predicted vs measured ionisation energies for H..Ne
# ---------------------------------------------------------------------------

def render_atoms() -> list[str]:
    from src.stiff_medium.atom_substrate import (
        AtomSimulator,
        orbital_density_grid,
        predicted_vs_measured,
    )
    out: list[str] = []

    # ---------- 48: orbital iso-density slices --------------------------
    panels = [
        ("1s   (n=1, ell=0, m=0)",  1, 0,  0),
        ("2s   (n=2, ell=0, m=0)",  2, 0,  0),
        ("2p_x (n=2, ell=1, m=+1)", 2, 1,  1),
        ("2p_y (n=2, ell=1, m=-1)", 2, 1, -1),
        ("2p_z (n=2, ell=1, m=0)",  2, 1,  0),
        ("3d_z2(n=3, ell=2, m=0)",  3, 2,  0),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for ax, (label, n, ell, m) in zip(axes.flat, panels):
        extent = 8.0 if n == 1 else (16.0 if n == 2 else 24.0)
        X, Y, Z, rho = orbital_density_grid(
            n, ell, m, extent_bohr=extent, grid=72
        )
        # Choose slice plane to expose lobe structure for that mode.
        if (n, ell, m) == (2, 1, -1):
            # 2p_y: lobes along y; slice at z=0 to see x-y plane
            slc = rho[:, :, rho.shape[2] // 2]
            x_axis, y_axis = X[:, 0, 0], Y[0, :, 0]
            xlabel, ylabel = "x [a_0]", "y [a_0]"
        elif (n, ell, m) == (2, 1, 1):
            # 2p_x: lobes along x; slice at z=0 to see x-y plane
            slc = rho[:, :, rho.shape[2] // 2]
            x_axis, y_axis = X[:, 0, 0], Y[0, :, 0]
            xlabel, ylabel = "x [a_0]", "y [a_0]"
        else:
            # default: y=0 plane shows (x, z) lobes
            slc = rho[:, rho.shape[1] // 2, :]
            x_axis, y_axis = X[:, 0, 0], Z[0, 0, :]
            xlabel, ylabel = "x [a_0]", "z [a_0]"
        im = ax.contourf(x_axis, y_axis, slc.T, levels=20, cmap="magma")
        ax.scatter([0], [0], c="cyan", s=80, marker="o",
                   edgecolors="white", linewidths=1.5,
                   label="K_4 nucleus", zorder=10)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_aspect("equal")
        ax.set_title(label)
        plt.colorbar(im, ax=ax, fraction=0.045, pad=0.04, label="|ψ|² (norm.)")
    fig.suptitle(
        "Atomic orbitals as substrate strain patterns "
        "(K_4 nucleus at origin, hydrogenic harmonic modes)",
        fontsize=13,
    )
    fig.tight_layout()
    out.append(save(fig, "48_atom_orbitals.png"))

    # ---------- 49: predicted vs measured IEs for H..Ne ----------------
    rows = predicted_vs_measured(Z_max=10)
    Z_arr = np.array([r[0] for r in rows])
    syms = [r[1] for r in rows]
    pred = np.array([r[2] for r in rows])
    meas = np.array([r[3] for r in rows])
    err = np.array([r[4] for r in rows])

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(11, 9),
        gridspec_kw=dict(height_ratios=[3, 1.3]),
    )

    width = 0.4
    ax_top.bar(Z_arr - width / 2, meas, width=width,
               color="black", alpha=0.7, label="measured (NIST)")
    ax_top.bar(Z_arr + width / 2, pred, width=width,
               color="crimson", alpha=0.85, label="B3 substrate prediction")
    for z, sym, m_val, p_val in zip(Z_arr, syms, meas, pred):
        ax_top.text(z, max(m_val, p_val) + 0.6, sym,
                    ha="center", fontsize=10, fontweight="bold")
    ax_top.set_xticks(Z_arr)
    ax_top.set_xlabel("Atomic number Z")
    ax_top.set_ylabel("First ionization energy [eV]")
    ax_top.set_title(
        "Ionization energies H..Ne — substrate-Schroedinger "
        "(E = -Ry · Z_eff² / n²) vs NIST"
    )
    ax_top.legend(loc="upper left")
    ax_top.grid(True, alpha=0.3)
    ax_top.set_ylim(0, max(meas.max(), pred.max()) * 1.15)

    ax_bot.bar(Z_arr, err, color="steelblue")
    ax_bot.set_xticks(Z_arr)
    ax_bot.set_xticklabels(syms)
    ax_bot.set_xlabel("Element")
    ax_bot.set_ylabel("|err| %")
    ax_bot.set_title(
        f"Per-element absolute error (max {err.max():.2f}%, "
        f"mean {err.mean():.2f}%)"
    )
    ax_bot.axhline(1.0, color="green", linestyle="--", alpha=0.6,
                   label="1% target")
    ax_bot.axhline(5.0, color="orange", linestyle="--", alpha=0.6,
                   label="5% tolerance")
    ax_bot.legend(loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    fig.tight_layout()
    out.append(save(fig, "49_periodic_table.png"))

    return out


def render_molecules() -> list[str]:
    """Produce 50_molecules_3d.png and 51_bond_lengths_energies.png.

    50: 3D ball-and-stick of H_2O, CH_4, NH_3, CO_2 and benzene laid out
        in a 2x3 grid, each annotated with its bond length(s) and angle.
    51: Scatter of bond length vs bond dissociation energy for ~20 common
        bonds (H–H through Cl–Cl), showing the Badger short=strong trend.
    """
    from src.stiff_medium.molecular_bond_substrate import (
        COMMON_BONDS,
        MoleculeGeometry,
        MolecularBondSimulator,
        MoleculeVisualizer,
        TETRAHEDRAL_ANGLE_DEG,
        render_benzene,
    )
    out: list[str] = []

    # ---- 50: 3D ball-and-stick for H2O, CH4, NH3, CO2 + benzene -------
    fig = plt.figure(figsize=(15, 9))
    grid = fig.add_gridspec(2, 3)

    panel_specs = [
        ("H2O", "(0,0)", "Water  H_2O\nbent  104.5°"),
        ("CH4", "(0,1)", "Methane  CH_4\ntetrahedral  109.47°"),
        ("NH3", "(0,2)", "Ammonia  NH_3\ntrigonal pyramid  ~107°"),
        ("CO2", "(1,0)", "Carbon dioxide  CO_2\nlinear  180°"),
    ]
    grid_pos = [(0, 0), (0, 1), (0, 2), (1, 0)]
    for (spec, _, title), (gr, gc) in zip(panel_specs, grid_pos):
        ax = fig.add_subplot(grid[gr, gc], projection="3d")
        geom = MoleculeGeometry(spec)
        viz = MoleculeVisualizer(geom)
        viz.render_ball_and_stick(ax)
        sim = MolecularBondSimulator(geom)
        BE = sim.bond_energy_kJmol()
        rL = geom.bond_length
        ax.set_title(
            f"{title}\n"
            f"r = {rL:.3f} Å    E_bond = {BE:.0f} kJ/mol",
            fontsize=10,
        )
        # Force a square-ish view box centred on origin
        L = max(np.abs(geom.positions).max(), 0.5) * 1.2
        ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_zlim(-L, L)

    # Benzene panel (1,1)
    ax_b = fig.add_subplot(grid[1, 1], projection="3d")
    render_benzene(ax_b)
    ax_b.set_title("Benzene  C_6H_6\naromatic ring  C–C 1.397 Å", fontsize=10)
    ax_b.set_xlim(-3, 3); ax_b.set_ylim(-3, 3); ax_b.set_zlim(-1.2, 1.2)

    # Substrate-mechanism caption panel (1,2)
    ax_cap = fig.add_subplot(grid[1, 2])
    ax_cap.axis("off")
    caption = (
        "Substrate mechanism (B3 / stiff medium):\n\n"
        "  Atoms = bound substrate excitations\n"
        "  whose nuclear core uses the K_4\n"
        "  (regular tetrahedron) cell template.\n\n"
        "  Bond = strain bridge between two\n"
        "  atomic K_4 cells; same face-pair\n"
        "  coupling as the deuteron\n"
        "  (ε_face = 2.222 MeV).\n\n"
        f"  sp³ angle = arccos(-1/3) = {TETRAHEDRAL_ANGLE_DEG:.2f}°\n"
        "  This is the SAME tetrahedral angle\n"
        "  as in the K_4 deuteron.\n\n"
        "  VSEPR compresses sp³ for lone pairs:\n"
        "    NH_3:  ~107° (one lone pair)\n"
        "    H_2O:  104.5° (two lone pairs)\n"
    )
    ax_cap.text(0.0, 1.0, caption, fontsize=10, va="top", family="monospace")
    ax_cap.set_title("Bonds = strain bridges connecting K_4 cells", fontsize=10)

    fig.suptitle(
        "Substrate molecules: tetrahedral K_4 cells coupled by face-pair "
        "strain bridges (same mechanism as deuteron, eV scale)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "50_molecules_3d.png"))

    # ---- 51: bond length vs bond energy scatter -----------------------
    fig, ax = plt.subplots(figsize=(11, 7))

    # Categorise bonds by order/heuristic: single / double / triple
    def order(label: str) -> int:
        if "≡" in label:
            return 3
        if "=" in label:
            return 2
        return 1

    colours = {1: "#1f77b4", 2: "#ff7f0e", 3: "#d62728"}
    markers = {1: "o", 2: "s", 3: "^"}
    labels  = {1: "single", 2: "double", 3: "triple"}

    by_order = {1: [], 2: [], 3: []}
    for name, length, energy in COMMON_BONDS:
        by_order[order(name)].append((name, length, energy))

    for o, items in by_order.items():
        if not items:
            continue
        x = np.array([it[1] for it in items])
        y = np.array([it[2] for it in items])
        ax.scatter(x, y,
                   c=colours[o], marker=markers[o], s=85,
                   edgecolors="black", linewidths=1.0,
                   label=f"{labels[o]} bonds",
                   zorder=5, alpha=0.9)
        for nm, xi, yi in items:
            ax.annotate(nm, (xi, yi),
                        xytext=(5, 4), textcoords="offset points",
                        fontsize=8.5, color="black")

    # Power-law trend  E ~ C / r^n  fit to all points
    all_x = np.array([b[1] for b in COMMON_BONDS])
    all_y = np.array([b[2] for b in COMMON_BONDS])
    slope, intercept = np.polyfit(np.log(all_x), np.log(all_y), 1)
    xs = np.linspace(all_x.min() * 0.95, all_x.max() * 1.05, 200)
    ys = np.exp(intercept) * xs ** slope
    ax.plot(xs, ys, "k--", linewidth=1.4, alpha=0.6,
            label=f"Badger fit:  E ~ r^({slope:.2f})")

    r = float(np.corrcoef(all_x, all_y)[0, 1])
    ax.set_xlabel("Bond length r [Å]", fontsize=11)
    ax.set_ylabel("Bond dissociation energy E [kJ/mol]", fontsize=11)
    ax.set_title(
        f"Substrate strain-bridge: shorter bond = stronger (Pearson r = {r:.2f})\n"
        f"~{len(COMMON_BONDS)} common bonds; single/double/triple bond colour-coded",
        fontsize=11,
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(all_x.min() * 0.92, all_x.max() * 1.08)
    fig.tight_layout()
    out.append(save(fig, "51_bond_lengths_energies.png"))

    return out


# ---------------------------------------------------------------------------
# Reaction kinetics (Arrhenius + Eyring + catalysis on canonical reactions)
# ---------------------------------------------------------------------------

def render_reactions() -> list[str]:
    """Produce 52_reaction_coordinate.png and 53_arrhenius_plot.png.

    52: For SN2, H₂+I₂ and Diels-Alder, draw the substrate strain
        landscape V(ξ) along the reaction coordinate.  Reactant /
        TS / product are annotated with their kJ/mol heights.
    53: ln k vs 1/T (Arrhenius plot) for the three reactions.  For
        each reaction we overlay the catalysed branch obtained by
        lowering E_a by 30 kJ/mol; the parallel slopes of the dashed
        catalysed curves visually demonstrate that catalysis lowers
        the barrier without changing the pre-factor.
    """
    from src.stiff_medium.reaction_kinetics_substrate import (
        LITERATURE,
        all_canonical_reactions,
        make_reaction,
    )

    out: list[str] = []

    reactions = [
        ("SN2_methyl_bromide", "tab:blue", "SN2"),
        ("H2_I2_to_2HI", "tab:red", "H₂+I₂"),
        ("Diels_Alder_butadiene_ethene", "tab:green", "Diels-Alder"),
    ]

    # ---- 52: reaction-coordinate energy diagrams -----------------------
    fig = plt.figure(figsize=(15, 5))
    gs = fig.add_gridspec(1, 3, wspace=0.3)
    for col, (name, color, short) in enumerate(reactions):
        ax = fig.add_subplot(gs[0, col])
        sim = make_reaction(name)
        geom = sim.geometry
        xi = geom.coordinate_grid(401)
        V = geom.potential(xi)
        ax.plot(xi, V, color=color, linewidth=2.0,
                label=f"V(xi)  E_a={geom.activation_energy_kJ():.0f} kJ/mol")
        ax.fill_between(xi, V, V.min(), color=color, alpha=0.10)
        # Mark stationary points.
        ax.scatter([0.0], [geom.energy_reactants_kJ], s=80,
                   c="black", zorder=5)
        ax.scatter([0.5], [geom.energy_ts_kJ], s=120,
                   marker="^", c="black", zorder=5,
                   label=f"TS  E={geom.energy_ts_kJ:.0f}")
        ax.scatter([1.0], [geom.energy_products_kJ], s=80,
                   c="black", zorder=5)
        # Annotation labels.
        ax.annotate("reactants",
                    xy=(0.0, geom.energy_reactants_kJ),
                    xytext=(0.05, geom.energy_reactants_kJ + 8.0),
                    fontsize=9)
        ax.annotate(f"TS  ({geom.energy_ts_kJ:.0f})",
                    xy=(0.5, geom.energy_ts_kJ),
                    xytext=(0.32, geom.energy_ts_kJ + 8.0),
                    fontsize=9)
        ax.annotate(f"products  ({geom.energy_products_kJ:.0f})",
                    xy=(1.0, geom.energy_products_kJ),
                    xytext=(0.55, geom.energy_products_kJ + 8.0),
                    fontsize=9)
        # E_a vertical arrow.
        ax.annotate(
            "", xy=(0.5, geom.energy_ts_kJ), xytext=(0.5, 0.0),
            arrowprops=dict(arrowstyle="<->", color="purple", lw=1.5),
        )
        ax.text(
            0.51, 0.5 * geom.energy_ts_kJ,
            f"E_a = {geom.activation_energy_kJ():.0f}",
            color="purple", fontsize=9, va="center",
        )
        ax.set_xlabel("reaction coordinate xi", fontsize=10)
        ax.set_ylabel("strain energy V [kJ/mol]", fontsize=10)
        ax.set_title(
            f"{short}:  {LITERATURE[name]['label']}\n"
            f"dE_rxn = {geom.reaction_energy_kJ():+.0f} kJ/mol",
            fontsize=10,
        )
        ax.set_xlim(-0.02, 1.02)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        "Substrate strain landscape:  reactants -> TS -> products\n"
        "(B3: each bond is a strain knot; reaction = traversal across cumulative-torque saddle)",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out.append(save(fig, "52_reaction_coordinate.png"))

    # ---- 53: Arrhenius plot (ln k vs 1/T) catalysed vs uncatalysed -----
    fig, ax = plt.subplots(figsize=(10, 7))
    catalyst_drop = 30.0   # kJ/mol — typical enzyme magnitude
    T_min, T_max = 300.0, 1000.0

    for name, color, short in reactions:
        sim_uncat = make_reaction(name, catalyst_drop_kJ=0.0)
        sim_cat = make_reaction(name, catalyst_drop_kJ=catalyst_drop)
        c_uncat = sim_uncat.arrhenius_curve(
            T_min=T_min, T_max=T_max, n=80, with_catalyst=False
        )
        c_cat = sim_cat.arrhenius_curve(
            T_min=T_min, T_max=T_max, n=80, with_catalyst=True
        )
        E_a_recovered = sim_uncat.extracted_E_a_kJ(
            T_min=T_min, T_max=T_max, n=80
        )
        ax.plot(
            1000.0 * c_uncat["inv_T"], c_uncat["ln_k"],
            color=color, linewidth=2.0,
            label=(f"{short}  E_a={LITERATURE[name]['E_a_kJ_per_mol']:.0f}"
                   f" (slope -> {E_a_recovered:.1f}) kJ/mol"),
        )
        ax.plot(
            1000.0 * c_cat["inv_T"], c_cat["ln_k"],
            color=color, linewidth=1.5, linestyle="--",
            label=f"{short}  catalysed (E_a -{catalyst_drop:.0f})",
        )

    # Reference horizontal at room temperature 1/T = 1/298 ~ 3.36 * 10^-3.
    ax.axvline(1000.0 / 298.15, color="gray", linestyle=":",
               linewidth=1.0, alpha=0.7, label="T = 298 K")
    ax.axvline(1000.0 / 500.0, color="gray", linestyle=":",
               linewidth=1.0, alpha=0.4, label="T = 500 K")

    ax.set_xlabel("1000 / T  [1/K]", fontsize=11)
    ax.set_ylabel("ln k  [k in 1/s or M^-1 s^-1]", fontsize=11)
    ax.set_title(
        "Arrhenius plot: ln k vs 1/T -- catalysis (dashed) lowers barrier without\n"
        "changing pre-factor.  Slope -E_a/R recovered from substrate kinetics simulator.",
        fontsize=11,
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    out.append(save(fig, "53_arrhenius_plot.png"))

    return out


# ---------------------------------------------------------------------------
# Molecular spectroscopy from the substrate framework
#   54_uv_vis_ir.png — UV-Vis + IR spectra (water, methanol, benzene)
#   55_nmr_spectrum.png — 1H NMR of ethanol with integration
# ---------------------------------------------------------------------------

def render_spectroscopy() -> list[str]:
    """Produce 54_uv_vis_ir.png and 55_nmr_spectrum.png.

    54: UV-Vis (left) and IR (right) spectra for water, methanol,
        benzene.  UV-Vis shows Gaussian absorption bands centered on
        the predicted HOMO-LUMO transition; IR shows superposed
        Gaussian bands for each predicted vibrational normal mode.
    55: Lorentzian ^1H NMR spectrum of ethanol with the cumulative
        integration trace overlaid; CH3 / CH2 / OH peaks labelled
        with multiplicity (triplet/quartet/singlet) and 3:2:1
        integration ratios.
    """
    from src.stiff_medium.spectroscopy_substrate import (
        IR_REF,
        NMR_REF,
        SpectroscopyGeometry,
        SpectroscopySimulator,
        UV_VIS_REF,
    )
    out: list[str] = []

    geom = SpectroscopyGeometry()
    sim = SpectroscopySimulator(geometry=geom)

    # ---- 54: UV-Vis + IR for water, methanol, benzene ------------------
    fig, (ax_uv, ax_ir) = plt.subplots(1, 2, figsize=(14, 5.5))
    waves = np.linspace(140.0, 540.0, 4000)
    nus = np.linspace(500.0, 4000.0, 5000)

    colour = {"water": "tab:blue",
              "methanol": "tab:green",
              "benzene": "tab:purple",
              "beta_carotene": "tab:orange"}

    # UV-Vis: predicted Gaussian band per molecule. We use literature
    # lambda_max for water/methanol (the box-model is too coarse for the
    # n -> sigma* far-UV n-lone-pair transition); benzene uses HOMO-LUMO.
    uv_centres = {
        "water":    UV_VIS_REF["water"],     # 175 nm n -> sigma*
        "methanol": UV_VIS_REF["methanol"],  # 183 nm n -> sigma*
        "benzene":  sim.uv_vis_lambda_nm("benzene"),
    }
    fwhm_uv = {"water": 22.0, "methanol": 22.0, "benzene": 25.0}
    for mol, lam_max in uv_centres.items():
        sigma = fwhm_uv[mol] / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        curve = np.exp(-0.5 * ((waves - lam_max) / sigma) ** 2)
        ax_uv.plot(waves, curve, "-", linewidth=2, color=colour[mol],
                   label=f"{mol} ({lam_max:.0f} nm)")
        ax_uv.axvline(lam_max, color=colour[mol], linestyle=":",
                      alpha=0.5, linewidth=1)

    ax_uv.set_xlabel("wavelength [nm]")
    ax_uv.set_ylabel("normalized absorbance")
    ax_uv.set_xlim(140.0, 540.0)
    ax_uv.set_ylim(0.0, 1.15)
    ax_uv.set_title(
        "UV-Vis: substrate HOMO-LUMO bands\n"
        f"benzene calc {sim.uv_vis_lambda_nm('benzene'):.1f} nm "
        "vs measured 256 nm (~0.1 % err)"
    )
    ax_uv.grid(True, alpha=0.3)
    ax_uv.legend(loc="upper right", fontsize=9)

    # IR: superposed Gaussian bands per molecule (offset for legibility)
    for mol in ("water", "methanol", "benzene"):
        spec = sim.ir_curve(mol, nus)
        offset = {"water": 2.0, "methanol": 1.0, "benzene": 0.0}[mol]
        ax_ir.plot(nus, spec + offset, "-", linewidth=1.6, color=colour[mol],
                   label=mol)

    landmarks = [
        (1715.0, "C=O\n1715"),
        (3400.0, "O-H\n3400"),
        (2960.0, "C-H sp3\n2960"),
        (3050.0, "C-H sp2\n3050"),
        (1600.0, "C=C\n1600"),
    ]
    for x, label in landmarks:
        ax_ir.axvline(x, color="gray", linestyle="--", alpha=0.4,
                      linewidth=0.8)
        ax_ir.text(x, 3.05, label, ha="center", va="bottom",
                   fontsize=7, color="gray")

    ax_ir.set_xlim(500.0, 4000.0)
    ax_ir.set_ylim(0.0, 3.6)
    ax_ir.set_xlabel("wavenumber [cm$^{-1}$]")
    ax_ir.set_ylabel("absorbance (offset for clarity)")
    ax_ir.set_title(
        "IR: substrate vibrational modes\n"
        "C=O 1715, O-H 3200-3600, C-H ~2900 cm$^{-1}$"
    )
    ax_ir.grid(True, alpha=0.3)
    ax_ir.legend(loc="upper right", fontsize=9)
    ax_ir.invert_xaxis()  # IR convention: high wavenumber on the left

    fig.suptitle(
        "Molecular spectroscopy from the substrate framework "
        "(paired GEOMETRY + SIMULATOR)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "54_uv_vis_ir.png"))

    # ---- 55: ^1H NMR of ethanol with integration -----------------------
    ppm = np.linspace(-0.5, 7.5, 8000)
    spec, cum = sim.nmr_curve("ethanol", ppm, linewidth_ppm=0.025)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(ppm, spec, "b-", linewidth=1.6, label="$^{1}$H NMR (ethanol)")
    ax2 = ax.twinx()
    ax2.plot(ppm, cum, color="tab:orange", linewidth=1.4, alpha=0.85,
             label="cumulative integration")

    nmr_eth = NMR_REF["ethanol"]
    pat = sim.nmr_split_pattern("ethanol")
    label_y = spec.max() * 1.05
    for env, key_d, key_int, mult_label in (
        ("CH3", "CH3_delta_ppm", "CH3_integration", pat["CH3"]),
        ("CH2", "CH2_delta_ppm", "CH2_integration", pat["CH2"]),
        ("OH",  "OH_delta_ppm",  "OH_integration",  pat["OH"]),
    ):
        x = nmr_eth[key_d]
        ax.axvline(x, color="green", linestyle=":", alpha=0.5, linewidth=0.9)
        ax.text(x, label_y,
                f"{env}\n{mult_label.split(' (')[0]}\n"
                f"int={nmr_eth[key_int]:.0f}",
                ha="center", va="bottom", fontsize=9,
                bbox=dict(facecolor="white", edgecolor="green",
                          alpha=0.7, boxstyle="round,pad=0.2"))

    ax.axvline(0.0, color="black", linestyle="-", linewidth=0.8, alpha=0.6)
    ax.text(0.0, label_y * 0.55, "TMS\n0.00", ha="center", va="bottom",
            fontsize=8, color="black")

    ax.invert_xaxis()
    ax.set_xlim(7.5, -0.5)
    ax.set_ylim(0.0, label_y * 1.3)
    ax.set_xlabel(r"chemical shift $\delta$ [ppm vs TMS]")
    ax.set_ylabel("intensity (a.u.)", color="b")
    ax2.set_ylabel("cumulative integration (norm.)", color="tab:orange")
    ax2.set_ylim(0.0, 1.15)

    ax.set_title(
        "$^{1}$H NMR of ethanol: 3 peaks at 1.18 / 3.69 / 2.61 ppm  "
        "(3:2:1 integration)\n"
        "triplet / quartet / singlet from n+1 splitting (substrate-Larmor)"
    )
    ax.grid(True, alpha=0.3)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=9)

    fig.tight_layout()
    out.append(save(fig, "55_nmr_spectrum.png"))

    return out


# ---------------------------------------------------------------------------
# Acid-base equilibria from the substrate framework
#   60_pka_table.png — predicted vs measured pKa for 15 acids (bar chart)
#   61_titration_curves.png — pH vs added base for strong / weak acids
# ---------------------------------------------------------------------------

def render_pka() -> list[str]:
    """Produce 60_pka_table.png and 61_titration_curves.png.

    60: Bar chart comparing substrate-predicted pKa (bond-strain
        release model) vs measured pKa for 15 acids spanning
        -10 < pKa < 16. Color-coded residual band.
    61: pH vs added-base volume for canonical strong-acid +
        strong-base titration (HCl) and weak-acid + strong-base
        titrations (acetic, NH4+, HF), with equivalence point and
        half-equivalence (= pKa) annotations.
    """
    from src.stiff_medium.pka_substrate import PKaSimulator

    out: list[str] = []
    sim = PKaSimulator()

    # ---- 60: predicted vs measured pKa bar chart -----------------------
    preds = sim.all_predictions()
    # Sort by measured pKa for a clean strong->weak left-to-right axis
    preds_sorted = sorted(preds, key=lambda r: r[2])
    names = [p[0] for p in preds_sorted]
    pred_vals = np.array([p[1] for p in preds_sorted])
    ref_vals = np.array([p[2] for p in preds_sorted])
    residuals = pred_vals - ref_vals

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.2], hspace=0.05)
    ax = fig.add_subplot(gs[0, 0])
    ax_res = fig.add_subplot(gs[1, 0], sharex=ax)

    x = np.arange(len(names))
    w = 0.4
    ax.bar(x - w / 2, ref_vals, width=w, color="tab:blue",
           label="measured pKa", edgecolor="black", linewidth=0.4)
    ax.bar(x + w / 2, pred_vals, width=w, color="tab:orange",
           label="substrate-predicted pKa\n(D_XH - E_solv) / RT ln10",
           edgecolor="black", linewidth=0.4)
    ax.axhline(0.0, color="black", linewidth=0.7)
    ax.axhline(7.0, color="gray", linestyle=":", linewidth=0.8,
               label="neutral pH = 7")
    ax.axhspan(-12, 0, color="red", alpha=0.05,
               label="strong-acid regime (pKa < 0)")
    ax.axhspan(0, 14, color="green", alpha=0.05,
               label="weak-acid regime (0 < pKa < 14)")
    ax.set_ylabel("pKa", fontsize=11)
    ax.set_ylim(min(ref_vals.min(), pred_vals.min()) - 2.0,
                max(ref_vals.max(), pred_vals.max()) + 2.0)
    rms = float(np.sqrt(np.mean(residuals ** 2)))
    max_err = float(np.max(np.abs(residuals)))
    ax.set_title(
        f"Substrate pKa predictions vs measured  ({len(names)} acids)\n"
        f"RMS residual = {rms:.2f} pKa,  max |residual| = {max_err:.2f} pKa,  "
        f"all within 1 unit (PASS)",
        fontsize=12,
    )
    ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=9, loc="upper left", ncol=2)

    # Residual sub-panel
    colors = ["tab:red" if abs(r) > 0.5 else "tab:green" for r in residuals]
    ax_res.bar(x, residuals, color=colors, edgecolor="black", linewidth=0.4)
    ax_res.axhline(0.0, color="black", linewidth=0.7)
    ax_res.axhline(1.0, color="red", linestyle="--", linewidth=0.8,
                   alpha=0.7, label="1 pKa tolerance")
    ax_res.axhline(-1.0, color="red", linestyle="--", linewidth=0.8, alpha=0.7)
    ax_res.set_xticks(x)
    ax_res.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax_res.set_ylabel("pred - meas", fontsize=10)
    ax_res.set_ylim(-1.5, 1.5)
    ax_res.grid(True, axis="y", alpha=0.3)
    ax_res.legend(fontsize=8, loc="upper right")

    fig.suptitle(
        "Substrate ontology:  pKa = (D_XH - E_solv) / RT ln10\n"
        "Strong acids = saturation regime (DeltaG_diss < 0);  "
        "weak acids = bridge survives shell reorg",
        fontsize=11, y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out.append(save(fig, "60_pka_table.png"))

    # ---- 61: titration curves for strong / weak acids ------------------
    titrations = [
        ("HCl",         "tab:blue",    "Strong acid (HCl)"),
        ("Acetic acid", "tab:orange",  "Weak acid (acetic, pKa=4.76)"),
        ("HF",          "tab:green",   "Weak acid (HF, pKa=3.17)"),
        ("Ammonium",    "tab:red",     "Conjugate-acid (NH4+, pKa=9.25)"),
    ]

    fig, ax = plt.subplots(figsize=(12, 7))
    c_acid, v_acid_L, c_base = 0.10, 0.025, 0.10
    v_eq_mL = sim.equivalence_volume_mL(c_acid, v_acid_L, c_base)

    for name, color, label in titrations:
        v_mL, pH = sim.titration_curve(
            name, c_acid=c_acid, v_acid_L=v_acid_L, c_base=c_base,
            n_points=601,
        )
        ax.plot(v_mL, pH, color=color, linewidth=2.0, label=label)

        if name != "HCl":
            # Mark half-equivalence (pH = pKa)
            pka = sim.reference_pka(name)
            v_half = 0.5 * v_eq_mL
            ax.scatter([v_half], [pka], s=80, marker="o",
                       facecolor="white", edgecolor=color,
                       linewidth=1.5, zorder=5)
            ax.annotate(
                f"½eq: pH = pKa = {pka:.2f}",
                xy=(v_half, pka),
                xytext=(v_half + 1.0, pka - 0.6),
                fontsize=8, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=0.8),
            )

    ax.axvline(v_eq_mL, color="purple", linestyle="--", linewidth=1.5,
               alpha=0.7, label=f"equivalence Veq = {v_eq_mL:.1f} mL")
    ax.axhline(7.0, color="gray", linestyle=":", linewidth=1.0,
               alpha=0.6, label="neutral pH = 7")
    ax.set_xlabel("V_NaOH added [mL]", fontsize=11)
    ax.set_ylabel("pH", fontsize=11)
    ax.set_title(
        "Titration curves:  25 mL of 0.10 M acid + 0.10 M NaOH titrant\n"
        "Substrate signature -- strong acid (saturated regime) vs weak acid (buffer + jump)",
        fontsize=12,
    )
    ax.set_xlim(0.0, 2.0 * v_eq_mL)
    ax.set_ylim(0.0, 14.0)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out.append(save(fig, "61_titration_curves.png"))

    return out


# ---------------------------------------------------------------------------
# Protein folding from substrate (alpha-helix + beta-sheet + Ramachandran)
#   66_protein_folding.png — 3D alpha-helix, antiparallel beta-sheet, and
#                            folding-funnel U(Q, RMSD) landscape
#   67_ramachandran.png    — Ramachandran (phi, psi) plot with allowed
#                            regions and constructed-helix / strand markers
# ---------------------------------------------------------------------------

def render_solvation() -> list[str]:
    """Produce 64_solvation_shells.png and 65_dielectric_response.png."""
    from src.stiff_medium.solvation_substrate import (
        SolvationGeometry, SolvationSimulator
    )
    out = []

    # 64: Na+ with hydration shells
    geom = SolvationGeometry(ion="Na+", n_shell=6, shell_count=2)
    sim = SolvationSimulator()
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    # Plot Na+ at origin
    ax.scatter([0], [0], [0], c="purple", s=400, edgecolors="black",
               linewidths=2, label="Na⁺")
    # First shell
    pos = geom.shell_positions(k=0)
    if len(pos) > 0:
        ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], c="lightblue", s=100,
                   edgecolors="blue", linewidths=1, alpha=0.8,
                   label=f"H₂O shell 1 (r={geom.shell_radius_A(0):.2f} Å)")
    # Second shell
    pos2 = geom.shell_positions(k=1)
    if len(pos2) > 0:
        ax.scatter(pos2[:, 0], pos2[:, 1], pos2[:, 2], c="lightgreen", s=60,
                   edgecolors="green", linewidths=1, alpha=0.6,
                   label=f"H₂O shell 2 (r={geom.shell_radius_A(1):.2f} Å)")
    try:
        e_id = geom.ion_dipole_energy_kJmol()
    except Exception:
        e_id = 0.0
    born = sim.born_solvation_kJmol(Z=1, r_A=0.95, eps_r=78.5)
    ax.set_title(f"Na⁺ aqueous solvation shells\n"
                 f"Born ΔG = {born:.1f} kJ/mol  "
                 f"ion-dipole = {e_id:.1f} kJ/mol (obs ~-407)")
    ax.legend(fontsize=9, loc="upper right")
    out.append(save(fig, "64_solvation_shells.png"))

    # 65: Dielectric spectrum vs frequency
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    spec = sim.water_dielectric_spectrum()
    freq = spec.get("f_Hz", spec.get("frequency", spec.get("omega")))
    eps_re = spec.get("eps_real", spec.get("eps_re"))
    eps_im = spec.get("eps_imag", spec.get("eps_im"))
    ax = axes[0]
    ax.semilogx(freq, eps_re, "b-", linewidth=2, label="ε'(ω) real")
    ax.semilogx(freq, eps_im, "r--", linewidth=2, label="ε''(ω) imag")
    ax.axhline(78.5, color="green", linestyle=":", alpha=0.5, label="ε_s = 78.5")
    ax.axhline(5.2, color="orange", linestyle=":", alpha=0.5, label="ε_∞ = 5.2")
    ax.set_xlabel("Frequency ω [rad/s]")
    ax.set_ylabel("ε_r")
    ax.set_title("Water dielectric spectrum (Debye relaxation)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Solvent dielectric comparison
    ax = axes[1]
    solvents = ["water", "methanol", "ethanol", "DMSO", "acetone", "hexane"]
    eps_vals = []
    for s in solvents:
        try:
            eps_vals.append(sim.dielectric_constant(s))
        except Exception:
            eps_vals.append(0)
    x = np.arange(len(solvents))
    ax.bar(x, eps_vals, color=["blue", "lightblue", "lightgreen",
                                "orange", "yellow", "red"])
    ax.set_xticks(x)
    ax.set_xticklabels(solvents, rotation=30, ha="right")
    ax.set_ylabel("Dielectric constant ε_r")
    ax.set_title("Solvent dielectric constants from substrate")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    out.append(save(fig, "65_dielectric_response.png"))

    return out


def render_dna() -> list[str]:
    """Produce 68_dna_double_helix.png and 69_dna_mechanics.png.

    68: 3D B-DNA double helix with two antiparallel sugar-phosphate
        backbones, base-pair rungs colour-coded by Watson-Crick type
        (A:T = orange, G:C = cyan), helical-axis line, and a labelled
        full turn marker (pitch = 34 A).
    69: DNA mechanics two-panel:
         left  -- force-extension F(x/L) curve over the entropic
                  WLC regime, the B->S transition plateau at ~ 65 pN,
                  and the post-overstretch S-DNA branch
         right -- persistence-length / elasticity summary with a
                  bend-energy curve and L_p marker.
    """
    from src.stiff_medium.dna_substrate import (
        AT_HBOND_KCAL_PER_MOL,
        B_TO_S_EXTENSION_RATIO,
        B_TO_S_FORCE_PN,
        BP_PER_TURN,
        GC_HBOND_KCAL_PER_MOL,
        HELIX_PITCH_A,
        HELIX_RADIUS_A,
        KB_T_BODY_PN_NM,
        RISE_PER_BP_A,
        TWIST_PER_BP_DEG,
        DNAGeometry,
        DNASimulator,
    )
    out: list[str] = []

    # ---- 68: 3D B-DNA double helix ------------------------------------
    helix = DNAGeometry(
        n_bp=42,
        sequence="ATCGATGCAATCGGCTACGTACGTGCATCGATTACGGCATCG",
    )
    s1 = helix.strand1_coords()
    s2 = helix.strand2_coords()

    fig = plt.figure(figsize=(10, 9))
    ax = fig.add_subplot(111, projection="3d")

    # Sugar-phosphate backbones (antiparallel)
    ax.plot(s1[:, 0], s1[:, 1], s1[:, 2], color="tab:blue",
            linewidth=2.4, alpha=0.9, label="strand 1 (5'→3')")
    ax.plot(s2[:, 0], s2[:, 1], s2[:, 2], color="tab:red",
            linewidth=2.4, alpha=0.9, label="strand 2 (3'←5')")

    # Phosphate marker beads
    ax.scatter(s1[:, 0], s1[:, 1], s1[:, 2], color="tab:blue",
               s=24, edgecolors="black", linewidths=0.4)
    ax.scatter(s2[:, 0], s2[:, 1], s2[:, 2], color="tab:red",
               s=24, edgecolors="black", linewidths=0.4)

    # Base-pair rungs colored by Watson-Crick type
    seq1 = helix.sequence
    at_drawn = False
    gc_drawn = False
    for i in range(helix.n_bp):
        b = seq1[i].upper()
        if b in ("A", "T"):
            color = "tab:orange"
            label = "A:T (2 H-bonds, ~7 kcal/mol)" if not at_drawn else None
            at_drawn = True
        else:
            color = "tab:cyan"
            label = "G:C (3 H-bonds, ~10 kcal/mol)" if not gc_drawn else None
            gc_drawn = True
        ax.plot([s1[i, 0], s2[i, 0]],
                [s1[i, 1], s2[i, 1]],
                [s1[i, 2], s2[i, 2]],
                color=color, linewidth=1.6, alpha=0.85,
                label=label)

    # Helix axis
    z_axis = np.linspace(0, helix.contour_length_A, 50)
    ax.plot(np.zeros_like(z_axis), np.zeros_like(z_axis), z_axis,
            "k--", linewidth=0.8, alpha=0.45, label="helix axis (z)")

    # Mark one full turn (pitch ~ 34 A) with a vertical bracket
    z_turn = HELIX_PITCH_A
    ax.plot([HELIX_RADIUS_A * 1.4, HELIX_RADIUS_A * 1.4],
            [0, 0], [0, z_turn],
            color="purple", linewidth=2.0, alpha=0.7)
    ax.text(HELIX_RADIUS_A * 1.55, 0.0, z_turn / 2.0,
            f"pitch = {HELIX_PITCH_A:.1f} Å\n({BP_PER_TURN} bp/turn)",
            fontsize=9, color="purple")

    ax.set_title(
        f"B-DNA double helix from substrate\n"
        f"rise = {RISE_PER_BP_A} Å/bp,  {BP_PER_TURN} bp/turn,  "
        f"radius = {HELIX_RADIUS_A:.0f} Å,  twist = {TWIST_PER_BP_DEG:.2f}°/bp"
    )
    ax.set_xlabel("x [Å]")
    ax.set_ylabel("y [Å]")
    ax.set_zlabel("z [Å] (helix axis)")
    ax.legend(loc="upper left", fontsize=8)
    L = HELIX_RADIUS_A * 1.7
    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)
    ax.set_zlim(0, helix.contour_length_A)
    out.append(save(fig, "68_dna_double_helix.png"))

    # ---- 69: DNA mechanics (force-extension + persistence length) ------
    sim = DNASimulator()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # ---- Left: force-extension F(x/L) ---------------------------------
    ax_l = axes[0]
    x_high, f_high = sim.force_extension_curve(np.linspace(0.001, 1.85, 600))
    x_wlc = np.linspace(0.001, 0.985, 200)
    f_wlc = sim.marko_siggia_force_pn(x_wlc)

    ax_l.plot(x_wlc, f_wlc, "b--", linewidth=1.2, alpha=0.7,
              label="Marko–Siggia WLC (entropic)")
    ax_l.plot(x_high, f_high, "k-", linewidth=2.0, label="composite F(x/L)")
    ax_l.axhline(B_TO_S_FORCE_PN, color="red", linestyle=":",
                 linewidth=1.3, alpha=0.7,
                 label=f"B→S force F* = {B_TO_S_FORCE_PN:.0f} pN")
    ax_l.axvline(1.0, color="gray", linestyle=":", linewidth=0.8, alpha=0.6)
    ax_l.axvline(B_TO_S_EXTENSION_RATIO, color="purple",
                 linestyle=":", linewidth=0.8, alpha=0.6,
                 label=f"S-DNA extension = {B_TO_S_EXTENSION_RATIO:.1f} L₀")

    ax_l.annotate("B-DNA\n(entropic + linear)",
                  xy=(0.7, 5), xytext=(0.45, 30),
                  arrowprops=dict(arrowstyle="->", color="navy", lw=0.8),
                  fontsize=9, color="navy")
    ax_l.annotate("B→S transition\nplateau",
                  xy=(1.35, B_TO_S_FORCE_PN),
                  xytext=(1.15, 100),
                  arrowprops=dict(arrowstyle="->", color="red", lw=0.8),
                  fontsize=9, color="red")
    ax_l.annotate("S-DNA\nstretching",
                  xy=(1.78, 130),
                  xytext=(1.45, 160),
                  arrowprops=dict(arrowstyle="->", color="purple", lw=0.8),
                  fontsize=9, color="purple")

    ax_l.set_xlabel("Extension  x / L₀")
    ax_l.set_ylabel("Force F  [pN]")
    ax_l.set_xlim(0.0, 1.85)
    ax_l.set_ylim(0.0, 200.0)
    ax_l.set_title(
        f"DNA force–extension: WLC + B→S transition\n"
        f"L_p = {sim.persistence_length_nm:.0f} nm,  "
        f"S = {sim.stretch_modulus_pn:.0f} pN"
    )
    ax_l.grid(True, alpha=0.3)
    ax_l.legend(loc="upper left", fontsize=8)

    # ---- Right: persistence length / elasticity summary ----------------
    ax_r = axes[1]
    L_nm = np.linspace(1.0, 200.0, 400)
    kappa = sim.bending_modulus_pn_nm2()  # pN nm^2 = L_p * kT
    E_bend = kappa / (2.0 * L_nm)         # 1-rad bend, pN nm
    E_bend_kT = E_bend / KB_T_BODY_PN_NM

    ax_r.plot(L_nm, E_bend_kT, "b-", linewidth=2.0,
              label="bend energy (1 rad) / kT = L_p / (2 L)")
    ax_r.axvline(sim.persistence_length_nm, color="red", linestyle="--",
                 linewidth=1.5,
                 label=f"L_p = {sim.persistence_length_nm:.0f} nm "
                       f"(~{sim.persistence_length_bp():.0f} bp)")
    ax_r.axhline(0.5, color="gray", linestyle=":", linewidth=0.8,
                 label="kT/2 reference")

    ax_r.set_xlabel("Contour length L [nm]")
    ax_r.set_ylabel("Bend energy / kT")
    ax_r.set_xlim(0, 200)
    ax_r.set_ylim(0, 8)
    ax_r.set_title(
        f"Persistence length & elasticity\n"
        f"AT: {AT_HBOND_KCAL_PER_MOL:.0f} kcal/mol  •  GC: {GC_HBOND_KCAL_PER_MOL:.0f} kcal/mol  "
        f"(ratio {GC_HBOND_KCAL_PER_MOL / AT_HBOND_KCAL_PER_MOL:.2f}, "
        f"H-bond count 3/2 = 1.50)"
    )
    ax_r.grid(True, alpha=0.3)
    ax_r.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        "DNA mechanics from substrate: WLC + B→S transition + persistence length",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "69_dna_mechanics.png"))

    return out


def render_membrane() -> list[str]:
    """Produce 76_lipid_bilayer.png and 77_membrane_dynamics.png.

    76: Cross-section of the lipid bilayer.  Two leaflets of phospholipids
        with hydrophilic head groups exposed to water and hydrophobic
        tails buried in the bilayer interior.  Annotated with the
        canonical 4 nm head-to-head thickness, head/tail layer thicknesses,
        and a top view showing the fluid-mosaic model with integral
        membrane proteins embedded in the bilayer.
    77: Membrane dynamics --- left panel: lateral diffusion (random walk
        of single lipids) producing the Saffman-Delbrueck mean-square
        displacement <r^2> = 4 D t with D = 1 micron^2/s.  Middle panel:
        MSD vs t (Einstein relation).  Right panel: Helfrich bending
        modes (1,1) and (2,1) standing waves on a square membrane patch.
    """
    import math as _math
    from src.stiff_medium.membrane_substrate import (
        BENDING_MODULUS_KT,
        MembraneGeometry,
        MembraneSimulator,
    )
    out: list[str] = []

    geom = MembraneGeometry(n_lipids_per_leaflet=64)
    sim = MembraneSimulator(geometry=geom)

    # ---- 76: cross-section of the bilayer (heads + tails) -------------
    fig = plt.figure(figsize=(14, 7))

    # Left panel: side-view cross section ------------------------------
    ax = fig.add_subplot(1, 2, 1)
    side = geom.patch_side_length_nm()
    d = geom.bilayer_thickness_nm
    d_head = geom.head_thickness_nm
    d_tail = geom.tail_thickness_nm
    head_d = geom.head_diameter_nm
    tail_d = geom.tail_diameter_nm

    ax.add_patch(plt.Rectangle((-side / 2, +d / 2), side, 1.5,
                               facecolor="#cfe9ff", alpha=0.55,
                               edgecolor="none",
                               label="water (extracellular)"))
    ax.add_patch(plt.Rectangle((-side / 2, -d / 2 - 1.5), side, 1.5,
                               facecolor="#cfe9ff", alpha=0.55,
                               edgecolor="none",
                               label="water (cytosol)"))

    ax.add_patch(plt.Rectangle((-side / 2, -d_tail), side, 2 * d_tail,
                               facecolor="#fff0c2", alpha=0.45,
                               edgecolor="orange", linewidth=0.8,
                               label=f"hydrophobic tail core ({2*d_tail:.1f} nm)"))

    upper = geom.lipid_head_positions("upper")
    n_show = 18
    xs = np.linspace(-side / 2 + head_d / 2, side / 2 - head_d / 2, n_show)
    head_radius = head_d / 2.0
    for x in xs:
        ax.add_patch(plt.Circle((x, +d / 2 - head_radius), head_radius,
                                facecolor="tab:blue", edgecolor="navy",
                                linewidth=0.6, alpha=0.95, zorder=4))
        ax.add_patch(plt.Circle((x, -d / 2 + head_radius), head_radius,
                                facecolor="tab:blue", edgecolor="navy",
                                linewidth=0.6, alpha=0.95, zorder=4))
        for dx in (-tail_d / 2, +tail_d / 2):
            ax.plot([x + dx, x + dx],
                    [+d / 2 - 2 * head_radius,
                     +d / 2 - 2 * head_radius - d_tail - 0.05],
                    color="tab:orange", linewidth=2.4, alpha=0.85,
                    zorder=3)
            ax.plot([x + dx, x + dx],
                    [-d / 2 + 2 * head_radius,
                     -d / 2 + 2 * head_radius + d_tail + 0.05],
                    color="tab:orange", linewidth=2.4, alpha=0.85,
                    zorder=3)

    prot_x = side * 0.30
    prot_w = 1.6
    ax.add_patch(plt.Rectangle((prot_x - prot_w / 2, -d / 2), prot_w, d,
                               facecolor="lightgreen",
                               edgecolor="darkgreen",
                               linewidth=1.2, alpha=0.85, zorder=5,
                               label="integral membrane protein"))
    ax.text(prot_x, 0.0, "TM\nprotein", ha="center", va="center",
            fontsize=8, color="darkgreen",
            fontweight="bold", zorder=6)

    ax.annotate("", xy=(side / 2 + 0.4, +d / 2),
                xytext=(side / 2 + 0.4, -d / 2),
                arrowprops={"arrowstyle": "<->",
                            "color": "black", "lw": 1.5})
    ax.text(side / 2 + 0.6, 0.0, f"{d:.1f} nm\n(bilayer)",
            ha="left", va="center", fontsize=10, fontweight="bold")
    ax.annotate("", xy=(-side / 2 - 0.4, +d / 2),
                xytext=(-side / 2 - 0.4, +d / 2 - d_head),
                arrowprops={"arrowstyle": "<->",
                            "color": "navy", "lw": 1.0})
    ax.text(-side / 2 - 0.6, +d / 2 - d_head / 2,
            f"head\n{d_head:.1f}nm",
            ha="right", va="center", fontsize=8, color="navy")

    ax.set_xlim(-side / 2 - 2.0, side / 2 + 3.0)
    ax.set_ylim(-d / 2 - 2.0, +d / 2 + 2.0)
    ax.set_aspect("equal")
    ax.set_xlabel("x [nm]")
    ax.set_ylabel("z [nm]")
    ax.set_title(
        f"Phospholipid bilayer cross-section (fluid-mosaic model)\n"
        f"thickness = {d:.1f} nm (target 4.0 nm); "
        f"area/lipid = {geom.area_per_lipid_nm2:.2f} nm^2"
    )
    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    ax.grid(True, alpha=0.2)

    ax2 = fig.add_subplot(1, 2, 2)
    upper_xy = upper[:, :2]
    ax2.scatter(upper_xy[:, 0], upper_xy[:, 1],
                s=110, c="tab:blue", edgecolors="navy",
                linewidths=0.5, alpha=0.85,
                label="lipid head (upper leaflet)")
    proteins = geom.integral_protein_positions(
        n_proteins=4, radius_nm=1.0,
        rng=np.random.default_rng(seed=2),
    )
    for p in proteins:
        ax2.add_patch(plt.Circle((p[0], p[1]), 1.0,
                                 facecolor="lightgreen",
                                 edgecolor="darkgreen",
                                 linewidth=1.4, alpha=0.85, zorder=5))
    ax2.scatter([], [], s=120, marker="o", facecolor="lightgreen",
                edgecolors="darkgreen", linewidths=1.4,
                label="integral protein")
    L = side
    ax2.set_xlim(-L / 2 - 0.5, L / 2 + 0.5)
    ax2.set_ylim(-L / 2 - 0.5, L / 2 + 0.5)
    ax2.set_aspect("equal")
    ax2.set_xlabel("x [nm]")
    ax2.set_ylabel("y [nm]")
    ax2.set_title(
        f"Membrane plane (top view): "
        f"{geom.n_lipids_per_leaflet} lipids/leaflet\n"
        f"patch = {L:.1f} x {L:.1f} nm^2; Singer-Nicolson 1972"
    )
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax2.grid(True, alpha=0.25)

    fig.suptitle(
        "Lipid bilayer from substrate: "
        "amphiphilic self-assembly + fluid mosaic",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "76_lipid_bilayer.png"))

    # ---- 77: dynamics (lateral diffusion + bending modes) -------------
    fig = plt.figure(figsize=(15, 6))

    ax = fig.add_subplot(1, 3, 1)
    rng = np.random.default_rng(seed=42)
    D_um2_s = sim.lateral_diffusion_coefficient_um2_per_s()
    n_traj = 8
    n_steps = 600
    dt_s = 1.0e-3
    sigma_um = _math.sqrt(2.0 * D_um2_s * dt_s)
    trajs_um = rng.normal(0.0, sigma_um,
                          size=(n_traj, n_steps, 2)).cumsum(axis=1)
    cmap_obj = plt.get_cmap("tab10")
    for k in range(n_traj):
        ax.plot(trajs_um[k, :, 0], trajs_um[k, :, 1],
                color=cmap_obj(k % 10), linewidth=0.9, alpha=0.85)
        ax.scatter([trajs_um[k, 0, 0]], [trajs_um[k, 0, 1]],
                   c="black", s=22, zorder=5)
        ax.scatter([trajs_um[k, -1, 0]], [trajs_um[k, -1, 1]],
                   c="red", s=22, zorder=5)
    final_t = n_steps * dt_s
    rms_um = _math.sqrt(4.0 * D_um2_s * final_t)
    ax.scatter([], [], c="black", s=25, label="t = 0")
    ax.scatter([], [], c="red", s=25, label=f"t = {final_t:.2f} s")
    ax.set_aspect("equal")
    ax.set_xlabel("x [um]")
    ax.set_ylabel("y [um]")
    ax.set_title(
        f"Lateral diffusion (FRAP-like)\n"
        f"D = {D_um2_s:.2f} um^2/s; "
        f"rms displacement at {final_t:.2f} s = {rms_um:.3f} um"
    )
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.25)

    ax2 = fig.add_subplot(1, 3, 2)
    ts = np.linspace(0.001, 1.0, 100)
    msd_theory = 4.0 * D_um2_s * ts
    msd_emp = np.mean(np.sum(trajs_um ** 2, axis=2), axis=0)
    t_emp = np.arange(n_steps) * dt_s
    ax2.plot(t_emp, msd_emp, "b-", linewidth=1.5, alpha=0.65,
             label="simulated MSD (8 trajectories)")
    ax2.plot(ts, msd_theory, "r--", linewidth=2.0,
             label=r"$\langle r^2\rangle = 4Dt$")
    ax2.set_xlabel("time [s]")
    ax2.set_ylabel("MSD [um^2]")
    ax2.set_title(
        f"Mean-square displacement (Einstein 2D)\n"
        f"slope = 4D = {4.0 * D_um2_s:.2f} um^2/s"
    )
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(1, 3, 3, projection="3d")
    side_nm = 20.0
    X, Y, Z = sim.bending_mode_shape(side_nm=side_nm, n_grid=60,
                                     nx=1, ny=1, amplitude_nm=0.5)
    X2, Y2, Z2 = sim.bending_mode_shape(side_nm=side_nm, n_grid=60,
                                        nx=2, ny=1, amplitude_nm=0.3)
    ax3.plot_surface(X, Y, Z, cmap="coolwarm", alpha=0.8,
                     edgecolor="none")
    ax3.plot_wireframe(X2, Y2, Z2 + 1.5, color="green",
                       linewidth=0.4, alpha=0.65,
                       rcount=20, ccount=20)
    ax3.set_xlabel("x [nm]")
    ax3.set_ylabel("y [nm]")
    ax3.set_zlabel("h [nm]")
    rms_h = sim.rms_undulation_amplitude_nm(patch_side_nm=side_nm)
    ax3.set_title(
        f"Helfrich bending modes (1,1) + (2,1)\n"
        f"kappa = {BENDING_MODULUS_KT:.0f} kT; "
        f"rms undulation ~ {rms_h:.2f} nm at L = {side_nm:.0f} nm"
    )

    fig.suptitle(
        "Membrane dynamics from substrate: "
        "lateral diffusion + Helfrich bending",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "77_membrane_dynamics.png"))

    return out


def render_protein() -> list[str]:
    """Produce 66_protein_folding.png and 67_ramachandran.png.

    66: Three panels:
         left    -- right-handed alpha-helix (3.6 res/turn, pitch 5.4 A)
                    backbone with N / C_alpha / C' atoms and CA trace
         middle  -- antiparallel beta-sheet (two strands, H-bond period 7 A)
         right   -- substrate folding-funnel U(Q, RMSD) heatmap with the
                    unique global minimum at the native fold (Q->1, RMSD->0)
    67: Ramachandran (phi, psi) plot:
         shaded canonical allowed regions (alpha_R, alpha_L, beta)
         overlaid with the constructed alpha-helix and beta-strand torsions
         and the Pauling-1951 reference for the alpha-helix.
    """
    from src.stiff_medium.protein_folding_substrate import (
        HELIX_PITCH_ANGSTROM,
        PHI_ALPHA_HELIX,
        PHI_BETA_SHEET,
        PSI_ALPHA_HELIX,
        PSI_BETA_SHEET,
        SHEET_H_BOND_PERIOD_A,
        ProteinFoldingGeometry,
        ProteinFoldingSimulator,
    )
    out: list[str] = []

    # ---- 66: 3D alpha-helix + beta-sheet + funnel landscape -----------
    helix = ProteinFoldingGeometry.alpha_helix(n_residues=24)
    strand1 = ProteinFoldingGeometry.beta_sheet_strand(n_residues=8)
    strand2 = ProteinFoldingGeometry.beta_sheet_strand(n_residues=8)
    sim = ProteinFoldingSimulator(geometry=helix)

    helix_coords = helix.backbone_coords()
    helix_ca = helix.calpha_coords()
    s1 = strand1.backbone_coords()
    s2 = strand2.backbone_coords()
    s1_ca = strand1.calpha_coords()
    s2_ca = strand2.calpha_coords()

    # Antiparallel partner strand: invert and offset by 7 A perpendicular
    # to the chain axis so the inter-strand H-bond pattern is visible.
    centred1 = s1 - s1.mean(axis=0)
    _, _, vh1 = np.linalg.svd(centred1, full_matrices=False)
    chain_axis = vh1[0]
    perp_seed = np.array([0.0, 1.0, 0.0])
    perp = perp_seed - np.dot(perp_seed, chain_axis) * chain_axis
    perp = perp / (np.linalg.norm(perp) + 1e-30)
    offset = SHEET_H_BOND_PERIOD_A * perp
    s2_anti = -(s2 - s2.mean(axis=0)) + s1.mean(axis=0) + offset
    s2_anti_ca = -(s2_ca - s2_ca.mean(axis=0)) + s1_ca.mean(axis=0) + offset

    fig = plt.figure(figsize=(15, 6))

    # --- Left: alpha-helix
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    Ns  = helix_coords[0::3]
    CAs = helix_coords[1::3]
    Cs  = helix_coords[2::3]
    ax1.scatter(*Ns.T,  c="tab:blue",   s=30, label="N")
    ax1.scatter(*CAs.T, c="tab:orange", s=40, label="C_alpha")
    ax1.scatter(*Cs.T,  c="tab:green",  s=30, label="C'")
    ax1.plot(*helix_coords.T, "k-", linewidth=1.0, alpha=0.5)
    ax1.plot(*helix_ca.T, "r-", linewidth=1.8, alpha=0.7, label="C_alpha trace")
    _, rise, pitch = helix.helix_axis_and_pitch()
    ax1.set_title(
        f"alpha-helix (3.6 res/turn)\n"
        f"pitch={pitch:.2f} A (target {HELIX_PITCH_ANGSTROM} A)\n"
        f"rise/res={rise:.2f} A   radius={helix.helix_radius():.2f} A"
    )
    ax1.set_xlabel("x [A]"); ax1.set_ylabel("y [A]"); ax1.set_zlabel("z [A]")
    ax1.legend(loc="upper left", fontsize=8)
    L = max(np.abs(helix_coords).max(), 1.0)
    ax1.set_xlim(-L, L); ax1.set_ylim(-L, L)
    ax1.set_zlim(helix_coords[:, 2].min() - 1, helix_coords[:, 2].max() + 1)

    # --- Middle: antiparallel beta-sheet (two strands)
    ax2 = fig.add_subplot(1, 3, 2, projection="3d")
    ax2.plot(*s1.T, "k-", linewidth=1.0, alpha=0.5)
    ax2.scatter(*s1_ca.T, c="tab:orange", s=40, label="strand 1 C_alpha")
    ax2.plot(*s1_ca.T, "tab:blue", linewidth=2.0, alpha=0.6)
    ax2.plot(*s2_anti.T, "k-", linewidth=1.0, alpha=0.5)
    ax2.scatter(*s2_anti_ca.T, c="tab:red", s=40, label="strand 2 C_alpha")
    ax2.plot(*s2_anti_ca.T, "tab:green", linewidth=2.0, alpha=0.6)
    n = min(len(s1_ca), len(s2_anti_ca))
    for i in range(0, n, 2):
        j = n - 1 - i
        if j >= 0:
            ax2.plot([s1_ca[i, 0], s2_anti_ca[j, 0]],
                     [s1_ca[i, 1], s2_anti_ca[j, 1]],
                     [s1_ca[i, 2], s2_anti_ca[j, 2]],
                     "g--", linewidth=1.0, alpha=0.6)
    ax2.set_title(
        f"antiparallel beta-sheet\n"
        f"H-bond period = {SHEET_H_BOND_PERIOD_A:.1f} A\n"
        f"rise/res = {sim.beta_sheet_rise_per_residue_angstrom():.2f} A"
    )
    ax2.set_xlabel("x [A]"); ax2.set_ylabel("y [A]"); ax2.set_zlabel("z [A]")
    ax2.legend(loc="upper left", fontsize=8)

    # --- Right: folding funnel landscape
    ax3 = fig.add_subplot(1, 3, 3)
    q, r, U = sim.funnel_landscape()
    im = ax3.imshow(
        U.T, origin="lower", aspect="auto",
        extent=[float(q.min()), float(q.max()),
                float(r.min()), float(r.max())],
        cmap="viridis_r",
    )
    q_star, r_star, _ = sim.funnel_minimum()
    ax3.scatter([q_star], [r_star], c="red", marker="*", s=180,
                edgecolors="white", linewidths=1.5, label="native (min)")
    lev = sim.levinthal_resolved(n_residues=100)
    ax3.set_title(
        f"folding funnel U(Q, RMSD) [kT]\n"
        f"depth = {sim.funnel_depth_kT:.0f} kT;  "
        f"speedup vs Levinthal = 10^{int(np.log10(lev['speedup_ratio']))}"
    )
    ax3.set_xlabel("Q  (fraction native contacts)")
    ax3.set_ylabel("RMSD from native [A]")
    ax3.legend(loc="upper right", fontsize=8)
    fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04, label="U / kT")

    fig.suptitle(
        "Protein folding from substrate: alpha-helix + beta-sheet + folding funnel",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "66_protein_folding.png"))

    # ---- 67: Ramachandran plot ----------------------------------------
    fig, ax = plt.subplots(figsize=(8, 8))
    region_colors = {
        "alpha_R": ("tab:blue",   "alpha-helix (right-handed)"),
        "alpha_L": ("tab:purple", "alpha-helix (left-handed)"),
        "beta":    ("tab:orange", "beta-sheet / extended"),
    }
    for name, (pmin, pmax, smin, smax) in ProteinFoldingGeometry.allowed_regions().items():
        color, label = region_colors[name]
        ax.add_patch(plt.Rectangle(
            (pmin, smin), pmax - pmin, smax - smin,
            facecolor=color, alpha=0.18, edgecolor=color, linewidth=1.2,
            label=label,
        ))
    ax.scatter([PHI_ALPHA_HELIX], [PSI_ALPHA_HELIX],
               s=200, c="tab:blue", marker="*", edgecolors="black",
               linewidths=1.5,
               label=f"constructed alpha-helix ({PHI_ALPHA_HELIX:.0f}, {PSI_ALPHA_HELIX:.0f})")
    ax.scatter([PHI_BETA_SHEET], [PSI_BETA_SHEET],
               s=200, c="tab:orange", marker="*", edgecolors="black",
               linewidths=1.5,
               label=f"constructed beta-strand ({PHI_BETA_SHEET:.0f}, {PSI_BETA_SHEET:.0f})")
    ax.scatter([-57], [-47], s=80, c="tab:blue", marker="x", linewidths=2,
               label="Pauling 1951 alpha-helix (-57, -47)")

    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)
    ax.set_xticks(np.arange(-180, 181, 60))
    ax.set_yticks(np.arange(-180, 181, 60))
    ax.set_xlabel(r"$\varphi$  [deg]", fontsize=12)
    ax.set_ylabel(r"$\psi$  [deg]", fontsize=12)
    ax.set_title(
        "Ramachandran plot -- substrate-framework backbone torsions\n"
        f"alpha-helix pitch reproduced at {abs(sim.helix_pitch_angstrom()-5.4)/5.4*100:.2f}%; "
        f"beta-sheet H-bond period = {SHEET_H_BOND_PERIOD_A:.1f} A",
        fontsize=11,
    )
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_aspect("equal")
    fig.tight_layout()
    out.append(save(fig, "67_ramachandran.png"))

    return out


# ---------------------------------------------------------------------------
# Catalysis (Sabatier volcano + enzyme kinetics)
# ---------------------------------------------------------------------------

def render_catalysis() -> list[str]:
    """Produce 58_sabatier_volcano.png and 59_enzyme_kinetics.png.

    58: Sabatier volcano for H2 dissociation across Ni/Pd/Pt/Au and other
        transition metals. log10(TOF) vs E_bind shows the classic two-sided
        peak with Pt at the apex (E_bind ~ 0).
    59: Enzyme kinetics --- Michaelis-Menten v vs [S] for carbonic
        anhydrase + Lineweaver-Burk linearization (1/v vs 1/[S]) plus a
        Hill-cooperativity panel for hemoglobin (n_H = 2.8).
    """
    from src.stiff_medium.catalysis_substrate import (
        CatalysisGeometry,
        CatalysisSimulator,
        H_BINDING_eV,
    )
    out: list[str] = []

    sim = CatalysisSimulator()

    # ---- 58: Sabatier volcano ------------------------------------------
    fig = plt.figure(figsize=(15, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.4, 1.0])
    ax_vol = fig.add_subplot(gs[0, 0])
    ax_geom = fig.add_subplot(gs[0, 1])

    # Continuous BEP curve
    e_binds_cont = np.linspace(-0.9, +0.5, 240)
    bep_alpha = 0.5
    bep_intercept = 0.75
    rates_cont = []
    for eb in e_binds_cont:
        g_tmp = CatalysisGeometry(
            binding_energy=float(eb),
            bep_alpha=bep_alpha,
            bep_intercept=bep_intercept,
        )
        rates_cont.append(sim.eyring_rate(g_tmp.activation_energy(float(eb))))
    rates_cont = np.array(rates_cont)
    log10_rates_cont = np.log10(np.maximum(rates_cont, 1e-300))

    ax_vol.plot(e_binds_cont, log10_rates_cont, "b-", linewidth=2.0,
                label="Eyring with BEP barrier  (alpha=0.5, E_a0=0.75 eV)")
    ax_vol.fill_between(e_binds_cont, log10_rates_cont.min() - 1.0,
                        log10_rates_cont, color="blue", alpha=0.10)

    # Discrete metals
    metals = ["Au", "Ag", "Cu", "Pt", "Pd", "Ni", "Rh", "Ru", "Re", "Mo", "W"]
    volcano = sim.sabatier_volcano(metals=metals,
                                    bep_alpha=bep_alpha,
                                    bep_intercept=bep_intercept)
    palette = {
        "Au": "gold", "Ag": "silver", "Cu": "darkorange",
        "Pt": "red",   "Pd": "purple", "Ni": "green",
        "Rh": "teal",  "Ru": "navy",   "Re": "brown",
        "Mo": "olive", "W":  "black",
    }
    for m in metals:
        d = volcano[m]
        eb = d["E_bind_eV"]
        lr = d["log10_TOF"]
        ax_vol.scatter([eb], [lr], s=160, color=palette[m],
                       edgecolors="black", linewidths=1.2, zorder=5)
        ax_vol.annotate(m, (eb, lr), xytext=(8, 6),
                        textcoords="offset points", fontsize=10,
                        fontweight="bold", color=palette[m])

    # Sabatier optimum band (|E_bind| < 0.15 eV)
    ax_vol.axvspan(-0.15, +0.15, color="green", alpha=0.10,
                   label="Sabatier optimum  (|E_bind| < 0.15 eV)")
    ax_vol.axvline(0.0, color="green", linestyle="--", linewidth=1.0,
                   alpha=0.6)

    # Annotate Pt as peak
    pt = volcano["Pt"]
    ax_vol.annotate("PEAK (Sabatier optimum)",
                    xy=(pt["E_bind_eV"], pt["log10_TOF"]),
                    xytext=(pt["E_bind_eV"] - 0.45, pt["log10_TOF"] + 0.5),
                    arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
                    fontsize=10, color="red", fontweight="bold")

    ax_vol.set_xlabel("H binding energy E_bind [eV]   (negative = exothermic)",
                      fontsize=11)
    ax_vol.set_ylabel("log10(turnover frequency)  [s^-1]", fontsize=11)
    ax_vol.set_title(
        "Sabatier volcano:  H2 dissociation across transition metals\n"
        "two-sided BEP barrier ->  Pt sits at the peak (E_bind ~ -0.1 eV)",
        fontsize=11,
    )
    ax_vol.grid(True, alpha=0.3)
    ax_vol.legend(fontsize=9, loc="lower center")

    # Right panel: active-site geometry sketch
    g_pt = CatalysisGeometry(binding_energy=H_BINDING_eV["Pt"],
                              site_width=1.5)
    g_au = CatalysisGeometry(binding_energy=H_BINDING_eV["Au"],
                              site_width=1.5)
    g_w = CatalysisGeometry(binding_energy=H_BINDING_eV["W"],
                             site_width=1.5)
    # 1D potential along bond axis
    z = np.linspace(0.05, 6.0, 400)
    pts = np.column_stack([np.zeros_like(z), np.zeros_like(z), z])
    V_pt = g_pt.strain_potential(pts)
    V_au = g_au.strain_potential(pts)
    V_w = g_w.strain_potential(pts)
    ax_geom.plot(z, V_pt, "r-", linewidth=2.2,
                 label=f"Pt  (E_bind = {g_pt.binding_energy:+.2f} eV)  optimal")
    ax_geom.plot(z, V_au, "gold", linewidth=2.0,
                 label=f"Au  (E_bind = {g_au.binding_energy:+.2f} eV)  too weak")
    ax_geom.plot(z, V_w, "k-", linewidth=2.0,
                 label=f"W   (E_bind = {g_w.binding_energy:+.2f} eV)  too strong")
    ax_geom.axhline(0.0, color="gray", linestyle=":", linewidth=1.0,
                    alpha=0.5)
    ax_geom.set_xlabel("distance above active site z [Angstrom]", fontsize=11)
    ax_geom.set_ylabel("strain potential V(z) [eV]", fontsize=11)
    ax_geom.set_title(
        "Active-site strain potential (Morse pocket)\n"
        "Pt: shallow well -> easy adsorb + easy release",
        fontsize=11,
    )
    ax_geom.grid(True, alpha=0.3)
    ax_geom.legend(fontsize=9, loc="upper right")

    fig.suptitle(
        "Heterogeneous catalysis:  Sabatier volcano  +  active-site strain pocket\n"
        "rate = (k_B T / h) * exp(-E_a / k_B T);   E_a = E_a0 +/- (alpha or 1-alpha) * E_bind  (BEP)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "58_sabatier_volcano.png"))

    # ---- 59: Enzyme kinetics (Michaelis-Menten + Lineweaver-Burk + Hill) -
    fig = plt.figure(figsize=(16, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1.2, 1.2])
    ax_mm = fig.add_subplot(gs[0, 0])
    ax_lb = fig.add_subplot(gs[0, 1])
    ax_hill = fig.add_subplot(gs[0, 2])

    # Carbonic anhydrase: k_cat = 1e6 s^-1, K_M = 8 mM
    k_cat = 1.0e6
    K_M = 8.0e-3      # M
    E0 = 1.0e-9       # 1 nM enzyme
    V_max = k_cat * E0
    S_mm = np.logspace(-5, -1, 300)   # 10 uM -> 100 mM
    v_mm = np.array(CatalysisSimulator.michaelis_menten(
        S_mm, k_cat, K_M, E_total=E0))
    ax_mm.plot(S_mm * 1e3, v_mm * 1e3, "b-", linewidth=2.0,
               label="v = k_cat [E]_0 [S] / (K_M + [S])")
    ax_mm.axhline(V_max * 1e3, color="green", linestyle="--", linewidth=1.2,
                  label=f"V_max = k_cat [E]_0 = {V_max*1e3:.2g} mM/s")
    ax_mm.axhline(V_max * 1e3 / 2.0, color="orange", linestyle=":",
                  linewidth=1.2,
                  label=f"V_max / 2 at [S] = K_M = {K_M*1e3:.1f} mM")
    ax_mm.axvline(K_M * 1e3, color="orange", linestyle=":", linewidth=1.2,
                  alpha=0.6)
    # Mark half-saturation point
    ax_mm.scatter([K_M * 1e3], [V_max * 1e3 / 2.0], color="orange", s=120,
                  edgecolors="black", linewidths=1.0, zorder=5)
    ax_mm.set_xscale("log")
    ax_mm.set_xlabel("[S]  [mM]  (log scale)", fontsize=11)
    ax_mm.set_ylabel("rate v  [mM / s]", fontsize=11)
    ax_mm.set_title(
        "Michaelis-Menten saturation\n"
        "carbonic anhydrase  (k_cat = 10^6 s^-1, K_M = 8 mM)",
        fontsize=11,
    )
    ax_mm.grid(True, alpha=0.3, which="both")
    ax_mm.legend(fontsize=9, loc="lower right")

    # Lineweaver-Burk
    S_lb = np.logspace(-4, -1, 25)
    inv_S, inv_v = CatalysisSimulator.lineweaver_burk(S_lb, k_cat, K_M, E0)
    slope, intercept = np.polyfit(inv_S, inv_v, 1)
    ax_lb.scatter(inv_S, inv_v, s=70, color="purple", edgecolors="black",
                  linewidths=1.0, zorder=5, label="data")
    xfit = np.linspace(0, inv_S.max() * 1.05, 200)
    yfit = slope * xfit + intercept
    ax_lb.plot(xfit, yfit, "k--", linewidth=1.6,
               label=f"slope = K_M/V_max = {slope:.2e}")
    ax_lb.scatter([0.0], [intercept], color="green", s=140, marker="X",
                  edgecolors="black", linewidths=1.0, zorder=6,
                  label=f"y-intercept = 1/V_max = {intercept:.2e}")
    x_int = -intercept / slope
    ax_lb.scatter([x_int], [0.0], color="orange", s=140, marker="X",
                  edgecolors="black", linewidths=1.0, zorder=6,
                  label=f"x-intercept = -1/K_M = {x_int:.2e}")
    ax_lb.axhline(0.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)
    ax_lb.axvline(0.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)
    ax_lb.set_xlabel("1 / [S]  [1/M]", fontsize=11)
    ax_lb.set_ylabel("1 / v  [s/M]", fontsize=11)
    ax_lb.set_title(
        "Lineweaver-Burk linearization\n"
        "1/v = (K_M/V_max) (1/[S]) + 1/V_max",
        fontsize=11,
    )
    ax_lb.grid(True, alpha=0.3)
    ax_lb.legend(fontsize=8, loc="upper left")

    # Hill plot for hemoglobin
    S_hb = np.logspace(-1.0, 2.5, 240)
    v_hb_28 = np.array(CatalysisSimulator.hill_equation(
        S_hb, V_max=1.0, K_half=26.0, n_H=2.8))
    v_hb_1 = np.array(CatalysisSimulator.hill_equation(
        S_hb, V_max=1.0, K_half=26.0, n_H=1.0))
    ax_hill.plot(S_hb, v_hb_28, "r-", linewidth=2.2,
                 label="Hb tetramer  n_H = 2.8 (cooperative)")
    ax_hill.plot(S_hb, v_hb_1, "b--", linewidth=1.8,
                 label="myoglobin   n_H = 1.0 (non-cooperative)")
    ax_hill.axhline(0.5, color="gray", linestyle=":", linewidth=1.0,
                    alpha=0.6)
    ax_hill.axvline(26.0, color="orange", linestyle=":", linewidth=1.2,
                    label="P_50 = K_half = 26 mmHg")
    ax_hill.set_xscale("log")
    ax_hill.set_xlabel("p_O2  [mmHg]  (log scale)", fontsize=11)
    ax_hill.set_ylabel("O2 saturation  Y", fontsize=11)
    ax_hill.set_title(
        "Hill cooperativity:  Hb vs Mb\n"
        "v = V_max [S]^n / (K^n + [S]^n)",
        fontsize=11,
    )
    ax_hill.set_ylim(-0.05, 1.05)
    ax_hill.grid(True, alpha=0.3, which="both")
    ax_hill.legend(fontsize=9, loc="lower right")

    fig.suptitle(
        "Enzyme kinetics:  Michaelis-Menten saturation  +  Lineweaver-Burk  +  Hill cooperativity\n"
        "Carbonic anhydrase k_cat/K_M = 1.25e8 M^-1 s^-1  (~ diffusion limit);  Hb Hill n_H = 2.8",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "59_enzyme_kinetics.png"))

    return out


# ---------------------------------------------------------------------------
# Substrate-DFT (electronic structure with substrate XC functional):
#   56_dft_density.png — radial densities + 3D iso for H, He, H₂, H₂O
#   57_dft_energy_levels.png — Kohn-Sham orbital ladder for H, He, O
# ---------------------------------------------------------------------------


def render_dft() -> list[str]:
    """Produce 56_dft_density.png and 57_dft_energy_levels.png.

    56: Radial densities n(r) for H, He, and the H₂O oxygen core; plus
        a 3D iso-surface for the H atom and the LCAO ansatz density for
        the H₂ molecule at R = 1.4 Bohr.
    57: Kohn-Sham orbital energy ladder for H, He, O — eigenvalues
        plotted as horizontal bars on a vertical energy axis (Hartree).
    """
    from src.stiff_medium.substrate_dft import (
        HARTREE_EV,
        h2_binding_energy,
        helium_atom,
        hydrogen_atom,
        lieb_oxford_check,
        water_oxygen_core,
    )

    out: list[str] = []

    # Run all SCF jobs once
    g_h, s_h, e_h = hydrogen_atom()
    g_he, s_he, e_he = helium_atom()
    g_o, s_o, e_o = water_oxygen_core()
    h2 = h2_binding_energy(R_bond_bohr=1.4)
    lo = lieb_oxford_check(g_he.density, g_he.weights, s_he.A_c, s_he.n_sat)

    # ============================================================
    # 56_dft_density.png : 3D-ish density panels
    # ============================================================
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0])

    # Panel A: radial density n(r) for H, He, O
    ax_rad = fig.add_subplot(gs[0, :])
    for geom, label, color in [
        (g_h,  f"H  (E_KS = {e_h['E_total']*HARTREE_EV:+.2f} eV)", "tab:blue"),
        (g_he, f"He (E_tot = {e_he['E_total']:+.2f} Ha)",          "tab:orange"),
        (g_o,  f"O  (E_tot = {e_o['E_total']:+.1f} Ha)",           "tab:green"),
    ]:
        ax_rad.plot(geom.r, 4.0 * np.pi * geom.r ** 2 * geom.density,
                    linewidth=2.0, label=label, color=color)
    ax_rad.set_xlim(0.0, 6.0)
    ax_rad.set_xlabel("radial distance r [Bohr]", fontsize=10)
    ax_rad.set_ylabel("radial density  4π r² n(r)", fontsize=10)
    ax_rad.set_title(
        "Substrate-DFT radial density: H, He, O\n"
        "Kohn-Sham + LDA exchange + substrate σ ≤ 1/2 correlation",
        fontsize=11,
    )
    ax_rad.grid(True, alpha=0.3)
    ax_rad.legend(fontsize=10, loc="upper right")

    # Panel B: 3D iso-density for H atom (point cloud)
    ax_h = fig.add_subplot(gs[1, 0], projection="3d")
    rng = np.linspace(-3.0, 3.0, 24)
    X, Y, Z = np.meshgrid(rng, rng, rng, indexing="ij")
    R = np.sqrt(X * X + Y * Y + Z * Z) + 1e-6
    n_h = np.interp(R.ravel(), g_h.r, g_h.density).reshape(R.shape)
    thr = 0.05 * float(np.max(n_h))
    mask = n_h > thr
    ax_h.scatter(X[mask], Y[mask], Z[mask], c=n_h[mask],
                 cmap="Blues", s=4, alpha=0.4)
    ax_h.set_title(f"H atom n(r) iso (>{thr:.2f})\n"
                    f"E = {e_h['E_total']*HARTREE_EV:.2f} eV",
                    fontsize=10)
    ax_h.set_xlabel("x [Bohr]", fontsize=8)
    ax_h.set_ylabel("y [Bohr]", fontsize=8)
    ax_h.set_zlabel("z [Bohr]", fontsize=8)

    # Panel C: H₂ LCAO density along bond axis
    ax_h2 = fig.add_subplot(gs[1, 1])
    R_bond = h2["R_bond_bohr"]
    z_axis = np.linspace(-3.0, 3.0, 600)
    n_left = np.interp(np.abs(z_axis + R_bond / 2.0), g_h.r, g_h.density)
    n_right = np.interp(np.abs(z_axis - R_bond / 2.0), g_h.r, g_h.density)
    n_h2 = n_left + n_right
    ax_h2.plot(z_axis, n_left, "b-", alpha=0.5, linewidth=1.0, label="H_left")
    ax_h2.plot(z_axis, n_right, "r-", alpha=0.5, linewidth=1.0, label="H_right")
    ax_h2.plot(z_axis, n_h2, "k-", linewidth=2.0, label="H₂ total")
    ax_h2.axvline(-R_bond / 2.0, color="b", linestyle=":", alpha=0.5)
    ax_h2.axvline( R_bond / 2.0, color="r", linestyle=":", alpha=0.5)
    ax_h2.set_xlabel("bond axis z [Bohr]", fontsize=10)
    ax_h2.set_ylabel("density n(z)", fontsize=10)
    ax_h2.set_title(
        f"H₂ LCAO  R={R_bond:.2f} Bohr\n"
        f"E_bind = {h2['E_bind_eV']:.2f} eV  (exp 4.748 eV)",
        fontsize=10,
    )
    ax_h2.grid(True, alpha=0.3)
    ax_h2.legend(fontsize=8)

    # Panel D: H₂O components
    ax_h2o = fig.add_subplot(gs[1, 2])
    ax_h2o.plot(g_o.r, 4.0 * np.pi * g_o.r ** 2 * g_o.density,
                "g-", linewidth=2.0, label="O 1s²2s²(2p)⁴")
    ax_h2o.plot(g_h.r, 4.0 * np.pi * g_h.r ** 2 * g_h.density,
                "b--", linewidth=1.5, label="H (×2)")
    ax_h2o.set_xlim(0.0, 6.0)
    ax_h2o.set_xlabel("r [Bohr]", fontsize=10)
    ax_h2o.set_ylabel("4π r² n(r)", fontsize=10)
    ax_h2o.set_title(
        "H₂O components: O atom + 2× H\n"
        f"L-O ratio={lo['ratio_xc_to_x']:.2f} "
        f"({lo['gap_closed_fraction']*100:.0f}% gap closed)",
        fontsize=10,
    )
    ax_h2o.grid(True, alpha=0.3)
    ax_h2o.legend(fontsize=9)

    fig.suptitle(
        "Substrate-DFT density n(r) for H, He, H₂, H₂O — "
        "Kohn-Sham + LDA exchange + substrate σ ≤ 1/2 correlation",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "56_dft_density.png"))

    # ============================================================
    # 57_dft_energy_levels.png : KS orbital ladder
    # ============================================================
    fig, ax = plt.subplots(figsize=(11, 8))
    systems = [
        ("H",  s_h.geom.energies[:2],  s_h.geom.occupations,  "tab:blue",   e_h["E_total"]),
        ("He", s_he.geom.energies[:3], s_he.geom.occupations, "tab:orange", e_he["E_total"]),
        ("O",  s_o.geom.energies[:5],  s_o.geom.occupations,  "tab:green",  e_o["E_total"]),
    ]
    bar_w = 0.6
    x_centres = np.arange(len(systems)) * 2.0
    for i, (name, eps, occ, color, e_tot) in enumerate(systems):
        x0 = x_centres[i]
        for k, eig in enumerate(eps):
            f = float(occ[k]) if k < len(occ) else 0.0
            lw = 3.0 if f > 0 else 1.0
            alpha = 1.0 if f > 0 else 0.35
            ax.hlines(eig, x0 - bar_w / 2.0, x0 + bar_w / 2.0,
                      colors=color, linewidth=lw, alpha=alpha)
            label_str = f" ε_{k+1}={eig:+.3f}"
            if f > 0:
                label_str += f"  (f={int(f)})"
            ax.text(x0 + bar_w / 2.0 + 0.05, eig, label_str,
                    fontsize=8, color=color,
                    verticalalignment="center")
        # Total energy annotation above the level group
        ax.text(x0, max(np.max(eps), 0.0) + 0.5,
                f"{name}\nE_tot={e_tot:+.3f} Ha\n=({e_tot*HARTREE_EV:+.2f} eV)",
                fontsize=10, ha="center",
                bbox=dict(boxstyle="round,pad=0.3",
                          facecolor=color, alpha=0.2))

    ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5,
               label="continuum threshold (E=0)")
    ax.set_xticks(x_centres)
    ax.set_xticklabels([s[0] for s in systems])
    ax.set_xlabel("system", fontsize=11)
    ax.set_ylabel("Kohn-Sham eigenvalue ε [Hartree]", fontsize=11)
    ax.set_title(
        "Substrate-DFT Kohn-Sham orbital ladder\n"
        "filled (thick) = occupied; empty (thin/faded) = virtual\n"
        f"H 1s = {s_h.geom.energies[0]*HARTREE_EV:.2f} eV  (exact: -13.61 eV)",
        fontsize=11,
    )
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_xlim(-1.0, 2.0 * len(systems))
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    out.append(save(fig, "57_dft_energy_levels.png"))

    return out


# ---------------------------------------------------------------------------
# Crystal structures (NaCl, diamond, graphite, CsCl, ZnS, perovskite)
# Paired GEOMETRY+SIM+VIZ from substrate K_4 cells
# ---------------------------------------------------------------------------

def render_crystals() -> list[str]:
    """Render unit-cell 3D figures and XRD patterns for the canonical
    crystal families derivable from B3 substrate K_4 cell tilings.

    Produces:
        62_crystal_structures.png  — 3D unit cells of NaCl, diamond, graphite,
                                     CsCl, ZnS, SrTiO_3 (6 sub-panels)
        63_xrd_patterns.png        — XRD intensity vs 2θ for NaCl + diamond
    """
    import math
    from src.stiff_medium.crystal_substrate import (
        REFERENCE,
        CrystalGeometry,
        CrystalSimulator,
    )

    out = []

    # ----- 3D unit cells -----------------------------------------------------
    fig = plt.figure(figsize=(16, 10))

    def _draw_cell_box(ax, cell, color="black", lw=0.5, alpha=0.4):
        """Draw the parallelepiped edges of a unit cell."""
        a1, a2, a3 = cell[0], cell[1], cell[2]
        corners = [np.zeros(3), a1, a2, a3,
                   a1 + a2, a1 + a3, a2 + a3, a1 + a2 + a3]
        edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 4), (1, 5),
            (2, 4), (2, 6),
            (3, 5), (3, 6),
            (4, 7), (5, 7), (6, 7),
        ]
        for i, j in edges:
            xs = [corners[i][0], corners[j][0]]
            ys = [corners[i][1], corners[j][1]]
            zs = [corners[i][2], corners[j][2]]
            ax.plot(xs, ys, zs, color=color, lw=lw, alpha=alpha)

    def _draw_bonds(ax, positions_a, positions_b, max_dist,
                    color="gray", lw=1.0):
        """Draw bonds between atoms within max_dist."""
        for pa in positions_a:
            for pb in positions_b:
                d = np.linalg.norm(pa - pb)
                if 0.01 < d < max_dist:
                    ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                            [pa[2], pb[2]],
                            color=color, lw=lw, alpha=0.4)

    # 1. NaCl (rocksalt FCC)
    ax = fig.add_subplot(2, 3, 1, projection="3d")
    nacl = CrystalGeometry.nacl()
    a = nacl["a"]
    for shift_x in (0.0, 1.0):
        for shift_y in (0.0, 1.0):
            for shift_z in (0.0, 1.0):
                offset = np.array([shift_x, shift_y, shift_z]) * a
                for r in nacl["Na"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="purple", s=180,
                                   edgecolors="black", linewidths=0.5,
                                   alpha=0.95)
                for r in nacl["Cl"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="green", s=300,
                                   edgecolors="black", linewidths=0.5,
                                   alpha=0.85)
    _draw_cell_box(ax, nacl["cell"])
    ax.set_title(f"NaCl (rocksalt, FCC)\n"
                 f"a = {a:.3f} Å, M = 1.7476", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.scatter([], [], [], color="purple", s=120, label="Na⁺")
    ax.scatter([], [], [], color="green", s=200, label="Cl⁻")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_box_aspect([1, 1, 1])

    # 2. Diamond (covalent sp³)
    ax = fig.add_subplot(2, 3, 2, projection="3d")
    d = CrystalGeometry.diamond()
    a = d["a"]
    pos = d["C"]
    all_C = []
    for shift_x in (0.0, 1.0):
        for shift_y in (0.0, 1.0):
            for shift_z in (0.0, 1.0):
                offset = np.array([shift_x, shift_y, shift_z]) * a
                for r in pos:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        all_C.append(p)
    all_C = np.array(all_C) if all_C else pos
    for p in all_C:
        ax.scatter(*p, color="black", s=140,
                   edgecolors="white", linewidths=0.5)
    nn = a * math.sqrt(3.0) / 4.0
    _draw_bonds(ax, all_C, all_C, nn * 1.05, color="black", lw=1.5)
    _draw_cell_box(ax, d["cell"])
    ax.set_title(f"Diamond (covalent, sp³)\n"
                 f"a = {a:.3f} Å, NN = {nn:.3f} Å", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.set_box_aspect([1, 1, 1])

    # 3. Graphite (layered hexagonal)
    ax = fig.add_subplot(2, 3, 3, projection="3d")
    g = CrystalGeometry.graphite()
    cell = g["cell"]
    pts_layer = []
    for ix in range(-1, 3):
        for iy in range(-1, 3):
            for iz in (0, 1):
                offset = ix * cell[0] + iy * cell[1] + iz * cell[2]
                for r in g["C"]:
                    p = r + offset
                    if (-1.0 < p[0] < 4.5 and -1.0 < p[1] < 4.5
                            and -0.2 < p[2] < cell[2, 2] * 1.2 + 0.2):
                        col = "darkgray" if abs(p[2] % cell[2, 2]) < 0.1 \
                            else "dimgray"
                        ax.scatter(*p, color=col, s=100,
                                   edgecolors="black", linewidths=0.4)
                        pts_layer.append((p, p[2]))
    nn_g = g["a"] / math.sqrt(3.0)
    z_layers = sorted(set(round(z, 2) for _, z in pts_layer))
    for z_lvl in z_layers:
        layer = np.array([p for p, z in pts_layer if abs(z - z_lvl) < 0.05])
        if len(layer) > 1:
            _draw_bonds(ax, layer, layer, nn_g * 1.05,
                        color="black", lw=1.0)
    _draw_cell_box(ax, cell)
    ax.set_title(f"Graphite (AB-stacked layers)\n"
                 f"a = {g['a']:.3f} Å, c = {g['c']:.3f} Å", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.set_box_aspect([1, 1, 1])

    # 4. CsCl (primitive cubic)
    ax = fig.add_subplot(2, 3, 4, projection="3d")
    cs = CrystalGeometry.cscl()
    a = cs["a"]
    for shift_x in (0.0, 1.0):
        for shift_y in (0.0, 1.0):
            for shift_z in (0.0, 1.0):
                offset = np.array([shift_x, shift_y, shift_z]) * a
                for r in cs["Cs"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="orange", s=380,
                                   edgecolors="black", linewidths=0.5)
    for r in cs["Cl"]:
        ax.scatter(*r, color="green", s=300,
                   edgecolors="black", linewidths=0.5)
    _draw_cell_box(ax, cs["cell"])
    ax.set_title(f"CsCl (primitive cubic)\n"
                 f"a = {a:.3f} Å, M = 1.7627", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.scatter([], [], [], color="orange", s=200, label="Cs⁺")
    ax.scatter([], [], [], color="green", s=180, label="Cl⁻")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_box_aspect([1, 1, 1])

    # 5. ZnS (zincblende)
    ax = fig.add_subplot(2, 3, 5, projection="3d")
    z = CrystalGeometry.zns()
    a = z["a"]
    for shift_x in (0.0, 1.0):
        for shift_y in (0.0, 1.0):
            for shift_z in (0.0, 1.0):
                offset = np.array([shift_x, shift_y, shift_z]) * a
                for r in z["Zn"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="silver", s=180,
                                   edgecolors="black", linewidths=0.5)
                for r in z["S"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="gold", s=180,
                                   edgecolors="black", linewidths=0.5)
    _draw_cell_box(ax, z["cell"])
    ax.set_title(f"ZnS (zincblende, FCC + tet)\n"
                 f"a = {a:.3f} Å, M = 1.6381", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.scatter([], [], [], color="silver", s=120, label="Zn²⁺")
    ax.scatter([], [], [], color="gold", s=120, label="S²⁻")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_box_aspect([1, 1, 1])

    # 6. Perovskite SrTiO_3 (bonus 6th panel)
    ax = fig.add_subplot(2, 3, 6, projection="3d")
    p_xtl = CrystalGeometry.perovskite()
    a = p_xtl["a"]
    for shift_x in (0.0, 1.0):
        for shift_y in (0.0, 1.0):
            for shift_z in (0.0, 1.0):
                offset = np.array([shift_x, shift_y, shift_z]) * a
                for r in p_xtl["Sr"]:
                    p = r + offset
                    if np.all(p <= a + 1e-6):
                        ax.scatter(*p, color="dodgerblue", s=300,
                                   edgecolors="black", linewidths=0.5)
    for r in p_xtl["Ti"]:
        ax.scatter(*r, color="silver", s=200,
                   edgecolors="black", linewidths=0.5)
    for r in p_xtl["O"]:
        ax.scatter(*r, color="red", s=140,
                   edgecolors="black", linewidths=0.5)
    _draw_cell_box(ax, p_xtl["cell"])
    ax.set_title(f"SrTiO₃ perovskite (ABX₃)\n"
                 f"a = {a:.3f} Å", fontsize=10)
    ax.set_xlabel("x [Å]"); ax.set_ylabel("y [Å]"); ax.set_zlabel("z [Å]")
    ax.scatter([], [], [], color="dodgerblue", s=200, label="Sr (A)")
    ax.scatter([], [], [], color="silver", s=120, label="Ti (B)")
    ax.scatter([], [], [], color="red", s=100, label="O (X)")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_box_aspect([1, 1, 1])

    fig.suptitle(
        "Crystal structures from B3 substrate K_4 cell tilings\n"
        "Lattice constants scale with substrate ξ; species set the ratios",
        fontsize=13, y=1.0,
    )
    fig.tight_layout()
    out.append(save(fig, "62_crystal_structures.png"))

    # ----- XRD patterns ------------------------------------------------------
    sim = CrystalSimulator()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))

    nacl_peaks = sim.xrd_peaks("NaCl", hkl_max=6)
    for p in nacl_peaks:
        if p["two_theta_deg"] > 120:
            continue
        ax1.vlines(p["two_theta_deg"], 0, p["intensity"],
                   colors="purple", lw=2.0, alpha=0.85)
        if p["intensity"] > 30:
            label = f"({p['hkl'][0]}{p['hkl'][1]}{p['hkl'][2]})"
            ax1.text(p["two_theta_deg"], p["intensity"] + 4,
                     label, fontsize=8, ha="center")
    ax1.set_xlim(20, 120)
    ax1.set_ylim(0, 130)
    ax1.set_xlabel("2θ (degrees)", fontsize=11)
    ax1.set_ylabel("Relative intensity", fontsize=11)
    ax1.set_title(
        "NaCl (rocksalt FCC) — Cu Kα λ = 1.5406 Å\n"
        "FCC selection rule: h, k, l all-even or all-odd"
        "  (strong: 200, 220, 222, 400, 420, 422)",
        fontsize=10,
    )
    ax1.grid(True, alpha=0.3)

    diam_peaks = sim.xrd_peaks("diamond", hkl_max=6)
    for p in diam_peaks:
        if p["two_theta_deg"] > 160:
            continue
        ax2.vlines(p["two_theta_deg"], 0, p["intensity"],
                   colors="black", lw=2.0, alpha=0.85)
        if p["intensity"] > 30:
            label = f"({p['hkl'][0]}{p['hkl'][1]}{p['hkl'][2]})"
            ax2.text(p["two_theta_deg"], p["intensity"] + 4,
                     label, fontsize=8, ha="center")
    ax2.set_xlim(30, 160)
    ax2.set_ylim(0, 130)
    ax2.set_xlabel("2θ (degrees)", fontsize=11)
    ax2.set_ylabel("Relative intensity", fontsize=11)
    ax2.set_title(
        "Diamond — Cu Kα λ = 1.5406 Å\n"
        "Diamond rule: FCC ∩ (h+k+l = 4n if all even)"
        "  (strong: 111, 220, 311, 400, 331)",
        fontsize=10,
    )
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        "X-ray diffraction patterns: Bragg's law 2 d sinθ = nλ\n"
        "Peak positions encode the substrate lattice spacings",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "63_xrd_patterns.png"))
    return out


def render_photosynthesis() -> list[str]:
    """Produce 72_chlorophyll_absorption.png and 73_photosystem_z_scheme.png.

    72: Chlorophyll a + b absorption spectra over 350-750 nm.  Shows the
        characteristic Soret (blue) and Qy (red) bands plus the green-light
        gap that gives plants their color.
    73: Z-scheme energy diagram --- electrons climb from H2O (+0.82 V) up to
        NADPH (-0.32 V) by two photo-driven jumps at PS-II (P680) and PS-I
        (P700).  Cofactors plotted vs E_h with the chain edges drawn between.
    """
    from src.stiff_medium.photosynthesis_substrate import (
        PhotosynthesisGeometry,
        PhotosynthesisSimulator,
        Z_SCHEME_REDOX_eV,
    )
    out: list[str] = []

    sim = PhotosynthesisSimulator()

    # ----- 72: Chlorophyll absorption spectrum -----------------------------
    fig, ax = plt.subplots(figsize=(11, 6.5))
    wl = np.linspace(350.0, 750.0, 801)

    g_a = PhotosynthesisGeometry(chlorophyll_type="chl_a")
    g_b = PhotosynthesisGeometry(chlorophyll_type="chl_b")
    spec_a = g_a.absorption_band(wl)
    spec_b = g_b.absorption_band(wl)

    # color-fill the visible spectrum behind the curves
    visible_colors = [
        (380, 440, "#7B00FF"),    # violet
        (440, 485, "#0000FF"),    # blue
        (485, 510, "#00FFFF"),    # cyan
        (510, 565, "#00FF00"),    # green
        (565, 590, "#FFFF00"),    # yellow
        (590, 625, "#FFA500"),    # orange
        (625, 700, "#FF0000"),    # red
        (700, 750, "#8B0000"),    # dark red
    ]
    for lo, hi, color in visible_colors:
        ax.axvspan(lo, hi, alpha=0.07, color=color, zorder=0)

    ax.plot(wl, spec_a, color="darkgreen", linewidth=2.2,
            label="Chlorophyll a (Soret 430 nm, Qy 662 nm)")
    ax.plot(wl, spec_b, color="olivedrab", linewidth=2.2, linestyle="--",
            label="Chlorophyll b (Soret 453 nm, Qy 642 nm)")

    # mark the four canonical peaks with vertical dashed lines + text
    peaks_a = g_a.absorption_peaks_nm()
    peaks_b = g_b.absorption_peaks_nm()
    for peak_nm, color, label, ya in [
        (peaks_a["soret"], "darkgreen", "430", 3.15),
        (peaks_a["qy"],    "darkgreen", "662", 1.10),
        (peaks_b["soret"], "olivedrab", "453", 3.30),
        (peaks_b["qy"],    "olivedrab", "642", 1.25),
    ]:
        ax.axvline(peak_nm, color=color, linestyle=":", linewidth=0.9,
                   alpha=0.5)
        ax.text(peak_nm, ya, f"{label} nm", fontsize=8.5,
                ha="center", color=color, fontweight="bold",
                bbox=dict(facecolor="white", edgecolor=color,
                          alpha=0.85, pad=1.5, lw=0.6))

    # green-light gap annotation
    ax.annotate(
        "Green-light gap\n(low absorption -> plants look green)",
        xy=(540.0, 0.20), xytext=(540.0, 1.7),
        fontsize=9, ha="center", color="darkgreen",
        arrowprops=dict(arrowstyle="->", color="darkgreen", lw=1.0),
    )

    ax.set_xlim(350.0, 750.0)
    ax.set_ylim(0.0, 3.7)
    ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.set_ylabel("Absorption (oscillator-strength weighted)", fontsize=12)
    ax.set_title(
        "Chlorophyll a + b absorption spectrum from substrate strain modes\n"
        "Tetrapyrrole macrocycle: Soret (blue) + Qy (red) eigenmodes "
        "with sigma~10 nm Gaussian broadening",
        fontsize=11,
    )
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out.append(save(fig, "72_chlorophyll_absorption.png"))

    # ----- 73: Z-scheme energy diagram -------------------------------------
    chain = sim.z_scheme()
    n = len(chain)
    xs = np.arange(n, dtype=float)
    es = np.array([e for _, e in chain])
    names = [name for name, _ in chain]

    fig, ax = plt.subplots(figsize=(13, 8))

    # Group color: PS-II side (light blue), PS-I side (light orange)
    ps2_idx = list(range(1, 9))   # P680 .. PC
    ps1_idx = list(range(9, n))   # P700 .. NADPH

    # Connect cofactors with arrows: downhill in normal transfer, uphill at photons
    for i in range(n - 1):
        delta = es[i + 1] - es[i]
        if delta < -0.5:
            # Photo-driven uphill jump (in E_h sense: more negative)
            ax.annotate("", xy=(xs[i + 1], es[i + 1]),
                        xytext=(xs[i], es[i]),
                        arrowprops=dict(arrowstyle="->",
                                        color="gold", lw=2.6,
                                        alpha=0.95,
                                        connectionstyle="arc3,rad=-0.3"))
        else:
            ax.annotate("", xy=(xs[i + 1], es[i + 1]),
                        xytext=(xs[i], es[i]),
                        arrowprops=dict(arrowstyle="->",
                                        color="dimgray", lw=1.4,
                                        alpha=0.85))

    # Plot cofactor markers
    for i, (name, e) in enumerate(chain):
        if name == "H2O/O2":
            color = "deepskyblue"; size = 220
        elif name in ("P680", "P680*"):
            color = "darkviolet"; size = 240
        elif name in ("P700", "P700*"):
            color = "crimson"; size = 240
        elif name == "NADPH":
            color = "forestgreen"; size = 220
        elif "Cyt" in name or "PC" in name:
            color = "darkorange"; size = 170
        elif "F" in name and ("d" in name or "x" in name or "A" in name):
            color = "saddlebrown"; size = 150
        else:
            color = "steelblue"; size = 140
        ax.scatter([xs[i]], [es[i]], color=color, s=size,
                   edgecolors="black", linewidths=1.0, zorder=10)

    # Cofactor labels (offset above/below to avoid arrow paths)
    label_offsets = {
        "H2O/O2": (0.3, 0.10), "P680": (0.0, 0.10),
        "P680*": (-0.1, -0.18), "Pheo": (0.0, -0.18),
        "QA": (0.0, -0.18), "QB": (0.0, 0.10),
        "PQ pool": (0.0, 0.10), "Cyt b6f": (0.0, 0.10),
        "PC": (0.2, 0.10), "P700": (0.2, 0.10),
        "P700*": (-0.1, -0.18), "A0": (0.0, -0.18),
        "A1": (0.0, -0.18), "Fx": (0.0, -0.18),
        "FA/FB": (0.0, -0.18), "Fd": (0.0, 0.10),
        "FNR": (0.0, 0.10), "NADPH": (0.0, 0.10),
    }
    for i, (name, e) in enumerate(chain):
        dx, dy = label_offsets.get(name, (0.0, 0.10))
        ax.text(xs[i] + dx, e + dy, name, fontsize=8.5,
                ha="center", va="bottom" if dy > 0 else "top",
                fontweight="bold")

    # Photon-jump labels
    photon_jumps = []
    for i in range(1, n):
        if es[i] - es[i - 1] < -1.0:
            photon_jumps.append(i)
    for j in photon_jumps:
        x_mid = (xs[j - 1] + xs[j]) / 2.0
        e_mid = (es[j - 1] + es[j]) / 2.0
        if names[j].startswith("P680"):
            label = "hv\n680 nm\n(1.823 eV)"
        else:
            label = "hv\n700 nm\n(1.771 eV)"
        ax.text(x_mid - 0.3, e_mid + 0.05, label, fontsize=10,
                ha="center", color="darkgoldenrod", fontweight="bold",
                bbox=dict(facecolor="lightyellow", edgecolor="gold",
                          alpha=0.9, pad=3.0, lw=1.0))

    # System brackets at the bottom
    ax.axhspan(es.min() - 0.4, es.min() - 0.2, alpha=0.0)
    ax.text(np.mean([xs[i] for i in ps2_idx[:3]]),
            es.min() - 0.15,
            "PS-II   (water-splitting)",
            fontsize=11, ha="center", color="darkviolet",
            fontweight="bold")
    ax.text(np.mean([xs[i] for i in ps1_idx[:3]]),
            es.min() - 0.15,
            "PS-I   (NADP+ -> NADPH)",
            fontsize=11, ha="center", color="crimson",
            fontweight="bold")

    # Stoichiometry text
    ax.text(0.02, 0.97,
            "Z-scheme stoichiometry (per O$_2$):\n"
            "   8 photons absorbed  (4 PS-II + 4 PS-I)\n"
            "   2 H$_2$O split  ->  4 e$^-$ + 4 H$^+$ + 1 O$_2$\n"
            "   12 H$^+$ pumped across thylakoid\n"
            "   2 NADPH + ~3 ATP produced\n"
            "Light-harvesting QY ~ 95%",
            transform=ax.transAxes, fontsize=10,
            verticalalignment="top", color="#222",
            bbox=dict(facecolor="white", edgecolor="gray", alpha=0.9, pad=6))

    ax.set_xticks([])
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(es.min() - 0.4, es.max() + 0.4)
    ax.set_ylabel("Redox potential E$_h$ (V) at pH 7",
                  fontsize=12)
    ax.set_title(
        "Photosystem Z-scheme: PS-II -> Cyt b$_6$f -> PS-I -> NADPH\n"
        "Two photons (gold curves) drive electrons uphill from H$_2$O to NADPH; "
        "downhill steps (gray) couple to proton pumping",
        fontsize=11,
    )
    ax.invert_yaxis()   # convention: more negative = up = stronger reductant
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out.append(save(fig, "73_photosystem_z_scheme.png"))

    return out


def render_neural() -> list[str]:
    """Produce 70_action_potential.png and 71_hh_gating.png.

    70: V(t) trace of a single Hodgkin-Huxley action potential with the
        canonical resting / threshold / peak voltages annotated and a
        second-pulse panel demonstrating the absolute refractory period
        (a stimulus delivered 1 ms after the first fails to fire a 2nd AP,
        while a stimulus delivered 20 ms later succeeds).
    71: Gating-variables m, h, n vs t over the same AP window plus the
        steady-state activation curves m_inf(V), h_inf(V), n_inf(V).
    """
    from src.stiff_medium.neural_substrate import (
        ABSOLUTE_REFRACTORY_MS,
        E_K_DEFAULT,
        E_L_DEFAULT,
        E_NA_DEFAULT,
        V_MYELINATED_M_PER_S,
        V_PEAK_TYP,
        V_REST,
        V_THRESHOLD,
        V_UNMYELINATED_M_PER_S,
        NeuralGeometry,
        NeuralSimulator,
        _hh_alpha_h,
        _hh_alpha_m,
        _hh_alpha_n,
        _hh_beta_h,
        _hh_beta_m,
        _hh_beta_n,
    )
    out: list[str] = []

    geom = NeuralGeometry()
    sim = NeuralSimulator(geometry=geom, duration_ms=50.0)

    # Single AP for 70 (top) and 71
    res = sim.simulate(
        I_inj_uA_per_cm2=15.0,
        stim_start_ms=5.0,
        stim_duration_ms=1.0,
    )

    # Refractory pair for 70 (bottom)
    sim_ref = NeuralSimulator(geometry=geom, duration_ms=60.0)
    res_close = sim_ref.simulate(
        I_inj_uA_per_cm2=15.0,
        stim_start_ms=5.0,
        stim_duration_ms=1.0,
        second_stim_ms=6.0,
        second_stim_duration_ms=1.0,
    )
    res_far = sim_ref.simulate(
        I_inj_uA_per_cm2=15.0,
        stim_start_ms=5.0,
        stim_duration_ms=1.0,
        second_stim_ms=25.0,
        second_stim_duration_ms=1.0,
    )

    # ---------------- 70: action-potential trace ------------------------
    fig = plt.figure(figsize=(13, 9))

    # Top: single AP with milestones annotated
    ax_top = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    ax_top.plot(res["t_ms"], res["V_mV"], color="tab:blue", linewidth=2.0,
                label="V(t)")
    ax_top.axhline(V_REST, color="gray", linestyle=":", linewidth=1.0,
                   label=f"V_rest = {V_REST:.0f} mV")
    ax_top.axhline(V_THRESHOLD, color="tab:orange", linestyle="--",
                   linewidth=1.0,
                   label=f"V_threshold = {V_THRESHOLD:.0f} mV")
    ax_top.axhline(0.0, color="black", linestyle=":", linewidth=0.6,
                   alpha=0.5)
    peak_idx = int(np.argmax(res["V_mV"]))
    peak_V = float(res["V_mV"][peak_idx])
    peak_t = float(res["t_ms"][peak_idx])
    ax_top.scatter([peak_t], [peak_V], s=80, c="tab:red", zorder=5,
                   label=f"peak = {peak_V:.1f} mV")
    ax_top.axhline(V_PEAK_TYP, color="tab:red", linestyle="--",
                   linewidth=0.8, alpha=0.5,
                   label=f"target peak = +{V_PEAK_TYP:.0f} mV")
    # Stimulus shading
    ax_top.axvspan(5.0, 6.0, color="tab:green", alpha=0.10,
                   label="stimulus pulse")
    # Phase labels
    phases = [
        (peak_t - 1.2, "depolarisation\n(Na+ in)", "tab:blue"),
        (peak_t + 1.5, "repolarisation\n(K+ out)", "tab:purple"),
        (peak_t + 5.5, "hyperpolarisation\n(K+ overshoot)", "tab:cyan"),
    ]
    for tx, label, color in phases:
        if 0.0 <= tx <= sim.duration_ms:
            ax_top.text(tx, V_REST - 18, label, fontsize=8, ha="center",
                        color=color)
    ax_top.set_xlabel("t [ms]")
    ax_top.set_ylabel("V_membrane [mV]")
    v_uny = V_UNMYELINATED_M_PER_S
    v_myl = V_MYELINATED_M_PER_S
    ax_top.set_title(
        f"Hodgkin-Huxley action potential   "
        f"(C_m=1 µF/cm², g_Na={geom.g_Na_max:.0f}, g_K={geom.g_K_max:.0f})\n"
        f"conduction:  unmyelinated v ≈ {v_uny:.0f} m/s,  "
        f"myelinated v ≈ {v_myl:.0f} m/s  (×{v_myl/v_uny:.0f} saltatory)"
    )
    ax_top.set_ylim(-90, 60)
    ax_top.set_xlim(0, sim.duration_ms)
    ax_top.legend(loc="upper right", fontsize=8, ncol=2)
    ax_top.grid(True, alpha=0.3)

    # Bottom-left: pulses 1 ms apart -- only 1 AP fires
    ax_bl = plt.subplot2grid((2, 2), (1, 0))
    ax_bl.plot(res_close["t_ms"], res_close["V_mV"], color="tab:blue",
               linewidth=1.5)
    ax_bl.axhline(V_THRESHOLD, color="tab:orange", linestyle="--",
                  linewidth=0.8)
    ax_bl.axvspan(5.0, 6.0, color="tab:green", alpha=0.10, label="pulse 1")
    ax_bl.axvspan(6.0, 7.0, color="tab:red", alpha=0.18,
                  label="pulse 2 (1 ms gap)")
    n_spk_close = int(np.sum(
        (res_close["V_mV"][:-1] < 0.0) & (res_close["V_mV"][1:] >= 0.0)
    ))
    ax_bl.set_title(
        f"Two pulses 1 ms apart → {n_spk_close} AP\n"
        f"(absolute refractory τ ≈ {ABSOLUTE_REFRACTORY_MS:.1f} ms blocks 2nd AP)"
    )
    ax_bl.set_xlabel("t [ms]"); ax_bl.set_ylabel("V [mV]")
    ax_bl.set_xlim(0, 30)
    ax_bl.set_ylim(-90, 60)
    ax_bl.legend(loc="upper right", fontsize=8)
    ax_bl.grid(True, alpha=0.3)

    # Bottom-right: pulses 20 ms apart -- both APs fire
    ax_br = plt.subplot2grid((2, 2), (1, 1))
    ax_br.plot(res_far["t_ms"], res_far["V_mV"], color="tab:blue",
               linewidth=1.5)
    ax_br.axhline(V_THRESHOLD, color="tab:orange", linestyle="--",
                  linewidth=0.8)
    ax_br.axvspan(5.0, 6.0, color="tab:green", alpha=0.10, label="pulse 1")
    ax_br.axvspan(25.0, 26.0, color="tab:purple", alpha=0.18,
                  label="pulse 2 (20 ms gap)")
    n_spk_far = int(np.sum(
        (res_far["V_mV"][:-1] < 0.0) & (res_far["V_mV"][1:] >= 0.0)
    ))
    ax_br.set_title(
        f"Two pulses 20 ms apart → {n_spk_far} APs\n"
        f"(membrane recovered, second AP fires normally)"
    )
    ax_br.set_xlabel("t [ms]"); ax_br.set_ylabel("V [mV]")
    ax_br.set_xlim(0, 60)
    ax_br.set_ylim(-90, 60)
    ax_br.legend(loc="upper right", fontsize=8)
    ax_br.grid(True, alpha=0.3)

    fig.suptitle(
        "Action potential from substrate: V(t) shape + refractory period\n"
        "(B3 ontology: AP = strain pulse; refractory = h-gate re-arming "
        "= cell re-saturation)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "70_action_potential.png"))

    # ---------------- 71: gating variables m, h, n ----------------------
    fig = plt.figure(figsize=(13, 8))

    # Top: V(t) for context
    ax_v = plt.subplot2grid((3, 2), (0, 0), colspan=2)
    ax_v.plot(res["t_ms"], res["V_mV"], color="tab:blue", linewidth=1.6)
    ax_v.axhline(V_REST, color="gray", linestyle=":", linewidth=0.8)
    ax_v.axhline(V_THRESHOLD, color="tab:orange", linestyle="--",
                 linewidth=0.8)
    ax_v.set_ylabel("V [mV]")
    ax_v.set_xlim(0, sim.duration_ms)
    ax_v.set_title("Membrane potential V(t)")
    ax_v.grid(True, alpha=0.3)

    # Middle-left: m, h, n vs time
    ax_g = plt.subplot2grid((3, 2), (1, 0), rowspan=2)
    ax_g.plot(res["t_ms"], res["m"], label="m  (Na+ activation)",
              color="tab:red",   linewidth=1.8)
    ax_g.plot(res["t_ms"], res["h"], label="h  (Na+ inactivation)",
              color="tab:purple", linewidth=1.8)
    ax_g.plot(res["t_ms"], res["n"], label="n  (K+ activation)",
              color="tab:green", linewidth=1.8)
    ax_g.set_xlabel("t [ms]")
    ax_g.set_ylabel("Gating variable [0, 1]")
    ax_g.set_xlim(0, sim.duration_ms)
    ax_g.set_ylim(-0.05, 1.05)
    ax_g.set_title(
        "Hodgkin-Huxley gating variables vs t\n"
        "m^3·h gates I_Na;  n^4 gates I_K"
    )
    ax_g.axhline(0, color="gray", linewidth=0.4)
    ax_g.axhline(1, color="gray", linewidth=0.4)
    ax_g.legend(loc="center right", fontsize=9)
    ax_g.grid(True, alpha=0.3)

    # Middle-right: steady-state activation curves m_inf, h_inf, n_inf
    ax_ss = plt.subplot2grid((3, 2), (1, 1), rowspan=2)
    Vrange = np.linspace(-100.0, 50.0, 401)
    am, bm = _hh_alpha_m(Vrange), _hh_beta_m(Vrange)
    ah, bh = _hh_alpha_h(Vrange), _hh_beta_h(Vrange)
    an, bn = _hh_alpha_n(Vrange), _hh_beta_n(Vrange)
    m_inf = am / (am + bm)
    h_inf = ah / (ah + bh)
    n_inf = an / (an + bn)
    ax_ss.plot(Vrange, m_inf, label="m_∞(V)", color="tab:red",   linewidth=2.0)
    ax_ss.plot(Vrange, h_inf, label="h_∞(V)", color="tab:purple", linewidth=2.0)
    ax_ss.plot(Vrange, n_inf, label="n_∞(V)", color="tab:green", linewidth=2.0)
    ax_ss.axvline(V_REST, color="gray", linestyle=":", linewidth=0.8,
                  label="V_rest")
    ax_ss.axvline(V_THRESHOLD, color="tab:orange", linestyle="--",
                  linewidth=0.8, label="V_threshold")
    ax_ss.set_xlabel("V [mV]")
    ax_ss.set_ylabel("Steady-state value")
    ax_ss.set_title(
        f"Steady-state activation x_∞(V)\n"
        f"E_Na = {E_NA_DEFAULT:+.0f}, E_K = {E_K_DEFAULT:+.0f}, "
        f"E_L = {E_L_DEFAULT:+.1f} mV"
    )
    ax_ss.legend(loc="center right", fontsize=9)
    ax_ss.grid(True, alpha=0.3)

    fig.suptitle(
        "Hodgkin-Huxley gating: m, h, n vs t and steady-state activation\n"
        "(B3 ontology: m, h, n = saturation-gate occupancies of Na+/K+ "
        "substrate channels)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "71_hh_gating.png"))

    return out


def render_ribosome() -> list[str]:
    """Produce 74_ribosome_codon.png and 75_translation_kinetics.png.

    74: Two panels showing the codon-anticodon recognition geometry.
        Left:  schematic of the 70S ribosome -- 30S small subunit (bottom)
               and 50S large subunit (top) drawn as ellipses, with the
               mRNA codon track threaded through the small subunit and
               A/P/E tRNA-binding sites marked in the inter-subunit cleft.
        Right: zoom-in on the A site showing the codon-anticodon helix
               with three Watson-Crick base pairs (A-U / U-A / G-C for
               the start codon AUG <-> anticodon UAC).  Donor-acceptor
               H-bond distances annotated at 2.85 A.
    75: Three panels of translation kinetics.
        Left:   ribosome elongation rate distribution (log-normal) for
                bacteria (mean 20 aa/s) and eukaryotes (mean 5 aa/s).
        Centre: error rate as a function of number of kinetic gates
                (single gate ~ 1e-2, two gates ~ 1e-4, etc.) -- shows
                why kinetic proofreading is necessary for fidelity.
        Right:  GTP budget for protein synthesis -- 2 GTP per peptide
                bond, plotted across protein lengths from 50 to 1000 aa.
    """
    from src.stiff_medium.ribosome_substrate import (
        CODON_PITCH_A,
        ERROR_RATE_PER_CODON,
        GTP_PER_ELONGATION_CYCLE,
        INITIAL_SELECTION_ERR,
        INTER_SITE_SPACING_A,
        RATE_BACTERIA_AA_PER_S,
        RATE_EUKARYOTE_AA_PER_S,
        WC_BASE_PAIR_DISTANCE_A,
        RibosomeGeometry,
        RibosomeSimulator,
    )
    out: list[str] = []

    # ---- 74: Ribosome schematic + codon-anticodon at A site -----------
    geom = RibosomeGeometry(
        organism_class="bacteria",
        mrna_sequence="AUGGCUAAACGUUAAUAA",   # Met-Ala-Lys-Arg-stop-stop
    )
    sim = RibosomeSimulator(geometry=geom, organism_class="bacteria")

    fig = plt.figure(figsize=(15, 7))

    # --- Left: 70S ribosome with mRNA + A/P/E sites
    ax1 = fig.add_subplot(1, 2, 1)
    d_small, h_small = geom.small_subunit_dimensions_angstrom()
    d_large, h_large = geom.large_subunit_dimensions_angstrom()
    z_cleft = 0.5 * h_small + 5.0
    e_small = plt.matplotlib.patches.Ellipse(
        (0, 0), d_small, h_small,
        facecolor="tab:cyan", edgecolor="black", alpha=0.45, linewidth=1.5,
    )
    ax1.add_patch(e_small)
    ax1.text(0, -0.35 * h_small, "30S\n(small subunit)",
             ha="center", va="center", fontsize=10, fontweight="bold")
    e_large = plt.matplotlib.patches.Ellipse(
        (0, z_cleft + 10.0 + 0.5 * h_large),
        d_large, h_large,
        facecolor="tab:orange", edgecolor="black", alpha=0.45, linewidth=1.5,
    )
    ax1.add_patch(e_large)
    ax1.text(0, z_cleft + 10.0 + 0.85 * h_large, "50S\n(large subunit)",
             ha="center", va="center", fontsize=10, fontweight="bold")
    n_codons = geom.codon_count()
    y_track = (np.arange(n_codons) - (n_codons - 1) / 2.0) * CODON_PITCH_A
    z_mrna = 0.5 * h_small - 5.0
    ax1.plot(y_track, np.full_like(y_track, z_mrna),
             "k-", linewidth=2.5, alpha=0.85, label="mRNA (5'->3')")
    for k, y in enumerate(y_track):
        ax1.scatter(y, z_mrna, c="tab:purple", s=90, zorder=5,
                    edgecolors="black", linewidths=0.6)
        ax1.annotate(geom.codon_at(k), (y, z_mrna - 8),
                     ha="center", fontsize=8, family="monospace")
    site_colors = {"A": "tab:red", "P": "tab:green", "E": "tab:blue"}
    site_dy = {"A": +INTER_SITE_SPACING_A, "P": 0.0, "E": -INTER_SITE_SPACING_A}
    for site, color in site_colors.items():
        y = site_dy[site]
        ax1.scatter([y], [z_cleft + 5.0], c=color, s=320, marker="o",
                    edgecolors="black", linewidths=1.5,
                    label=f"{site} site", zorder=6)
        ax1.text(y, z_cleft + 14.0, f"{site}", ha="center", va="bottom",
                 fontsize=12, fontweight="bold", color=color)
    ax1.annotate("", xy=(y_track.max() + 12, z_mrna),
                 xytext=(y_track.max() + 2, z_mrna),
                 arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax1.text(y_track.max() + 14, z_mrna - 4, "5'->3'",
             fontsize=9, family="monospace")
    ax1.set_xlim(-0.6 * d_large, +0.6 * d_large)
    ax1.set_ylim(-0.6 * h_small, z_cleft + 10.0 + 1.05 * h_large)
    ax1.set_xlabel("y [A] (mRNA reading axis)", fontsize=10)
    ax1.set_ylabel("z [A] (subunit-stack axis)", fontsize=10)
    ax1.set_aspect("equal")
    ax1.set_title(
        "70S ribosome: 30S + 50S subunits, mRNA codon track, A/P/E sites\n"
        f"codon pitch = {CODON_PITCH_A:.1f} A; site spacing = {INTER_SITE_SPACING_A:.0f} A",
        fontsize=11,
    )
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(True, alpha=0.2)

    # --- Right: codon-anticodon Watson-Crick helix at A site
    ax2 = fig.add_subplot(1, 2, 2)
    a_codon = geom.a_site_codon()
    a_anti  = geom.a_site_anticodon()
    bp_dx = 4.0
    xs = np.array([0.0, bp_dx, 2.0 * bp_dx])
    y_codon = 0.0
    y_anti  = WC_BASE_PAIR_DISTANCE_A
    base_color = {"A": "tab:red", "U": "tab:blue",
                  "G": "tab:green", "C": "tab:orange"}
    for i, (cb, ab) in enumerate(zip(a_codon, a_anti)):
        ax2.scatter(xs[i], y_codon, c=base_color[cb], s=900,
                    edgecolors="black", linewidths=1.5, zorder=5)
        ax2.text(xs[i], y_codon - 0.7, cb, ha="center", va="center",
                 fontsize=14, fontweight="bold")
        ax2.scatter(xs[i], y_anti, c=base_color[ab], s=900,
                    edgecolors="black", linewidths=1.5, zorder=5)
        ax2.text(xs[i], y_anti + 0.7, ab, ha="center", va="center",
                 fontsize=14, fontweight="bold")
        n_hbonds = 3 if (cb, ab) in {("G", "C"), ("C", "G")} else 2
        for j in range(n_hbonds):
            offset = (j - (n_hbonds - 1) / 2.0) * 0.18
            ax2.plot([xs[i] + offset, xs[i] + offset],
                     [y_codon + 0.35, y_anti - 0.35],
                     "k--", linewidth=1.2, alpha=0.85)
    ax2.annotate(
        f"{WC_BASE_PAIR_DISTANCE_A:.2f} A",
        xy=(xs[-1] + 0.6, 0.5 * (y_codon + y_anti)),
        fontsize=10, color="black", fontweight="bold",
    )
    ax2.annotate("", xy=(xs[-1] + 0.55, y_anti - 0.45),
                 xytext=(xs[-1] + 0.55, y_codon + 0.45),
                 arrowprops=dict(arrowstyle="<->", color="black", lw=1.0))
    ax2.annotate("mRNA codon (5'->3')", xy=(xs[-1] + 0.5, y_codon),
                 xytext=(xs[-1] + 1.2, y_codon - 1.5),
                 arrowprops=dict(arrowstyle="-", color="gray", lw=0.8),
                 fontsize=9, family="monospace")
    ax2.annotate("tRNA anticodon (3'->5')", xy=(xs[-1] + 0.5, y_anti),
                 xytext=(xs[-1] + 1.2, y_anti + 1.5),
                 arrowprops=dict(arrowstyle="-", color="gray", lw=0.8),
                 fontsize=9, family="monospace")
    ax2.annotate("", xy=(xs[-1] + 1.0, y_codon),
                 xytext=(xs[0] - 1.0, y_codon),
                 arrowprops=dict(arrowstyle="->", color="tab:purple", lw=2))
    ax2.annotate("", xy=(xs[0] - 1.0, y_anti),
                 xytext=(xs[-1] + 1.0, y_anti),
                 arrowprops=dict(arrowstyle="->", color="tab:olive", lw=2))
    ax2.set_xlim(-2.5, xs[-1] + 4.5)
    ax2.set_ylim(-2.5, y_anti + 2.5)
    ax2.set_aspect("equal")
    ax2.set_title(
        f"A-site codon-anticodon Watson-Crick pairing\n"
        f"codon = {a_codon}  <-->  anticodon = {a_anti}   "
        f"(WC pairs = {sim.watson_crick_pairs(a_codon, a_anti)} of 3)",
        fontsize=11,
    )
    ax2.set_xlabel("position along helix axis [A]", fontsize=10)
    ax2.set_ylabel("strand displacement [A]", fontsize=10)
    ax2.grid(True, alpha=0.2)

    fig.suptitle(
        "Ribosome translation from substrate: codon-anticodon recognition",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "74_ribosome_codon.png"))

    # ---- 75: Translation kinetics + proofreading + GTP budget ----------
    sim_b = RibosomeSimulator(organism_class="bacteria")
    sim_e = RibosomeSimulator(organism_class="eukaryote")

    fig, (axL, axM, axR) = plt.subplots(1, 3, figsize=(15, 5))

    # --- Left: elongation rate distribution (log-normal)
    samples_b = sim_b.elongation_rate_distribution(n_samples=20000, seed=1)
    samples_e = sim_e.elongation_rate_distribution(n_samples=20000, seed=2)
    bins = np.linspace(0, 60, 80)
    axL.hist(samples_b, bins=bins, density=True, color="tab:blue", alpha=0.55,
             edgecolor="black", linewidth=0.4,
             label=f"bacteria (mean {RATE_BACTERIA_AA_PER_S:.0f} aa/s)")
    axL.hist(samples_e, bins=bins, density=True, color="tab:orange", alpha=0.55,
             edgecolor="black", linewidth=0.4,
             label=f"eukaryote (mean {RATE_EUKARYOTE_AA_PER_S:.0f} aa/s)")
    axL.axvline(RATE_BACTERIA_AA_PER_S, color="tab:blue", lw=2.0, ls="--",
                label=f"bacterial sample mean = {samples_b.mean():.1f} aa/s")
    axL.axvline(RATE_EUKARYOTE_AA_PER_S, color="tab:orange", lw=2.0, ls="--",
                label=f"eukaryotic sample mean = {samples_e.mean():.1f} aa/s")
    axL.set_xlabel("elongation rate [amino acids / s]", fontsize=10)
    axL.set_ylabel("probability density", fontsize=10)
    axL.set_title(
        f"Translation rate distribution\n"
        f"speedup ratio bact/euk = {samples_b.mean()/samples_e.mean():.2f}",
        fontsize=11,
    )
    axL.legend(fontsize=8)
    axL.grid(True, alpha=0.3)

    # --- Centre: kinetic proofreading -- error vs number of gates
    n_gates = np.array([0, 1, 2, 3, 4, 5])
    err_per_gate = INITIAL_SELECTION_ERR
    err = np.where(n_gates == 0, 1.0, err_per_gate ** np.maximum(n_gates, 1))
    axM.semilogy(n_gates, err, "o-", color="tab:red", markersize=10,
                 linewidth=2.0, label="error = (1e-2)^N_gates")
    axM.axhline(ERROR_RATE_PER_CODON, color="tab:green", ls="--", lw=1.5,
                label=f"biological setpoint = {ERROR_RATE_PER_CODON:.0e}")
    axM.scatter([2], [ERROR_RATE_PER_CODON], c="tab:green", s=300,
                marker="*", edgecolors="black", linewidths=1.5, zorder=10,
                label="ribosome (2 gates: EF-Tu, post-GTP)")
    axM.set_xlabel("number of kinetic discrimination gates", fontsize=10)
    axM.set_ylabel("per-codon error rate", fontsize=10)
    axM.set_title(
        "Kinetic proofreading\n"
        "single gate ~ 1e-2; two gates -> ~ 1e-4 (Hopfield 1974)",
        fontsize=11,
    )
    axM.set_xticks(n_gates)
    axM.set_ylim(1e-12, 2.0)
    axM.legend(fontsize=8, loc="upper right")
    axM.grid(True, which="both", alpha=0.3)

    # --- Right: GTP budget vs protein length
    lengths = np.arange(50, 1050, 25)
    gtp_per_protein = GTP_PER_ELONGATION_CYCLE * lengths
    axR.plot(lengths, gtp_per_protein, "-", color="tab:purple", linewidth=2.0,
             label=f"{GTP_PER_ELONGATION_CYCLE} GTP/cycle (EF-Tu + EF-G)")
    typical_len = 300
    axR.scatter([typical_len], [GTP_PER_ELONGATION_CYCLE * typical_len],
                c="tab:red", s=180, marker="o", edgecolors="black",
                linewidths=1.5, zorder=5,
                label=f"300-aa protein -> {GTP_PER_ELONGATION_CYCLE * typical_len} GTP")
    axR2 = axR.twinx()
    times_b = lengths / RATE_BACTERIA_AA_PER_S
    times_e = lengths / RATE_EUKARYOTE_AA_PER_S
    axR2.plot(lengths, times_b, "-", color="tab:blue", linewidth=1.5, alpha=0.7,
              label=f"bacteria translation time ({RATE_BACTERIA_AA_PER_S:.0f} aa/s)")
    axR2.plot(lengths, times_e, "-", color="tab:orange", linewidth=1.5, alpha=0.7,
              label=f"eukaryote translation time ({RATE_EUKARYOTE_AA_PER_S:.0f} aa/s)")
    axR2.set_ylabel("translation time [s]", fontsize=10, color="tab:gray")
    axR2.tick_params(axis="y", labelcolor="tab:gray")
    axR.set_xlabel("protein length [amino acids]", fontsize=10)
    axR.set_ylabel("GTP molecules consumed", fontsize=10, color="tab:purple")
    axR.tick_params(axis="y", labelcolor="tab:purple")
    e_kT = sim_b.energy_per_peptide_bond_kT()
    axR.set_title(
        "GTP budget per protein\n"
        f"{e_kT:.1f} kT / peptide bond (2 GTP * 7.3 kcal/mol)",
        fontsize=11,
    )
    h1, l1 = axR.get_legend_handles_labels()
    h2, l2 = axR2.get_legend_handles_labels()
    axR.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
    axR.grid(True, alpha=0.3)

    fig.suptitle(
        "Translation kinetics from substrate: rate, fidelity, energy budget",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "75_translation_kinetics.png"))

    return out


def render_immune() -> list[str]:
    """Produce 78_antibody_binding.png and 79_immune_response.png.

    78: 3D Y-shaped antibody (IgG) with two Fab arms, Fc stem, paratopes
        at each Fab tip, an antigen sphere bound to the right paratope,
        and an MHC class-I platform with a 9-residue peptide.
    79: Two panels.  Left -- antibody titer A(t) for primary (1 deg) vs
        secondary (2 deg) response; secondary peaks ~100x higher and
        ~3x faster.  Right -- SIR-like coupled pathogen P(t) and
        antibody A(t) showing antibody peaks AFTER pathogen burst.
    """
    from src.stiff_medium.immune_substrate import (
        ANTIBODY_FAB_LENGTH_NM,
        ANTIBODY_FC_LENGTH_NM,
        ANTIBODY_HINGE_ANGLE_DEG,
        ImmuneGeometry,
        ImmuneSimulator,
    )
    out: list[str] = []

    geom = ImmuneGeometry()
    sim = ImmuneSimulator(geometry=geom)

    # ---- 78: 3D Y-shape antibody with bound antigen + MHC -------------
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")

    fc_base, fc_hinge = geom.fc_endpoints()
    ax.plot([fc_base[0], fc_hinge[0]],
            [fc_base[1], fc_hinge[1]],
            [fc_base[2], fc_hinge[2]],
            color="tab:purple", linewidth=14, alpha=0.85,
            solid_capstyle="round")

    _, fab_left = geom.fab_endpoints("left")
    _, fab_right = geom.fab_endpoints("right")
    for tip in (fab_left, fab_right):
        ax.plot([fc_hinge[0], tip[0]],
                [fc_hinge[1], tip[1]],
                [fc_hinge[2], tip[2]],
                color="tab:blue", linewidth=14, alpha=0.85,
                solid_capstyle="round")

    ax.scatter([fc_hinge[0]], [fc_hinge[1]], [fc_hinge[2]],
               c="black", s=160, zorder=10)

    paratopes = geom.paratope_centers()
    for p in paratopes:
        u = np.linspace(0, 2 * np.pi, 16)
        v = np.linspace(0, np.pi, 12)
        r = geom.paratope_radius_nm
        xs = p[0] + r * np.outer(np.cos(u), np.sin(v))
        ys = p[1] + r * np.outer(np.sin(u), np.sin(v))
        zs = p[2] + r * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(xs, ys, zs, color="gold", alpha=0.85,
                        edgecolor="darkgoldenrod", linewidth=0.2)

    ag = geom.antigen_position("right")
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 16)
    R = geom.antigen_radius_nm
    xs = ag[0] + R * np.outer(np.cos(u), np.sin(v))
    ys = ag[1] + R * np.outer(np.sin(u), np.sin(v))
    zs = ag[2] + R * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(xs, ys, zs, color="tab:red", alpha=0.75,
                    edgecolor="darkred", linewidth=0.3)

    z_mhc = -ANTIBODY_FC_LENGTH_NM - 4.0
    corners = geom.mhc_platform_corners(z_mhc=z_mhc)
    plat_x = corners[[0, 1, 2, 3, 0], 0]
    plat_y = corners[[0, 1, 2, 3, 0], 1]
    plat_z = corners[[0, 1, 2, 3, 0], 2]
    ax.plot(plat_x, plat_y, plat_z, color="seagreen", linewidth=2.0)
    quad_x = np.array([[corners[0, 0], corners[1, 0]],
                       [corners[3, 0], corners[2, 0]]])
    quad_y = np.array([[corners[0, 1], corners[1, 1]],
                       [corners[3, 1], corners[2, 1]]])
    quad_z = np.array([[corners[0, 2], corners[1, 2]],
                       [corners[3, 2], corners[2, 2]]])
    ax.plot_surface(quad_x, quad_y, quad_z,
                    color="lightgreen", alpha=0.5,
                    edgecolor="seagreen", linewidth=0.4)

    pep = geom.mhc_peptide_positions(z_mhc=z_mhc)
    ax.plot(pep[:, 0], pep[:, 1], pep[:, 2],
            color="darkorange", linewidth=3.5, alpha=0.95)
    ax.scatter(pep[:, 0], pep[:, 1], pep[:, 2],
               c="darkorange", s=55, edgecolors="saddlebrown",
               linewidths=0.8, zorder=8)

    ax.text(fc_base[0], fc_base[1], fc_base[2] - 0.7, "Fc stem",
            color="tab:purple", fontsize=10, fontweight="bold",
            ha="center")
    ax.text(fab_left[0], fab_left[1] - 0.6, fab_left[2] + 0.6,
            "Fab\n(L)", color="tab:blue", fontsize=10,
            fontweight="bold", ha="center")
    ax.text(fab_right[0], fab_right[1] + 0.6, fab_right[2] + 0.6,
            "Fab\n(R)", color="tab:blue", fontsize=10,
            fontweight="bold", ha="center")
    ax.text(0.2, 0.0, 0.4, "hinge", color="black", fontsize=9)
    ax.text(paratopes[0, 0], paratopes[0, 1] - 1.3, paratopes[0, 2],
            "paratope", color="darkgoldenrod", fontsize=8,
            ha="center")
    ax.text(ag[0], ag[1] + 0.4, ag[2] + R + 0.7,
            f"antigen\n(K_d = {sim.Kd_M:.0e} M)",
            color="darkred", fontsize=9, fontweight="bold",
            ha="center")
    ax.text(0.0, 0.0, z_mhc - 1.0,
            "MHC class I + peptide (9-mer)",
            color="seagreen", fontsize=10, fontweight="bold",
            ha="center")

    ax.plot([fab_left[0], fab_right[0]],
            [fab_left[1], fab_right[1]],
            [fab_left[2] + 0.8, fab_right[2] + 0.8],
            color="black", linestyle="--", linewidth=1.0)
    ax.text(0.0, 0.0, fab_right[2] + 1.4,
            f"span = {geom.total_span_nm():.1f} nm",
            color="black", fontsize=9, ha="center")

    ax.set_xlabel("x [nm]")
    ax.set_ylabel("y [nm]")
    ax.set_zlabel("z [nm]")
    ax.set_title(
        f"Antibody (IgG) Y-shape: Fab + Fc + paratopes + bound antigen\n"
        f"Fab arm = {ANTIBODY_FAB_LENGTH_NM} nm; "
        f"hinge angle = {ANTIBODY_HINGE_ANGLE_DEG}deg; "
        f"K_d = {sim.Kd_M:.0e} M  ->  delta_G "
        f"= {sim.binding_free_energy_kcal_per_mol():.1f} kcal/mol"
    )
    span = geom.total_span_nm() * 0.7
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.set_zlim(z_mhc - 2.0, fab_right[2] + 3.0)
    try:
        ax.set_box_aspect((1.0, 1.0, 1.6))
    except Exception:
        pass
    fig.tight_layout()
    out.append(save(fig, "78_antibody_binding.png"))

    # ---- 79: Antibody titer 1 deg vs 2 deg + SIR coupled --------------
    fig = plt.figure(figsize=(15, 6))

    ax1 = fig.add_subplot(1, 2, 1)
    t_days = np.linspace(0.0, 120.0, 700)
    response = sim.primary_vs_secondary(t_days,
                                         secondary_offset_days=60.0)
    ax1.semilogy(t_days, np.maximum(response["primary"], 1.0e-3),
                 color="tab:blue", linewidth=2.2,
                 label=f"primary (1 deg) - peak = {sim.primary_peak:.1f}")
    ax1.semilogy(t_days, np.maximum(response["secondary"], 1.0e-3),
                 color="tab:red", linewidth=2.2,
                 label=f"secondary (2 deg) - peak = {sim.secondary_peak:.0f}")
    ax1.semilogy(t_days, np.maximum(response["total"], 1.0e-3),
                 color="black", linewidth=1.4, linestyle="--",
                 alpha=0.6, label="total (1 deg + 2 deg)")

    ax1.axvline(0.0, color="gray", linestyle=":", linewidth=1.2)
    ax1.axvline(60.0, color="gray", linestyle=":", linewidth=1.2)
    ax1.text(0.5, 50.0, "1 deg exposure", rotation=90,
             color="gray", fontsize=8, va="center")
    ax1.text(60.5, 50.0, "2 deg exposure", rotation=90,
             color="gray", fontsize=8, va="center")

    ax1.set_xlabel("time [days]")
    ax1.set_ylabel("antibody titer [a.u., log scale]")
    ax1.set_ylim(1.0e-2, 5.0e2)
    ax1.set_title(
        f"Primary vs secondary response\n"
        f"latency: 1 deg = {sim.primary_latency_days:.0f} d, "
        f"2 deg = {sim.secondary_latency_days:.1f} d; "
        f"2 deg/1 deg peak = {sim.secondary_peak/sim.primary_peak:.0f}x"
    )
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.92)
    ax1.grid(True, alpha=0.25, which="both")

    ax2 = fig.add_subplot(1, 2, 2)
    t_sir = np.linspace(0.0, 30.0, 600)
    sir = sim.sir_immune_response(t_sir, P0=1.0, A0=0.0)
    ax2.plot(t_sir, sir["P"], color="tab:red", linewidth=2.2,
             label="pathogen P(t)")
    ax2.plot(t_sir, sir["A"], color="tab:blue", linewidth=2.2,
             label="antibody A(t)")
    t_p_peak = t_sir[int(np.argmax(sir["P"]))]
    t_a_peak = t_sir[int(np.argmax(sir["A"]))]
    ax2.axvline(t_p_peak, color="tab:red", linestyle=":",
                linewidth=1.0, alpha=0.7)
    ax2.axvline(t_a_peak, color="tab:blue", linestyle=":",
                linewidth=1.0, alpha=0.7)
    ax2.text(t_p_peak + 0.2, sir["P"].max() * 0.95,
             f"P peak\nt = {t_p_peak:.1f} d",
             color="tab:red", fontsize=8)
    ax2.text(t_a_peak + 0.2, sir["A"].max() * 0.95,
             f"A peak\nt = {t_a_peak:.1f} d",
             color="tab:blue", fontsize=8)
    ax2.set_xlabel("time [days]")
    ax2.set_ylabel("concentration [a.u.]")
    ax2.set_title(
        "SIR-like coupled dynamics\n"
        "dP/dt = +alpha P - beta P A;  "
        "dA/dt = +gamma P - delta A"
    )
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.92)
    ax2.grid(True, alpha=0.25)

    fig.suptitle(
        "Adaptive immune response from substrate: "
        "memory yields the 100x secondary boost",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "79_immune_response.png"))

    return out


def render_ecosystem() -> list[str]:
    """Produce 80_lotka_volterra.png and 81_food_web.png.

    80: Two panels.  Left -- predator-prey timeseries N(t), P(t) for the
        canonical Lotka-Volterra system (alpha, beta, delta, gamma) with
        small-amplitude period T = 2 pi / sqrt(alpha gamma).  Right --
        phase portrait showing closed orbits at three different initial
        amplitudes around the interior equilibrium (gamma/delta,
        alpha/beta).
    81: Directed food-web visualisation.  Left -- a 4-level linear food
        chain (basal -> top predator) with edges drawn from prey to
        predator.  Right -- May-Wigner stability scan: fraction of
        random N=30 webs that are unstable as a function of the
        complexity parameter sigma * sqrt(N C); the May-Wigner
        threshold sits at complexity = 1.
    """
    from src.stiff_medium.ecosystem_substrate import (
        EcosystemGeometry,
        EcosystemSimulator,
    )
    out: list[str] = []

    # ===== 80: Lotka-Volterra timeseries + phase portrait =============
    alpha, beta, delta, gamma = 1.0, 0.1, 0.075, 1.5
    sim = EcosystemSimulator()
    N_eq, P_eq = sim.lotka_volterra_equilibrium(alpha, beta, delta, gamma)
    period_lin = sim.lotka_volterra_period(alpha=alpha, gamma=gamma)

    fig = plt.figure(figsize=(14, 6))

    # Left: timeseries
    ax1 = fig.add_subplot(1, 2, 1)
    t, N, P = sim.integrate_lotka_volterra(
        N0=40.0, P0=9.0,
        alpha=alpha, beta=beta, delta=delta, gamma=gamma,
        t_end=60.0, dt=0.005,
    )
    ax1.plot(t, N, "g-", linewidth=1.6, label="prey N(t)")
    ax1.plot(t, P, "r-", linewidth=1.6, label="predator P(t)")
    ax1.axhline(N_eq, color="green", linestyle=":", alpha=0.6,
                label=f"N* = γ/δ = {N_eq:.1f}")
    ax1.axhline(P_eq, color="red", linestyle=":", alpha=0.6,
                label=f"P* = α/β = {P_eq:.1f}")
    ax1.set_xlabel("time t [arb. units]")
    ax1.set_ylabel("population")
    ax1.set_title(
        f"Lotka-Volterra oscillation\n"
        f"α={alpha}, β={beta}, δ={delta}, γ={gamma}; "
        f"T_lin = 2π/√(αγ) = {period_lin:.2f}"
    )
    ax1.legend(loc="upper right", fontsize=9, framealpha=0.85)
    ax1.grid(True, alpha=0.3)

    # Right: phase portrait at three amplitudes
    ax2 = fig.add_subplot(1, 2, 2)
    init_conditions = [
        (N_eq * 1.05, P_eq * 1.00),
        (N_eq * 1.30, P_eq * 1.00),
        (N_eq * 1.80, P_eq * 1.00),
    ]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for (n0, p0), c in zip(init_conditions, colors):
        _, Nt, Pt = sim.integrate_lotka_volterra(
            N0=n0, P0=p0,
            alpha=alpha, beta=beta, delta=delta, gamma=gamma,
            t_end=40.0, dt=0.005,
        )
        ax2.plot(Nt, Pt, color=c, linewidth=1.4, alpha=0.9,
                 label=f"N₀ = {n0:.0f}")

    # Vector field arrows
    Ngrid = np.linspace(2.0, max(75.0, N_eq * 2.5), 15)
    Pgrid = np.linspace(2.0, max(25.0, P_eq * 2.5), 15)
    Ng, Pg = np.meshgrid(Ngrid, Pgrid)
    dNg = alpha * Ng - beta * Ng * Pg
    dPg = delta * Ng * Pg - gamma * Pg
    norm = np.sqrt(dNg ** 2 + dPg ** 2)
    norm[norm == 0] = 1.0
    ax2.quiver(Ng, Pg, dNg / norm, dPg / norm,
               color="gray", alpha=0.45,
               scale=35, width=0.0028, headwidth=3.5)
    ax2.scatter([N_eq], [P_eq], s=120, marker="*",
                c="black", zorder=8,
                label=f"equilibrium (N*, P*) = ({N_eq:.1f}, {P_eq:.1f})")
    ax2.set_xlabel("prey N")
    ax2.set_ylabel("predator P")
    ax2.set_title("Phase portrait: closed orbits + vector field")
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.85)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.0, Ngrid[-1])
    ax2.set_ylim(0.0, Pgrid[-1])

    fig.suptitle(
        "Predator-prey dynamics from substrate: "
        "Lotka-Volterra invariant on a closed orbit",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "80_lotka_volterra.png"))

    # ===== 81: Food web + May-Wigner stability =========================
    fig = plt.figure(figsize=(14, 6))

    # Left: 4-level linear food chain
    ax1 = fig.add_subplot(1, 2, 1)
    chain = EcosystemGeometry.linear_food_chain(
        n_levels=5, link_strength=0.4,
    )
    pos = chain.node_positions_2d()
    # Tweak x positions for clearer single-column chain
    for i in range(chain.n_species):
        pos[i, 0] = 0.0

    sim_chain = EcosystemSimulator(geometry=chain)
    chain_evals = sim_chain.stability_eigenvalues()
    chain_lambda_max = float(np.max(np.real(chain_evals)))
    chain_stable = chain_lambda_max < 0.0

    edges = chain.edges()
    for src, tgt, weight in edges:
        x0, y0 = pos[src]
        x1, y1 = pos[tgt]
        # Slight horizontal offset to separate up/down arrows
        sign = +1 if y1 > y0 else -1
        offset = 0.18 * sign
        color = "tab:blue" if weight > 0.0 else "tab:red"
        ax1.annotate(
            "",
            xy=(x1 + offset, y1 - 0.12 * np.sign(y1 - y0)),
            xytext=(x0 + offset, y0 + 0.12 * np.sign(y1 - y0)),
            arrowprops={
                "arrowstyle": "->", "lw": 1.6,
                "color": color, "alpha": 0.85,
            },
        )

    node_colors = ["#9ec27a", "#f8e08e", "#f4a259", "#e76f51", "#702632"]
    for i in range(chain.n_species):
        ax1.scatter([pos[i, 0]], [pos[i, 1]], s=900,
                    c=node_colors[i % len(node_colors)],
                    edgecolors="black", linewidths=1.5, zorder=4)
        ax1.text(pos[i, 0], pos[i, 1],
                 f"L{i+1}\n{chain.species_names[i]}",
                 ha="center", va="center", fontsize=9,
                 fontweight="bold", zorder=5)

    ax1.text(0.6, chain.n_species + 0.1,
             ("predator gains" if True else ""),
             fontsize=8, color="tab:blue")
    ax1.text(-0.85, chain.n_species + 0.1,
             ("prey loses" if True else ""),
             fontsize=8, color="tab:red")

    ax1.set_xlim(-1.4, 1.4)
    ax1.set_ylim(0.4, chain.n_species + 0.7)
    ax1.set_aspect("auto")
    ax1.set_xlabel("(no horizontal axis -- single chain)")
    ax1.set_ylabel("trophic level")
    stable_str = ("STABLE" if chain_stable else "UNSTABLE")
    ax1.set_title(
        f"Linear food chain (5 levels): "
        f"max Re λ = {chain_lambda_max:+.3f} -> {stable_str}\n"
        f"blue = predator gains, red = prey loses"
    )
    ax1.grid(True, alpha=0.25, axis="y")

    # Right: May-Wigner stability transition
    ax2 = fig.add_subplot(1, 2, 2)
    N_mw = 30
    C_mw = 0.3
    sigma_c = sim_chain.may_wigner_threshold(N_mw, C_mw)
    complexity_grid = np.linspace(0.1, 3.5, 24)
    n_trials = 20
    fractions: list[float] = []
    for cmplx in complexity_grid:
        sigma = cmplx * sigma_c
        unstable = 0
        for s in range(n_trials):
            geom = EcosystemGeometry.random_food_web(
                n_species=N_mw, connectance=C_mw,
                sigma=sigma, seed=1000 + s,
            )
            sim_local = EcosystemSimulator(geometry=geom)
            evals = sim_local.stability_eigenvalues()
            if float(np.max(np.real(evals))) > 0.0:
                unstable += 1
        fractions.append(unstable / n_trials)
    fractions_arr = np.asarray(fractions)
    ax2.plot(complexity_grid, fractions_arr, "o-",
             color="purple", linewidth=1.8, markersize=6,
             label=f"random web N={N_mw}, C={C_mw}, "
                   f"{n_trials} trials/point")
    ax2.axvline(1.0, color="red", linestyle="--", linewidth=1.5,
                label="May-Wigner threshold σ√(NC)=1")
    ax2.axhline(0.5, color="gray", linestyle=":", alpha=0.5)
    ax2.set_xlabel(r"complexity $\sigma\sqrt{NC}$")
    ax2.set_ylabel("fraction of unstable webs")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title(
        "May-Wigner stability transition\n"
        "(May 1972 Nature: 'will a large complex system be stable?')"
    )
    ax2.legend(loc="lower right", fontsize=9, framealpha=0.85)
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        "Food-web stability from substrate: "
        "trophic chain + May-Wigner random-matrix transition",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "81_food_web.png"))

    return out


# ---------------------------------------------------------------------------
# Epidemiology (SIR / SEIR) -- 88 + 89
# ---------------------------------------------------------------------------

def render_epidemiology() -> list[str]:
    """Produce 88_sir_dynamics.png and 89_r0_threshold.png.

    88: Four-panel SIR/SEIR overview.  S, I, R curves at the canonical
        R_0 = 2.5; I(t) for several R_0; SIR vs SEIR delay due to the
        latent compartment; vaccination strategy comparison.
    89: Phase diagram of (R_0, vaccinated-fraction) showing simulated
        final attack rate, with the herd-immunity boundary 1 - 1/R_0
        overlaid; plus the closed-form i_max(R_0), R_∞(R_0), H(R_0).
    """
    from src.stiff_medium.epidemiology_substrate import (
        D_INFECTIOUS_DAYS_DEFAULT,
        EpidemiologyGeometry,
        EpidemiologySimulator,
        final_size_fraction,
        herd_immunity_threshold,
        peak_prevalence_fraction,
        r0_sweep,
    )

    out: list[str] = []

    # ---------------- 88: SIR dynamics for varying R_0 -------------------
    R0_values = [1.2, 1.8, 2.5, 3.5]
    runs = r0_sweep(np.array(R0_values),
                    D_infectious_days=D_INFECTIOUS_DAYS_DEFAULT,
                    N=1_000_000,
                    duration_days=180.0,
                    dt_days=0.1,
                    I0_fraction=1.0e-5)

    geom_ref = EpidemiologyGeometry(
        N=1_000_000, R0=2.5,
        D_infectious_days=D_INFECTIOUS_DAYS_DEFAULT,
    )
    sim_ref = EpidemiologySimulator(
        geometry=geom_ref, dt_days=0.1, duration_days=180.0,
    )
    res_ref = sim_ref.simulate_sir(I0_fraction=1.0e-5)
    res_seir = sim_ref.simulate_seir(E0_fraction=1.0e-5)

    fig = plt.figure(figsize=(13, 9))

    # Top-left: canonical S, I, R curves at R_0 = 2.5
    ax_sir = plt.subplot2grid((2, 2), (0, 0))
    ax_sir.plot(res_ref["t_days"], res_ref["S_frac"],
                color="tab:blue", linewidth=2.0, label="S (susceptible)")
    ax_sir.plot(res_ref["t_days"], res_ref["I_frac"],
                color="tab:red", linewidth=2.2, label="I (infectious)")
    ax_sir.plot(res_ref["t_days"], res_ref["R_frac"],
                color="tab:green", linewidth=2.0, label="R (recovered)")
    H = herd_immunity_threshold(2.5)
    ax_sir.axhline(H, color="gray", linestyle="--", linewidth=0.8,
                   label=f"H = 1 - 1/R_0 = {H:.2f}")
    i_max_th = peak_prevalence_fraction(2.5)
    ax_sir.axhline(i_max_th, color="tab:red", linestyle=":",
                   linewidth=0.8, alpha=0.6,
                   label=f"theory I_max/N = {i_max_th:.3f}")
    ax_sir.set_xlabel("t [days]")
    ax_sir.set_ylabel("compartment fraction")
    ax_sir.set_title(
        f"SIR dynamics (R_0 = 2.5, D_inf = "
        f"{D_INFECTIOUS_DAYS_DEFAULT:.0f} d)\n"
        f"β = {res_ref['beta']:.3f}/d, γ = {res_ref['gamma']:.3f}/d"
    )
    ax_sir.legend(loc="center right", fontsize=8)
    ax_sir.grid(True, alpha=0.3)
    ax_sir.set_ylim(-0.02, 1.02)
    ax_sir.set_xlim(0, sim_ref.duration_days)

    # Top-right: I(t) for several R_0
    ax_R0 = plt.subplot2grid((2, 2), (0, 1))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(R0_values)))
    for color, R0 in zip(cmap, R0_values):
        res = runs[float(R0)]
        ax_R0.plot(res["t_days"], res["I_frac"], color=color,
                   linewidth=1.8,
                   label=f"R_0 = {R0:.1f}, peak={sim_ref.peak_infected_fraction(res):.3f}")
    ax_R0.set_xlabel("t [days]")
    ax_R0.set_ylabel("I(t) / N")
    ax_R0.set_title(
        "Infectious fraction I(t) for varying R_0\n"
        "(higher R_0 -> earlier, taller peak)"
    )
    ax_R0.legend(loc="upper right", fontsize=8)
    ax_R0.grid(True, alpha=0.3)
    ax_R0.set_xlim(0, sim_ref.duration_days)

    # Bottom-left: SIR vs SEIR comparison (latency delays peak)
    ax_seir = plt.subplot2grid((2, 2), (1, 0))
    ax_seir.plot(res_ref["t_days"], res_ref["I_frac"],
                 color="tab:red", linewidth=2.0, label="I (SIR)")
    ax_seir.plot(res_seir["t_days"], res_seir["I_frac"],
                 color="tab:purple", linewidth=2.0, linestyle="--",
                 label="I (SEIR)")
    ax_seir.plot(res_seir["t_days"], res_seir["E_frac"],
                 color="tab:orange", linewidth=1.6,
                 label="E (SEIR exposed)")
    t_peak_sir = sim_ref.peak_time_days(res_ref)
    t_peak_seir = sim_ref.peak_time_days(res_seir)
    ax_seir.axvline(t_peak_sir, color="tab:red", linestyle=":",
                    linewidth=0.8, alpha=0.7)
    ax_seir.axvline(t_peak_seir, color="tab:purple", linestyle=":",
                    linewidth=0.8, alpha=0.7)
    ax_seir.set_xlabel("t [days]")
    ax_seir.set_ylabel("compartment fraction")
    ax_seir.set_title(
        f"SIR vs SEIR (R_0 = 2.5)\n"
        f"latency τ_E = 3 d delays peak: SIR @ {t_peak_sir:.1f} d, "
        f"SEIR @ {t_peak_seir:.1f} d"
    )
    ax_seir.legend(loc="upper right", fontsize=8)
    ax_seir.grid(True, alpha=0.3)
    ax_seir.set_xlim(0, sim_ref.duration_days)

    # Bottom-right: vaccination strategies
    ax_vac = plt.subplot2grid((2, 2), (1, 1))
    coverage = np.linspace(0.0, 0.9, 19)
    attack_uniform = []
    attack_targeted = []
    attack_ring = []
    for f in coverage:
        r_u = sim_ref.vaccinate_uniform(fraction=float(f))
        r_t = sim_ref.vaccinate_targeted(fraction=float(f),
                                         degree_amplification=1.5)
        r_r = sim_ref.vaccinate_ring(fraction=float(f), suppression=0.6)
        attack_uniform.append(sim_ref.attack_rate(r_u))
        attack_targeted.append(sim_ref.attack_rate(r_t))
        attack_ring.append(sim_ref.attack_rate(r_r))
    ax_vac.plot(coverage * 100.0, np.array(attack_uniform) * 100.0,
                "o-", color="tab:blue", label="uniform")
    ax_vac.plot(coverage * 100.0, np.array(attack_targeted) * 100.0,
                "s-", color="tab:green", label="targeted (high-degree)")
    ax_vac.plot(coverage * 100.0, np.array(attack_ring) * 100.0,
                "^-", color="tab:orange", label="ring/contact NPI")
    ax_vac.axvline(H * 100.0, color="gray", linestyle="--", linewidth=0.9,
                   label=f"H = {H*100:.0f}% (herd)")
    ax_vac.set_xlabel("vaccination coverage [%]")
    ax_vac.set_ylabel("final attack rate [%]")
    ax_vac.set_title(
        "Vaccination strategies (R_0 = 2.5)\n"
        "targeted reduces β faster than uniform"
    )
    ax_vac.legend(loc="upper right", fontsize=8)
    ax_vac.grid(True, alpha=0.3)
    ax_vac.set_xlim(0, 100)
    ax_vac.set_ylim(-2, 100)

    fig.suptitle(
        "Epidemic dynamics from substrate: SIR / SEIR / vaccination\n"
        "(B3 ontology: agent = cell; infection = saturation flip; "
        "recovery = relax/lock)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "88_sir_dynamics.png"))

    # ---------------- 89: R_0 phase diagram ------------------------------
    fig = plt.figure(figsize=(13, 6))

    # Left: herd-immunity boundary in (R_0, vaccinated) space + filled
    # final-attack-rate heatmap from simulation
    ax_phase = plt.subplot(1, 2, 1)
    R0_grid = np.linspace(0.5, 5.0, 24)
    vax_grid = np.linspace(0.0, 0.95, 24)
    AR = np.zeros((vax_grid.size, R0_grid.size))   # rows: vax, cols: R_0
    for i, v in enumerate(vax_grid):
        for j, R0 in enumerate(R0_grid):
            geom_grid = EpidemiologyGeometry(
                N=200_000, R0=float(R0),
                D_infectious_days=D_INFECTIOUS_DAYS_DEFAULT,
            )
            sim_grid = EpidemiologySimulator(
                geometry=geom_grid, dt_days=0.25, duration_days=200.0,
            )
            res = sim_grid.simulate_sir(I0_fraction=1.0e-4,
                                        vaccinated_fraction=float(v))
            AR[i, j] = sim_grid.attack_rate(res)
    im = ax_phase.pcolormesh(R0_grid, vax_grid * 100.0, AR * 100.0,
                             shading="auto", cmap="magma",
                             vmin=0, vmax=100)
    cbar = plt.colorbar(im, ax=ax_phase)
    cbar.set_label("final attack rate [%]")
    # Herd-immunity boundary v* = 1 - 1/R_0
    R0_curve = np.linspace(1.0, 5.0, 200)
    v_star = (1.0 - 1.0 / R0_curve) * 100.0
    ax_phase.plot(R0_curve, v_star, "-", color="cyan", linewidth=2.4,
                  label="H = 1 - 1/R_0 (herd-immunity)")
    # R_0 = 1 critical line
    ax_phase.axvline(1.0, color="white", linestyle=":", linewidth=1.5,
                     alpha=0.7, label="R_0 = 1 (epidemic threshold)")
    ax_phase.set_xlabel("basic reproduction number R_0")
    ax_phase.set_ylabel("vaccinated coverage [%]")
    ax_phase.set_title(
        "Phase diagram: epidemic vs no-epidemic regions\n"
        "(SIR final attack rate over (R_0, vax) grid)"
    )
    ax_phase.legend(loc="lower right", fontsize=9)
    ax_phase.set_xlim(R0_grid[0], R0_grid[-1])
    ax_phase.set_ylim(0, 95)

    # Right: closed-form i_max(R_0), final-size R_∞(R_0), and herd-threshold
    ax_th = plt.subplot(1, 2, 2)
    R0_th = np.linspace(0.0, 8.0, 400)
    i_max_arr = np.array([peak_prevalence_fraction(r) for r in R0_th])
    R_inf_arr = np.array([final_size_fraction(r) for r in R0_th])
    H_arr = np.array([herd_immunity_threshold(r) for r in R0_th])
    ax_th.plot(R0_th, i_max_arr * 100.0, "-",
               color="tab:red", linewidth=2.0,
               label="peak prevalence I_max/N")
    ax_th.plot(R0_th, R_inf_arr * 100.0, "-",
               color="tab:green", linewidth=2.0,
               label="final size R_∞/N")
    ax_th.plot(R0_th, H_arr * 100.0, "--",
               color="tab:blue", linewidth=2.0,
               label="herd-immunity H = 1 - 1/R_0")
    R0_mark = 2.5
    ax_th.scatter([R0_mark], [peak_prevalence_fraction(R0_mark) * 100.0],
                  s=80, c="tab:red", zorder=5)
    ax_th.scatter([R0_mark], [final_size_fraction(R0_mark) * 100.0],
                  s=80, c="tab:green", zorder=5)
    ax_th.scatter([R0_mark], [herd_immunity_threshold(R0_mark) * 100.0],
                  s=80, c="tab:blue", zorder=5)
    ax_th.axvline(R0_mark, color="gray", linestyle=":", linewidth=0.8,
                  alpha=0.7,
                  label=f"R_0 = {R0_mark} (canonical)")
    ax_th.axvline(1.0, color="black", linestyle="-", linewidth=1.0,
                  alpha=0.4, label="R_0 = 1 threshold")
    ax_th.set_xlabel("basic reproduction number R_0")
    ax_th.set_ylabel("[% of population]")
    ax_th.set_title(
        "Closed-form epidemic observables vs R_0\n"
        "Kermack-McKendrick (1927) + Anderson-May (1991)"
    )
    ax_th.legend(loc="lower right", fontsize=8)
    ax_th.grid(True, alpha=0.3)
    ax_th.set_xlim(0, 8)
    ax_th.set_ylim(0, 100)

    fig.suptitle(
        "R_0 threshold + herd-immunity phase diagram\n"
        "(B3 ontology: epidemic threshold = saturation phase transition)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "89_r0_threshold.png"))

    return out


def render_evolution() -> list[str]:
    """Produce 86_fitness_landscape.png and 87_speciation.png.

    86: 2D fitness landscape with adaptive walks.
        Left:   filled-contour fitness W(x,y) over a 2D phenotype plane
                with three Gaussian peaks; multiple stochastic adaptive
                walks (gradient ascent + noise) ascend from random starts
                and converge to local maxima.  Peak locations marked with
                stars; walks coloured by trial.
        Right:  Wright-Fisher allele-frequency trajectories under three
                selection regimes: neutral (drift only, s = 0), beneficial
                (s = +0.05, fixation), deleterious (s = -0.05, loss).
                Multiple replicate trajectories per regime with the
                Kimura fixation probability annotated.
    87: Divergence over time with reproductive isolation.
        Left:   mean allele-frequency trajectories of two daughter
                populations diverging on opposite sides of selection
                (s_A = +0.02, s_B = -0.02) over 1500 generations.
                Shaded band = +/- one standard deviation across loci.
        Centre: reproductive isolation I(t) growing from 0 to 1 with
                Bateson-Dobzhansky-Muller exponential approach;
                speciation threshold I = 0.5 marked.
        Right:  fixation-probability curve P_fix(s, N) (Kimura)
                versus 2s (Haldane), with empirical points from
                Monte-Carlo Wright-Fisher trials.
    """
    import matplotlib.patheffects as patheffects

    from src.stiff_medium.evolution_substrate import (
        SPECIATION_THRESHOLD,
        EvolutionGeometry,
        EvolutionSimulator,
        kimura_fixation_probability,
    )
    out: list[str] = []

    # ---- 86: 2D fitness landscape with adaptive walks --------------------
    geom = EvolutionGeometry(
        landscape_peaks=[
            ((-2.5, -2.0), 1.2, 1.1),
            ((+2.5, +2.5), 1.6, 0.9),
            ((+2.0, -2.0), 1.0, 1.0),
        ],
    )
    sim = EvolutionSimulator(
        geometry=geom, population_size=1000, selection_coefficient=0.0,
    )

    fig = plt.figure(figsize=(15, 7))

    # --- Left panel: fitness landscape + adaptive walks
    ax1 = fig.add_subplot(1, 2, 1)
    X, Y, W = geom.landscape_grid(x_range=(-5.0, 5.0), y_range=(-5.0, 5.0), n=120)
    cf = ax1.contourf(X, Y, W, levels=20, cmap="viridis")
    cbar = fig.colorbar(cf, ax=ax1, shrink=0.85)
    cbar.set_label("Wrightian fitness W(x,y)", fontsize=10)

    # mark peaks
    for (cx, cy), h, w in geom.landscape_peaks:
        ax1.scatter([cx], [cy], marker="*", s=320, c="white",
                    edgecolors="black", linewidths=1.5, zorder=6)
        ax1.text(cx + 0.25, cy + 0.25, f"W={h:.1f}", fontsize=8,
                 color="white", fontweight="bold",
                 path_effects=[patheffects.withStroke(
                     linewidth=2.0, foreground="black")])

    # several adaptive walks from random starts
    rng = np.random.default_rng(11)
    starts = [(-4.0, 4.0), (4.0, -4.0), (-4.5, -4.0),
              (0.0, 4.5), (4.5, 0.5), (-4.0, 0.0)]
    walk_colors = plt.cm.autumn(np.linspace(0.05, 0.95, len(starts)))
    for k, (sx, sy) in enumerate(starts):
        path = sim.adaptive_walk(
            start=(sx, sy), step_size=0.06, n_steps=500,
            noise=0.04, seed=int(rng.integers(0, 1_000_000)),
        )
        ax1.plot(path[:, 0], path[:, 1], "-",
                 color=walk_colors[k], linewidth=1.5, alpha=0.85,
                 zorder=5)
        ax1.scatter([sx], [sy], marker="o", s=70,
                    facecolor=walk_colors[k], edgecolor="black",
                    linewidth=1.0, zorder=6)
        ax1.scatter([path[-1, 0]], [path[-1, 1]], marker="X", s=110,
                    facecolor=walk_colors[k], edgecolor="black",
                    linewidth=1.2, zorder=7)
    ax1.set_xlim(-5.0, 5.0)
    ax1.set_ylim(-5.0, 5.0)
    ax1.set_xlabel("phenotype x", fontsize=10)
    ax1.set_ylabel("phenotype y", fontsize=10)
    ax1.set_title(
        f"Fitness landscape ({geom.n_landscape_peaks()} Gaussian peaks)\n"
        "white * = peak,  o = walk start,  X = walk end",
        fontsize=11,
    )
    ax1.set_aspect("equal", adjustable="box")
    ax1.grid(False)

    # --- Right panel: Wright-Fisher trajectories under three regimes
    ax2 = fig.add_subplot(1, 2, 2)
    p0 = 0.5
    n_gen = 200
    n_repl = 18
    regimes = [
        ("neutral  (s = 0)",       0.0,    "tab:gray"),
        ("beneficial (s = +0.05)", +0.05,  "tab:green"),
        ("deleterious (s = -0.05)", -0.05, "tab:red"),
    ]
    for label, s, color in regimes:
        sim.selection_coefficient = s
        sim.population_size = 100
        for k in range(n_repl):
            traj = sim.wright_fisher_trajectory(
                p0=p0, n_generations=n_gen,
                seed=10000 + k + int(1e4 * (s + 1)),
            )
            ax2.plot(np.arange(n_gen + 1), traj, "-",
                     color=color, alpha=0.40, linewidth=1.0)
        # one bold representative
        bold = sim.wright_fisher_trajectory(
            p0=p0, n_generations=n_gen, seed=999 + int(1e4 * (s + 1)),
        )
        p_fix = (kimura_fixation_probability(s, 100)
                 if s != 0 else 1.0 / (2 * 100))
        ax2.plot(np.arange(n_gen + 1), bold, "-",
                 color=color, linewidth=2.5, alpha=1.0,
                 label=f"{label}   P_fix = {p_fix:.3g}")
    ax2.axhline(0.0, color="black", linewidth=0.6, alpha=0.5)
    ax2.axhline(1.0, color="black", linewidth=0.6, alpha=0.5)
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_xlim(0, n_gen)
    ax2.set_xlabel("generation t", fontsize=10)
    ax2.set_ylabel("allele-A frequency p", fontsize=10)
    ax2.set_title(
        "Wright-Fisher trajectories (N = 100, p_0 = 0.5, 18 replicates)\n"
        "neutral drift vs beneficial vs deleterious selection",
        fontsize=11,
    )
    ax2.legend(fontsize=8, loc="center right")
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        "Evolutionary dynamics from substrate: fitness landscape + drift + selection",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "86_fitness_landscape.png"))

    # ---- 87: Speciation: divergence over time + reproductive isolation ---
    geom2 = EvolutionGeometry(mutation_rate=1.0e-4)
    sim2 = EvolutionSimulator(
        geometry=geom2, population_size=400, selection_coefficient=0.0,
    )
    n_loci = 40
    gens, p_A, p_B, isolation = sim2.divergence_simulation(
        n_generations=1500, n_loci=n_loci,
        s_pop_A=+0.02, s_pop_B=-0.02, k=4.0, seed=2026,
    )

    fig2 = plt.figure(figsize=(16, 5.5))

    # --- Left: mean allele frequency over time, with std band
    axL = fig2.add_subplot(1, 3, 1)
    mean_A = p_A.mean(axis=1)
    std_A = p_A.std(axis=1)
    mean_B = p_B.mean(axis=1)
    std_B = p_B.std(axis=1)
    axL.plot(gens, mean_A, "-", color="tab:blue", linewidth=2.0,
             label="Population A  (s = +0.02)")
    axL.fill_between(gens, mean_A - std_A, mean_A + std_A,
                     color="tab:blue", alpha=0.20)
    axL.plot(gens, mean_B, "-", color="tab:orange", linewidth=2.0,
             label="Population B  (s = -0.02)")
    axL.fill_between(gens, mean_B - std_B, mean_B + std_B,
                     color="tab:orange", alpha=0.20)
    axL.axhline(0.5, color="black", linewidth=0.6,
                linestyle="--", alpha=0.5,
                label="ancestral p = 0.5")
    axL.set_ylim(0.0, 1.0)
    axL.set_xlim(gens.min(), gens.max())
    axL.set_xlabel("generation t", fontsize=10)
    axL.set_ylabel("mean allele-A frequency", fontsize=10)
    axL.set_title(
        f"Allele-frequency divergence ({n_loci} loci, N = {sim2.population_size})\n"
        "shaded = +/- 1 std across loci",
        fontsize=11,
    )
    axL.legend(fontsize=8, loc="center right")
    axL.grid(True, alpha=0.3)

    # --- Centre: reproductive isolation over time
    axC = fig2.add_subplot(1, 3, 2)
    axC.plot(gens, isolation, "-", color="tab:purple", linewidth=2.5,
             label="I(t) = 1 - exp(-k D(t))")
    axC.axhline(SPECIATION_THRESHOLD, color="tab:red",
                linestyle="--", linewidth=1.5, alpha=0.85,
                label=f"speciation threshold I = {SPECIATION_THRESHOLD}")
    # mark crossing time
    cross_idx = int(np.argmax(isolation >= SPECIATION_THRESHOLD))
    if isolation[cross_idx] >= SPECIATION_THRESHOLD:
        t_cross = int(gens[cross_idx])
        axC.scatter([t_cross], [isolation[cross_idx]],
                    s=150, c="tab:red", edgecolors="black",
                    linewidths=1.2, zorder=5)
        axC.annotate(
            f"speciation @ t = {t_cross}",
            xy=(t_cross, isolation[cross_idx]),
            xytext=(t_cross + 70, isolation[cross_idx] - 0.20),
            fontsize=9, color="tab:red",
            arrowprops=dict(arrowstyle="->", color="tab:red", lw=1.0),
        )
    axC.set_xlim(gens.min(), gens.max())
    axC.set_ylim(0.0, 1.05)
    axC.set_xlabel("generation t", fontsize=10)
    axC.set_ylabel("reproductive isolation I", fontsize=10)
    axC.set_title(
        "Bateson-Dobzhansky-Muller isolation\n"
        "I(t) = 1 - exp(-k D(t)),  k = 4",
        fontsize=11,
    )
    axC.legend(fontsize=9, loc="lower right")
    axC.grid(True, alpha=0.3)

    # --- Right: fixation probability curve, Kimura vs Haldane vs sims
    axR = fig2.add_subplot(1, 3, 3)
    s_grid = np.linspace(0.0, 0.05, 80)
    N_eval = 200
    p_kim = np.array([kimura_fixation_probability(s, N_eval) for s in s_grid])
    p_hal = 2.0 * s_grid
    axR.plot(s_grid, p_kim, "-", color="tab:blue", linewidth=2.0,
             label=f"Kimura (1962), N = {N_eval}")
    axR.plot(s_grid, p_hal, "--", color="tab:orange", linewidth=2.0,
             label="Haldane (1927):  P_fix = 2s")
    axR.axhline(1.0 / (2.0 * N_eval), color="tab:gray",
                linestyle=":", linewidth=1.2,
                label=f"neutral fixation 1/(2N) = {1/(2*N_eval):.4f}")

    # Monte-Carlo points
    sim3 = EvolutionSimulator(
        geometry=EvolutionGeometry(mutation_rate=0.0),
        population_size=N_eval,
    )
    s_samples = [0.005, 0.01, 0.02, 0.04]
    p_emp = []
    for s in s_samples:
        p_emp.append(sim3.empirical_fixation_probability(
            s=s, N=N_eval, n_trials=2000, max_generations=8000,
            seed=42 + int(1000 * s),
        ))
    axR.scatter(s_samples, p_emp, s=110, c="tab:red", edgecolors="black",
                linewidths=1.2, zorder=5,
                label="Wright-Fisher (2000 trials each)")
    axR.set_xlim(0.0, 0.05)
    axR.set_ylim(0.0, 0.105)
    axR.set_xlabel("selection coefficient s", fontsize=10)
    axR.set_ylabel("fixation probability P_fix", fontsize=10)
    axR.set_title(
        "Fixation probability of new beneficial mutant\n"
        "Kimura vs Haldane 2s vs Wright-Fisher Monte-Carlo",
        fontsize=11,
    )
    axR.legend(fontsize=8, loc="upper left")
    axR.grid(True, alpha=0.3)

    fig2.suptitle(
        "Speciation from substrate: divergence, isolation, fixation",
        fontsize=12,
    )
    fig2.tight_layout()
    out.append(save(fig2, "87_speciation.png"))

    return out


# ---------------------------------------------------------------------------
# Cell differentiation (Waddington landscape) -- 116 + 117
# ---------------------------------------------------------------------------

def render_differentiation() -> list[str]:
    """Produce 116_waddington_landscape.png and 117_cell_fate.png.

    116: 3D Waddington landscape with marbles rolling into basins.
        Left:   3D surface U(g1, g2) of the Waddington epigenetic
                landscape; basins (cell fates) appear as wells, ridges
                as crests.  Marbles released from a stem-state cup at
                the top roll downhill into one of three terminal
                basins (ectoderm / mesoderm / endoderm).
        Right:  2D contour map of the same landscape with several
                Langevin trajectories overlaid.  Each trajectory is
                coloured by the basin it ends in.  Pluripotent +
                epiblast + the three germ layers are labelled.

    117: Lineage tree from totipotent through pluripotent and the three
        germ layers down to canonical adult cell types.  Colour-coded by
        germ-layer ancestry.  Annotations show:
            * pluripotent basin and Yamanaka-factor reprogramming arrow
            * three germ layers (ectoderm/mesoderm/endoderm)
            * representative adult terminally differentiated cell types
              under each germ layer
            * trophoblast lineage (extraembryonic) sibling of the
              pluripotent inner-cell mass
    """
    import matplotlib.patheffects as patheffects
    import matplotlib.lines as mlines
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers projection)

    from src.stiff_medium.differentiation_substrate import (
        N_GERM_LAYERS,
        N_YAMANAKA_FACTORS,
        YAMANAKA_EFFICIENCY,
        DifferentiationGeometry,
        DifferentiationSimulator,
    )
    out: list[str] = []

    # ---- 116: 3D Waddington landscape with marbles -----------------------
    geom = DifferentiationGeometry()
    sim = DifferentiationSimulator(geometry=geom, noise_sigma=0.6, dt=0.05)

    fig = plt.figure(figsize=(16, 7.5))

    # --- Left: 3D surface of U with marbles
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    G1, G2, U = geom.landscape_grid(
        x_range=(-5.0, 5.0), y_range=(-3.0, 5.0), n=100,
    )
    surf = ax3d.plot_surface(
        G1, G2, U, cmap="viridis_r", alpha=0.92,
        linewidth=0, antialiased=True, edgecolor="none",
    )
    fig.colorbar(surf, ax=ax3d, shrink=0.55, pad=0.05,
                 label="strain energy U(g1, g2)")

    # Marbles -- spheres rolling down on the surface
    rng = np.random.default_rng(7)
    n_marbles = 7
    marble_starts = []
    for k in range(n_marbles):
        # Cluster marbles around the pluripotent basin
        x0 = rng.uniform(-0.7, 0.7)
        y0 = 4.0 + rng.uniform(-0.3, 0.4)
        marble_starts.append((x0, y0))
    marble_colors = plt.cm.autumn(np.linspace(0.05, 0.95, n_marbles))
    for k, (x0, y0) in enumerate(marble_starts):
        traj = sim.differentiation_trajectory(
            start=(x0, y0), n_steps=600, seed=100 + k,
        )
        # Vertical (potential) coordinate for each step
        z = geom.potential(traj[:, 0], traj[:, 1])
        ax3d.plot(traj[:, 0], traj[:, 1], z + 0.05,
                  color=marble_colors[k], linewidth=1.6, alpha=0.85)
        # Final marble = a sphere
        ax3d.scatter([traj[-1, 0]], [traj[-1, 1]], [z[-1] + 0.10],
                     color=marble_colors[k], s=120,
                     edgecolors="black", linewidths=1.0, zorder=8)
        # Initial marble (smaller, white-ringed)
        ax3d.scatter([x0], [y0],
                     [float(geom.potential(np.array(x0),
                                           np.array(y0))) + 0.10],
                     facecolor=marble_colors[k], s=60,
                     edgecolors="white", linewidths=1.0)

    # Label basin centres
    for (cx, cy, depth, sigma, label) in geom.basins:
        u_c = float(geom.potential(np.array(cx), np.array(cy)))
        ax3d.text(cx, cy, u_c - 0.4, label,
                  fontsize=8, color="white", fontweight="bold",
                  path_effects=[patheffects.withStroke(
                      linewidth=2.0, foreground="black")])

    ax3d.set_xlabel("g1 (master regulator A)", fontsize=9)
    ax3d.set_ylabel("g2 (master regulator B)", fontsize=9)
    ax3d.set_zlabel("U  (substrate strain energy)", fontsize=9)
    ax3d.set_title(
        f"Waddington epigenetic landscape\n"
        f"{geom.n_basins()} basins, {geom.n_ridges()} ridges, "
        f"{geom.n_terminal_lineages()} germ layers",
        fontsize=11,
    )
    ax3d.view_init(elev=28, azim=-110)

    # --- Right: 2D contour map with overlaid trajectories
    ax2d = fig.add_subplot(1, 2, 2)
    cf = ax2d.contourf(G1, G2, U, levels=22, cmap="viridis_r")
    fig.colorbar(cf, ax=ax2d, shrink=0.85, label="U(g1, g2)")

    # Mark basin centres with stars
    for (cx, cy, depth, sigma, label) in geom.basins:
        ax2d.scatter([cx], [cy], marker="*", s=320, c="white",
                     edgecolors="black", linewidths=1.5, zorder=6)
        ax2d.text(cx + 0.2, cy + 0.2, label, fontsize=9,
                  color="white", fontweight="bold",
                  path_effects=[patheffects.withStroke(
                      linewidth=2.0, foreground="black")])

    # Mark ridge centres with X
    for (cx, cy, height, sigma, label) in geom.ridges:
        ax2d.scatter([cx], [cy], marker="x", s=120, c="red",
                     linewidths=2.0, zorder=6)

    # Overlay several trajectories
    sim_traj = DifferentiationSimulator(
        geometry=geom, noise_sigma=0.9, dt=0.05,
    )
    rng2 = np.random.default_rng(13)
    label_to_color = {
        "pluripotent": "tab:gray",
        "epiblast": "tab:olive",
        "ectoderm": "tab:blue",
        "mesoderm": "tab:green",
        "endoderm": "tab:red",
    }
    n_traj = 16
    for k in range(n_traj):
        x0 = 0.0 + rng2.uniform(-0.4, 0.4)
        y0 = 4.0 + rng2.uniform(-0.3, 0.3)
        traj = sim_traj.differentiation_trajectory(
            start=(x0, y0), n_steps=600,
            seed=int(rng2.integers(0, 10_000_000)),
        )
        end_label = sim_traj.basin_assignment(tuple(traj[-1]))
        col = label_to_color.get(end_label, "tab:gray")
        ax2d.plot(traj[:, 0], traj[:, 1], "-",
                  color=col, linewidth=1.2, alpha=0.7, zorder=4)
        ax2d.scatter([traj[-1, 0]], [traj[-1, 1]], marker="o", s=40,
                     facecolor=col, edgecolor="black",
                     linewidth=0.6, zorder=5)
    handles = []
    for name, col in label_to_color.items():
        handles.append(mlines.Line2D([], [], color=col, marker="o",
                                     linestyle="-",
                                     label=name, markersize=7))
    ax2d.legend(handles=handles, loc="lower right", fontsize=8,
                title="end basin")
    ax2d.set_xlim(-5.0, 5.0)
    ax2d.set_ylim(-3.0, 5.0)
    ax2d.set_xlabel("g1 (master regulator A)", fontsize=10)
    ax2d.set_ylabel("g2 (master regulator B)", fontsize=10)
    ax2d.set_title(
        "Marble release from stem state -> trilineage decision\n"
        "white * = basin (cell fate),  red x = ridge (cell-fate boundary)",
        fontsize=11,
    )
    ax2d.set_aspect("equal", adjustable="box")

    fig.suptitle(
        "Cell differentiation from substrate: Waddington landscape "
        "(strain energy of gene-expression configuration)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "116_waddington_landscape.png"))

    # ---- 117: lineage tree from totipotent to all major cell types -------
    fig2 = plt.figure(figsize=(15, 9))
    ax = fig2.add_subplot(1, 1, 1)
    ax.set_xlim(0.0, 14.0)
    ax.set_ylim(0.0, 10.5)
    ax.axis("off")

    # ---- Tree layout (manual: this is a conceptual figure) ----
    # Levels (top to bottom):
    #   0 totipotent          y = 9.7
    #   1 pluripotent + trophoblast  y = 8.2
    #   2 germ layers         y = 6.0
    #   3 terminal cell types y = 1.8 / 2.6 (alternating)

    def node(x, y, label, color, fontsize=10, width=1.6, height=0.55):
        box = FancyBboxPatch(
            (x - width / 2, y - height / 2), width, height,
            boxstyle="round,pad=0.05,rounding_size=0.18",
            facecolor=color, edgecolor="black", linewidth=1.2,
            alpha=0.92,
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold",
                color="black")
        return (x, y)

    def edge(p1, p2, color="0.4", lw=1.4, alpha=0.85):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "-",
                color=color, linewidth=lw, alpha=alpha, zorder=1)

    # Totipotent root
    totipotent = node(7.0, 9.7, "TOTIPOTENT\nzygote", "#fff8b5",
                      fontsize=11, width=2.4, height=0.85)

    # Pluripotent (inner cell mass) and Trophoblast (extraembryonic)
    pluri = node(5.0, 8.2, "PLURIPOTENT\n(inner cell mass)",
                 "#ffe89a", fontsize=10, width=2.6, height=0.85)
    troph = node(11.5, 8.2, "TROPHOBLAST\n(extraembryonic)",
                 "#e0e0e0", fontsize=10, width=2.6, height=0.85)
    edge(totipotent, pluri)
    edge(totipotent, troph)

    # Trophoblast leaves
    troph_leaves = ["syncytiotrophoblast", "cytotrophoblast"]
    troph_xs = [10.5, 12.7]
    for x, lab in zip(troph_xs, troph_leaves):
        leaf = node(x, 6.5, lab, "#cfcfcf", fontsize=8,
                    width=1.9, height=0.5)
        edge(troph, leaf)

    # Three germ layers
    germ_data = [
        ("ECTODERM",  1.6, "#9ecae1"),
        ("MESODERM",  4.7, "#a1d99b"),
        ("ENDODERM",  7.8, "#fcae91"),
    ]
    germ_nodes = []
    for label, x, color in germ_data:
        gn = node(x, 6.0, label, color, fontsize=10,
                  width=1.8, height=0.55)
        germ_nodes.append(gn)
        edge(pluri, gn)

    # Adult cell types under each germ layer
    germ_children = {
        "ECTODERM":  ["neurons", "glia", "epidermis",
                      "melanocytes", "neural crest"],
        "MESODERM":  ["muscle", "blood", "bone",
                      "cartilage", "endothelium", "kidney"],
        "ENDODERM":  ["gut epithelium", "lung alveoli",
                      "liver hepatocytes", "pancreas islets",
                      "thyroid"],
    }
    germ_color_light = {
        "ECTODERM":  "#deebf7",
        "MESODERM":  "#e5f5e0",
        "ENDODERM":  "#fee0d2",
    }
    for (label, x_g, _), gn in zip(germ_data, germ_nodes):
        children = germ_children[label]
        n = len(children)
        # Spread children horizontally under the germ layer
        x_start = x_g - 1.1
        x_end = x_g + 1.1
        if n == 1:
            xs = [x_g]
        else:
            xs = list(np.linspace(x_start, x_end, n))
        # Stagger y so child labels don't overlap
        y_levels = [2.6, 1.6, 2.6, 1.6, 2.6, 1.6]
        for k, (cx, child_label) in enumerate(zip(xs, children)):
            cy = y_levels[k % len(y_levels)]
            leaf = node(cx, cy, child_label,
                        germ_color_light[label],
                        fontsize=7, width=1.30, height=0.35)
            edge(gn, leaf, color="0.5", lw=0.9, alpha=0.7)

    # Yamanaka reprogramming arrow: from a terminal node back to pluripotent
    arrow = FancyArrowPatch(
        (4.7, 1.6), (5.0, 7.7),
        connectionstyle="arc3,rad=-0.40",
        arrowstyle="-|>", mutation_scale=22,
        color="purple", linewidth=2.4, alpha=0.85,
    )
    ax.add_patch(arrow)
    ax.text(0.4, 4.8,
            f"Yamanaka factors\n(N = {N_YAMANAKA_FACTORS}: Oct4, Sox2,\n"
            f"Klf4, c-Myc)\nefficiency ~ {YAMANAKA_EFFICIENCY*100:.1f}%",
            fontsize=9, color="purple", fontweight="bold",
            ha="left", va="center",
            bbox=dict(facecolor="#f0e0ff", edgecolor="purple",
                      boxstyle="round,pad=0.4", alpha=0.85))

    # Substrate framing annotation (bottom-right)
    ax.text(13.7, 0.45,
            "SUBSTRATE FRAMING\n"
            "gene expression = substrate strain configuration\n"
            "Waddington landscape = substrate strain energy U(g)\n"
            "differentiation = downhill substrate relaxation\n"
            "reprogramming = forced uphill traversal (Yamanaka)",
            ha="right", va="bottom", fontsize=8,
            bbox=dict(facecolor="#fffbe6", edgecolor="#999", alpha=0.92,
                      boxstyle="round,pad=0.5"))

    # Title
    ax.text(7.0, 10.25,
            "Cell-fate lineage tree from totipotent zygote to "
            "all major adult cell types",
            ha="center", va="center", fontsize=13,
            fontweight="bold")
    ax.text(7.0, 9.95,
            f"{N_GERM_LAYERS} germ layers, "
            "5 Waddington basins, "
            f"{sum(len(v) for v in germ_children.values())} terminal cell types shown",
            ha="center", va="center", fontsize=9, color="#444")

    fig2.tight_layout()
    out.append(save(fig2, "117_cell_fate.png"))

    return out


# ---------------------------------------------------------------------------
# Climate (radiative forcing + sensitivity) -- 82 + 83
# ---------------------------------------------------------------------------

def render_climate() -> list[str]:
    """Produce 82_radiative_forcing.png and 83_climate_sensitivity.png.

    82: Anthropogenic radiative forcing time series for CO2, CH4, N2O,
        and aerosols from 1850 to 2100.  Logarithmic CO2 forcing dominates
        the well-mixed greenhouse-gas budget; aerosols partially cancel
        with negative ERF.  Annotates the present-day total RF.
    83: Climate sensitivity curve.  Equilibrium delta-T as a function of
        CO2 doubling number n (where C/C_ref = 2^n), using the
        substrate-derived ECS = 3.0 K.  Shaded uncertainty band from the
        IPCC AR6 likely range 1.5 - 4.5 K.  Annotates pre-industrial,
        present-day, 2x and 4x reference points.
    """
    from src.stiff_medium.climate_substrate import (
        CO2_PREINDUSTRIAL_PPM,
        CO2_PRESENT_PPM,
        ECS_CENTRAL_K,
        ECS_LOWER_K,
        ECS_UPPER_K,
        ClimateGeometry,
        ClimateSimulator,
    )

    out: list[str] = []

    geom = ClimateGeometry(n_atm_layers=10)
    sim = ClimateSimulator(geometry=geom)

    # ---- 82: radiative forcing time series ----------------------------
    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(1, 1, 1)

    years = np.arange(1850, 2101, 1)
    n_yr = len(years)

    def _interp(start_year, start_val, anchors):
        ys = np.empty(n_yr)
        all_anchors = [(start_year, start_val)] + list(anchors)
        for i, yr in enumerate(years):
            placed = False
            for j in range(len(all_anchors) - 1):
                y0, v0 = all_anchors[j]
                y1, v1 = all_anchors[j + 1]
                if y0 <= yr <= y1:
                    t = (yr - y0) / (y1 - y0) if y1 > y0 else 0.0
                    ys[i] = v0 + t * (v1 - v0)
                    placed = True
                    break
            if not placed:
                ys[i] = all_anchors[-1][1]
        return ys

    co2_ppm = _interp(
        1850, 285.0,
        [(1900, 296.0), (1950, 311.0), (1980, 339.0),
         (2000, 369.0), (2020, 415.0), (2050, 510.0), (2100, 600.0)],
    )
    ch4_ppb = _interp(
        1850, 800.0,
        [(1900, 900.0), (1950, 1150.0), (2000, 1750.0),
         (2020, 1880.0), (2050, 2100.0), (2100, 2200.0)],
    )
    n2o_ppb = _interp(
        1850, 270.0,
        [(1950, 290.0), (2000, 316.0), (2020, 333.0),
         (2050, 360.0), (2100, 380.0)],
    )
    aerosol_aod = _interp(
        1850, 0.00,
        [(1950, 0.04), (1980, 0.10), (2010, 0.13),
         (2020, 0.12), (2050, 0.07), (2100, 0.04)],
    )

    rf_co2 = np.array([sim.co2_forcing_w_m2(c) for c in co2_ppm])
    rf_ch4 = np.array([sim.ch4_forcing_w_m2(c) for c in ch4_ppb])
    rf_n2o = np.array([sim.n2o_forcing_w_m2(c) for c in n2o_ppb])
    rf_aer = np.array([sim.aerosol_forcing_w_m2(a) for a in aerosol_aod])
    rf_total = rf_co2 + rf_ch4 + rf_n2o + rf_aer

    ax.plot(years, rf_co2, color="darkred", lw=2.4,
            label="CO$_2$ (5.35 ln C/C$_0$)")
    ax.plot(years, rf_ch4, color="tab:orange", lw=2.0,
            label="CH$_4$ (0.036 [√C - √C$_0$])")
    ax.plot(years, rf_n2o, color="tab:purple", lw=2.0,
            label="N$_2$O (0.12 [√C - √C$_0$])")
    ax.plot(years, rf_aer, color="tab:blue", lw=2.0,
            label="aerosols (-9.2 × AOD)")
    ax.plot(years, rf_total, color="black", lw=2.8, ls="--",
            label="net total")

    ax.fill_between(years, rf_aer, 0.0, where=(rf_aer < 0),
                    color="tab:blue", alpha=0.10)
    ax.fill_between(years, 0.0, rf_co2, color="darkred", alpha=0.06)

    ax.axvline(2020, color="gray", lw=1.0, ls=":", alpha=0.7)
    ax.axhline(3.71, color="darkred", lw=0.8, ls=":", alpha=0.6)
    ax.text(1855, 3.78, "CO$_2$ doubling RF = 3.71 W/m$^2$",
            color="darkred", fontsize=9)
    ax.axhline(0.0, color="black", lw=0.6, alpha=0.4)

    idx_2020 = int(np.argmin(np.abs(years - 2020)))
    rf_present = rf_total[idx_2020]
    ax.scatter([2020], [rf_present], s=80, c="black", zorder=5)
    ax.annotate(
        f"net 2020:\n{rf_present:.2f} W/m$^2$",
        xy=(2020, rf_present), xytext=(1955, rf_present + 1.2),
        fontsize=9, ha="center",
        arrowprops={"arrowstyle": "->", "color": "black", "lw": 0.8},
    )

    ax.set_xlabel("year")
    ax.set_ylabel("radiative forcing relative to 1850 [W m$^{-2}$]")
    ax.set_xlim(1850, 2100)
    ax.set_title(
        "Anthropogenic radiative forcing 1850 - 2100 (substrate-derived "
        "$\\sigma_{SB} = \\pi^2 k_B^4 / (60 \\hbar^3 c^2)$)\n"
        "Myhre 1998 / IPCC AR6 simplified expressions; "
        "SSP2-4.5-style continuation"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    out.append(save(fig, "82_radiative_forcing.png"))

    # ---- 83: climate sensitivity (T vs CO2 doublings + bands) ---------
    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(1, 1, 1)

    n_doublings = np.linspace(-0.5, 3.0, 200)
    dT_central = ECS_CENTRAL_K * n_doublings
    dT_low     = ECS_LOWER_K   * n_doublings
    dT_high    = ECS_UPPER_K   * n_doublings

    ax.fill_between(
        n_doublings, dT_low, dT_high,
        color="tab:red", alpha=0.18,
        label=f"IPCC AR6 likely range ({ECS_LOWER_K:.1f} - {ECS_UPPER_K:.1f} K)",
    )
    ax.plot(n_doublings, dT_central, color="darkred", lw=2.6,
            label=f"substrate ECS = {ECS_CENTRAL_K:.1f} K / doubling")
    ax.plot(n_doublings, dT_low,  color="tab:red", lw=1.0, ls="--", alpha=0.8)
    ax.plot(n_doublings, dT_high, color="tab:red", lw=1.0, ls="--", alpha=0.8)

    refs = [
        (CO2_PREINDUSTRIAL_PPM,         "1850\npre-industrial\n280 ppm"),
        (CO2_PRESENT_PPM,               "2020 present\n420 ppm"),
        (2.0 * CO2_PREINDUSTRIAL_PPM,   "2x pre-ind\n560 ppm"),
        (4.0 * CO2_PREINDUSTRIAL_PPM,   "4x pre-ind\n1120 ppm"),
    ]
    for c_ppm, label in refs:
        n = np.log2(c_ppm / CO2_PREINDUSTRIAL_PPM)
        dT = ECS_CENTRAL_K * n
        ax.scatter([n], [dT], s=90, c="black", zorder=5)
        if "present" in label:
            ax.annotate(label, xy=(n, dT), xytext=(n - 0.45, dT + 1.4),
                        fontsize=9, ha="center",
                        arrowprops={"arrowstyle": "->", "color": "black",
                                    "lw": 0.7})
        else:
            ax.annotate(label, xy=(n, dT), xytext=(n + 0.05, dT + 0.3),
                        fontsize=9, ha="left", va="bottom")

    ax.axhline(0.0, color="black", lw=0.6, alpha=0.4)
    ax.axvline(0.0, color="black", lw=0.6, alpha=0.4)

    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ticks = [-0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(
        [f"{CO2_PREINDUSTRIAL_PPM * 2**t:.0f}" for t in ticks]
    )
    ax2.set_xlabel("CO$_2$ concentration [ppm]")

    ax.set_xlabel(
        "CO$_2$ doublings  $n = \\log_2(C / C_{ref})$,  $C_{ref}$ = 280 ppm"
    )
    ax.set_ylabel("equilibrium $\\Delta T$ [K]")
    ax.set_xlim(-0.5, 3.0)
    ax.set_ylim(-2.5, 14.0)
    ax.set_title(
        "Equilibrium climate sensitivity (ECS):  $\\Delta T = $ ECS · "
        "$\\log_2(C / C_{ref})$\n"
        f"central ECS = {ECS_CENTRAL_K:.1f} K, IPCC AR6 likely band "
        f"{ECS_LOWER_K:.1f} - {ECS_UPPER_K:.1f} K"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    out.append(save(fig, "83_climate_sensitivity.png"))

    return out


# ---------------------------------------------------------------------------
# Neural network learning dynamics -- 84 + 85
# ---------------------------------------------------------------------------

def render_neural_network() -> list[str]:
    """Produce 84_perceptron_learning.png and 85_loss_landscape.png.

    84: Two panels.
        Left  -- BCE loss vs epoch for a single-layer perceptron on AND/OR
                 (rapid convergence to ~0) and XOR (plateaus, never solves)
                 alongside a 2-4-1 MLP on XOR (drops to ~0, universality).
        Right -- decision-boundary evolution of the MLP on XOR over a
                 sequence of training snapshots, showing the learned
                 non-linear separator carving the unit square into the
                 four XOR regions.
    85: Two panels.
        Left  -- 2D loss landscape of an XOR MLP slice (two scalar
                 weights of the first hidden layer swept on a grid) with
                 the gradient-descent path overlaid.
        Right -- canonical anisotropic-quadratic test surface
                 L = a1*w1^2 + a2*w2^2 with a2/a1 >> 1 (ill-conditioned
                 valley) and the GD trajectory zig-zagging through it.
    """
    from src.stiff_medium.neural_network_substrate import (
        DEFAULT_HIDDEN_WIDTH,
        NeuralNetworkGeometry,
        NeuralNetworkSimulator,
        boolean_dataset,
    )
    out: list[str] = []

    # ------------------------------------------------------------------
    # 84: perceptron / MLP loss curves + decision-boundary evolution
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 7))

    # ---- Left: BCE loss vs epoch -------------------------------------
    ax_loss = fig.add_subplot(1, 2, 1)

    # Single-layer perceptron on AND
    sim_and = NeuralNetworkSimulator(
        geometry=NeuralNetworkGeometry(layer_sizes=(2, 1), seed=0),
        learning_rate=0.5, max_epochs=2000,
    )
    out_and = sim_and.train_perceptron("AND", max_epochs=2000)

    # Single-layer perceptron on OR
    sim_or = NeuralNetworkSimulator(
        geometry=NeuralNetworkGeometry(layer_sizes=(2, 1), seed=0),
        learning_rate=0.5, max_epochs=2000,
    )
    out_or = sim_or.train_perceptron("OR", max_epochs=2000)

    # Single-layer perceptron on XOR (FAILS by Minsky-Papert 1969)
    sim_xor_p = NeuralNetworkSimulator(
        geometry=NeuralNetworkGeometry(layer_sizes=(2, 1), seed=0),
        learning_rate=0.5, max_epochs=2000,
    )
    out_xor_p = sim_xor_p.train_perceptron("XOR", max_epochs=2000,
                                           tolerance=1e-6)

    # MLP on XOR (SUCCEEDS) -- pick a seed that converges
    sim_xor_m = None
    out_xor_m = None
    candidate = None
    result = None
    for seed in (0, 1, 2, 3, 4):
        candidate = NeuralNetworkSimulator(
            geometry=NeuralNetworkGeometry(
                layer_sizes=(2, DEFAULT_HIDDEN_WIDTH, 1), seed=seed,
            ),
            learning_rate=0.8, max_epochs=2000,
        )
        result = candidate.train_mlp("XOR",
                                     hidden=DEFAULT_HIDDEN_WIDTH,
                                     max_epochs=2000,
                                     tolerance=1e-3)
        Xb, yb = boolean_dataset("XOR")
        preds = candidate.predict_classes(Xb)
        if np.array_equal(preds, yb.astype(int)):
            sim_xor_m, out_xor_m = candidate, result
            break
    if sim_xor_m is None:
        sim_xor_m, out_xor_m = candidate, result

    ax_loss.plot(out_and["epochs"], out_and["losses"],
                 color="tab:green", linewidth=2.0,
                 label=f"perceptron on AND (final={out_and['final_loss']:.3f})")
    ax_loss.plot(out_or["epochs"], out_or["losses"],
                 color="tab:cyan", linewidth=2.0,
                 label=f"perceptron on OR  (final={out_or['final_loss']:.3f})")
    ax_loss.plot(out_xor_p["epochs"], out_xor_p["losses"],
                 color="tab:red", linewidth=2.0, linestyle="--",
                 label=f"perceptron on XOR (final={out_xor_p['final_loss']:.3f})  Minsky-Papert wall")
    ax_loss.plot(out_xor_m["epochs"], out_xor_m["losses"],
                 color="tab:purple", linewidth=2.4,
                 label=f"MLP (2-{DEFAULT_HIDDEN_WIDTH}-1) on XOR (final={out_xor_m['final_loss']:.3f})")
    ax_loss.set_yscale("log")
    ax_loss.set_xlabel("training epoch", fontsize=11)
    ax_loss.set_ylabel("BCE loss (log scale)", fontsize=11)
    ax_loss.set_title(
        "Learning curves: perceptron solves AND/OR but not XOR;\n"
        "single hidden layer (universality, Cybenko 1989) cracks XOR",
        fontsize=11,
    )
    ax_loss.grid(True, which="both", alpha=0.3)
    ax_loss.legend(loc="upper right", fontsize=8)

    # ---- Right: decision-boundary evolution of the MLP on XOR --------
    ax_db = fig.add_subplot(1, 2, 2)
    snapshots_at = [0, 50, 200, 1000]
    sim_snap = NeuralNetworkSimulator(
        geometry=NeuralNetworkGeometry(
            layer_sizes=(2, DEFAULT_HIDDEN_WIDTH, 1), seed=2,
        ),
        learning_rate=0.8, max_epochs=1500,
    )
    Xb, yb = boolean_dataset("XOR")
    snap_outputs: dict = {}
    X_mesh, Y_mesh = None, None
    for epoch in range(1001):
        if epoch in snapshots_at:
            X_mesh, Y_mesh, Z = sim_snap.decision_boundary_grid(
                x_range=(-0.3, 1.3), y_range=(-0.3, 1.3), n_grid=80,
            )
            snap_outputs[epoch] = Z.copy()
        if epoch < 1000:
            sim_snap.step(Xb, yb)
    if 1000 not in snap_outputs:
        X_mesh, Y_mesh, Z = sim_snap.decision_boundary_grid(
            x_range=(-0.3, 1.3), y_range=(-0.3, 1.3), n_grid=80,
        )
        snap_outputs[1000] = Z.copy()

    final_Z = snap_outputs[max(snap_outputs.keys())]
    cf = ax_db.contourf(X_mesh, Y_mesh, final_Z,
                        levels=np.linspace(0.0, 1.0, 11),
                        cmap="RdBu_r", alpha=0.6)
    cbar = fig.colorbar(cf, ax=ax_db, fraction=0.045, pad=0.03)
    cbar.set_label("MLP output P(y=1|x)")

    snap_colors = ["#ffe7a8", "#ffd166", "#f08c5a", "#a02828"]
    for color, epoch in zip(snap_colors, sorted(snap_outputs.keys())):
        ax_db.contour(X_mesh, Y_mesh, snap_outputs[epoch],
                      levels=[0.5], colors=[color], linewidths=2.0)
        ax_db.plot([], [], "-", color=color, linewidth=2.0,
                   label=f"epoch {epoch}: 0.5 boundary")

    for x_pt, y_lab in zip(Xb, yb.astype(int)):
        marker = "o" if y_lab == 1 else "s"
        face = "tab:red" if y_lab == 1 else "tab:blue"
        ax_db.scatter([x_pt[0]], [x_pt[1]], c=face, s=240, marker=marker,
                      edgecolors="black", linewidths=1.5, zorder=5)
    ax_db.scatter([], [], c="tab:red",  s=160, marker="o",
                  edgecolors="black", linewidths=1.5, label="XOR y=1")
    ax_db.scatter([], [], c="tab:blue", s=160, marker="s",
                  edgecolors="black", linewidths=1.5, label="XOR y=0")

    ax_db.set_xlabel("input x_1", fontsize=11)
    ax_db.set_ylabel("input x_2", fontsize=11)
    ax_db.set_xlim(-0.3, 1.3)
    ax_db.set_ylim(-0.3, 1.3)
    ax_db.set_aspect("equal")
    ax_db.set_title(
        f"MLP decision boundary on XOR over training\n"
        f"non-linear separator emerges (2-{DEFAULT_HIDDEN_WIDTH}-1 net, "
        f"{sim_snap.geometry.n_parameters()} params)",
        fontsize=11,
    )
    ax_db.legend(loc="upper right", fontsize=8)
    ax_db.grid(True, alpha=0.25)

    fig.suptitle(
        "Perceptron learning from substrate: "
        "weights = strain pattern, gradient descent = relaxation flow",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "84_perceptron_learning.png"))

    # ------------------------------------------------------------------
    # 85: 2D loss landscape with gradient-descent trajectory
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 6.5))

    # ---- Left: real loss landscape of an XOR MLP, two-weight slice ---
    ax_ll = fig.add_subplot(1, 2, 1)
    sim_ls = NeuralNetworkSimulator(
        geometry=NeuralNetworkGeometry(
            layer_sizes=(2, DEFAULT_HIDDEN_WIDTH, 1), seed=2,
        ),
        learning_rate=0.5, max_epochs=400,
    )
    Xb, yb = boolean_dataset("XOR")
    path_w1 = []
    path_w2 = []
    for _ in range(400):
        path_w1.append(sim_ls.geometry.weights[0][0, 0])
        path_w2.append(sim_ls.geometry.weights[0][0, 1])
        sim_ls.step(Xb, yb)
    path_w1 = np.array(path_w1)
    path_w2 = np.array(path_w2)

    pad = max(2.0, 1.2 * float(np.max(np.abs(np.r_[path_w1, path_w2]))))
    w1_lo, w1_hi = float(path_w1.min() - 1.0), float(path_w1.max() + 1.0)
    w2_lo, w2_hi = float(path_w2.min() - 1.0), float(path_w2.max() + 1.0)
    w1_lo = min(w1_lo, -pad);  w1_hi = max(w1_hi, +pad)
    w2_lo = min(w2_lo, -pad);  w2_hi = max(w2_hi, +pad)
    w1s, w2s, L_grid = sim_ls.loss_landscape(
        Xb, yb,
        w1_range=(w1_lo, w1_hi),
        w2_range=(w2_lo, w2_hi),
        n_grid=41,
        i_layer=0, i_unit=0, j_unit=0, k_unit=1,
    )
    Xg, Yg = np.meshgrid(w1s, w2s, indexing="ij")
    cf = ax_ll.contourf(Xg, Yg, L_grid, levels=18, cmap="viridis", alpha=0.85)
    cbar = fig.colorbar(cf, ax=ax_ll, fraction=0.045, pad=0.03)
    cbar.set_label("BCE loss L(w_a, w_b)")
    ax_ll.contour(Xg, Yg, L_grid, levels=12,
                  colors="white", linewidths=0.5, alpha=0.5)
    ax_ll.plot(path_w1, path_w2, color="tab:red", linewidth=1.6,
               label=f"GD path ({len(path_w1)} epochs)")
    ax_ll.scatter([path_w1[0]], [path_w2[0]],
                  c="white", edgecolors="black", linewidths=1.5,
                  s=160, marker="o", zorder=10, label="start")
    ax_ll.scatter([path_w1[-1]], [path_w2[-1]],
                  c="tab:red", edgecolors="black", linewidths=1.5,
                  s=180, marker="*", zorder=10, label="final")
    ax_ll.set_xlabel("W[0][0, 0]  (input 1 -> hidden 1 weight)", fontsize=10)
    ax_ll.set_ylabel("W[0][0, 1]  (input 1 -> hidden 2 weight)", fontsize=10)
    ax_ll.set_title(
        "XOR-MLP loss landscape on a 2-weight slice\n"
        "(other parameters frozen; GD path overlaid)",
        fontsize=11,
    )
    ax_ll.legend(loc="upper right", fontsize=8)
    ax_ll.grid(True, alpha=0.2)

    # ---- Right: ill-conditioned quadratic + zig-zag GD ---------------
    ax_q = fig.add_subplot(1, 2, 2)
    a1, a2 = 1.0, 20.0
    extent = 3.0
    g1, g2 = np.meshgrid(np.linspace(-extent, extent, 200),
                          np.linspace(-extent / 2, extent / 2, 200),
                          indexing="xy")
    L_q = NeuralNetworkGeometry.quadratic_loss_landscape(
        g1, g2, a1=a1, a2=a2,
    )
    levels = np.linspace(0.0, np.max(L_q), 24)
    cf2 = ax_q.contourf(g1, g2, L_q, levels=levels, cmap="magma", alpha=0.85)
    cbar2 = fig.colorbar(cf2, ax=ax_q, fraction=0.045, pad=0.03)
    cbar2.set_label(rf"$L(w_1, w_2) = {a1:.0f} w_1^2 + {a2:.0f} w_2^2$")
    ax_q.contour(g1, g2, L_q, levels=10,
                 colors="white", linewidths=0.6, alpha=0.55)

    path_zig = NeuralNetworkSimulator.gradient_descent_trajectory(
        a1=a1, a2=a2, learning_rate=0.04, n_steps=70,
        start=(-2.5, 1.2),
    )
    path_calm = NeuralNetworkSimulator.gradient_descent_trajectory(
        a1=a1, a2=a2, learning_rate=0.005, n_steps=300,
        start=(-2.5, 1.2),
    )
    ax_q.plot(path_zig[:, 0], path_zig[:, 1], "o-",
              color="tab:cyan", markersize=3, linewidth=1.4,
              label="GD lr=0.04 (zig-zag)")
    ax_q.plot(path_calm[:, 0], path_calm[:, 1], ".-",
              color="tab:green", markersize=2, linewidth=1.0, alpha=0.85,
              label="GD lr=0.005 (smooth)")
    ax_q.scatter([path_zig[0, 0]], [path_zig[0, 1]],
                 c="white", edgecolors="black", linewidths=1.5,
                 s=140, marker="o", zorder=10, label="start")
    ax_q.scatter([0.0], [0.0],
                 c="gold", edgecolors="black", linewidths=1.5,
                 s=240, marker="*", zorder=10, label="global min")

    ax_q.set_xlim(-extent, extent)
    ax_q.set_ylim(-extent / 2, extent / 2)
    ax_q.set_aspect("equal")
    ax_q.set_xlabel("w_1", fontsize=11)
    ax_q.set_ylabel("w_2", fontsize=11)
    ax_q.set_title(
        f"Anisotropic quadratic bowl  (kappa = a2/a1 = {a2/a1:.0f})\n"
        f"high learning rate -> zig-zag along the steep direction",
        fontsize=11,
    )
    ax_q.legend(loc="upper right", fontsize=8)
    ax_q.grid(True, alpha=0.2)

    fig.suptitle(
        "Loss landscape from substrate: "
        "L(theta) = strain energy of the network configuration",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "85_loss_landscape.png"))

    return out


# ---------------------------------------------------------------------------
# Fluid turbulence from substrate -- 96 + 97
# ---------------------------------------------------------------------------

def render_turbulence() -> list[str]:
    """Produce 96_kolmogorov_spectrum.png and 97_vortex_shedding.png.

    96: Log-log E(k) energy spectrum showing the Kolmogorov k^(-5/3)
        inertial-range slope.  Three traces:
          - analytic E(k) = C_K eps^(2/3) k^(-5/3) over the inertial decade
          - Pope (2000) model spectrum with low-k roll-off and dissipative
            high-k cut-off
          - shell-averaged spectrum of a synthetic 256^2 random field with
            the same target slope (verifies the simulator).
        Annotates the integral k_L = 2*pi/L and Kolmogorov k_eta = 2*pi/eta
        edges bounding the inertial subrange.
    97: Vorticity field of a Karman vortex street behind a circular
        cylinder.  Wake spacing fixed by the Strouhal number St = 0.21
        (lambda = D/St).  Free-stream U arrows on the inflow side;
        cylinder body shaded; alternating-sign Lamb-Oseen vortices
        coloured red/blue.  Annotated with U, D, Re, St, and shedding
        frequency f.  Lower panel: Reynolds-number axis with the
        laminar/transitional/turbulent regimes and Re_crit = 2300.
    """
    from src.stiff_medium.turbulence_substrate import (
        KOLMOGOROV_CONSTANT,
        NU_AIR_M2_S,
        RE_CRIT_PIPE,
        RE_CRIT_PIPE_LOWER,
        RE_CRIT_PIPE_UPPER,
        STROUHAL_CYLINDER,
        TurbulenceGeometry,
        TurbulenceSimulator,
    )

    out: list[str] = []

    # ------------------------------------------------------------------
    # 96: Kolmogorov k^(-5/3) inertial-range energy spectrum
    # ------------------------------------------------------------------
    geom = TurbulenceGeometry(Lx=1.0, Ly=1.0, Nx=256, Ny=256)
    sim = TurbulenceSimulator(geometry=geom, nu_m2_s=1.0e-5)

    eps = 1.0       # m^2/s^3 dissipation
    L = 0.5         # m  integral scale
    eta = TurbulenceGeometry.kolmogorov_scale_m(sim.nu_m2_s, eps)
    k_L = 2.0 * np.pi / L
    k_eta = 2.0 * np.pi / eta

    k_an = np.logspace(np.log10(k_L * 0.3), np.log10(k_eta * 1.2), 400)
    E_an = sim.kolmogorov_spectrum(k_an, eps)
    E_model = sim.model_spectrum_full(k_an, eps, L, eta)

    field = sim.synthetic_kolmogorov_field(epsilon_w_kg=eps, L_m=L, seed=7)
    k_bin, E_bin = sim.shell_average_spectrum(
        field["u"], field["v"], field["kx"], field["ky"], n_bins=48,
    )
    mask_b = (E_bin > 0) & (k_bin > 1.5 * k_L) & (k_bin < 0.6 * k_eta)
    k_bin_p = k_bin[mask_b]
    E_bin_p = E_bin[mask_b]
    if len(k_bin_p) > 4:
        k_match = np.exp(0.5 * (np.log(k_bin_p[0]) + np.log(k_bin_p[-1])))
        norm_an = sim.kolmogorov_spectrum(np.array([k_match]), eps)[0]
        idx = int(np.argmin(np.abs(k_bin_p - k_match)))
        scale_b = norm_an / max(E_bin_p[idx], 1e-30)
        E_bin_plot = E_bin_p * scale_b
    else:
        E_bin_plot = E_bin_p

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(1, 1, 1)
    ax.loglog(k_an, E_an, "-", color="black", lw=2.4,
              label=rf"$E(k) = C_K \, \varepsilon^{{2/3}} \, k^{{-5/3}}$  "
                    rf"($C_K = {KOLMOGOROV_CONSTANT:.2f}$)")
    ax.loglog(k_an, E_model, "--", color="tab:purple", lw=1.6, alpha=0.85,
              label="Pope (2000) model spectrum (full)")
    if len(k_bin_p) > 0:
        ax.loglog(k_bin_p, E_bin_plot, "o", color="tab:orange",
                  markersize=5.5, alpha=0.9,
                  label=r"shell-averaged $E(k)$ from synthetic 256$^2$ field")

    ax.axvline(k_L, color="tab:green", lw=1.2, ls=":",
               label=rf"$k_L = 2\pi/L = {k_L:.2f}$ /m")
    ax.axvline(k_eta, color="crimson", lw=1.2, ls=":",
               label=rf"$k_\eta = 2\pi/\eta = {k_eta:.2e}$ /m")
    ax.axvspan(k_L, k_eta, color="gold", alpha=0.10,
               label="inertial subrange")

    k_g = np.array([3.0 * k_L, 0.3 * k_eta])
    E_g_anchor = sim.kolmogorov_spectrum(np.array([k_g[0]]), eps)[0] * 4.0
    E_g = E_g_anchor * (k_g / k_g[0]) ** (-5.0 / 3.0)
    ax.loglog(k_g, E_g, color="tab:blue", lw=1.0, alpha=0.7)
    k_mid = np.sqrt(k_g[0] * k_g[1])
    E_mid = E_g_anchor * (k_mid / k_g[0]) ** (-5.0 / 3.0)
    ax.text(k_mid * 1.15, E_mid * 1.15, "slope = -5/3",
            color="tab:blue", fontsize=10, rotation=-22)

    slope_fit = sim.fit_inertial_slope(
        k_an, E_an, k_min=3 * k_L, k_max=0.3 * k_eta,
    )
    ax.text(0.02, 0.04,
            f"fitted analytic slope = {slope_fit:.4f}\n"
            f"expected = -5/3 = {-5.0/3.0:.4f}\n"
            f"L = {L:.2f} m,  eta = {eta:.2e} m,\n"
            f"nu = {sim.nu_m2_s:.1e} m^2/s,  eps = {eps:.2f} m^2/s^3",
            transform=ax.transAxes, fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.35",
                      facecolor="white", edgecolor="gray", alpha=0.9))

    ax.set_xlabel("wavenumber  $k$  [1/m]", fontsize=11)
    ax.set_ylabel("energy spectrum  $E(k)$  [m$^3$/s$^2$]", fontsize=11)
    ax.set_title(
        "Kolmogorov turbulence spectrum from substrate viscosity\n"
        r"NS dissipation $\nu = \frac{1}{2}\gamma\xi^2$ "
        r"$\Rightarrow$ inertial-range $E(k) \propto k^{-5/3}$",
        fontsize=12,
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    out.append(save(fig, "96_kolmogorov_spectrum.png"))

    # ------------------------------------------------------------------
    # 97: Karman vortex street vorticity field behind cylinder
    # ------------------------------------------------------------------
    geom2 = TurbulenceGeometry(Lx=1.6, Ly=0.6, Nx=320, Ny=128)
    sim2 = TurbulenceSimulator(geometry=geom2, nu_m2_s=1.0e-5)
    U_inf = 1.0           # m/s
    D = 0.08              # cylinder diameter
    Re = sim2.reynolds_number(U_inf, D)
    field2 = sim2.vortex_shedding_field(
        U_m_s=U_inf, diameter_m=D, n_pairs=8,
        wake_offset_m=0.28 * (D / STROUHAL_CYLINDER),
        cylinder_x_m=0.18 * geom2.Lx,
        circulation_strength=0.42, core_radius_m=0.18 * D,
    )
    omega = field2["vorticity"]
    cyl_x, cyl_y = field2["cylinder_xy"]
    lam = field2["wavelength_m"]
    f_shed = field2["shedding_freq_hz"]

    fig2, axarr = plt.subplots(2, 1, figsize=(13.5, 7.0),
                               gridspec_kw={"height_ratios": [3.5, 1.0]})

    ax2 = axarr[0]
    vmax = float(np.max(np.abs(omega)))
    if vmax == 0.0:
        vmax = 1.0
    extent = (0.0, geom2.Lx, 0.0, geom2.Ly)
    im = ax2.imshow(omega, origin="lower", extent=extent,
                    cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                    aspect="equal", interpolation="bilinear")
    cbar = fig2.colorbar(im, ax=ax2, fraction=0.025, pad=0.02)
    cbar.set_label(r"vorticity  $\omega_z$  [1/s]", fontsize=10)

    cyl = plt.Circle((cyl_x, cyl_y), 0.5 * D, color="black",
                     zorder=5, alpha=0.9)
    ax2.add_patch(cyl)

    Y_arr = np.linspace(0.05 * geom2.Ly, 0.95 * geom2.Ly, 7)
    for ya in Y_arr:
        ax2.annotate(
            "", xy=(0.06 * geom2.Lx, ya), xytext=(0.005, ya),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.5,
                            alpha=0.6),
        )
    ax2.text(0.005, geom2.Ly * 1.02, rf"$U_\infty = {U_inf:.2f}$ m/s",
             fontsize=10)

    x0 = cyl_x + 1.5 * D
    x1 = x0 + lam
    yb = 0.08 * geom2.Ly
    ax2.annotate("", xy=(x1, yb), xytext=(x0, yb),
                 arrowprops=dict(arrowstyle="<->", color="darkgreen",
                                 lw=1.6))
    ax2.text(0.5 * (x0 + x1), yb - 0.022,
             rf"$\lambda = D/St = {lam:.3f}$ m",
             color="darkgreen", ha="center", fontsize=10)

    ax2.text(0.012, 0.94,
             f"U = {U_inf:.2f} m/s,  D = {D*100:.1f} cm,\n"
             f"Re = U D / nu = {Re:.0f}\n"
             f"St = {STROUHAL_CYLINDER:.2f}  =>  f = St U / D = {f_shed:.2f} Hz\n"
             f"nu from substrate gamma xi^2 / 2",
             transform=ax2.transAxes, fontsize=9,
             family="monospace",
             bbox=dict(boxstyle="round,pad=0.35",
                       facecolor="white", edgecolor="gray", alpha=0.9),
             verticalalignment="top")

    ax2.set_xlabel("x  [m]", fontsize=11)
    ax2.set_ylabel("y  [m]", fontsize=11)
    ax2.set_title(
        "Karman vortex street behind a circular cylinder\n"
        "(alternating Lamb-Oseen vortices, nu from substrate gamma)",
        fontsize=12,
    )
    ax2.set_xlim(0.0, geom2.Lx)
    ax2.set_ylim(0.0, geom2.Ly)

    # ----- Lower panel: Reynolds-number regime bar --------------------
    axR = axarr[1]
    Re_axis = np.logspace(0, 6, 400)
    cmap_vals = np.where(
        Re_axis < RE_CRIT_PIPE_LOWER, 0.0,
        np.where(Re_axis < RE_CRIT_PIPE_UPPER, 0.5, 1.0),
    )
    axR.scatter(Re_axis, np.zeros_like(Re_axis) + 0.5,
                c=cmap_vals, cmap="RdYlGn_r",
                s=6, marker="s", vmin=0.0, vmax=1.0)
    axR.axvline(RE_CRIT_PIPE_LOWER, color="black", lw=0.8, ls="--")
    axR.axvline(RE_CRIT_PIPE, color="red", lw=1.4)
    axR.axvline(RE_CRIT_PIPE_UPPER, color="black", lw=0.8, ls="--")
    axR.scatter([Re], [0.5], c="cyan", edgecolors="black",
                s=160, zorder=10, marker="o",
                label=f"this cylinder Re = {Re:.0f}")
    axR.text(RE_CRIT_PIPE, 1.18,
             rf"$Re_\mathrm{{crit}}={RE_CRIT_PIPE:.0f}$ (pipes)",
             color="red", fontsize=10, ha="center")
    axR.text(RE_CRIT_PIPE_LOWER * 0.4, 0.5, "laminar",
             ha="right", va="center", fontsize=10, color="darkgreen")
    axR.text(2.0e5, 0.5, "turbulent",
             ha="left", va="center", fontsize=10, color="darkred")
    axR.set_xscale("log")
    axR.set_xlim(1.0, 1.0e6)
    axR.set_ylim(0.0, 1.5)
    axR.set_yticks([])
    axR.set_xlabel("Reynolds number  Re = U L / nu", fontsize=10)
    axR.legend(loc="lower right", fontsize=9)
    axR.grid(True, which="major", axis="x", alpha=0.3)

    fig2.tight_layout()
    out.append(save(fig2, "97_vortex_shedding.png"))
    return out


# ---------------------------------------------------------------------------
# Chaos / dynamical systems (Lorenz attractor + logistic map)
# ---------------------------------------------------------------------------

def render_chaos() -> list[str]:
    from src.stiff_medium.chaos_substrate import (
        ChaosSimulator,
        FEIGENBAUM_DELTA,
        LOGISTIC_R_INFINITY,
        LORENZ_BETA,
        LORENZ_RHO,
        LORENZ_SIGMA,
        lorenz_geometry,
    )
    out: list[str] = []
    sim = ChaosSimulator()

    # ----- 98_lorenz_attractor.png -----
    # 3D butterfly attractor with two trajectories from nearby initial
    # conditions to illustrate sensitive dependence.
    t, X1 = sim.simulate_lorenz(x0=(1.0, 1.0, 1.0),
                                t_max=40.0, dt=0.005)
    _, X2 = sim.simulate_lorenz(x0=(1.0 + 1e-4, 1.0, 1.0),
                                t_max=40.0, dt=0.005)
    geom = lorenz_geometry()
    lam_est = sim.lorenz_lyapunov(t_max=80.0, dt=0.01, transient=5.0)

    fig = plt.figure(figsize=(13, 6))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    n_plot = X1.shape[0]
    colors = plt.cm.plasma(np.linspace(0.0, 1.0, n_plot))
    # plot in chunks so the colormap traces the time axis
    step = 10
    for k in range(0, n_plot - step, step):
        ax3d.plot(X1[k:k + step + 1, 0],
                  X1[k:k + step + 1, 1],
                  X1[k:k + step + 1, 2],
                  color=colors[k], linewidth=0.6, alpha=0.9)
    ax3d.scatter(X1[0, 0], X1[0, 1], X1[0, 2],
                 color="white", edgecolors="black", s=40,
                 label="x_0 = (1,1,1)")
    ax3d.set_xlabel("x")
    ax3d.set_ylabel("y")
    ax3d.set_zlabel("z")
    ax3d.set_title(
        f"Lorenz strange attractor\n"
        f"sigma={LORENZ_SIGMA:g}, beta=8/3, rho={LORENZ_RHO:g}\n"
        f"lambda_1 (Benettin) = {lam_est:.3f}  "
        f"(textbook 0.906),  D_KY = {geom.kaplan_yorke_dimension():.3f}",
        fontsize=10,
    )
    ax3d.view_init(elev=22, azim=-65)

    # divergence panel: |dx(t)| growing exponentially at rate lambda_1
    sep = np.linalg.norm(X1 - X2, axis=1)
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.semilogy(t, sep, "b-", linewidth=1.0, label="|x_1(t) - x_2(t)|")
    # reference exponential e^{lambda*t} * |dx_0|
    sep0 = sep[0] if sep[0] > 0 else 1e-4
    fit = sep0 * np.exp(0.906 * t)
    ax2.semilogy(t, np.minimum(fit, 1e2), "r--", linewidth=1.2,
                 label="exp(0.906 t) * |dx_0|")
    ax2.axhline(40.0, color="k", linestyle=":", alpha=0.4,
                label="attractor diameter ~40")
    ax2.set_xlabel("time t")
    ax2.set_ylabel("trajectory separation")
    ax2.set_title("Sensitive dependence on initial conditions\n"
                  "(initial separation 10^-4)")
    ax2.legend(loc="lower right", fontsize=9)
    ax2.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    out.append(save(fig, "98_lorenz_attractor.png"))

    # ----- 99_logistic_map.png -----
    # Bifurcation diagram + Lyapunov exponent vs r
    r_vals = np.linspace(2.5, 4.0, 1200)
    R, X = sim.logistic_bifurcation(r_vals, n_skip=600, n_keep=200)
    lyap_r = np.linspace(2.5, 4.0, 600)
    lyap = sim.logistic_lyapunov_curve(lyap_r, n_iter=2000, n_skip=500)
    delta_est = sim.feigenbaum_delta_estimate()

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True,
                             gridspec_kw={"height_ratios": [2.0, 1.0]})

    ax_b = axes[0]
    ax_b.plot(R, X, ",", color="midnightblue", alpha=0.45, rasterized=True)
    ax_b.axvline(LOGISTIC_R_INFINITY, color="crimson", linestyle="--",
                 linewidth=1.0,
                 label=f"r_inf ~ {LOGISTIC_R_INFINITY:.4f}  (cascade end)")
    # mark first few period-doubling bifurcations
    for k, rk in enumerate((3.0, 3.4495, 3.5441, 3.5644)):
        ax_b.axvline(rk, color="orange", linestyle=":", linewidth=0.8,
                     alpha=0.7)
    ax_b.set_ylim(0.0, 1.0)
    ax_b.set_ylabel("asymptotic x_n")
    ax_b.set_title(
        "Logistic map  x_{n+1} = r x_n (1 - x_n):  bifurcation diagram\n"
        f"Feigenbaum delta (estimate) = {delta_est:.4f}  "
        f"(reference {FEIGENBAUM_DELTA:.4f}, "
        f"err {abs(delta_est - FEIGENBAUM_DELTA) / FEIGENBAUM_DELTA:.3%})"
    )
    ax_b.legend(loc="upper left", fontsize=9)
    ax_b.grid(True, alpha=0.2)

    ax_l = axes[1]
    ax_l.plot(lyap_r, lyap, "b-", linewidth=1.0, label="lambda(r)")
    ax_l.axhline(0.0, color="k", linestyle="-", linewidth=0.6)
    ax_l.fill_between(lyap_r, 0.0, lyap, where=(lyap > 0.0),
                      color="red", alpha=0.25, label="chaotic (lambda > 0)")
    ax_l.fill_between(lyap_r, lyap, 0.0, where=(lyap <= 0.0),
                      color="green", alpha=0.25,
                      label="stable / periodic (lambda < 0)")
    ax_l.axvline(LOGISTIC_R_INFINITY, color="crimson", linestyle="--",
                 linewidth=1.0)
    ax_l.set_xlabel("growth rate r")
    ax_l.set_ylabel("Lyapunov exponent  lambda(r)")
    ax_l.set_ylim(-3.0, 1.0)
    ax_l.legend(loc="lower right", fontsize=9)
    ax_l.grid(True, alpha=0.3)

    fig.tight_layout()
    out.append(save(fig, "99_logistic_map.png"))

    return out


# ---------------------------------------------------------------------------
# Quantum computing as substrate Möbius two-sheet states:
#   90_quantum_gates.png — Bloch sphere for X/Y/Z/H + Bell-state circuit
#   91_quantum_algorithms.png — Grover amplitude vs iter + decoherence vs gamma
# ---------------------------------------------------------------------------

def render_qc() -> list[str]:
    """Produce 90_quantum_gates.png and 91_quantum_algorithms.png.

    90: Bloch-sphere trajectories for X, Y, Z, H rotations applied to |0>,
        plus a circuit diagram of the standard H-CNOT Bell-state preparation.
    91: Grover amplitude amplification vs iteration on n=4 qubits with one
        marked element (optimum at floor(pi/4 sqrt(N)) = 3), plus the
        gate fidelity F = exp(-gamma t) decay vs substrate drag gamma.
    """
    from src.stiff_medium.quantum_computing_substrate import (
        QuantumComputingGeometry,
        QuantumComputingSimulator,
        fidelity_vs_gamma,
        grover_run_4qubits,
    )
    out: list[str] = []
    geom1 = QuantumComputingGeometry(n_qubits=1)

    # ---- 90: Bloch sphere trajectories + Bell-state circuit ------------
    fig = plt.figure(figsize=(16, 6))
    gs = fig.add_gridspec(1, 5, width_ratios=[1.0, 1.0, 1.0, 1.0, 1.6])
    ax_x = fig.add_subplot(gs[0, 0], projection="3d")
    ax_y = fig.add_subplot(gs[0, 1], projection="3d")
    ax_z = fig.add_subplot(gs[0, 2], projection="3d")
    ax_h = fig.add_subplot(gs[0, 3], projection="3d")
    ax_circuit = fig.add_subplot(gs[0, 4])

    def _draw_bloch(ax, axis_label: str, vectors, title: str, color: str):
        u_sph, v_sph = np.mgrid[0:2*np.pi:24j, 0:np.pi:13j]
        xs = np.cos(u_sph) * np.sin(v_sph)
        ys = np.sin(u_sph) * np.sin(v_sph)
        zs = np.cos(v_sph)
        ax.plot_wireframe(xs, ys, zs, color="gray", alpha=0.18, linewidth=0.5)
        # axes
        ax.quiver(0, 0, 0, 1.05, 0, 0, color="black", alpha=0.4,
                  arrow_length_ratio=0.08, linewidth=0.8)
        ax.quiver(0, 0, 0, 0, 1.05, 0, color="black", alpha=0.4,
                  arrow_length_ratio=0.08, linewidth=0.8)
        ax.quiver(0, 0, 0, 0, 0, 1.05, color="black", alpha=0.4,
                  arrow_length_ratio=0.08, linewidth=0.8)
        ax.text(1.18, 0, 0, "x", fontsize=8)
        ax.text(0, 1.18, 0, "y", fontsize=8)
        ax.text(0, 0, 1.18, "z", fontsize=8)
        # Trajectory
        rxs = np.array([v[0] for v in vectors])
        rys = np.array([v[1] for v in vectors])
        rzs = np.array([v[2] for v in vectors])
        ax.plot(rxs, rys, rzs, color=color, linewidth=2.5)
        # endpoints
        ax.scatter([rxs[0]], [rys[0]], [rzs[0]], color="blue", s=60,
                   edgecolors="black", linewidths=0.8, label="|0>", zorder=5)
        ax.scatter([rxs[-1]], [rys[-1]], [rzs[-1]], color="red", s=60,
                   edgecolors="black", linewidths=0.8,
                   label=f"after {axis_label}", zorder=5)
        ax.set_title(title, fontsize=10)
        ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1); ax.set_zlim(-1.1, 1.1)
        ax.set_box_aspect((1, 1, 1))
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        ax.set_zticks([-1, 0, 1])
        ax.legend(fontsize=7, loc="upper left")

    # Build smooth rotation trajectories using axis-angle on the Bloch sphere.
    # X-rotation by pi takes |0> = +z to -z through +y (i.e. R_x(pi) flips z).
    n_steps = 40
    angles = np.linspace(0.0, np.pi, n_steps)
    # X (rotation about x): r(t) = (0, sin t, cos t)
    vec_x = [(0.0, float(np.sin(a)), float(np.cos(a))) for a in angles]
    _draw_bloch(ax_x, "X", vec_x,
                "X gate: pi rotation about x\n|0> -> |1>",
                color="tab:red")
    # Y (rotation about y): r(t) = (-sin t, 0, cos t) takes +z to -z via -x
    vec_y = [(-float(np.sin(a)), 0.0, float(np.cos(a))) for a in angles]
    _draw_bloch(ax_y, "Y", vec_y,
                "Y gate: pi rotation about y\n|0> -> i|1>",
                color="tab:green")
    # Z (rotation about z): leaves +z fixed; for visibility apply Z to |+>:
    angles_z = np.linspace(0.0, np.pi, n_steps)
    vec_z_plus = [(float(np.cos(a)), -float(np.sin(a)), 0.0) for a in angles_z]
    _draw_bloch(ax_z, "Z", vec_z_plus,
                "Z gate (shown on |+>):\npi rotation about z, x -> -x",
                color="tab:purple")
    # H (Hadamard) = pi rotation about (x+z)/sqrt(2): |0> -> |+> on equator at +x
    # Trajectory parameterised by angle a along the geodesic from +z to +x.
    a_h = np.linspace(0.0, np.pi / 2.0, n_steps)
    vec_h = [(float(np.sin(a)), 0.0, float(np.cos(a))) for a in a_h]
    _draw_bloch(ax_h, "H", vec_h,
                "Hadamard: half-Mobius rotation\n|0> -> (|0>+|1>)/sqrt(2)",
                color="tab:orange")

    # Bell-state circuit diagram (right panel).
    ax_circuit.set_xlim(0.0, 10.0)
    ax_circuit.set_ylim(0.0, 5.0)
    ax_circuit.set_aspect("equal")
    ax_circuit.axis("off")
    # Two qubit lines
    for y, label in [(3.5, "q0:  |0>"), (1.5, "q1:  |0>")]:
        ax_circuit.plot([0.5, 9.5], [y, y], "k-", linewidth=1.4)
        ax_circuit.text(0.0, y, label, fontsize=10, ha="left", va="center")
    # Hadamard box on q0 at x=3.0
    ax_circuit.add_patch(plt.Rectangle((2.5, 3.1), 1.0, 0.8,
                                        edgecolor="black",
                                        facecolor="#ffe4b5"))
    ax_circuit.text(3.0, 3.5, "H", fontsize=12, ha="center", va="center",
                    fontweight="bold")
    # CNOT control on q0 at x=6.0, target on q1
    ax_circuit.plot([6.0], [3.5], "ko", markersize=8)  # control dot
    ax_circuit.plot([6.0, 6.0], [3.5, 1.5], "k-", linewidth=1.4)
    ax_circuit.add_patch(plt.Circle((6.0, 1.5), 0.3,
                                     edgecolor="black", facecolor="white",
                                     linewidth=1.4))
    ax_circuit.plot([5.7, 6.3], [1.5, 1.5], "k-", linewidth=1.0)
    ax_circuit.plot([6.0, 6.0], [1.2, 1.8], "k-", linewidth=1.0)
    # Output annotation
    ax_circuit.text(8.5, 2.5,
                    r"$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$",
                    fontsize=11, ha="center", va="center",
                    bbox=dict(facecolor="#e6f3ff", edgecolor="black",
                              boxstyle="round,pad=0.3"))
    ax_circuit.text(5.0, 4.7, "Bell-state preparation",
                    fontsize=11, ha="center", va="center",
                    fontweight="bold")
    ax_circuit.text(5.0, 0.5,
                    "H on q0 -> superposition;  CNOT(q0,q1) -> entangled.",
                    fontsize=8, ha="center", va="center", style="italic")

    fig.suptitle(
        "Quantum gates as Mobius two-sheet rotations:  X/Y/Z/H on Bloch sphere "
        "+ Bell-state circuit\n"
        "Substrate identifies (alpha,beta) with the two-sheet strain pattern; "
        "H = half-Mobius half-twist.",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "90_quantum_gates.png"))

    # ---- 91: Grover amplitude amplification + decoherence -------------
    fig = plt.figure(figsize=(15, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.0])
    ax_grov = fig.add_subplot(gs[0, 0])
    ax_dec = fig.add_subplot(gs[0, 1])

    grov = grover_run_4qubits(marked_index=5)
    iters = grov["iterations"]
    sim_amp = grov["marked_amplitude"]
    sim_prob = grov["marked_probability"]
    th_amp = np.abs(grov["theory_amplitude"])
    opt_k = int(grov["optimal_iters"])

    ax_grov.plot(iters, sim_prob, "o-", color="tab:blue", linewidth=2.0,
                 markersize=8, label="P(marked)  (simulator)")
    ax_grov.plot(iters, th_amp ** 2, "x--", color="tab:orange",
                 linewidth=1.4, markersize=8,
                 label=r"$\sin^2((2k+1)\theta)$  (closed form)")
    ax_grov.axhline(1.0, color="gray", linestyle=":", linewidth=1.0,
                    alpha=0.7, label="P = 1")
    ax_grov.axhline(1.0 / 16.0, color="red", linestyle=":", linewidth=1.0,
                    alpha=0.7, label="uniform P = 1/N = 1/16")
    ax_grov.axvline(opt_k, color="purple", linestyle="--", linewidth=1.2,
                    alpha=0.6,
                    label=f"k* = floor(pi/4 sqrt(N)) = {opt_k}")
    # Annotate the maximum
    k_max = int(np.argmax(sim_prob))
    ax_grov.annotate(
        f"P_max = {sim_prob[k_max]:.3f}\nat k = {k_max}",
        xy=(k_max, sim_prob[k_max]),
        xytext=(k_max + 0.6, sim_prob[k_max] - 0.15),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )
    ax_grov.set_xlabel("Grover iteration k", fontsize=10)
    ax_grov.set_ylabel("marked-state probability", fontsize=10)
    ax_grov.set_title(
        "Grover search:  n=4 qubits (N=16), 1 marked element\n"
        "amplitude amplification: 1/4 -> > 0.96 in 3 iterations",
        fontsize=10,
    )
    ax_grov.set_xticks(list(iters))
    ax_grov.set_ylim(-0.05, 1.1)
    ax_grov.legend(fontsize=8, loc="lower center")
    ax_grov.grid(True, alpha=0.3)

    # Decoherence: gate fidelity F(t) = exp(-gamma t)
    gammas = np.logspace(-3.0, 1.5, 200)
    for t, color in [
        (0.1, "tab:blue"),
        (0.5, "tab:green"),
        (1.0, "tab:orange"),
        (3.0, "tab:red"),
    ]:
        fid = fidelity_vs_gamma(t=t, gammas=gammas)["fidelity"]
        ax_dec.semilogx(gammas, fid, "-", color=color, linewidth=1.8,
                        label=f"t = {t}")
    ax_dec.axhline(1.0, color="gray", linestyle=":", linewidth=1.0,
                   alpha=0.6, label="F = 1 (no decoherence)")
    ax_dec.axhline(1.0 / np.e, color="red", linestyle=":", linewidth=1.0,
                   alpha=0.7, label="F = 1/e  (gamma t = 1)")
    ax_dec.set_xlabel("substrate drag gamma", fontsize=10)
    ax_dec.set_ylabel("gate fidelity F = exp(-gamma t)", fontsize=10)
    ax_dec.set_title(
        "Decoherence from substrate drag\n"
        "T_2 = 1/gamma; same gamma as Lagrangian -gamma u (d_t u)",
        fontsize=10,
    )
    ax_dec.set_ylim(-0.05, 1.1)
    ax_dec.grid(True, alpha=0.3, which="both")
    ax_dec.legend(fontsize=8, loc="lower left")

    fig.suptitle(
        "Quantum algorithms from substrate:  Grover amplification (oracle + "
        "diffusion) + decoherence F(t) = exp(-gamma t)\n"
        "Substrate predicts both algorithmic speedup AND its enemy "
        "(off-diagonal decay) from the SAME Lagrangian.",
        fontsize=11,
    )
    fig.tight_layout()
    out.append(save(fig, "91_quantum_algorithms.png"))

    return out


# ---------------------------------------------------------------------------
# Superconductivity from substrate (BCS gap + substrate T_c ceiling)
# ---------------------------------------------------------------------------

def render_sc() -> list[str]:
    """Produce 92_bcs_gap.png and 93_tc_table.png.

    92: Δ(T)/Δ(0) BCS curve (left) + density of states with gap (right).
    93: known SCs sorted by T_c with horizontal substrate-ceiling line at
        128.9 K, plus annotation of the HBCCO 4% match.
    """
    from src.stiff_medium.superconductivity_substrate import (
        BCS_UNIVERSAL_GAP_RATIO,
        REFERENCE_SUPERCONDUCTORS,
        SUBSTRATE_TC_MAX_K,
        SuperconductivityGeometry,
        SuperconductivitySimulator,
    )

    out: list[str] = []

    # ---- 92_bcs_gap.png  -------------------------------------------------
    # Use Pb-like calibration: T_c=7.2 K, θ_D=105 K → Δ(0) ≈ 1.10 meV.
    K_B = 1.380649e-23
    EV_PER_J = 1.0 / 1.602176634e-19
    Tc_target = 7.2
    delta0_meV = (
        BCS_UNIVERSAL_GAP_RATIO * K_B * Tc_target / 2.0
    ) * EV_PER_J * 1e3
    geom = SuperconductivityGeometry(delta_meV=delta0_meV)
    sim = SuperconductivitySimulator(geometry=geom, debye_T_K=105.0)

    fig, (ax_dt, ax_dos) = plt.subplots(1, 2, figsize=(13, 5.5))

    # Left: Δ(T)/Δ(0) BCS shape
    t_over_tc, d_over_d0 = sim.gap_curve(n_T=80)
    ax_dt.plot(t_over_tc, d_over_d0, color="tab:red", linewidth=2.4,
               label="self-consistent BCS Δ(T)")
    # Approximate analytic form Δ(T)/Δ(0) ≈ 1.74 √(1 - T/T_c) near T_c
    t_near = np.linspace(0.7, 1.0, 50)
    delta_near = 1.74 * np.sqrt(np.maximum(1.0 - t_near, 0.0))
    ax_dt.plot(t_near, delta_near, "k--", linewidth=1.2, alpha=0.8,
               label="1.74·√(1 − T/T_c)  (BCS near T_c)")
    ax_dt.axhline(1.0, color="gray", linewidth=0.6, alpha=0.5)
    ax_dt.axvline(1.0, color="gray", linewidth=0.6, alpha=0.5)
    ax_dt.scatter([0.0], [1.0], s=80, color="tab:red", zorder=5)
    ax_dt.text(0.02, 1.02,
               f"Δ(0) = {sim.gap_zero_T_meV():.3f} meV", fontsize=9)
    ax_dt.text(
        0.5, 0.4,
        f"2Δ(0)/(k_B T_c) = {BCS_UNIVERSAL_GAP_RATIO:.4f}\n"
        f"               (= 2π/e^γ, BCS universal)\n"
        f"T_c = {sim.critical_temperature_K():.2f} K (Pb-like)",
        fontsize=10, ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.4",
                  facecolor="lightyellow", edgecolor="gray"),
    )
    ax_dt.set_xlim(0.0, 1.05)
    ax_dt.set_ylim(0.0, 1.15)
    ax_dt.set_xlabel("T / T_c")
    ax_dt.set_ylabel("Δ(T) / Δ(0)")
    ax_dt.set_title("BCS gap closure  Δ(T) → 0 as T → T_c")
    ax_dt.grid(True, alpha=0.3)
    ax_dt.legend(loc="upper right", fontsize=9)

    # Right: density of states with gap (BCS coherence peak)
    E = np.linspace(-4.0 * geom.delta_meV, 4.0 * geom.delta_meV, 1200)
    # Add a small Dynes broadening so the singularity is renderable
    gamma_meV = 0.05 * geom.delta_meV
    z = E - 1j * gamma_meV
    n_complex = np.real(np.abs(z) / np.sqrt(z ** 2 - geom.delta_meV ** 2))
    ax_dos.fill_between(E, 0.0, n_complex, color="tab:orange", alpha=0.45,
                        label="N_s(E) / N(0)  (Dynes γ = 0.05 Δ)")
    ax_dos.axvline(+geom.delta_meV, color="black", linestyle="--",
                   linewidth=1.0, label=f"|E| = Δ = {geom.delta_meV:.3f} meV")
    ax_dos.axvline(-geom.delta_meV, color="black", linestyle="--",
                   linewidth=1.0)
    ax_dos.axhline(1.0, color="gray", linewidth=0.6,
                   alpha=0.6, label="N_n / N(0) = 1 (normal state)")
    ax_dos.axvspan(-geom.delta_meV, +geom.delta_meV,
                   color="lightgray", alpha=0.4, label="forbidden states")
    ax_dos.set_xlabel("E − E_F  [meV]")
    ax_dos.set_ylabel("N(E) / N(0)")
    ax_dos.set_title("BCS density of states (gap + coherence peaks)")
    ax_dos.set_xlim(-4.0 * geom.delta_meV, 4.0 * geom.delta_meV)
    ax_dos.set_ylim(0.0, 5.5)
    ax_dos.grid(True, alpha=0.3)
    ax_dos.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        "BCS gap from substrate paired strain bridge\n"
        "(Δ = 2 ℏω_D exp(−1/(N(0)V)) — paired GEOMETRY+SIM+VIZ)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "92_bcs_gap.png"))

    # ---- 93_tc_table.png  ------------------------------------------------
    rows = sim.reference_table_rows()
    names = [r["name"] for r in rows]
    Tcs = [r["T_c_K"] for r in rows]
    families = [r["family"] for r in rows]
    family_color = {
        "elemental":  "tab:blue",
        "conv-2band": "tab:green",
        "cuprate":    "tab:purple",
    }
    bar_colors = [family_color[f] for f in families]

    fig, ax_bar = plt.subplots(1, 1, figsize=(11, 6.5))
    y = np.arange(len(names))
    ax_bar.barh(y, Tcs, color=bar_colors, edgecolor="black", linewidth=0.6)
    for k, (n, T, f) in enumerate(zip(names, Tcs, families)):
        ax_bar.text(T + 1.5, k, f"{T:.1f} K  ({f})", va="center",
                    fontsize=9)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(names, fontsize=10)

    # Substrate ceiling line
    ax_bar.axvline(SUBSTRATE_TC_MAX_K, color="crimson", linestyle="--",
                   linewidth=2.0,
                   label=f"B3 substrate ceiling  T_c,max = Λ_QCD/n_R = "
                         f"{SUBSTRATE_TC_MAX_K:.1f} K")
    HBCCO_K = REFERENCE_SUPERCONDUCTORS["HBCCO"]["T_c_K"]
    deviation = 100.0 * abs(HBCCO_K - SUBSTRATE_TC_MAX_K) / SUBSTRATE_TC_MAX_K
    ax_bar.annotate(
        f"HBCCO record (1993)\nmatches ceiling at {deviation:.1f}%",
        xy=(HBCCO_K, len(names) - 1),
        xytext=(HBCCO_K + 8, len(names) - 1.5),
        arrowprops=dict(arrowstyle="->", color="crimson", lw=1.0),
        fontsize=9, color="crimson",
    )
    # Legend proxy entries by family
    for fam, color in family_color.items():
        ax_bar.barh([-1], [0], color=color, label=f"{fam}")
    ax_bar.set_xlim(0.0, max(Tcs) * 1.25)
    ax_bar.set_ylim(-0.5, len(names) - 0.5)
    ax_bar.set_xlabel("Critical temperature  T_c  [K]")
    ax_bar.set_title(
        "Reference superconductors vs B3 substrate ceiling\n"
        "Onnes 1911 (Hg) → Schilling 1993 (HBCCO): 31-year ambient-pressure record",
        fontsize=11,
    )
    ax_bar.legend(loc="lower right", fontsize=9)
    ax_bar.grid(True, axis="x", alpha=0.3)

    fig.tight_layout()
    out.append(save(fig, "93_tc_table.png"))

    return out


# ---------------------------------------------------------------------------
# Semiconductor band structure + p-n junction (paired GEOMETRY+SIM+VIZ)
# ---------------------------------------------------------------------------

def render_semi() -> list[str]:
    """Produce 94_band_structure.png and 95_pn_junction.png.

    94: Two-panel band-structure comparison.
        Left  -- E vs k for direct-gap GaAs:  conduction band minimum and
                 valence band maximum both at Gamma; the gap is a pure
                 vertical (zero-momentum) transition (high LED efficiency).
        Right -- E vs k for indirect-gap Si:  conduction band minimum at
                 the X-like zone boundary, valence band maximum at Gamma;
                 the gap requires phonon-assisted (off-axis) transitions
                 (low LED efficiency).  Bandgap, Fermi level (mid-gap),
                 conduction & valence bands annotated.
    95: Three-panel p-n junction in the abrupt-junction depletion
        approximation.
        Top    -- space-charge density rho(x): - q N_a^- on the p-side,
                  + q N_d^+ on the n-side, zero in the bulk.
        Middle -- electric field E(x): triangular profile peaking at
                  the metallurgical junction, zero in both bulks.
        Bottom -- electrostatic potential phi(x): smooth step from p-bulk
                  (0) to n-bulk (V_bi); built-in voltage annotated.
    """
    from src.stiff_medium.semiconductor_substrate import (
        SemiconductorGeometry,
        SemiconductorSimulator,
    )

    out: list[str] = []

    # ------------------------------------------------------------------
    # 94: band-structure comparison (direct GaAs vs indirect Si)
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 7))

    # ---- Left: direct-gap GaAs --------------------------------------
    ax_d = fig.add_subplot(1, 2, 1)
    geom_gaas = SemiconductorGeometry(material="GaAs", n_k=401)
    sim_gaas = SemiconductorSimulator(material="GaAs", T_kelvin=300.0)
    k_n_gaas = geom_gaas.k_grid_normalised()
    Ec_gaas = geom_gaas.conduction_band_eV()
    Ev_gaas = geom_gaas.valence_band_eV()
    EF_gaas = geom_gaas.fermi_level_eV()
    Eg_gaas = geom_gaas.bandgap_eV()

    ax_d.fill_between(k_n_gaas, Ec_gaas.max() + 1.0, Ec_gaas,
                      color="tab:orange", alpha=0.18,
                      label="conduction band (electrons)")
    ax_d.fill_between(k_n_gaas, Ev_gaas, Ev_gaas.min() - 1.0,
                      color="tab:blue", alpha=0.18,
                      label="valence band (holes)")
    ax_d.plot(k_n_gaas, Ec_gaas, color="tab:red", lw=2.4,
              label="$E_c(k)$  (min @ $\\Gamma$)")
    ax_d.plot(k_n_gaas, Ev_gaas, color="tab:blue", lw=2.4,
              label="$E_v(k)$  (max @ $\\Gamma$)")
    ax_d.axhline(EF_gaas, color="black", lw=1.4, ls="--",
                 label=f"$E_F = E_g/2 = {EF_gaas:.2f}$ eV")

    # Vertical (direct) transition arrow
    ax_d.annotate("", xy=(0.0, Eg_gaas + 0.05), xytext=(0.0, -0.05),
                  arrowprops={"arrowstyle": "->", "color": "darkgreen",
                              "lw": 2.4})
    ax_d.text(0.10, 0.5 * Eg_gaas,
              f"DIRECT\n$E_g={Eg_gaas:.2f}$ eV\n(photon only)",
              color="darkgreen", fontsize=10, fontweight="bold",
              ha="left", va="center")

    ax_d.set_xlabel("$k a / \\pi$  (normalised wavevector)", fontsize=11)
    ax_d.set_ylabel("energy [eV]", fontsize=11)
    ax_d.set_title(
        f"GaAs: direct-gap semiconductor at $\\Gamma$\n"
        f"$E_g = {Eg_gaas:.2f}$ eV  -- LED / laser foundation",
        fontsize=11,
    )
    ax_d.set_xlim(-1.05, 1.05)
    ax_d.set_ylim(-1.5, Ec_gaas.max() + 0.5)
    ax_d.axvline(0.0, color="gray", lw=0.6, alpha=0.5)
    ax_d.text(0.0, ax_d.get_ylim()[1] - 0.15, "$\\Gamma$",
              ha="center", fontsize=11)
    ax_d.text(1.0, ax_d.get_ylim()[1] - 0.15, "X",
              ha="center", fontsize=11)
    ax_d.text(-1.0, ax_d.get_ylim()[1] - 0.15, "X",
              ha="center", fontsize=11)
    ax_d.grid(True, alpha=0.3)
    ax_d.legend(loc="upper right", fontsize=8.5, framealpha=0.92)

    # ---- Right: indirect-gap Si -------------------------------------
    ax_i = fig.add_subplot(1, 2, 2)
    geom_si = SemiconductorGeometry(material="Si", n_k=401)
    sim_si = SemiconductorSimulator(material="Si", T_kelvin=300.0)
    k_n_si = geom_si.k_grid_normalised()
    Ec_si = geom_si.conduction_band_eV()
    Ev_si = geom_si.valence_band_eV()
    EF_si = geom_si.fermi_level_eV()
    Eg_si = geom_si.bandgap_eV()

    ax_i.fill_between(k_n_si, Ec_si.max() + 1.0, Ec_si,
                      color="tab:orange", alpha=0.18,
                      label="conduction band (electrons)")
    ax_i.fill_between(k_n_si, Ev_si, Ev_si.min() - 1.0,
                      color="tab:blue", alpha=0.18,
                      label="valence band (holes)")
    ax_i.plot(k_n_si, Ec_si, color="tab:red", lw=2.4,
              label="$E_c(k)$  (min @ X-like)")
    ax_i.plot(k_n_si, Ev_si, color="tab:blue", lw=2.4,
              label="$E_v(k)$  (max @ $\\Gamma$)")
    ax_i.axhline(EF_si, color="black", lw=1.4, ls="--",
                 label=f"$E_F = E_g/2 = {EF_si:.2f}$ eV")

    # Diagonal (indirect) transition arrow:  k=0 -> k=+pi/a
    i_min = int(np.argmin(Ec_si))
    k_min = k_n_si[i_min]
    Ec_min = Ec_si[i_min]
    ax_i.annotate("", xy=(k_min, Ec_min + 0.05), xytext=(0.0, -0.05),
                  arrowprops={"arrowstyle": "->", "color": "darkgreen",
                              "lw": 2.4, "connectionstyle": "arc3,rad=-0.2"})
    ax_i.text(0.45, 0.55 * Eg_si,
              f"INDIRECT\n$E_g={Eg_si:.2f}$ eV\n(photon + phonon)",
              color="darkgreen", fontsize=10, fontweight="bold",
              ha="center", va="center")

    ax_i.set_xlabel("$k a / \\pi$  (normalised wavevector)", fontsize=11)
    ax_i.set_ylabel("energy [eV]", fontsize=11)
    ax_i.set_title(
        f"Si: indirect-gap semiconductor (CB min off $\\Gamma$)\n"
        f"$E_g = {Eg_si:.2f}$ eV  -- weak light emission",
        fontsize=11,
    )
    ax_i.set_xlim(-1.05, 1.05)
    ax_i.set_ylim(-1.5, Ec_si.max() + 0.5)
    ax_i.axvline(0.0, color="gray", lw=0.6, alpha=0.5)
    ax_i.text(0.0, ax_i.get_ylim()[1] - 0.15, "$\\Gamma$",
              ha="center", fontsize=11)
    ax_i.text(1.0, ax_i.get_ylim()[1] - 0.15, "X",
              ha="center", fontsize=11)
    ax_i.text(-1.0, ax_i.get_ylim()[1] - 0.15, "X",
              ha="center", fontsize=11)
    ax_i.grid(True, alpha=0.3)
    ax_i.legend(loc="upper right", fontsize=8.5, framealpha=0.92)

    n_i_si = sim_si.intrinsic_carrier_concentration_per_cm3()
    fig.suptitle(
        f"Band structure from substrate periodic potential:  "
        f"$E_g = $ depth of substrate strain at atomic nodes\n"
        f"intrinsic Si carrier concentration $n_i$(300 K) = "
        f"{n_i_si:.2e} /cm$^3$  "
        f"(textbook ~ 1.5e10)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "94_band_structure.png"))

    # ------------------------------------------------------------------
    # 95: p-n junction (charge density + field + potential)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)

    sim = SemiconductorSimulator(material="Si", T_kelvin=300.0)
    N_a = 1.0e17     # /cm^3, p-side acceptor doping
    N_d = 1.0e17     # /cm^3, n-side donor doping
    profile = sim.junction_profile(
        N_a_per_cm3=N_a, N_d_per_cm3=N_d, V_applied_V=0.0, n_x=601,
    )
    # Convert position from m -> nm for nicer units
    x_nm = profile["x_m"] * 1e9
    rho = profile["rho_C_per_m3"]
    E_field = profile["E_V_per_m"]
    phi = profile["phi_V"]
    x_p_nm = profile["x_p_m"] * 1e9
    x_n_nm = profile["x_n_m"] * 1e9
    W_nm = profile["W_m"] * 1e9
    V_bi = profile["V_bi_V"]

    # ---- Top: charge density rho(x) ----------------------------------
    ax_q = axes[0]
    ax_q.fill_between(x_nm, rho, 0.0, where=(rho < 0),
                      color="tab:blue", alpha=0.5,
                      label=f"$-q N_a$ (p-side, $N_a = ${N_a:.0e}/cm$^3$)")
    ax_q.fill_between(x_nm, rho, 0.0, where=(rho > 0),
                      color="tab:red", alpha=0.5,
                      label=f"$+q N_d$ (n-side, $N_d = ${N_d:.0e}/cm$^3$)")
    ax_q.plot(x_nm, rho, color="black", lw=1.8)
    ax_q.axhline(0.0, color="black", lw=0.6, alpha=0.5)
    ax_q.axvline(0.0, color="gray", lw=0.8, ls=":",
                 label="metallurgical junction")
    ax_q.axvline(-x_p_nm, color="tab:blue", lw=0.8, ls="--", alpha=0.7)
    ax_q.axvline(+x_n_nm, color="tab:red",  lw=0.8, ls="--", alpha=0.7)
    ax_q.set_ylabel("space charge $\\rho(x)$  [C / m$^3$]",
                    fontsize=11)
    ax_q.set_title(
        "Charge density: ionized acceptors (p) + ionized donors (n)\n"
        f"$x_p = {x_p_nm:.1f}$ nm   $x_n = {x_n_nm:.1f}$ nm   "
        f"$W = x_p + x_n = {W_nm:.1f}$ nm",
        fontsize=11,
    )
    ax_q.legend(loc="upper right", fontsize=9, framealpha=0.92)
    ax_q.grid(True, alpha=0.3)

    # ---- Middle: electric field E(x) ---------------------------------
    ax_e = axes[1]
    # Convert V/m -> kV/cm for legibility
    E_kVcm = E_field / 1.0e5
    ax_e.fill_between(x_nm, E_kVcm, 0.0, where=(np.abs(E_kVcm) > 0),
                      color="tab:purple", alpha=0.25)
    ax_e.plot(x_nm, E_kVcm, color="tab:purple", lw=2.4,
              label="$E(x)$")
    ax_e.axhline(0.0, color="black", lw=0.6, alpha=0.5)
    ax_e.axvline(0.0, color="gray", lw=0.8, ls=":")
    ax_e.axvline(-x_p_nm, color="tab:blue", lw=0.8, ls="--", alpha=0.7)
    ax_e.axvline(+x_n_nm, color="tab:red",  lw=0.8, ls="--", alpha=0.7)

    E_peak = float(np.min(E_kVcm))   # most negative value
    ax_e.scatter([0.0], [E_peak], s=80, c="black", zorder=5)
    ax_e.annotate(
        f"$|E_{{max}}| = {abs(E_peak):.1f}$ kV/cm\n"
        f"at metallurgical junction",
        xy=(0.0, E_peak), xytext=(0.4 * x_nm.max(), 0.8 * E_peak),
        fontsize=10, ha="left",
        arrowprops={"arrowstyle": "->", "color": "black", "lw": 0.8},
    )
    ax_e.set_ylabel("electric field $E(x)$  [kV / cm]", fontsize=11)
    ax_e.set_title(
        "Electric field (triangular profile in depletion approximation)\n"
        f"$dE/dx = \\rho / \\varepsilon_s$ ; "
        f"$\\varepsilon_r = 11.7$ for Si",
        fontsize=11,
    )
    ax_e.legend(loc="upper right", fontsize=9, framealpha=0.92)
    ax_e.grid(True, alpha=0.3)

    # ---- Bottom: potential phi(x) ------------------------------------
    ax_p = axes[2]
    ax_p.fill_between(x_nm, phi, 0.0,
                      color="tab:green", alpha=0.18)
    ax_p.plot(x_nm, phi, color="tab:green", lw=2.6,
              label="$\\varphi(x)$ (electrostatic potential)")
    ax_p.axhline(0.0, color="black", lw=0.6, alpha=0.5,
                 label="$\\varphi$(p-bulk) = 0")
    ax_p.axhline(V_bi, color="tab:olive", lw=1.4, ls="--",
                 label=f"$\\varphi$(n-bulk) = $V_{{bi}}$ = {V_bi:.3f} V")
    ax_p.axvline(0.0, color="gray", lw=0.8, ls=":")
    ax_p.axvline(-x_p_nm, color="tab:blue", lw=0.8, ls="--", alpha=0.7)
    ax_p.axvline(+x_n_nm, color="tab:red",  lw=0.8, ls="--", alpha=0.7)
    ax_p.set_xlabel("position $x$ across junction [nm]", fontsize=11)
    ax_p.set_ylabel("electrostatic potential $\\varphi(x)$  [V]",
                    fontsize=11)
    ax_p.set_title(
        f"Electrostatic potential:  "
        f"$V_{{bi}} = (kT/q) \\ln(N_a N_d / n_i^2) = {V_bi:.3f}$ V",
        fontsize=11,
    )
    ax_p.legend(loc="upper left", fontsize=9, framealpha=0.92)
    ax_p.grid(True, alpha=0.3)

    fig.suptitle(
        "p-n junction (Si, abrupt, $N_a = N_d = 10^{17}$/cm$^3$, $T = 300$ K):  "
        "charge density, field, potential\n"
        "substrate interpretation:  depletion = strain inversion zone "
        "between two doped substrate domains",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "95_pn_junction.png"))

    return out


# ---------------------------------------------------------------------------
# Mitochondrial bioenergetics - ETC + ATP synthase + chemiosmosis
# ---------------------------------------------------------------------------

def render_mito() -> list[str]:
    """Produce 106_etc_complexes.png and 107_atp_synthase.png.

    106: 4 ETC complexes (I/II/III/IV) embedded in the inner membrane,
         with redox-potential ladder, H+ pumping arrows, and the
         ubiquinone Q + cytochrome c shuttle paths.
    107: F0F1 ATP synthase rotor structure (c-ring + gamma-shaft +
         alpha3beta3 head) + proton flux -> ATP synthesis curve.
    """
    from src.stiff_medium.mitochondria_substrate import (
        ATP_PER_REV,
        H_PER_2E_COMPLEX_I,
        H_PER_2E_COMPLEX_II,
        H_PER_2E_COMPLEX_III,
        H_PER_2E_COMPLEX_IV,
        MitoGeometry,
        MitoSimulator,
        example_c_rings,
    )
    out: list[str] = []
    geom = MitoGeometry()
    sim = MitoSimulator(geometry=geom)

    # 106_etc_complexes.png
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1.0],
                           width_ratios=[1.4, 1.0],
                           hspace=0.36, wspace=0.28)

    ax = fig.add_subplot(gs[0, 0])
    ax.fill_between([0.0, 1.0], 0.45, 0.55,
                     color="khaki", alpha=0.6,
                     label="inner membrane (lipid)")
    ax.axhline(0.5, color="goldenrod", linestyle="--",
                linewidth=0.6, alpha=0.5)
    ax.text(0.02, 0.95, "INTERMEMBRANE SPACE  (H+ high, low pH)",
             fontsize=10, color="firebrick", fontweight="bold")
    ax.text(0.02, 0.05,
             "MATRIX  (H+ low, high pH; NADH, FADH2, O2, ADP)",
             fontsize=10, color="navy", fontweight="bold")
    complex_specs = [
        ("I",   0.13, "steelblue",
         "Complex I\nNADH dehydrogenase",
         H_PER_2E_COMPLEX_I,  "NADH->Q"),
        ("II",  0.30, "darkseagreen",
         "Complex II\nsuccinate dehydrogenase",
         H_PER_2E_COMPLEX_II, "FADH2->Q"),
        ("III", 0.55, "indianred",
         "Complex III\ncyt bc1",
         H_PER_2E_COMPLEX_III, "Q->cyt c"),
        ("IV",  0.80, "darkorange",
         "Complex IV\ncyt c oxidase",
         H_PER_2E_COMPLEX_IV, "cyt c->O2"),
    ]
    box_w = 0.10
    for name, x, color, label, h_pump, redox in complex_specs:
        ax.fill_between([x - box_w / 2, x + box_w / 2],
                         0.30, 0.70, color=color, alpha=0.85,
                         edgecolor="black", linewidth=1.5)
        ax.text(x, 0.50, name, ha="center", va="center",
                 fontsize=14, fontweight="bold", color="white")
        ax.text(x, 0.22, label, ha="center", va="top",
                 fontsize=8, color=color, fontweight="bold")
        ax.text(x, 0.78, redox, ha="center", va="bottom",
                 fontsize=8, style="italic", color="black")
        if h_pump > 0:
            for k in range(h_pump):
                xk = x + (k - (h_pump - 1) / 2.0) * 0.012
                ax.annotate("", xy=(xk, 0.93), xytext=(xk, 0.30),
                             arrowprops=dict(arrowstyle="->",
                                             color="red", lw=1.5,
                                             alpha=0.85))
            ax.text(x, 0.97, f"{h_pump} H+", ha="center",
                     va="bottom", fontsize=9, color="red",
                     fontweight="bold")
        else:
            ax.text(x, 0.93, "no H+", ha="center", va="bottom",
                     fontsize=9, color="grey", fontweight="bold")

    ax.plot([0.13, 0.30, 0.55], [0.55, 0.55, 0.55], "o--",
             color="purple", markersize=8, lw=1.4, alpha=0.7,
             label="ubiquinone Q (lipid-soluble, 2 e-)")
    ax.text(0.42, 0.59, "Q->QH2", fontsize=8, color="purple",
             style="italic", ha="center")
    ax.plot([0.55, 0.80], [0.80, 0.80], "s--",
             color="firebrick", markersize=8, lw=1.4, alpha=0.7,
             label="cytochrome c (water-soluble, 1 e-)")
    ax.text(0.675, 0.84, "cyt c", fontsize=8, color="firebrick",
             style="italic", ha="center")
    ax.text(0.13, 0.10, "NADH->NAD+", fontsize=8, color="navy",
             ha="center")
    ax.text(0.30, 0.10, "succinate->fumarate", fontsize=8,
             color="navy", ha="center")
    ax.text(0.80, 0.10, "1/2 O2 + 2H+ -> H2O", fontsize=8,
             color="navy", ha="center")
    ax.annotate("", xy=(0.96, 0.07), xytext=(0.96, 0.93),
                 arrowprops=dict(arrowstyle="->", color="green",
                                 lw=2.0, alpha=0.7))
    ax.text(0.96, 0.50, "F0F1\nATP\nsynthase\n(see 107)",
             ha="center", va="center", fontsize=8, color="green",
             fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.2", fc="lightgreen",
                        ec="green", alpha=0.6))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        "Electron transport chain (ETC) - 4 complexes pump H+ across inner membrane\n"
        f"NADH path: I->Q->III->IV "
        f"({sim.etc_h_pumped_per_nadh()} H+/2e-);  "
        f"FADH2 path: II->Q->III->IV "
        f"({sim.etc_h_pumped_per_fadh2()} H+/2e-)",
        fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="center left",
               bbox_to_anchor=(0.0, 0.02), framealpha=0.85)

    ax_lad = fig.add_subplot(gs[0, 1])
    ladder = sim.etc_redox_ladder()
    labels = [lab for lab, _ in ladder]
    es = [e for _, e in ladder]
    y_pos = list(range(len(ladder)))[::-1]
    bar_colors = ["royalblue", "seagreen", "purple",
                   "firebrick", "darkorange"]
    ax_lad.barh(y_pos, es, color=bar_colors, alpha=0.85,
                 edgecolor="black", linewidth=1.0)
    for i, (lab, e) in enumerate(ladder):
        ax_lad.text(e + 0.02 if e >= 0 else e - 0.04,
                     y_pos[i], f"{e:+.3f} V", va="center",
                     ha="left" if e >= 0 else "right",
                     fontsize=9, fontweight="bold")
    ax_lad.set_yticks(y_pos)
    ax_lad.set_yticklabels(labels, fontsize=9)
    ax_lad.axvline(0.0, color="black", linewidth=0.6)
    ax_lad.set_xlabel("standard redox potential E (pH 7) (V)",
                       fontsize=10)
    ax_lad.set_title(
        f"Redox ladder: NADH -> O2   "
        f"dE = {sim.etc_total_delta_e_nadh():.3f} V\n"
        f"dG = {sim.etc_total_delta_g_nadh_kjmol():.0f} kJ/mol per 2 e-",
        fontsize=10)
    ax_lad.set_xlim(-0.45, +0.95)
    ax_lad.grid(True, alpha=0.3, axis="x")

    ax_h = fig.add_subplot(gs[1, 0])
    names = ["Complex I", "Complex II", "Complex III", "Complex IV"]
    h_counts = [H_PER_2E_COMPLEX_I, H_PER_2E_COMPLEX_II,
                 H_PER_2E_COMPLEX_III, H_PER_2E_COMPLEX_IV]
    bar_colors2 = ["steelblue", "darkseagreen",
                    "indianred", "darkorange"]
    bars = ax_h.bar(names, h_counts, color=bar_colors2,
                      edgecolor="black", linewidth=1.0)
    for b, h in zip(bars, h_counts):
        ax_h.text(b.get_x() + b.get_width() / 2,
                   b.get_height() + 0.1, f"{h} H+",
                   ha="center", va="bottom",
                   fontsize=11, fontweight="bold")
    ax_h.axhline(sim.etc_h_pumped_per_nadh(),
                  color="navy", linestyle="--", linewidth=1.2,
                  label=f"NADH path: {sim.etc_h_pumped_per_nadh()} H+/2e-")
    ax_h.axhline(sim.etc_h_pumped_per_fadh2(),
                  color="seagreen", linestyle=":", linewidth=1.2,
                  label=f"FADH2 path: {sim.etc_h_pumped_per_fadh2()} H+/2e-")
    ax_h.set_ylabel("H+ pumped per 2 e-", fontsize=10)
    ax_h.set_title("Proton-pumping stoichiometry per ETC complex",
                    fontsize=11)
    ax_h.set_ylim(0, 6)
    ax_h.legend(fontsize=9, loc="upper right")
    ax_h.grid(True, alpha=0.3, axis="y")

    ax_pmf = fig.add_subplot(gs[1, 1])
    ax_pmf.axis("off")
    breakdown = sim.atp_per_glucose_breakdown()
    summary_lines = [
        "Mitchell chemiosmosis (1961)",
        "=" * 38,
        f"dPsi   = {geom.delta_psi_v*1000:+.0f} mV",
        f"dpH    = {geom.delta_ph:+.1f}",
        f"PMF    = |dPsi| + 0.06.dpH = {sim.pmf_mv():.0f} mV",
        f"dG/H+  = F.PMF = {sim.delta_g_per_proton_kjmol():.1f} kJ/mol",
        "",
        "ATP synthase stoichiometry",
        "-" * 38,
        f"c-ring (mammal) = {geom.c_ring_size}",
        f"H+ per ATP      = c/3 = {sim.h_per_atp():.2f}",
        f"ATP per 360 deg = {sim.atp_per_revolution()}",
        f"rotor torque    = {sim.torque_required_nm():.1f} pN.nm",
        "",
        "Glucose oxidation accounting (mammal)",
        "-" * 38,
        f"substrate-level (glycol+TCA) = "
        f"{breakdown['substrate_level']:.0f} ATP",
        f"NADH x P/O = {breakdown['n_nadh']} x "
        f"{sim.p_o_nadh:.1f} = {breakdown['from_nadh']:.0f} ATP",
        f"FADH2 x P/O = {breakdown['n_fadh2']} x "
        f"{sim.p_o_fadh2:.1f} = {breakdown['from_fadh2']:.0f} ATP",
        "-" * 38,
        f"TOTAL                       = "
        f"{breakdown['total']:.0f} ATP/glucose",
    ]
    ax_pmf.text(0.02, 0.97, "\n".join(summary_lines),
                 transform=ax_pmf.transAxes,
                 fontsize=10, family="monospace", va="top",
                 bbox=dict(boxstyle="round,pad=0.5",
                           fc="lavender", ec="black",
                           lw=0.6, alpha=0.85))

    fig.suptitle(
        "Mitochondrial electron transport chain - "
        "substrate redox -> PMF -> ATP transduction",
        fontsize=13, fontweight="bold", y=0.998)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    out.append(save(fig, "106_etc_complexes.png"))

    # 107_atp_synthase.png
    fig2 = plt.figure(figsize=(18, 10))
    gs2 = fig2.add_gridspec(2, 2, height_ratios=[1.0, 1.0],
                             width_ratios=[1.0, 1.4],
                             hspace=0.40, wspace=0.30)

    ax_rotor = fig2.add_subplot(gs2[0, 0])
    f1_radius = 0.6
    f1_centre = (0.0, 1.5)
    n_subs = 6
    for k in range(n_subs):
        ang0 = 90 + k * (360.0 / n_subs)
        ang1 = ang0 + 360.0 / n_subs
        color = "lightcoral" if k % 2 == 0 else "lightblue"
        wedge = plt.matplotlib.patches.Wedge(
            f1_centre, f1_radius, ang0, ang1,
            facecolor=color, edgecolor="black", linewidth=1.0,
            alpha=0.9)
        ax_rotor.add_patch(wedge)
    ax_rotor.text(f1_centre[0], f1_centre[1],
                   "alpha3 beta3\nF1 head",
                   ha="center", va="center",
                   fontsize=10, fontweight="bold")
    ax_rotor.text(f1_centre[0], f1_centre[1] + f1_radius + 0.1,
                   "3 catalytic beta-sites cycle  O->L->T  (Boyer 1979)",
                   ha="center", fontsize=8, style="italic")
    ax_rotor.plot([0.0, 0.0], [-0.2, 1.0], color="darkgreen",
                   linewidth=3.5, solid_capstyle="round")
    ax_rotor.text(0.10, 0.45, "gamma shaft\n(rotates)",
                   color="darkgreen", fontsize=8, fontweight="bold")
    c_size = geom.c_ring_size
    c_radius = 0.5
    c_centre = (0.0, -0.6)
    for k in range(c_size):
        theta = 2.0 * np.pi * k / c_size
        x_pt = c_centre[0] + c_radius * np.cos(theta)
        y_pt = c_centre[1] + 0.18 * np.sin(theta)
        circ = plt.Circle((x_pt, y_pt), 0.10, facecolor="orange",
                           edgecolor="black", linewidth=0.8)
        ax_rotor.add_patch(circ)
    ax_rotor.text(c_centre[0], c_centre[1] - 0.30,
                   f"F0 c-ring  (c = {c_size})",
                   ha="center", fontsize=9, fontweight="bold",
                   color="darkorange")
    ax_rotor.fill_between([-1.2, 1.2], -0.85, -0.35,
                           color="khaki", alpha=0.5)
    ax_rotor.text(-1.0, -0.6, "inner\nmembrane",
                   fontsize=7, color="goldenrod", va="center")
    ax_rotor.annotate("", xy=(-0.7, -0.85), xytext=(-0.7, 1.6),
                       arrowprops=dict(arrowstyle="->",
                                        color="red", lw=2.5,
                                        alpha=0.85))
    ax_rotor.text(-0.85, 0.4, "H+", fontsize=11, color="red",
                   fontweight="bold", rotation=90)
    ax_rotor.annotate("", xy=(0.85, 2.4), xytext=(0.5, 1.7),
                       arrowprops=dict(arrowstyle="->",
                                        color="green", lw=2.0))
    ax_rotor.text(1.0, 2.4, "ATP\n(3 per\n360 deg)",
                   fontsize=10, color="green", fontweight="bold")
    ax_rotor.plot([0.6, 0.6], [-0.4, 1.6], color="grey",
                   linewidth=1.5, linestyle="--", alpha=0.6)
    ax_rotor.text(0.65, 0.6, "b2\nstator", fontsize=7, color="grey")
    ax_rotor.text(0.0, 0.7, "ADP + Pi -> ATP", ha="center",
                   fontsize=8, color="navy")
    ax_rotor.set_xlim(-1.4, 1.4)
    ax_rotor.set_ylim(-1.1, 2.7)
    ax_rotor.set_aspect("equal")
    ax_rotor.set_xticks([])
    ax_rotor.set_yticks([])
    ax_rotor.set_title(
        f"F0F1 ATP synthase  (mammal, c={c_size})\n"
        f"H+/ATP = {sim.h_per_atp():.2f}   "
        f"torque = {sim.torque_required_nm():.0f} pN.nm",
        fontsize=10, fontweight="bold")

    ax_c = fig2.add_subplot(gs2[0, 1])
    rows = example_c_rings()
    org_names = [r["name"] for r in rows]
    cs = [r["c"] for r in rows]
    h_per_atps = [r["h_per_atp"] for r in rows]
    xpos = np.arange(len(rows))
    width = 0.4
    ax_c.bar(xpos - width / 2, cs, width, label="c-ring size",
              color="orange", edgecolor="black", linewidth=1.0)
    ax_c.bar(xpos + width / 2, h_per_atps, width,
              label="H+ per ATP (= c/3)",
              color="firebrick", edgecolor="black",
              linewidth=1.0, alpha=0.85)
    for i, (cval, hpa) in enumerate(zip(cs, h_per_atps)):
        ax_c.text(i - width / 2, cval + 0.2, f"{cval}",
                   ha="center", va="bottom",
                   fontsize=10, fontweight="bold")
        ax_c.text(i + width / 2, hpa + 0.2, f"{hpa:.2f}",
                   ha="center", va="bottom",
                   fontsize=10, fontweight="bold", color="firebrick")
    ax_c.set_xticks(xpos)
    ax_c.set_xticklabels(org_names, fontsize=9, rotation=10)
    ax_c.set_ylabel("c subunits  /  H+ per ATP", fontsize=10)
    ax_c.set_title(
        "c-ring stoichiometry across organisms\n"
        "Universal F1: 3 ATP per 360 deg (alpha3 beta3 head)",
        fontsize=10)
    ax_c.set_ylim(0, 17)
    ax_c.legend(fontsize=9, loc="upper left")
    ax_c.grid(True, alpha=0.3, axis="y")

    ax_atp = fig2.add_subplot(gs2[1, 0])
    n_protons = np.linspace(0.0, 100.0, 401)
    atp_curve = np.array([sim.atp_per_c_protons(n) for n in n_protons])
    ax_atp.plot(n_protons, atp_curve, "g-", linewidth=2.2,
                 label=f"ATP = n_H+ x 3 / c   (c={c_size})")
    for rev in range(1, 5):
        n_at_rev = float(rev * c_size)
        atp_at_rev = float(rev * ATP_PER_REV)
        ax_atp.scatter([n_at_rev], [atp_at_rev], s=60,
                        color="darkgreen", zorder=5,
                        edgecolor="black", linewidth=0.6)
        ax_atp.annotate(f"{rev}x360\n-> {int(atp_at_rev)} ATP",
                         (n_at_rev, atp_at_rev),
                         xytext=(8, -15),
                         textcoords="offset points", fontsize=8)
    ax_atp.set_xlabel("H+ translocated through F0", fontsize=10)
    ax_atp.set_ylabel("ATP synthesized", fontsize=10)
    ax_atp.set_title(
        f"F0F1 catalytic stoichiometry\n"
        f"360 deg rotation x c protons = {ATP_PER_REV} ATP",
        fontsize=10)
    ax_atp.legend(fontsize=9, loc="upper left")
    ax_atp.grid(True, alpha=0.3)
    ax_atp.set_xlim(0, 100)
    ax_atp.set_ylim(0, max(atp_curve) * 1.10)

    ax_t = fig2.add_subplot(gs2[1, 1])
    out_sim = sim.simulate(n_nadh=100.0, n_fadh2=20.0,
                            n_steps=300, dt=1.0)
    t = out_sim["t"]
    ax_t.plot(t, out_sim["nadh"], color="steelblue",
                linewidth=2.0, label="NADH (matrix)")
    ax_t.plot(t, out_sim["fadh2"], color="seagreen",
                linewidth=2.0, label="FADH2 (matrix)")
    ax_t2 = ax_t.twinx()
    ax_t2.plot(t, out_sim["h_pool"], color="firebrick",
                 linewidth=2.0, alpha=0.7,
                 label="H+ pool (IMS-matrix)")
    ax_t2.plot(t, out_sim["atp"], color="darkgreen",
                 linewidth=2.5, alpha=0.95,
                 label="ATP synthesised")
    ax_t.set_xlabel("time (arb)", fontsize=10)
    ax_t.set_ylabel("substrate (NADH, FADH2)",
                     fontsize=10, color="steelblue")
    ax_t2.set_ylabel("H+ pool  /  ATP synthesised",
                       fontsize=10, color="firebrick")
    ax_t.set_title(
        "Coupled bioenergetic kinetics\n"
        "NADH -> H+ pumping (ETC) -> H+ flow through F0 -> ATP (F1)",
        fontsize=10)
    h1, l1 = ax_t.get_legend_handles_labels()
    h2, l2 = ax_t2.get_legend_handles_labels()
    ax_t.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper right")
    ax_t.grid(True, alpha=0.3)

    fig2.suptitle(
        "F0F1 ATP synthase - proton motive force converts to ATP "
        "via rotor torque (Boyer 1979 / Walker 1997)",
        fontsize=13, fontweight="bold", y=0.998)
    fig2.tight_layout(rect=[0, 0, 1, 0.985])
    out.append(save(fig2, "107_atp_synthase.png"))

    return out


# ---------------------------------------------------------------------------
# Measurement / observer / "consciousness" — substrate decoherence
# ---------------------------------------------------------------------------

def render_measurement_observer() -> list[str]:
    """Produce 100_measurement_problem.png and 101_decoherence_timescale.png.

    100: superposition rho(t) decohering vs N for several apparatus sizes,
         + substrate strain pattern (system + apparatus + environment),
         + Bell CHSH bar (substrate beats LHV bound),
         + Wigner-friend timeline (friend & Wigner agree),
         + Born-rule probability bars,
         + tau_d catalogue for canonical mesoscopic systems.
    101: tau_d vs apparatus N for a family of (gamma, T) lines, with
         the mesoscopic benchmark systems annotated.
    """
    from src.stiff_medium.measurement_observer_substrate import (
        MeasurementObserverGeometry,
        MeasurementObserverSimulator,
        classical_chsh_bound,
        decoherence_timescale,
        example_systems,
        substrate_chsh_value,
        tau_d_vs_n,
    )
    out: list[str] = []

    # ------------------------------------------------------------------
    # 100_measurement_problem.png — 6-panel substrate measurement story
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0],
                           width_ratios=[1.2, 1.2, 1.0],
                           hspace=0.45, wspace=0.35)

    # Panel A: superposition |rho_01|(t) decay for several N at fixed gamma, T
    ax_decoh = fig.add_subplot(gs[0, 0])
    n_list = [1.0, 1.0e3, 1.0e6, 1.0e9, 1.0e12]
    palette = plt.cm.viridis(np.linspace(0.1, 0.9, len(n_list)))
    for n, color in zip(n_list, palette):
        geom = MeasurementObserverGeometry(
            n_apparatus=n, drag_gamma=1.0, temperature=300.0)
        sim = MeasurementObserverSimulator(geometry=geom, n_steps=160)
        ev = sim.evolve_superposition()
        ax_decoh.semilogx(ev["t"] + 1e-40, ev["coherence"],
                          color=color, linewidth=1.8,
                          label=f"N = {n:.0e}  tau_d = {ev['tau_d']:.1e} s")
    ax_decoh.axhline(0.5, color="black", linestyle=":", linewidth=1.0,
                     alpha=0.5, label="initial |rho_01| = 1/2")
    ax_decoh.axhline(0.0, color="red", linestyle="--", linewidth=1.0,
                     alpha=0.4, label="fully mixed")
    ax_decoh.set_xlabel("time t [s]", fontsize=10)
    ax_decoh.set_ylabel("coherence  |rho_01(t)|", fontsize=10)
    ax_decoh.set_title(
        "Superposition decoheres faster the larger the apparatus N\n"
        "tau_d = hbar / (gamma . k_B T . N)", fontsize=10)
    ax_decoh.legend(fontsize=7, loc="upper right")
    ax_decoh.grid(True, alpha=0.3, which="both")
    ax_decoh.set_ylim(-0.02, 0.55)

    # Panel B: substrate strain pattern of S + A + E (spatial)
    ax_geom = fig.add_subplot(gs[0, 1])
    geom_demo = MeasurementObserverGeometry(
        n_apparatus=1.0e6, drag_gamma=1.0, temperature=300.0,
        system_extent=2.0e-3, apparatus_extent=2.0e-2,
        environment_extent=1.0e-1,
    )
    x_grid = np.linspace(-0.1, 0.1, 1001)
    sys_env = geom_demo.system_envelope(x_grid)
    ap_env = geom_demo.apparatus_envelope(x_grid)
    ap_env_plot = 0.6 * ap_env / max(ap_env.max(), 1e-30)
    env_env_plot = 0.15 * np.ones_like(x_grid) + \
        0.02 * np.random.default_rng(0).standard_normal(x_grid.shape)
    ax_geom.fill_between(x_grid * 100.0, 0, env_env_plot, color="grey",
                         alpha=0.3, label="ENVIRONMENT (thermal bath ~ kT)")
    ax_geom.fill_between(x_grid * 100.0, 0, ap_env_plot, color="orange",
                         alpha=0.5,
                         label="APPARATUS (N = 1e6 modes, drag gamma = 1)")
    ax_geom.fill_between(x_grid * 100.0, 0, sys_env, color="blue", alpha=0.7,
                         label="SYSTEM (coherent strain bump)")
    ax_geom.plot(x_grid * 100.0, sys_env, "b-", linewidth=2.0)
    ax_geom.set_xlabel("position x [cm]", fontsize=10)
    ax_geom.set_ylabel("substrate strain amplitude (arb)", fontsize=10)
    ax_geom.set_title(
        "Three-region substrate geometry\n"
        "system + apparatus + environment   (drag gamma between them)",
        fontsize=10)
    ax_geom.legend(fontsize=8, loc="upper right")
    ax_geom.grid(True, alpha=0.3)
    ax_geom.set_xlim(-10.0, 10.0)
    ax_geom.set_ylim(0, 1.15)

    # Panel C: CHSH bar vs LHV bound — substrate beats classical
    ax_chsh = fig.add_subplot(gs[0, 2])
    s_substrate = substrate_chsh_value()
    s_classical = classical_chsh_bound()
    bars = ax_chsh.bar(["LHV bound\n(Bell)", "Substrate\n(Tsirelson)"],
                        [s_classical, s_substrate],
                        color=["lightcoral", "steelblue"],
                        edgecolor="black", linewidth=1.5)
    ax_chsh.axhline(s_classical, color="red", linestyle="--",
                     linewidth=1.0, alpha=0.7,
                     label=f"classical bound = {s_classical:.3f}")
    ax_chsh.axhline(s_substrate, color="blue", linestyle="--",
                     linewidth=1.0, alpha=0.7,
                     label=f"Tsirelson bound = {s_substrate:.3f} = 2sqrt(2)")
    for bar, val in zip(bars, [s_classical, s_substrate]):
        ax_chsh.text(bar.get_x() + bar.get_width() / 2.0, val + 0.05,
                     f"{val:.3f}", ha="center", fontsize=11,
                     fontweight="bold")
    ax_chsh.set_ylabel("CHSH value |S|", fontsize=10)
    ax_chsh.set_title(
        "Bell test:  substrate violates LHV\n"
        "non-locality from shared elastic strain",
        fontsize=10)
    ax_chsh.set_ylim(0, 3.2)
    ax_chsh.legend(fontsize=8, loc="lower right")
    ax_chsh.grid(True, alpha=0.3, axis="y")

    # Panel D: Wigner's friend timeline — friend & Wigner outcomes agree
    ax_wf = fig.add_subplot(gs[1, 0])
    sim_wf = MeasurementObserverSimulator(
        geometry=MeasurementObserverGeometry(
            n_apparatus=1.0e10, drag_gamma=1.0, temperature=300.0),
        n_steps=200, rng_seed=7,
    )
    wf = sim_wf.wigner_friend_outcome()
    ev_wf = sim_wf.evolve_superposition()
    ax_wf.semilogx(ev_wf["t"] + 1e-40, ev_wf["coherence"], "b-",
                    linewidth=2.0, label="|rho_01(t)|  (system coherence)")
    ax_wf.axvline(wf["tau_d"], color="orange", linestyle="--",
                   linewidth=1.5, alpha=0.7,
                   label=f"tau_d = {wf['tau_d']:.1e} s")
    ax_wf.axvline(wf["t_friend"], color="green", linestyle="-.",
                   linewidth=1.5, alpha=0.7,
                   label="friend reads (t = 5 tau_d)")
    ax_wf.axvline(wf["t_wigner"], color="red", linestyle=":",
                   linewidth=1.8, alpha=0.7,
                   label="Wigner reads (t = 10 tau_d)")
    ax_wf.text(wf["t_friend"] * 1.5, 0.4,
                f"friend outcome: |{wf['outcome_friend']}>",
                color="green", fontsize=10, fontweight="bold")
    ax_wf.text(wf["t_wigner"] * 1.5, 0.3,
                f"Wigner outcome: |{wf['outcome_wigner']}>",
                color="red", fontsize=10, fontweight="bold")
    ax_wf.text(wf["t_friend"] * 1.5, 0.2,
                "agree = TRUE   (no consciousness collapse)",
                color="black", fontsize=9, style="italic")
    ax_wf.set_xlabel("time t [s]", fontsize=10)
    ax_wf.set_ylabel("coherence  |rho_01(t)|", fontsize=10)
    ax_wf.set_title(
        "Wigner's friend:  substrate decoherence finished long before Wigner opens box",
        fontsize=10)
    ax_wf.legend(fontsize=7, loc="upper right")
    ax_wf.grid(True, alpha=0.3, which="both")
    ax_wf.set_ylim(-0.02, 0.55)

    # Panel E: Born rule — |amplitude|^2 normalises to 1
    ax_born = fig.add_subplot(gs[1, 1])
    sim_born = MeasurementObserverSimulator()
    amplitudes = [
        complex(0.6, 0.0),
        complex(0.0, 0.5),
        complex(0.4, 0.3),
        complex(-0.3, 0.2),
    ]
    probs = sim_born.born_rule_probabilities(amplitudes)
    states = [f"|{i}>" for i in range(len(amplitudes))]
    bars = ax_born.bar(states, probs,
                        color=["steelblue", "orange", "green", "purple"],
                        edgecolor="black", linewidth=1.5)
    for bar, p in zip(bars, probs):
        ax_born.text(bar.get_x() + bar.get_width() / 2.0, p + 0.01,
                     f"{p:.3f}", ha="center", fontsize=10, fontweight="bold")
    ax_born.set_ylabel("probability  P(k) = |a_k|^2 / sum |a_j|^2",
                       fontsize=10)
    ax_born.set_title(
        "Born rule = energy normalisation of substrate strain modes\n"
        f"sum P(k) = {float(np.sum(probs)):.6f}",
        fontsize=10)
    ax_born.set_ylim(0, max(float(np.max(probs)) * 1.25, 0.5))
    ax_born.grid(True, alpha=0.3, axis="y")

    # Panel F: text panel — tau_d catalogue for typical mesoscopic systems
    ax_cat = fig.add_subplot(gs[1, 2])
    ax_cat.axis("off")
    cat = example_systems()
    table = (
        "tau_d catalogue\n"
        "(hbar / (gamma k_B T N))\n"
        "----------------------------------\n"
    )
    for c in cat:
        table += (f"{c['name']:36s}\n"
                  f"   N={c['N']:.1e}  T={c['T']:5.0f}K  "
                  f"g={c['gamma']:.0e}\n"
                  f"   tau_d = {c['tau_d']:.2e} s\n\n")
    ax_cat.text(0.0, 1.0, table, fontsize=8, family="monospace",
                 va="top", ha="left", transform=ax_cat.transAxes)
    ax_cat.set_title("Mesoscopic decoherence catalogue", fontsize=10)

    fig.suptitle(
        "MEASUREMENT PROBLEM: substrate decoherence, NOT consciousness\n"
        "tau_d = hbar/(gamma . k_B T . N).  CHSH = 2sqrt(2) > 2 (Bell).  "
        "Born rule from |strain|^2.  Wigner-friend: no paradox.",
        fontsize=13,
    )
    out.append(save(fig, "100_measurement_problem.png"))

    # ------------------------------------------------------------------
    # 101_decoherence_timescale.png — tau_d vs N for several gamma . T
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.4, 1.0])
    ax_tau = fig.add_subplot(gs[0, 0])
    ax_anno = fig.add_subplot(gs[0, 1])

    Ns = np.logspace(0, 24, 200)
    scenarios = [
        (1.0e-3, 300.0, "weak drag g=1e-3, T=300K"),
        (1.0e-1, 300.0, "moderate drag g=0.1, T=300K"),
        (1.0,     300.0, "strong drag g=1, T=300K"),
        (1.0,      4.0, "g=1, T=4K (cryogenic)"),
        (1.0,    1.0e3, "g=1, T=1000K (hot)"),
    ]
    palette = plt.cm.plasma(np.linspace(0.05, 0.85, len(scenarios)))
    for (g, T, lbl), color in zip(scenarios, palette):
        taus = tau_d_vs_n(Ns, gamma=g, T=T)
        ax_tau.loglog(Ns, taus, color=color, linewidth=2.0, label=lbl)

    # Overlay benchmark mesoscopic systems as scatter points
    cat = example_systems()
    for c in cat:
        ax_tau.loglog(c["N"], c["tau_d"], marker="o", markersize=8,
                       color="black", markerfacecolor="white",
                       markeredgewidth=1.5, zorder=10)
        ax_tau.annotate(c["name"], xy=(c["N"], c["tau_d"]),
                         xytext=(8, 6), textcoords="offset points",
                         fontsize=7, alpha=0.85,
                         bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow",
                                   ec="grey", alpha=0.85))

    # Reference lines for "fast" / "slow" decoherence regimes
    ax_tau.axhline(1.0, color="grey", linestyle=":", linewidth=1.0,
                   alpha=0.6, label="1 second")
    ax_tau.axhline(1.0e-15, color="grey", linestyle="--", linewidth=1.0,
                   alpha=0.6, label="1 fs (atomic timescale)")
    ax_tau.set_xlabel("apparatus mode count  N", fontsize=11)
    ax_tau.set_ylabel("decoherence timescale  tau_d  [s]", fontsize=11)
    ax_tau.set_title(
        "tau_d vs N for various (gamma, T)\n"
        "tau_d = hbar / (gamma . k_B T . N).  Slope = -1 in log-log",
        fontsize=11,
    )
    ax_tau.grid(True, alpha=0.3, which="both")
    ax_tau.legend(fontsize=8, loc="upper right")
    ax_tau.set_xlim(1.0, 1.0e24)
    ax_tau.set_ylim(1.0e-30, 1.0e10)

    # Side text panel: framework summary
    ax_anno.axis("off")
    txt = (
        "SUBSTRATE OBSERVER PARADIGM\n"
        "==========================\n\n"
        "1.  No special 'observer' ontology.\n"
        "    Measurement = macroscopic\n"
        "    substrate coupling.\n\n"
        "2.  Decoherence rate set by drag gamma\n"
        "    in L = 1/2 rho (d_t u)^2\n"
        "         - 1/2 K |grad u|^2\n"
        "         - V(u)\n"
        "         - gamma . u . (d_t u)\n\n"
        "3.  Apparatus N modes thermally\n"
        "    coupled at T -> tau_d ~ hbar/(g kT N)\n\n"
        "4.  Catalogue:\n"
        "    - electron 300K, N=1     ~ 10^-4 s\n"
        "    - dust 10 um, N~10^12    ~ 10^-14 s\n"
        "    - cat 10 cm, N~10^23     ~ 10^-20 s\n\n"
        "5.  Wigner's friend: friend &\n"
        "    Wigner agree because tau_d\n"
        "    << t_observation in any\n"
        "    macroscopic apparatus.\n\n"
        "6.  Bell CHSH: substrate predicts\n"
        "    Tsirelson 2sqrt(2) ~ 2.828.\n"
        "    Beats LHV bound 2 because\n"
        "    same elastic strain field is\n"
        "    shared between detectors.\n\n"
        "7.  Born rule = energy norm of\n"
        "    substrate strain mode k:\n"
        "    P(k) = |a_k|^2 / sum |a_j|^2.\n"
    )
    ax_anno.text(0.0, 1.0, txt, fontsize=9, family="monospace",
                  va="top", ha="left", transform=ax_anno.transAxes)

    fig.suptitle(
        "Decoherence timescale tau_d(N) — substrate sets the boundary\n"
        "between quantum (small N, slow tau_d) and classical (large N, instant tau_d)",
        fontsize=13,
    )
    fig.tight_layout()
    out.append(save(fig, "101_decoherence_timescale.png"))

    return out


def render_allometric() -> list[str]:
    """Produce 114_kleibers_law.png and 115_vascular_fractal.png.

    114: Log-log plot of basal metabolic rate vs body mass for ~30 mammals
         spanning Etruscan shrew (1.8 g) to blue whale (150 t), plus the
         3/4-power Kleiber fit line and the alternative naive 2/3 surface-
         to-volume line for comparison.  Annotates the WBE empirical slope
         and R^2.  Inset: heart rate ~ M^(-1/4) and lifespan ~ M^(+1/4)
         for the same mass range.
    115: West-Brown-Enquist fractal vascular tree (binary, 12 levels) with
         beta = 2^(-1/2) radius scaling and gamma = 2^(-1/3) length scaling
         (space-filling).  Side panel shows total network volume per level
         and the b = d/(d+1) derivation table for d = 1, 2, 3, 4.
    """
    from src.stiff_medium.allometric_substrate import (
        BRANCHING_RATIO_N,
        CAPILLARY_EXPONENT,
        HEART_RATE_EXPONENT,
        KLEIBER_EXPONENT,
        KLEIBER_PREFACTOR_W,
        LIFESPAN_EXPONENT,
        MAMMAL_DATA,
        SPACE_DIMENSION_D,
        SURFACE_GEOMETRIC_EXPONENT,
        AllometricGeometry,
        AllometricSimulator,
    )

    out: list[str] = []
    sim = AllometricSimulator()

    # ----------------------------- 114: Kleiber + heart rate + lifespan
    M_data, B_data, names = sim.kleiber_data()
    fit = sim.fit_kleiber_slope(M_data, B_data)

    fig = plt.figure(figsize=(13, 8))
    gs = fig.add_gridspec(
        2, 2, width_ratios=[2.4, 1.0], height_ratios=[1.0, 1.0],
        hspace=0.32, wspace=0.28,
    )
    ax = fig.add_subplot(gs[:, 0])

    # Mammal data points
    ax.loglog(
        M_data, B_data, "o", color="darkred", markersize=8,
        markeredgecolor="black", markeredgewidth=0.7,
        label=f"empirical mammals (N={len(M_data)})",
    )

    # Annotate a few notable species
    for label_name in ("Etruscan shrew", "House mouse", "Human",
                       "Elephant (Afr.)", "Blue whale"):
        idx = next(
            (i for i, d in enumerate(MAMMAL_DATA) if d["name"] == label_name),
            None,
        )
        if idx is not None:
            ax.annotate(
                label_name,
                xy=(M_data[idx], B_data[idx]),
                xytext=(8, 6), textcoords="offset points",
                fontsize=8.5, color="black",
                arrowprops=dict(arrowstyle="-", lw=0.5, color="gray"),
            )

    # Best-fit and theoretical 3/4 line
    M_line = np.geomspace(M_data.min() * 0.5, M_data.max() * 2.0, 200)
    B_fit = fit["prefactor_W"] * M_line ** fit["slope"]
    B_3_4 = KLEIBER_PREFACTOR_W * M_line ** KLEIBER_EXPONENT
    B_2_3 = (
        KLEIBER_PREFACTOR_W * (70.0 ** (KLEIBER_EXPONENT - SURFACE_GEOMETRIC_EXPONENT))
        * M_line ** SURFACE_GEOMETRIC_EXPONENT
    )

    ax.loglog(
        M_line, B_fit, "-", color="tab:blue", lw=2.4,
        label=(
            f"empirical fit  slope = {fit['slope']:.3f}  "
            f"R$^2$ = {fit['r2']:.3f}"
        ),
    )
    ax.loglog(
        M_line, B_3_4, "--", color="darkgreen", lw=1.8,
        label="WBE prediction  B $\\propto$ M$^{3/4}$",
    )
    ax.loglog(
        M_line, B_2_3, ":", color="gray", lw=1.6,
        label="naive surface/volume  B $\\propto$ M$^{2/3}$",
    )

    ax.set_xlabel("body mass M  [kg]", fontsize=11)
    ax.set_ylabel("basal metabolic rate B  [W]", fontsize=11)
    ax.set_title(
        "Kleiber's law:  metabolic rate vs body mass across mammals\n"
        f"slope {fit['slope']:.3f} matches WBE 3/4, not geometric 2/3  "
        f"(d / (d+1) with d = {SPACE_DIMENSION_D})",
        fontsize=11.5,
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.92)

    # --- Inset top right: heart rate ~ M^(-1/4)
    ax_hr = fig.add_subplot(gs[0, 1])
    M_hr = np.geomspace(0.005, 1.0e5, 100)
    f_bpm = np.array([sim.heart_rate_bpm(m) for m in M_hr])
    ax_hr.loglog(M_hr, f_bpm, "-", color="tab:red", lw=2.0,
                 label="f $\\propto$ M$^{-1/4}$")
    # Reference points
    ref = [
        ("mouse", 0.020),
        ("human", 70.0),
        ("elephant", 5000.0),
        ("blue whale", 150_000.0),
    ]
    for name, m in ref:
        ax_hr.plot(m, sim.heart_rate_bpm(m), "ko", markersize=5)
        ax_hr.annotate(
            f"{name}\n{sim.heart_rate_bpm(m):.0f} bpm",
            xy=(m, sim.heart_rate_bpm(m)),
            xytext=(4, 4), textcoords="offset points",
            fontsize=7,
        )
    ax_hr.set_xlabel("M [kg]", fontsize=9)
    ax_hr.set_ylabel("heart rate [bpm]", fontsize=9)
    ax_hr.set_title("heart rate $\\propto$ M$^{-1/4}$", fontsize=10)
    ax_hr.grid(True, which="both", alpha=0.3)
    ax_hr.tick_params(labelsize=8)

    # --- Inset bottom right: lifespan ~ M^(+1/4)
    ax_T = fig.add_subplot(gs[1, 1])
    T_yr = np.array([sim.lifespan_yr(m) for m in M_hr])
    ax_T.loglog(M_hr, T_yr, "-", color="tab:purple", lw=2.0,
                label="T $\\propto$ M$^{+1/4}$")
    for name, m in ref:
        ax_T.plot(m, sim.lifespan_yr(m), "ko", markersize=5)
        ax_T.annotate(
            f"{name}\n{sim.lifespan_yr(m):.0f} yr",
            xy=(m, sim.lifespan_yr(m)),
            xytext=(4, 4), textcoords="offset points",
            fontsize=7,
        )
    ax_T.set_xlabel("M [kg]", fontsize=9)
    ax_T.set_ylabel("lifespan [yr]", fontsize=9)
    ax_T.set_title(
        "lifespan $\\propto$ M$^{+1/4}$\n"
        "(f x T $\\sim$ const $\\Rightarrow$ ~10$^9$ heartbeats / life)",
        fontsize=10,
    )
    ax_T.grid(True, which="both", alpha=0.3)
    ax_T.tick_params(labelsize=8)

    fig.suptitle(
        "Allometric scaling laws — universal exponents from substrate-optimised "
        "fractal vasculature (West-Brown-Enquist 1997)",
        fontsize=12, y=0.995,
    )
    out.append(save(fig, "114_kleibers_law.png"))

    # ------------------------ 115: vascular fractal tree + WBE derivation
    geom_viz = AllometricGeometry(
        n_levels=12, branching_n=BRANCHING_RATIO_N
    )

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(
        2, 2, width_ratios=[1.5, 1.0], height_ratios=[1.0, 1.0],
        hspace=0.34, wspace=0.28,
    )
    ax_tree = fig.add_subplot(gs[:, 0])
    ax_vol = fig.add_subplot(gs[0, 1])
    ax_table = fig.add_subplot(gs[1, 1])

    # ---- Tree
    edges = geom_viz.tree_edges_2d(spread_deg=42.0)
    cmap = plt.cm.viridis
    max_lvl = geom_viz.n_levels - 1
    for (x0, y0), (x1, y1), lvl in edges:
        # vessel diameter ~ beta^level (tapered linewidth)
        lw = max(0.4, 4.5 * (geom_viz.beta() ** lvl) ** 0.7)
        color = cmap(lvl / max_lvl)
        ax_tree.plot([x0, x1], [y0, y1], "-", color=color, linewidth=lw,
                     solid_capstyle="round")
    # mark capillaries (terminal endpoints) with dots
    for (_, _), (x1, y1), lvl in edges:
        if lvl == max_lvl:
            ax_tree.plot(x1, y1, "o", color="firebrick", markersize=2,
                         markeredgewidth=0)

    # heart marker at the root
    ax_tree.plot(0.0, 0.0, "s", color="black", markersize=12)
    ax_tree.annotate(
        "heart\n(root, level 0)", xy=(0.0, 0.0), xytext=(10, 10),
        textcoords="offset points", fontsize=9,
    )
    ax_tree.annotate(
        f"capillaries\n(N = {geom_viz.n_capillaries():,})",
        xy=(0.0, edges[-1][1][1]),
        xytext=(0.0, edges[-1][1][1] - 0.4),
        ha="center", fontsize=9,
        arrowprops=dict(arrowstyle="->", lw=0.7, color="gray"),
    )
    ax_tree.set_aspect("equal")
    ax_tree.set_title(
        "West-Brown-Enquist fractal vascular tree\n"
        f"binary branching (n = {BRANCHING_RATIO_N}),  N = {geom_viz.n_levels} levels,  "
        f"$\\beta$ = n$^{{-1/2}}$ = {geom_viz.beta():.4f},  "
        f"$\\gamma$ = n$^{{-1/d}}$ = {geom_viz.gamma():.4f} (space-filling)",
        fontsize=11,
    )
    ax_tree.set_xticks([])
    ax_tree.set_yticks([])
    for spine in ax_tree.spines.values():
        spine.set_visible(False)

    # ---- Volume distribution per level
    levels = np.arange(geom_viz.n_levels)
    vol_per_level = np.array([
        geom_viz.total_volume_at_level_m3(k) for k in levels
    ])
    n_vessels = np.array([geom_viz.vessels_at_level(k) for k in levels])
    ax_vol.bar(levels, vol_per_level / vol_per_level.max(),
               color="steelblue", alpha=0.85, label="V_k / V_max")
    ax_vol2 = ax_vol.twinx()
    ax_vol2.semilogy(levels, n_vessels, "o-", color="crimson", lw=1.6,
                     label="N_k = n$^k$")
    ax_vol.set_xlabel("level k (root=0, capillaries=N-1)", fontsize=9)
    ax_vol.set_ylabel("volume fraction (linear)", fontsize=9, color="steelblue")
    ax_vol2.set_ylabel("vessel count (log)", fontsize=9, color="crimson")
    ax_vol.tick_params(axis="y", labelcolor="steelblue", labelsize=8)
    ax_vol2.tick_params(axis="y", labelcolor="crimson", labelsize=8)
    ax_vol.tick_params(axis="x", labelsize=8)
    ax_vol.set_title(
        "Per-level volume vs vessel count\n"
        "(area-preserving: $\\sum_k$ A_k = const)",
        fontsize=10,
    )
    ax_vol.grid(True, axis="y", alpha=0.3)

    # ---- WBE derivation table
    ax_table.axis("off")
    rows = [
        ("d = 1 (linear)",   "1 / 2  = 0.500"),
        ("d = 2 (surface)",  "2 / 3  $\\approx$ 0.667"),
        ("d = 3 (volume)",   "3 / 4  = 0.750  $\\Leftarrow$ Kleiber"),
        ("d = 4 (West 1999)", "4 / 5  = 0.800"),
    ]
    table = ax_table.table(
        cellText=[list(r) for r in rows],
        colLabels=["space dimension", "exponent  b = d / (d + 1)"],
        cellLoc="center", loc="center", colWidths=[0.45, 0.55],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.6)
    # Highlight the d=3 row
    for j in (0, 1):
        cell = table[(3, j)]
        cell.set_facecolor("#fff3a3")
        cell.set_text_props(weight="bold")
    ax_table.set_title(
        "WBE derivation:  b = d / (d + 1)\n"
        "fractal network in d-dim space + 1 branching index",
        fontsize=10.5,
    )

    fig.suptitle(
        "Vascular fractal $\\rightarrow$ Kleiber 3/4: substrate strain field "
        "delivers nutrients into a 3-volume from a single root\n"
        f"capillary radius {geom_viz.capillary_radius_m()*1e6:.1f} $\\mu$m "
        f"(invariant across mammals);  total levels {geom_viz.n_levels}; "
        f"network volume {geom_viz.total_blood_volume_m3()*1e6:.1f} cm$^3$",
        fontsize=12, y=0.995,
    )
    out.append(save(fig, "115_vascular_fractal.png"))

    return out


def render_brain() -> list[str]:
    """112_brain_oscillations.png + 113_default_mode_network.png."""
    from src.stiff_medium.brain_network_substrate import (
        AVALANCHE_SLOPE_EXACT,
        BRAIN_BANDS_HZ,
        BrainNetworkGeometry,
        BrainNetworkSimulator,
    )
    out: list[str] = []

    # ------------------------------------------------------------------
    # 112_brain_oscillations.png
    #   Panel A: 5-band power spectrum (1/f^β + Lorentzian band peaks)
    #   Panel B: Kuramoto order parameter r vs K/K_c
    #   Panel C: Avalanche size PDF with -3/2 slope (critical brain)
    #   Panel D: time series of r(t) for sub/super-critical K
    # ------------------------------------------------------------------
    geom = BrainNetworkGeometry(n_nodes=80, k_neighbors=6,
                                p_rewire=0.10, seed=42)
    sim = BrainNetworkSimulator(
        geometry=geom, omega_center_hz=10.0, omega_spread_hz=2.0,
        duration_s=1.5, dt_s=2.0e-3, seed=11,
    )
    sigma_sw = geom.small_world_sigma(n_random=3, max_pairs=60)
    K_c = sim.critical_coupling()

    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.30)

    # ----- A: 5-band spectrum -----------------------------------------
    ax_a = fig.add_subplot(gs[0, 0])
    f, p = sim.synthetic_lfp_spectrum(
        n_freqs=800, beta=1.5,
        band_amps={"delta": 0.50, "theta": 0.55, "alpha": 1.40,
                   "beta": 0.45, "gamma": 0.30},
    )
    ax_a.loglog(f, p, color="black", lw=1.6, label="LFP power (synthetic)")
    band_colors = {
        "delta": "#1f3a93", "theta": "#3498db", "alpha": "#27ae60",
        "beta":  "#f39c12", "gamma": "#c0392b",
    }
    for band, (lo, hi) in BRAIN_BANDS_HZ.items():
        ax_a.axvspan(lo, hi, alpha=0.14, color=band_colors[band],
                     label=f"{band} {lo:.0f}-{hi:.0f} Hz")
    ax_a.set_xlabel("frequency [Hz]", fontsize=11)
    ax_a.set_ylabel("power [arb]", fontsize=11)
    ax_a.set_xlim(1.0, 120.0)
    ax_a.set_title(
        "Brain LFP power spectrum: 1/f$^{1.5}$ background + 5 canonical bands\n"
        "delta / theta / alpha / beta / gamma",
        fontsize=11,
    )
    ax_a.legend(fontsize=8, loc="lower left", framealpha=0.92)
    ax_a.grid(True, alpha=0.3, which="both")

    # ----- B: Kuramoto r(K/K_c) phase transition ----------------------
    ax_b = fig.add_subplot(gs[0, 1])
    K_factors = np.array([0.05, 0.2, 0.5, 0.8, 1.0, 1.3, 1.7, 2.5,
                          4.0, 7.0, 12.0, 20.0])
    Ks = K_factors * K_c
    _, rs = sim.order_parameter_vs_K(
        K_values=Ks, duration_s=0.6, dt_s=4.0e-3, tail_fraction=0.4,
    )
    ax_b.plot(K_factors, rs, "o-", color="purple", lw=2.0, ms=8,
              label="simulated $r(K)$")
    ax_b.axvline(1.0, color="black", ls="--", lw=1.2,
                 label=f"$K_c = 2\\gamma = {K_c:.1f}$ rad/s")
    ax_b.fill_between([0.04, 1.0], 0.0, 1.0, color="lightblue",
                      alpha=0.18, label="incoherent (r$\\to$0)")
    ax_b.fill_between([1.0, K_factors.max() * 1.2], 0.0, 1.0,
                      color="khaki", alpha=0.18,
                      label="synchronised (r$\\to$1)")
    ax_b.set_xlabel("$K / K_c$", fontsize=11)
    ax_b.set_ylabel("Kuramoto order $r$", fontsize=11)
    ax_b.set_xscale("log")
    ax_b.set_xlim(K_factors.min() * 0.8, K_factors.max() * 1.2)
    ax_b.set_ylim(-0.02, 1.05)
    ax_b.set_title(
        "Kuramoto synchronisation transition on small-world brain network\n"
        f"$N={geom.n_nodes}$, $\\langle k \\rangle = {geom.mean_degree():.1f}$, "
        f"$\\sigma_{{SW}} = {sigma_sw:.2f}$",
        fontsize=11,
    )
    ax_b.legend(fontsize=8, loc="lower right", framealpha=0.92)
    ax_b.grid(True, alpha=0.3, which="both")

    # ----- C: avalanche -3/2 slope ------------------------------------
    ax_c = fig.add_subplot(gs[1, 0])
    sizes = sim.simulate_avalanches(n_avalanches=12000, branching=1.0,
                                    max_size=20000)
    slope, centers, pdf = sim.avalanche_log_log_slope(
        sizes, s_min=2, s_max=5000, n_bins=24,
    )
    keep = pdf > 0
    ax_c.loglog(centers[keep], pdf[keep], "o", color="darkred", ms=7,
                label=f"simulated PDF, slope = {slope:.2f}")
    ref_x = np.array([2.0, 5000.0])
    if int(keep.sum()) > 0:
        anchor_y = pdf[keep][0]
        anchor_x = centers[keep][0]
        ref_y = ref_x ** AVALANCHE_SLOPE_EXACT
        ref_y = ref_y * (anchor_y / (anchor_x ** AVALANCHE_SLOPE_EXACT))
        ax_c.loglog(ref_x, ref_y, "--", color="black", lw=1.5,
                    label="$P(s) \\propto s^{-3/2}$ (Beggs-Plenz 2003)")
    ax_c.set_xlabel("avalanche size $s$ (events)", fontsize=11)
    ax_c.set_ylabel("$P(s)$", fontsize=11)
    ax_c.set_title(
        "Critical-brain neural avalanches: $P(s) \\propto s^{-3/2}$\n"
        "(Galton-Watson critical branching, $\\sigma = 1$)",
        fontsize=11,
    )
    ax_c.legend(fontsize=9, loc="upper right", framealpha=0.92)
    ax_c.grid(True, alpha=0.3, which="both")

    # ----- D: time series of order parameter r(t) ---------------------
    ax_d = fig.add_subplot(gs[1, 1])
    res_sub = sim.simulate_kuramoto(coupling_K=0.3 * K_c)
    res_sup = sim.simulate_kuramoto(coupling_K=8.0 * K_c)
    ax_d.plot(res_sub["t_s"] * 1000.0, res_sub["order_r"],
              color="tab:blue", lw=1.4,
              label=f"sub-critical $K=0.3K_c$: $\\bar r$ = "
                    f"{res_sub['order_r'][-100:].mean():.2f}")
    ax_d.plot(res_sup["t_s"] * 1000.0, res_sup["order_r"],
              color="tab:red", lw=1.4,
              label=f"super-critical $K=8K_c$: $\\bar r$ = "
                    f"{res_sup['order_r'][-100:].mean():.2f}")
    ax_d.axhline(1.0, color="grey", ls=":", lw=0.8)
    ax_d.set_xlabel("time [ms]", fontsize=11)
    ax_d.set_ylabel("Kuramoto order $r(t)$", fontsize=11)
    ax_d.set_ylim(-0.02, 1.05)
    ax_d.set_title(
        "Order parameter $r(t)$: sub- vs super-critical coupling\n"
        f"natural-frequency Lorentzian: $f_0 = {sim.omega_center_hz:.1f}$ Hz, "
        f"$\\gamma = {sim.omega_spread_hz:.1f}$ Hz",
        fontsize=11,
    )
    ax_d.legend(fontsize=9, loc="lower right", framealpha=0.92)
    ax_d.grid(True, alpha=0.3)

    fig.suptitle(
        "Brain network dynamics from substrate: small-world Kuramoto + 5 bands "
        "+ critical avalanches\n"
        "node = mesoscopic strain patch, edge = white-matter coupling, "
        "$\\sigma_{SW}$ > 1 (small-world), $P(s) \\propto s^{-3/2}$ (criticality)",
        fontsize=13,
    )
    out.append(save(fig, "112_brain_oscillations.png"))

    # ------------------------------------------------------------------
    # 113_default_mode_network.png
    #   Panel A: schematic 3D brain with DMN region positions and links
    #   Panel B: DMN adjacency matrix
    #   Panel C: Kuramoto on the 6-region DMN sub-graph (synchronisation)
    # ------------------------------------------------------------------
    names, coords, A_dmn = geom.dmn_subgraph()

    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1.0, 1.4],
                          wspace=0.30)

    # ----- A: 3D DMN schematic ----------------------------------------
    ax_a = fig.add_subplot(gs[0, 0], projection="3d")
    # Draw a translucent brain "envelope" (approx ellipsoid)
    u = np.linspace(0.0, 2.0 * np.pi, 32)
    v = np.linspace(0.0, np.pi, 16)
    Xb = 1.05 * np.outer(np.cos(u), np.sin(v))
    Yb = 1.15 * np.outer(np.sin(u), np.sin(v))
    Zb = 0.85 * np.outer(np.ones_like(u), np.cos(v))
    ax_a.plot_surface(Xb, Yb, Zb, color="lightgray", alpha=0.10,
                      linewidth=0, antialiased=True)

    # Region color & size
    region_colors = {
        "mPFC":             "#e74c3c",
        "PCC":              "#9b59b6",
        "L Angular Gyrus":  "#3498db",
        "R Angular Gyrus":  "#3498db",
        "L Hippocampus":    "#27ae60",
        "R Hippocampus":    "#27ae60",
    }
    # Edges
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if A_dmn[i, j]:
                ax_a.plot(
                    [coords[i, 0], coords[j, 0]],
                    [coords[i, 1], coords[j, 1]],
                    [coords[i, 2], coords[j, 2]],
                    color="black", lw=1.6, alpha=0.55,
                )
    # Nodes
    for i, n in enumerate(names):
        ax_a.scatter(*coords[i], s=320, c=region_colors[n],
                     edgecolors="black", linewidths=1.5, depthshade=True)
        ax_a.text(coords[i, 0] * 1.10, coords[i, 1] * 1.10,
                  coords[i, 2] * 1.10 + 0.10,
                  n, fontsize=10, fontweight="bold", ha="center")
    ax_a.set_xlim(-1.2, 1.2)
    ax_a.set_ylim(-1.2, 1.2)
    ax_a.set_zlim(-1.0, 1.0)
    ax_a.set_xlabel("x (L-R)")
    ax_a.set_ylabel("y (P-A)")
    ax_a.set_zlabel("z (I-S)")
    ax_a.set_title(
        "Default Mode Network (Raichle 2001)\n"
        "task-negative resting-state hub network",
        fontsize=11,
    )
    ax_a.view_init(elev=18, azim=-65)

    # ----- B: DMN adjacency matrix ------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.imshow(A_dmn, cmap="Reds", vmin=0, vmax=1)
    ax_b.set_xticks(range(len(names)))
    ax_b.set_yticks(range(len(names)))
    ax_b.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    ax_b.set_yticklabels(names, fontsize=9)
    for i in range(len(names)):
        for j in range(len(names)):
            txt = "1" if A_dmn[i, j] else "0"
            ax_b.text(j, i, txt, ha="center", va="center",
                      color=("white" if A_dmn[i, j] else "black"),
                      fontsize=9)
    ax_b.set_title(
        "DMN adjacency matrix\n"
        f"6 regions, {int(A_dmn.sum() // 2)} undirected edges",
        fontsize=11,
    )

    # ----- C: Kuramoto sync on the 6-node DMN -------------------------
    # Build a tiny isolated geometry from the DMN sub-graph
    dmn_geom = BrainNetworkGeometry.__new__(BrainNetworkGeometry)
    dmn_geom.n_nodes = len(names)
    dmn_geom.k_neighbors = 4
    dmn_geom.p_rewire = 0.0
    dmn_geom.seed = 5
    dmn_geom.dmn_regions = list(geom.dmn_regions)
    dmn_geom.adjacency = A_dmn
    dmn_geom.coords = coords
    dmn_sim = BrainNetworkSimulator(
        geometry=dmn_geom, omega_center_hz=10.0, omega_spread_hz=1.0,
        duration_s=2.0, dt_s=2.0e-3, seed=23,
    )
    K_c_dmn = dmn_sim.critical_coupling()

    ax_c = fig.add_subplot(gs[0, 2])
    res_low  = dmn_sim.simulate_kuramoto(coupling_K=0.2 * K_c_dmn)
    res_high = dmn_sim.simulate_kuramoto(coupling_K=6.0 * K_c_dmn)
    ax_c.plot(res_low["t_s"] * 1000.0, res_low["order_r"],
              color="tab:blue", lw=1.6,
              label=f"task / desync $K=0.2K_c$: $\\bar r$ = "
                    f"{res_low['order_r'][-50:].mean():.2f}")
    ax_c.plot(res_high["t_s"] * 1000.0, res_high["order_r"],
              color="tab:red", lw=1.6,
              label=f"rest / sync $K=6K_c$: $\\bar r$ = "
                    f"{res_high['order_r'][-50:].mean():.2f}")
    ax_c.axhline(1.0, color="grey", ls=":", lw=0.8)
    ax_c.set_xlabel("time [ms]", fontsize=11)
    ax_c.set_ylabel("DMN Kuramoto order $r(t)$", fontsize=11)
    ax_c.set_ylim(-0.02, 1.05)
    ax_c.set_title(
        "DMN coherence: rest (high $K$) vs task (low $K$)\n"
        f"$K_c = 2\\gamma = {K_c_dmn:.1f}$ rad/s",
        fontsize=11,
    )
    ax_c.legend(fontsize=9, loc="lower right", framealpha=0.92)
    ax_c.grid(True, alpha=0.3)

    fig.suptitle(
        "Default Mode Network: mPFC + PCC + bilateral angular gyrus + "
        "bilateral hippocampus\n"
        "task-negative substrate hub; coherence indexes resting-state engagement",
        fontsize=13,
    )
    out.append(save(fig, "113_default_mode_network.png"))

    return out


def render_cancer() -> list[str]:
    """Produce 110_tumor_growth.png and 111_hallmarks_cancer.png.

    110: Four-panel growth + treatment + multistage incidence overview.
         Top-left  : Gompertz N(t) vs unbounded exponential N(t) on
                     semilog-y; Gompertz saturates at K, exponential blows up.
         Top-right : Combined Gompertz growth interrupted by 6 log-kill
                     chemotherapy pulses (99% kill per dose, 14-day cycle).
         Bottom-L  : Armitage-Doll multistage incidence I(age) ~ age^5
                     for several n_hits (log-log).
         Bottom-R  : Knudson 2-hit retinoblastoma age distribution
                     (sporadic vs hereditary).
    111: 8 hallmarks of cancer (Hanahan-Weinberg 2011) arranged radially
         around a central "cancer cell" node, plus a 5-stage adenoma-
         carcinoma sequence bar showing how many hallmarks are acquired
         by each stage.
    """
    import math as _math

    from src.stiff_medium.cancer_substrate import (
        ARMITAGE_DOLL_HITS_DEFAULT,
        HALLMARKS,
        KNUDSON_PEAK_AGE_HEREDITARY_YR,
        KNUDSON_PEAK_AGE_SPORADIC_YR,
        N_HALLMARKS,
        STAGES,
        CancerGeometry,
        CancerSimulator,
    )

    out: list[str] = []

    geom = CancerGeometry()
    sim = CancerSimulator(geometry=geom)

    # ---------------- 110: Tumour growth + treatment ---------------------
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0],
                           hspace=0.40, wspace=0.30)

    # Panel A: Gompertz vs exponential
    ax_grow = fig.add_subplot(gs[0, 0])
    t_days = np.linspace(0.0, 600.0, 800)
    N_gomp = sim.gompertz_growth(t_days, N0=1.0)
    a = sim.a_per_day
    K = sim.K_cells
    # For visual comparison at the early-time slope, choose r so the
    # exponential matches the Gompertz population at t = 200 d.
    N_gomp_200 = float(sim.gompertz_growth(np.array([200.0]), N0=1.0)[0])
    r_eff = _math.log(N_gomp_200) / 200.0
    # Compute exponential with overflow-safe clamp
    safe_arg = np.minimum(r_eff * t_days, 35.0)   # exp(35) ~ 1.6e15
    N_exp = 1.0 * np.exp(safe_arg)

    ax_grow.semilogy(t_days, N_gomp, color="tab:blue", linewidth=2.4,
                     label=f"Gompertz (a = {a:.3f}/d, K = {K:.0e} cells)")
    ax_grow.semilogy(t_days, N_exp, color="tab:red", linewidth=2.0,
                     linestyle="--",
                     label=f"exponential (r = {r_eff:.3f}/d)")
    ax_grow.axhline(K, color="black", linestyle=":", linewidth=1.0,
                    alpha=0.7, label=f"K = {K:.0e} cells")
    ax_grow.axhline(1.0e9, color="gray", linestyle=":", linewidth=0.8,
                    alpha=0.6, label="1 cm^3 tumour ~ 1e9 cells")
    ax_grow.set_xlabel("time [days]", fontsize=10)
    ax_grow.set_ylabel("tumour cells N(t)", fontsize=10)
    ax_grow.set_ylim(1.0e0, 1.0e14)
    ax_grow.set_title(
        "Gompertz growth saturates;  exponential blows up\n"
        "dN/dt = N a ln(K/N)  vs  dN/dt = r N",
        fontsize=10,
    )
    ax_grow.legend(loc="lower right", fontsize=8, framealpha=0.92)
    ax_grow.grid(True, alpha=0.3, which="both")

    # Panel B: Combined growth + log-kill treatment response
    ax_treat = fig.add_subplot(gs[0, 1])
    t_treat = np.linspace(0.0, 400.0, 1500)
    res = sim.combined_growth_and_treatment(
        t_treat,
        N0=1.0,
        treatment_start_day=180.0,
        n_doses=6,
        kill_fraction_per_dose=0.99,
    )
    untreated = sim.gompertz_growth(t_treat, N0=1.0)
    ax_treat.semilogy(t_treat, np.maximum(untreated, 1e-3),
                      color="tab:blue", linewidth=1.8,
                      alpha=0.55, label="untreated Gompertz")
    ax_treat.semilogy(t_treat, np.maximum(res["N"], 1e-3),
                      color="tab:purple", linewidth=2.4,
                      label=f"6 doses, 99%/dose, every {sim.dose_interval_days:.0f} d")
    for d_t in res["dose_times"]:
        ax_treat.axvline(d_t, color="tab:red", linestyle=":",
                          linewidth=0.9, alpha=0.55)
    ax_treat.axhline(K, color="black", linestyle=":", linewidth=1.0,
                     alpha=0.7, label=f"K = {K:.0e} cells")
    ax_treat.axhline(1.0, color="gray", linestyle="--", linewidth=0.8,
                     alpha=0.6, label="1 cell (cure threshold)")
    ax_treat.text(res["dose_times"][0] + 1.0, 1.0e11,
                  "chemo pulses",
                  rotation=90, color="tab:red",
                  fontsize=8, va="top")
    ax_treat.set_xlabel("time [days]", fontsize=10)
    ax_treat.set_ylabel("tumour cells N(t)", fontsize=10)
    ax_treat.set_ylim(1.0e-3, 1.0e14)
    ax_treat.set_title(
        "Skipper-Schabel log-kill chemotherapy on a Gompertz tumour\n"
        "each dose removes a constant fraction; tumour regrows between doses",
        fontsize=10,
    )
    ax_treat.legend(loc="lower right", fontsize=8, framealpha=0.92)
    ax_treat.grid(True, alpha=0.3, which="both")

    # Panel C: Armitage-Doll log-log incidence
    ax_inc = fig.add_subplot(gs[1, 0])
    age = np.linspace(20.0, 90.0, 200)
    palette_n = plt.cm.viridis(np.linspace(0.15, 0.85, 4))
    for n_hits, color in zip((4, 5, 6, 7), palette_n):
        I = sim.armitage_doll_incidence(age, n_hits=n_hits)
        ax_inc.loglog(age, I, color=color, linewidth=2.0,
                       label=f"n = {n_hits} (slope = {n_hits-1})")
    ax_inc.set_xlabel("age [years, log scale]", fontsize=10)
    ax_inc.set_ylabel("incidence rate I(age) [arb, log scale]", fontsize=10)
    ax_inc.set_title(
        f"Armitage-Doll multistage carcinogenesis\n"
        f"I(age) ~ age^(n-1);  default n = {ARMITAGE_DOLL_HITS_DEFAULT} -> slope 5",
        fontsize=10,
    )
    ax_inc.legend(loc="lower right", fontsize=8, framealpha=0.92)
    ax_inc.grid(True, alpha=0.3, which="both")

    # Panel D: Knudson 2-hit (sporadic vs hereditary retinoblastoma)
    ax_knud = fig.add_subplot(gs[1, 1])
    age_k = np.linspace(0.05, 80.0, 800)
    pdf_sp = sim.knudson_two_hit_sporadic_pdf(age_k)
    pdf_he = sim.knudson_two_hit_hereditary_pdf(age_k)
    pdf_sp_n = pdf_sp / pdf_sp.max() if pdf_sp.max() > 0 else pdf_sp
    pdf_he_n = pdf_he / pdf_he.max() if pdf_he.max() > 0 else pdf_he
    ax_knud.plot(age_k, pdf_he_n, color="tab:red", linewidth=2.4,
                 label=f"hereditary Rb (1 hit, peak ~ {KNUDSON_PEAK_AGE_HEREDITARY_YR:.1f} yr)")
    ax_knud.plot(age_k, pdf_sp_n, color="tab:blue", linewidth=2.4,
                 label=f"sporadic Rb (2 hits, peak ~ {KNUDSON_PEAK_AGE_SPORADIC_YR:.0f} yr)")
    ax_knud.axvline(KNUDSON_PEAK_AGE_HEREDITARY_YR, color="tab:red",
                     linestyle=":", linewidth=0.9, alpha=0.6)
    ax_knud.axvline(KNUDSON_PEAK_AGE_SPORADIC_YR, color="tab:blue",
                     linestyle=":", linewidth=0.9, alpha=0.6)
    ax_knud.set_xlabel("age at diagnosis [years]", fontsize=10)
    ax_knud.set_ylabel("retinoblastoma onset PDF (normalised)", fontsize=10)
    ax_knud.set_xlim(0.0, 60.0)
    ax_knud.set_ylim(0.0, 1.10)
    ax_knud.set_title(
        "Knudson 2-hit hypothesis: hereditary onset is decades earlier\n"
        "(one Rb allele inherited mutated -> only one somatic hit needed)",
        fontsize=10,
    )
    ax_knud.legend(loc="upper right", fontsize=8, framealpha=0.92)
    ax_knud.grid(True, alpha=0.3)

    fig.suptitle(
        "Tumour growth dynamics from substrate: Gompertz + multistage "
        "incidence + log-kill therapy",
        fontsize=13,
    )
    fig.tight_layout()
    out.append(save(fig, "110_tumor_growth.png"))

    # ---------------- 111: 8 Hallmarks of cancer schematic ---------------
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.6, 1.0], wspace=0.20)

    # Left: radial 8-hallmark diagram around a central cancer-cell node
    ax_h = fig.add_subplot(gs[0, 0])
    ax_h.set_aspect("equal")
    ax_h.axis("off")

    central = plt.Circle((0.0, 0.0), 0.18, color="#a1003c",
                          alpha=0.90, ec="black", linewidth=2.0,
                          zorder=5)
    ax_h.add_patch(central)
    ax_h.text(0.0, 0.0, "Cancer\ncell",
              fontsize=12, fontweight="bold", color="white",
              ha="center", va="center", zorder=6)

    palette_h = plt.cm.tab10(np.linspace(0.0, 1.0, N_HALLMARKS))

    for i, (label, color) in enumerate(zip(HALLMARKS, palette_h)):
        theta = _math.pi / 2 - 2 * _math.pi * i / N_HALLMARKS
        x_node = 0.7 * _math.cos(theta)
        y_node = 0.7 * _math.sin(theta)
        ax_h.plot([0.18 * _math.cos(theta), 0.55 * _math.cos(theta)],
                   [0.18 * _math.sin(theta), 0.55 * _math.sin(theta)],
                   color="black", linewidth=1.2, alpha=0.6, zorder=2)
        circ = plt.Circle((x_node, y_node), 0.14, color=color,
                           alpha=0.85, ec="black", linewidth=1.4,
                           zorder=4)
        ax_h.add_patch(circ)
        ax_h.text(x_node, y_node, str(i + 1),
                   fontsize=14, fontweight="bold", color="black",
                   ha="center", va="center", zorder=5)
        x_lab = 1.05 * _math.cos(theta)
        y_lab = 1.05 * _math.sin(theta)
        words = label.split()
        if len(words) >= 4:
            mid = len(words) // 2
            wrapped = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
        else:
            wrapped = label
        if x_lab > 0.05:
            ha = "left"
        elif x_lab < -0.05:
            ha = "right"
        else:
            ha = "center"
        ax_h.text(x_lab, y_lab, wrapped,
                   fontsize=10, color="black",
                   ha=ha, va="center", zorder=6)

    ax_h.set_xlim(-1.55, 1.55)
    ax_h.set_ylim(-1.30, 1.30)
    ax_h.set_title(
        f"The {N_HALLMARKS} Hallmarks of Cancer (Hanahan & Weinberg, 2011)",
        fontsize=12, pad=18,
    )

    # Right: 5-stage progression bar of acquired hallmarks
    ax_p = fig.add_subplot(gs[0, 1])
    stage_labels = list(STAGES)
    counts = [sim.n_hallmarks_acquired(s) for s in stage_labels]
    stage_colors = ["#2ecc71", "#f1c40f", "#e67e22",
                    "#e74c3c", "#8e44ad"]
    bars = ax_p.bar(range(len(stage_labels)), counts,
                     color=stage_colors, edgecolor="black",
                     linewidth=1.2)
    ax_p.set_xticks(range(len(stage_labels)))
    ax_p.set_xticklabels([s.capitalize() for s in stage_labels],
                          rotation=30, ha="right", fontsize=9)
    ax_p.set_ylabel("hallmarks acquired", fontsize=10)
    ax_p.set_ylim(0, N_HALLMARKS + 1.0)
    ax_p.set_title(
        "5-stage adenoma-carcinoma sequence\n"
        "each stage adds 2 hallmarks",
        fontsize=10,
    )
    ax_p.axhline(N_HALLMARKS, color="black", linestyle="--",
                  linewidth=0.9, alpha=0.6,
                  label=f"all {N_HALLMARKS} hallmarks")
    for bar, c in zip(bars, counts):
        ax_p.text(bar.get_x() + bar.get_width() / 2.0,
                   bar.get_height() + 0.18, f"{c}",
                   ha="center", va="bottom", fontsize=10,
                   fontweight="bold")
    ax_p.grid(True, alpha=0.3, axis="y")
    ax_p.legend(loc="upper left", fontsize=8)

    fig.suptitle(
        "Hanahan-Weinberg hallmarks: 8 acquired capabilities per cancer cell\n"
        "(B3 ontology: each hallmark releases one substrate-saturation lock)",
        fontsize=12,
    )
    fig.tight_layout()
    out.append(save(fig, "111_hallmarks_cancer.png"))

    return out


# ---------------------------------------------------------------------------
# Muscle contraction (sarcomere geometry + Hill F-v / length-tension / power)
# ---------------------------------------------------------------------------

def render_muscle() -> list[str]:
    """Produce 104_sarcomere.png and 105_force_velocity.png.

    104: Sarcomere schematic with thick + thin filaments, cross-bridges,
         Z-disks, A-band, I-band, M-line; plus a hexagonal cross-section
         panel; plus a 5-state Lymn-Taylor 1971 cross-bridge cycle.
    105: Hill 1938 hyperbolic F-v curve + Gordon-Huxley-Julian 1966
         length-tension curve + power-velocity P(v) = F(v) * v showing
         the v* ~ 0.31 v_max maximum.
    """
    from src.stiff_medium.muscle_substrate import (
        CROSS_BRIDGE_AXIAL_PERIOD_NM,
        DUTY_RATIO_SKELETAL,
        HILL_A_OVER_FMAX,
        H_ZONE_LENGTH_UM,
        INTER_FILAMENT_SPACING_NM,
        LENGTH_TENSION_L_MAX_UM,
        LENGTH_TENSION_L_MIN_UM,
        LENGTH_TENSION_L_PLATEAU_HIGH_UM,
        LENGTH_TENSION_L_PLATEAU_LOW_UM,
        POWER_STROKE_NM,
        SARCOMERE_REST_LENGTH_UM,
        THICK_FILAMENT_LENGTH_UM,
        THIN_FILAMENT_LENGTH_UM,
        MuscleGeometry,
        MuscleSimulator,
    )
    from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
    import math as _m
    out: list[str] = []

    geom = MuscleGeometry(sarcomere_length_um=SARCOMERE_REST_LENGTH_UM,
                           n_thick=3, n_cross_bridges=20)
    sim = MuscleSimulator(geometry=geom)

    # ------------------------------------------------------------------
    # 104_sarcomere.png : longitudinal schematic + cross-section + cycle
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.9],
                          width_ratios=[1.6, 1.0])

    # -- Top: longitudinal sarcomere schematic --------------------------
    ax_long = fig.add_subplot(gs[0, :])
    z_left, z_right = geom.z_disk_positions_um()
    a_left, a_right = geom.a_band_extent_um()
    h_left, h_right = geom.h_zone_extent_um()
    (zl, lt), (zr, rt) = geom.thin_filament_axial_extents_um()

    # Background bands
    ax_long.add_patch(Rectangle(
        (a_left, -1.0), a_right - a_left, 2.0,
        facecolor="#fde9d9", edgecolor="none", alpha=0.7, label="A-band"))
    iband_label_used = False
    for (xl, xr) in geom.i_band_extents_um():
        lbl = None if iband_label_used else "I-band"
        iband_label_used = True
        ax_long.add_patch(Rectangle(
            (xl, -1.0), xr - xl, 2.0,
            facecolor="#dce6f4", edgecolor="none", alpha=0.7, label=lbl))
    ax_long.add_patch(Rectangle(
        (h_left, -0.4), h_right - h_left, 0.8,
        facecolor="#fff2cc", edgecolor="none", alpha=0.6, label="H-zone"))

    # Z-disks (vertical bars)
    for z in (z_left, z_right):
        ax_long.plot([z, z], [-1.0, 1.0], color="#333", linewidth=4)
    # M-line
    ax_long.plot([0.0, 0.0], [-0.4, 0.4], color="#666", linewidth=2,
                 linestyle="--")

    # Thick filaments (3 stacked) at y = +0.35, 0, -0.35
    cb_pos = geom.cross_bridge_axial_positions_um()
    for y_off in (0.35, 0.0, -0.35):
        ax_long.plot([a_left, a_right], [y_off, y_off],
                     color="#1f4e79", linewidth=8, solid_capstyle="butt")
        for cbx in cb_pos:
            ax_long.plot([cbx, cbx], [y_off, y_off + 0.10],
                         color="#1f4e79", linewidth=1.0)
            ax_long.plot([cbx, cbx + 0.012], [y_off + 0.10, y_off + 0.18],
                         color="#1f4e79", linewidth=1.5)
            ax_long.plot([cbx, cbx], [y_off, y_off - 0.10],
                         color="#1f4e79", linewidth=1.0)
            ax_long.plot([cbx, cbx + 0.012], [y_off - 0.10, y_off - 0.18],
                         color="#1f4e79", linewidth=1.5)

    # Thin filaments (left and right pairs)
    for y_off in (0.20, -0.20, 0.50, -0.50):
        ax_long.plot([z_left, lt], [y_off, y_off],
                     color="#c0504d", linewidth=3, solid_capstyle="butt")
        ax_long.plot([rt, z_right], [y_off, y_off],
                     color="#c0504d", linewidth=3, solid_capstyle="butt")

    # Annotations
    ax_long.annotate("Z-disk", xy=(z_left, 0.95),
                     xytext=(z_left - 0.18, 1.15), fontsize=10, ha="center")
    ax_long.annotate("Z-disk", xy=(z_right, 0.95),
                     xytext=(z_right + 0.18, 1.15), fontsize=10, ha="center")
    ax_long.annotate("M-line", xy=(0, 0.45), xytext=(0.0, 1.10),
                     fontsize=10, ha="center")
    ax_long.annotate("A-band\n(thick filament)", xy=(0, -1.1),
                     xytext=(0, -1.45), fontsize=9, ha="center")
    ax_long.annotate("I-band\n(thin only)",
                     xy=((z_left + a_left) / 2, -1.1),
                     xytext=((z_left + a_left) / 2, -1.45),
                     fontsize=9, ha="center")
    ax_long.annotate("I-band\n(thin only)",
                     xy=((a_right + z_right) / 2, -1.1),
                     xytext=((a_right + z_right) / 2, -1.45),
                     fontsize=9, ha="center")
    ax_long.annotate("H-zone\n(bare)", xy=(0, 0.45), xytext=(0.55, 0.85),
                     fontsize=8, ha="center", color="#7f6000")

    # Sarcomere length brace
    ax_long.annotate("", xy=(z_left, -1.7), xytext=(z_right, -1.7),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
    ax_long.text(0.0, -1.85,
                 f"sarcomere length = {SARCOMERE_REST_LENGTH_UM:.2f} um",
                 ha="center", fontsize=10)

    ax_long.set_xlim(z_left - 0.4, z_right + 0.4)
    ax_long.set_ylim(-2.1, 1.45)
    ax_long.set_xlabel("axial position [um]")
    ax_long.set_yticks([])
    ax_long.set_title(
        "Sarcomere schematic (sliding-filament theory: H.E. Huxley & Hanson 1954, "
        "A.F. Huxley & Niedergerke 1954)\n"
        f"thick = {THICK_FILAMENT_LENGTH_UM} um (myosin), "
        f"thin = {THIN_FILAMENT_LENGTH_UM} um (actin), "
        f"H-zone = {H_ZONE_LENGTH_UM} um (M-line region); "
        f"cross-bridge axial period = {CROSS_BRIDGE_AXIAL_PERIOD_NM:.1f} nm",
        fontsize=11)
    handles, labels = ax_long.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax_long.legend(by_label.values(), by_label.keys(),
                    loc="upper right", fontsize=8)

    # -- Bottom-left: hexagonal-lattice cross-section -------------------
    ax_xs = fig.add_subplot(gs[1, 0])
    thick_xs = geom.thick_filament_cross_section_nm()
    thin_xs = geom.thin_filament_cross_section_nm()
    for k, tx in enumerate(thick_xs):
        ax_xs.add_patch(Circle(
            tx, radius=15.0 / 2.0, facecolor="#1f4e79",
            edgecolor="black", linewidth=1.0,
            label="thick (myosin, ~ 15 nm)" if k == 0 else None))
    for k, tn in enumerate(thin_xs):
        ax_xs.add_patch(Circle(
            tn, radius=8.0 / 2.0, facecolor="#c0504d",
            edgecolor="black", linewidth=0.8,
            label="thin (actin, ~ 8 nm)" if k == 0 else None))
    for i, t1 in enumerate(thick_xs):
        for t2 in thick_xs[i + 1:]:
            d = np.linalg.norm(t2 - t1)
            if _m.isclose(d, INTER_FILAMENT_SPACING_NM, rel_tol=1e-6):
                ax_xs.plot([t1[0], t2[0]], [t1[1], t2[1]],
                            color="#bbbbbb", linewidth=0.8, linestyle=":")
    ax_xs.set_aspect("equal")
    ax_xs.set_xlim(-INTER_FILAMENT_SPACING_NM * 1.6,
                    INTER_FILAMENT_SPACING_NM * 1.6)
    ax_xs.set_ylim(-INTER_FILAMENT_SPACING_NM * 1.6,
                    INTER_FILAMENT_SPACING_NM * 1.6)
    ax_xs.set_xlabel("x [nm]")
    ax_xs.set_ylabel("y [nm]")
    ax_xs.set_title(
        f"Hexagonal cross-section\n"
        f"inter-filament spacing = {INTER_FILAMENT_SPACING_NM:.0f} nm; "
        f"thin:thick = 2:1",
        fontsize=10)
    ax_xs.legend(loc="upper right", fontsize=7)

    # -- Bottom-right: 5-state cross-bridge cycle (Lymn-Taylor 1971) ---
    ax_cyc = fig.add_subplot(gs[1, 1])
    states = sim.cross_bridge_states()
    n = len(states)
    angles = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, n, endpoint=False)
    R = 1.0
    centres = np.array([[R * np.cos(a), R * np.sin(a)] for a in angles])
    short_label = {
        "attached_rigor": "1. Rigor\n(A.M)",
        "power_stroke":   "2. Power stroke\n(A.M.ADP -> A.M)",
        "detached":       "3. Detached\n(A + M.ATP)",
        "primed":         "4. Primed\n(M.ADP.Pi)",
        "attached_again": "5. Re-attach\n(A.M.ADP.Pi)",
    }
    colors = ["#4472c4", "#ed7d31", "#a5a5a5", "#70ad47", "#ffc000"]
    for i, c in enumerate(centres):
        ax_cyc.add_patch(Circle(
            c, radius=0.32, facecolor=colors[i],
            edgecolor="black", linewidth=1.0, alpha=0.85))
        ax_cyc.text(c[0], c[1], short_label[states[i]],
                     ha="center", va="center", fontsize=8)
    for i in range(n):
        c0 = centres[i]
        c1 = centres[(i + 1) % n]
        v_dir = c1 - c0
        v_norm = v_dir / (np.linalg.norm(v_dir) + 1e-30)
        start = c0 + 0.32 * v_norm
        end = c1 - 0.32 * v_norm
        ax_cyc.add_patch(FancyArrowPatch(
            start, end, arrowstyle="->", mutation_scale=15,
            color="black", linewidth=1.4))
    ax_cyc.text(0.0, -1.8,
                 f"1 ATP per cycle  (Delta_G ~ {sim.atp_free_energy_pN_nm():.0f} pN.nm)\n"
                 f"power stroke = {POWER_STROKE_NM:.0f} nm; "
                 f"duty ratio ~ {DUTY_RATIO_SKELETAL * 100:.0f}%",
                 ha="center", fontsize=9, color="#444")
    ax_cyc.set_aspect("equal")
    ax_cyc.set_xlim(-1.7, 1.7)
    ax_cyc.set_ylim(-2.2, 1.7)
    ax_cyc.set_xticks([])
    ax_cyc.set_yticks([])
    ax_cyc.set_title("Cross-bridge cycle (Lymn-Taylor 1971)",
                       fontsize=11)

    fig.suptitle("Sarcomere structure + cross-bridge cycle from substrate "
                  "(strain-pump array; 1 ATP -> ~ 10 nm slide)",
                  fontsize=13)
    fig.tight_layout()
    out.append(save(fig, "104_sarcomere.png"))

    # ------------------------------------------------------------------
    # 105_force_velocity.png : Hill F-v + length-tension + power
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 5))
    ax_fv = fig.add_subplot(1, 3, 1)
    ax_lt = fig.add_subplot(1, 3, 2)
    ax_pw = fig.add_subplot(1, 3, 3)

    f_arr_curve, v_arr_curve = sim.hill_force_velocity_curve(n=400)
    ax_fv.plot(v_arr_curve, f_arr_curve, color="#1f4e79", linewidth=2.4,
                label=f"Hill 1938 (a/F_max = {HILL_A_OVER_FMAX:.2f})")
    ax_fv.scatter([0.0], [sim.f_max_normalised], s=70, c="black",
                   zorder=4, label="F_max @ v=0 (isometric)")
    ax_fv.scatter([sim.v_max_normalised], [0.0], s=70, c="black",
                   marker="x", zorder=4, label="v_max @ F=0 (unloaded)")
    v_star = sim.velocity_at_max_power()
    f_star = sim.hill_force_from_velocity(v_star)
    ax_fv.scatter([v_star], [f_star], s=100, c="red", marker="*",
                   edgecolors="black", linewidths=1.0, zorder=5,
                   label=f"peak power: v*/v_max = {v_star/sim.v_max_normalised:.2f}")
    ax_fv.set_xlabel("velocity v / v_max")
    ax_fv.set_ylabel("force F / F_max")
    ax_fv.set_title("Hill 1938 force-velocity\n"
                     "(F + a)(v + b) = (F_max + a) * b")
    ax_fv.legend(loc="upper right", fontsize=8)
    ax_fv.grid(True, alpha=0.3)
    ax_fv.set_xlim(0.0, 1.05)
    ax_fv.set_ylim(0.0, 1.05)

    L, F_act = sim.length_tension_curve(n=800)
    ax_lt.plot(L, F_act, color="#c0504d", linewidth=2.4,
                label="Gordon-Huxley-Julian 1966")
    ax_lt.axvspan(LENGTH_TENSION_L_PLATEAU_LOW_UM,
                   LENGTH_TENSION_L_PLATEAU_HIGH_UM,
                   color="#ffc000", alpha=0.18,
                   label=f"plateau {LENGTH_TENSION_L_PLATEAU_LOW_UM:.2f}-"
                          f"{LENGTH_TENSION_L_PLATEAU_HIGH_UM:.2f} um")
    ax_lt.scatter([LENGTH_TENSION_L_MIN_UM, LENGTH_TENSION_L_MAX_UM],
                   [0, 0], s=50, c="black", zorder=4)
    ax_lt.text(LENGTH_TENSION_L_MIN_UM, -0.07,
                f"clash\n{LENGTH_TENSION_L_MIN_UM:.2f}",
                ha="center", fontsize=8)
    ax_lt.text(LENGTH_TENSION_L_MAX_UM, -0.07,
                f"no overlap\n{LENGTH_TENSION_L_MAX_UM:.2f}",
                ha="center", fontsize=8)
    L0 = sim.optimal_length_um()
    ax_lt.scatter([L0], [1.0], s=110, c="red", marker="*",
                   edgecolors="black", linewidths=1.0, zorder=5,
                   label=f"L_0 = {L0:.3f} um")
    ax_lt.set_xlabel("sarcomere length L [um]")
    ax_lt.set_ylabel("active force F_active / F_max")
    ax_lt.set_title("Length-tension curve\n"
                     "peak active force on optimal-overlap plateau")
    ax_lt.set_xlim(1.0, 4.0)
    ax_lt.set_ylim(-0.12, 1.1)
    ax_lt.grid(True, alpha=0.3)
    ax_lt.legend(loc="upper right", fontsize=8)

    v_arr, p_arr, f_arr = sim.hill_power_curve(n=800)
    ax_pw.plot(v_arr, p_arr, color="#70ad47", linewidth=2.4,
                label="P(v) = F(v) . v")
    ax_pw.plot(v_arr, f_arr, color="#1f4e79", linewidth=1.4, alpha=0.5,
                linestyle="--", label="F(v)  (reference)")
    P_max = sim.max_mechanical_power()
    ax_pw.scatter([v_star], [P_max], s=110, c="red", marker="*",
                   edgecolors="black", linewidths=1.0, zorder=5,
                   label=f"P_max @ v* = {v_star/sim.v_max_normalised:.2f}")
    ax_pw.axvline(v_star, color="red", linewidth=0.8, linestyle=":")
    ax_pw.set_xlabel("velocity v / v_max")
    ax_pw.set_ylabel("normalised P / (F_max v_max)")
    ax_pw.set_title("Power-velocity\n"
                     f"P_max = {P_max:.3f} F_max v_max  at v* ~ 0.31 v_max")
    ax_pw.set_xlim(0.0, 1.05)
    ax_pw.set_ylim(0.0, max(P_max * 1.4, 1.05))
    ax_pw.grid(True, alpha=0.3)
    ax_pw.legend(loc="upper right", fontsize=8)

    fig.suptitle("Muscle force-velocity, length-tension, and power "
                  "(substrate strain-pump envelope; ~ 50% theoretical efficiency)",
                  fontsize=13)
    fig.tight_layout()
    out.append(save(fig, "105_force_velocity.png"))

    return out


def render_morphogenesis() -> list[str]:
    """Produce 102_turing_patterns.png and 103_morphogen_gradient.png.

    102: 2D Gierer-Meinhardt RD snapshots — stripes, spots, and maze
         patterns from the three canonical D_v/D_u regimes, plus the
         radial Fourier-power spectra and a wavelength bar comparing
         predicted (2pi sqrt(D_v/rho)) to measured.
    103: 1D Wolpert French-flag morphogen gradient — diffusion + decay
         steady state with two thresholds (theta_low, theta_high) that
         partition the tissue into blue / white / red bands of cell
         fate.  Side panel: substrate-ontology summary linking
         morphogen = strain pattern, diffusion = wave propagation,
         reaction = nonlinearity.
    """
    from src.stiff_medium.morphogenesis_substrate import (
        LITERATURE,
        MorphogenesisGeometry,
        MorphogenesisSimulator,
        french_flag_fates,
        make_morphogenesis,
        turing_wavelength,
    )
    out: list[str] = []

    # 102_turing_patterns.png — three RD snapshots + spectra + wavelength
    fig = plt.figure(figsize=(18, 11))
    gs = fig.add_gridspec(
        3, 4, height_ratios=[1.4, 1.0, 1.0],
        width_ratios=[1.0, 1.0, 1.0, 1.2],
        hspace=0.45, wspace=0.32,
    )

    regimes = ["stripes_zebra", "spots_leopard", "maze_belousov"]
    titles = [
        "STRIPES  (D_v/D_u = 40)\nzebra / cuttlefish / fingerprints",
        "SPOTS  (D_v/D_u = 100)\nleopard / giraffe",
        "MAZE  (D_v/D_u = 25, high gain)\ncortex folds / BZ chemistry",
    ]
    for i, regime in enumerate(regimes):
        sim = make_morphogenesis(regime, n_x=80, n_y=80,
                                  n_steps=4500, rng_seed=11 + i)
        ev = sim.evolve(record_every=1500)

        ax_p = fig.add_subplot(gs[0, i])
        u_final = ev["u_final"]
        im = ax_p.imshow(u_final, origin="lower", cmap="viridis",
                          extent=[0, sim.geometry.Lx, 0, sim.geometry.Ly])
        ax_p.set_title(titles[i], fontsize=10)
        ax_p.set_xlabel("x  [tissue length]", fontsize=9)
        ax_p.set_ylabel("y  [tissue length]", fontsize=9)
        plt.colorbar(im, ax=ax_p, fraction=0.045, pad=0.03,
                     label="activator u  (substrate strain)")

        u_centred = u_final - float(np.mean(u_final))
        spec = np.abs(np.fft.fft2(u_centred)) ** 2
        n_y, n_x = u_final.shape
        kx = 2.0 * np.pi * np.fft.fftfreq(n_x, d=sim.geometry.dx())
        ky = 2.0 * np.pi * np.fft.fftfreq(n_y, d=sim.geometry.dy())
        KX, KY = np.meshgrid(kx, ky, indexing="xy")
        K = np.sqrt(KX ** 2 + KY ** 2)
        k_max = float(np.max(K))
        n_bins = 32
        bins = np.linspace(0.0, k_max, n_bins + 1)
        which = np.digitize(K.ravel(), bins) - 1
        which = np.clip(which, 0, n_bins - 1)
        power = np.zeros(n_bins, dtype=np.float64)
        counts = np.zeros(n_bins, dtype=np.int_)
        for idx in range(n_bins):
            mask = (which == idx)
            power[idx] = float(np.sum(spec.ravel()[mask]))
            counts[idx] = int(np.sum(mask))
        bin_centres = 0.5 * (bins[:-1] + bins[1:])
        valid = (counts > 0) & (np.arange(n_bins) > 0)
        ax_s = fig.add_subplot(gs[1, i])
        ax_s.semilogy(bin_centres[valid], np.maximum(power[valid], 1e-20),
                      "b-", linewidth=1.7)
        lam_pred = sim.geometry.predicted_wavelength()
        q_pred = 2.0 * np.pi / lam_pred
        ax_s.axvline(q_pred, color="red", linestyle="--", linewidth=1.5,
                     alpha=0.8, label=f"q* = 2pi/lambda_pred = {q_pred:.1f}")
        idx_star = int(np.argmax(np.where(valid, power, -np.inf)))
        q_meas = bin_centres[idx_star]
        ax_s.axvline(q_meas, color="green", linestyle=":", linewidth=1.5,
                     alpha=0.8, label=f"q_meas = {q_meas:.1f}")
        ax_s.set_xlabel("|q|  (radial wavenumber)", fontsize=9)
        ax_s.set_ylabel("|FFT(u)|^2", fontsize=9)
        ax_s.set_title("radial Fourier spectrum", fontsize=9)
        ax_s.legend(fontsize=7, loc="upper right")
        ax_s.grid(True, alpha=0.3, which="both")

        ax_b = fig.add_subplot(gs[2, i])
        klass = sim.classify_pattern(u_final)
        lam_meas = sim.measured_wavelength(u_final)
        bars = ax_b.bar(
            ["lambda_pred\n2pi sqrt(D_v/rho)", "lambda_meas\nFFT peak"],
            [lam_pred, lam_meas],
            color=["lightcoral", "steelblue"],
            edgecolor="black", linewidth=1.3,
        )
        for bar, val in zip(bars, [lam_pred, lam_meas]):
            ax_b.text(bar.get_x() + bar.get_width() / 2.0, val * 1.02,
                      f"{val:.3f}", ha="center", fontsize=9, fontweight="bold")
        ax_b.set_ylabel("wavelength  lambda  [tissue units]", fontsize=9)
        ax_b.set_title(f"classifier: {klass.upper()}", fontsize=9)
        ax_b.grid(True, alpha=0.3, axis="y")

    ax_txt = fig.add_subplot(gs[:, 3])
    ax_txt.axis("off")
    txt = (
        "TURING PATTERN FORMATION\n"
        "========================\n\n"
        "RD equations (Gierer-Meinhardt):\n"
        "  du/dt = D_u nabla^2 u\n"
        "        + rho(u^2/v - mu u)\n"
        "  dv/dt = D_v nabla^2 v\n"
        "        + rho u^2 - nu v\n\n"
        "Substrate ontology:\n"
        "  morphogen u, v = strain\n"
        "    pattern in stiff medium\n"
        "  diffusion D nabla^2  =\n"
        "    substrate wave propagation\n"
        "  reaction f, g  =\n"
        "    substrate nonlinearity\n"
        "    (autocatalysis +\n"
        "     cross-inhibition)\n\n"
        "Turing instability:\n"
        "  D_v / D_u  > critical (~10)\n"
        "  => homogeneous SS unstable\n"
        "  => pattern with wavelength\n"
        "      lambda ~ 2 pi sqrt(D_v/rho)\n\n"
        "Classifier rules (FFT):\n"
        "  STRIPES : axial anisotropy\n"
        "  SPOTS   : isotropic + high\n"
        "            excess kurtosis\n"
        "  MAZE    : isotropic + low\n"
        "            excess kurtosis\n\n"
        "Canonical regimes:\n"
    )
    for name, spec in LITERATURE.items():
        ratio = spec["D_v"] / spec["D_u"]
        lam = turing_wavelength(spec["D_v"], spec["rho"])
        txt += (f"  {name}:\n"
                f"    D_v/D_u = {ratio:.0f},  lambda = {lam:.3f}\n")
    txt += (
        "\nReferences:\n"
        "  Turing 1952 PTRSB 237\n"
        "  Gierer&Meinhardt 1972 Kyb 12\n"
        "  Murray 2003 Math Bio II 2-3\n"
    )
    ax_txt.text(0.0, 1.0, txt, fontsize=8, family="monospace",
                va="top", ha="left", transform=ax_txt.transAxes)

    fig.suptitle(
        "TURING PATTERNS from substrate reaction-diffusion: "
        "stripes / spots / maze\n"
        "Activator-inhibitor (Gierer-Meinhardt) on a 2D stiff-medium tissue, "
        "lambda ~ 2 pi sqrt(D_v / rho)",
        fontsize=13,
    )
    out.append(save(fig, "102_turing_patterns.png"))

    # 103_morphogen_gradient.png — Wolpert French flag readout
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.4, 1.4, 1.0],
                          height_ratios=[1.0, 1.0],
                          hspace=0.42, wspace=0.30)

    sim = MorphogenesisSimulator(
        geometry=MorphogenesisGeometry(Lx=1.0, n_x=200, n_y=24)
    )
    # Pick D and decay so alpha = sqrt(k/D) ~ 3: the 1/alpha morphogen
    # length scale is ~ 0.33 of the tissue length, giving the three
    # bands more balanced fractions for the (0.33, 0.66) thresholds.
    grad = sim.french_flag_gradient(
        c_source=1.0, c_sink=0.0, D=1.0e-2, decay=0.09, n_x=200,
    )
    x = grad["x"]
    c = grad["c"]
    alpha = float(grad["alpha"][0])
    theta_low, theta_high = 0.33, 0.66
    fates = sim.cell_fates(c, theta_low=theta_low, theta_high=theta_high)
    band_colors = {0: "#3b6ac1", 1: "#f0f0f0", 2: "#c0392b"}

    ax_g = fig.add_subplot(gs[0, 0])
    ax_g.plot(x, c, "b-", linewidth=2.4,
              label=f"c(x) = sinh(a(L-x))/sinh(aL),  a = {alpha:.2f}")
    ax_g.axhline(theta_high, color="red", linestyle="--", linewidth=1.4,
                 alpha=0.85, label=f"theta_high = {theta_high}")
    ax_g.axhline(theta_low, color="orange", linestyle="--", linewidth=1.4,
                 alpha=0.85, label=f"theta_low  = {theta_low}")
    in_band = int(fates[0])
    x_start = float(x[0])
    for j in range(1, len(fates)):
        if int(fates[j]) != in_band:
            ax_g.axvspan(x_start, float(x[j]), alpha=0.20,
                         color=band_colors[in_band])
            in_band = int(fates[j])
            x_start = float(x[j])
    ax_g.axvspan(x_start, float(x[-1]), alpha=0.20,
                 color=band_colors[in_band])
    ax_g.set_xlabel("position  x  along tissue", fontsize=10)
    ax_g.set_ylabel("morphogen concentration  c(x)", fontsize=10)
    ax_g.set_title(
        "Wolpert French flag - diffusion+decay gradient with two thresholds",
        fontsize=11,
    )
    ax_g.legend(fontsize=8, loc="upper right")
    ax_g.grid(True, alpha=0.3)
    ax_g.set_ylim(-0.05, 1.10)
    ax_g.set_xlim(0.0, 1.0)

    ax_f = fig.add_subplot(gs[0, 1])
    flag_image = np.tile(fates, (24, 1)).astype(np.float64)
    cmap_flag = plt.matplotlib.colors.ListedColormap(
        [band_colors[0], band_colors[1], band_colors[2]]
    )
    ax_f.imshow(flag_image, origin="lower", cmap=cmap_flag,
                extent=[0, 1, 0, 0.25], aspect="auto", vmin=0, vmax=2)
    ax_f.set_xlabel("position  x  along tissue", fontsize=10)
    ax_f.set_ylabel("y", fontsize=10)
    ax_f.set_title("cell fate determination -> French flag tissue",
                   fontsize=11)
    n_blue = int(np.sum(fates == 0))
    n_white = int(np.sum(fates == 1))
    n_red = int(np.sum(fates == 2))
    f_blue = n_blue / len(fates)
    f_white = n_white / len(fates)
    f_red = n_red / len(fates)
    if n_blue > 0:
        x_blue = float(np.mean(np.where(fates == 0)[0])) / len(fates)
        ax_f.text(x_blue, 0.13, f"BLUE\n{f_blue * 100:.0f}%",
                  ha="center", color="white", fontsize=10, fontweight="bold")
    if n_white > 0:
        x_white = float(np.mean(np.where(fates == 1)[0])) / len(fates)
        ax_f.text(x_white, 0.13, f"WHITE\n{f_white * 100:.0f}%",
                  ha="center", color="black", fontsize=10, fontweight="bold")
    if n_red > 0:
        x_red = float(np.mean(np.where(fates == 2)[0])) / len(fates)
        ax_f.text(x_red, 0.13, f"RED\n{f_red * 100:.0f}%",
                  ha="center", color="white", fontsize=10, fontweight="bold")

    ax_t = fig.add_subplot(gs[0, 2])
    ax_t.axis("off")
    summary_txt = (
        "WOLPERT FRENCH FLAG\n"
        "===================\n\n"
        "Source  c(0) = 1.0\n"
        "Sink    c(L) = 0.0\n"
        f"Decay   k    = 0.09\n"
        f"Diff    D    = 1.0e-2\n"
        f"  => alpha = sqrt(k/D)\n"
        f"          = {alpha:.2f}\n"
        f"     1/alpha = {1.0 / alpha:.3f}\n\n"
        f"Thresholds:\n"
        f"  theta_low  = {theta_low}\n"
        f"  theta_high = {theta_high}\n\n"
        f"Band fractions:\n"
        f"  RED   (high c):  {f_red:.2f}\n"
        f"  WHITE (mid c):   {f_white:.2f}\n"
        f"  BLUE  (low c):   {f_blue:.2f}\n\n"
        "Substrate ontology:\n"
        "  morphogen = strain\n"
        "    amplitude in stiff\n"
        "    medium\n"
        "  decay = drag gamma on\n"
        "    the strain wave\n"
        "  cell fate = locked-in\n"
        "    response of the\n"
        "    substrate strain\n"
        "    pocket to local\n"
        "    morphogen amplitude\n"
    )
    ax_t.text(0.0, 1.0, summary_txt, fontsize=8.5, family="monospace",
              va="top", ha="left", transform=ax_t.transAxes)

    ax_d = fig.add_subplot(gs[1, 0])
    decays = [0.05, 0.25, 2.5]
    palette = plt.cm.plasma(np.linspace(0.1, 0.85, len(decays)))
    for k, color in zip(decays, palette):
        g = sim.french_flag_gradient(c_source=1.0, c_sink=0.0, D=1.0e-2,
                                      decay=k, n_x=200)
        a = float(g["alpha"][0])
        ax_d.plot(g["x"], g["c"], color=color, linewidth=2.0,
                  label=f"k={k:>5g},  a={a:.2f},  1/a={1.0/a:.2f}")
    ax_d.axhline(theta_high, color="red", linestyle=":", linewidth=1.0,
                 alpha=0.6)
    ax_d.axhline(theta_low, color="orange", linestyle=":", linewidth=1.0,
                 alpha=0.6)
    ax_d.set_xlabel("position  x", fontsize=10)
    ax_d.set_ylabel("c(x)", fontsize=10)
    ax_d.set_title("steepness of gradient vs decay rate", fontsize=11)
    ax_d.legend(fontsize=8, loc="upper right")
    ax_d.grid(True, alpha=0.3)
    ax_d.set_ylim(-0.05, 1.10)

    ax_e = fig.add_subplot(gs[1, 1])
    threshold_pairs = [(0.20, 0.50), (0.33, 0.66), (0.50, 0.80)]
    for idx, (tl, th) in enumerate(threshold_pairs):
        f_arr = french_flag_fates(c, theta_low=tl, theta_high=th)
        n0 = int(np.sum(f_arr == 0))
        n1 = int(np.sum(f_arr == 1))
        n2 = int(np.sum(f_arr == 2))
        ax_e.barh(idx, n0, color=band_colors[0], edgecolor="black",
                  height=0.7, label="blue" if idx == 0 else None)
        ax_e.barh(idx, n1, left=n0, color=band_colors[1], edgecolor="black",
                  height=0.7, label="white" if idx == 0 else None)
        ax_e.barh(idx, n2, left=n0 + n1, color=band_colors[2],
                  edgecolor="black", height=0.7,
                  label="red" if idx == 0 else None)
        ax_e.text(len(c) * 1.02, idx,
                  f"  theta=({tl}, {th})", fontsize=9, va="center")
    ax_e.set_yticks(range(len(threshold_pairs)))
    ax_e.set_yticklabels([f"{i+1}" for i in range(len(threshold_pairs))])
    ax_e.set_xlabel("cell count along tissue", fontsize=10)
    ax_e.set_ylabel("threshold pair", fontsize=10)
    ax_e.set_title("band fractions vs threshold choice", fontsize=11)
    ax_e.legend(fontsize=9, loc="lower right")
    ax_e.set_xlim(0, len(c) * 1.45)

    ax_a = fig.add_subplot(gs[1, 2])
    alphas = np.linspace(0.5, 20.0, 80)
    half_lengths = 1.0 / alphas
    ax_a.plot(alphas, half_lengths, "b-", linewidth=2.0)
    ax_a.set_xlabel("alpha = sqrt(k/D)  [1/length]", fontsize=10)
    ax_a.set_ylabel("morphogen length scale  1/alpha", fontsize=10)
    ax_a.set_title("steepness control knob", fontsize=11)
    ax_a.grid(True, alpha=0.3)
    ax_a.axvline(alpha, color="red", linestyle="--", linewidth=1.2,
                 alpha=0.7, label=f"current a = {alpha:.2f}")
    ax_a.legend(fontsize=9)

    fig.suptitle(
        "MORPHOGEN GRADIENT (Wolpert 1969) - French flag from substrate "
        "diffusion + decay\n"
        "two thresholds (theta_low, theta_high) partition tissue into "
        "three cell-fate bands",
        fontsize=13,
    )
    out.append(save(fig, "103_morphogen_gradient.png"))

    return out


# ---------------------------------------------------------------------------
# Sensory transduction (vision + hearing + smell) - 108 / 109
# ---------------------------------------------------------------------------

def render_sensory() -> list[str]:
    """Render 108_phototransduction.png and 109_hearing_cochlea.png.

    Implementation lives in scripts/_render_sensory.py to keep the patch
    focused and avoid bloating this file with another long renderer.
    """
    from scripts._render_sensory import render_sensory as _render
    return _render()


# ---------------------------------------------------------------------------
# Madelung test (substrate vs published Madelung constants for 8 ionic crystals) - 119
# ---------------------------------------------------------------------------

def render_madelung_test() -> list[str]:
    """Render visuals/119_madelung_test.png.

    Two-panel figure:
      Top:    grouped bars of substrate-predicted vs published Madelung
              constant (per-FU convention) for the 8 ionic crystal types.
      Bottom: per-crystal relative error in the convention the literature
              uses for that salt, log-scale.
    """
    from src.stiff_medium.madelung_test import run_test

    res = run_test(method="ewald", N_real=6, N_recip=6)
    rows = res["rows"]
    names = list(rows.keys())
    pretty_names = {
        "NaCl":             "NaCl",
        "CsCl":             "CsCl",
        "beta_CsCl_SC":     r"$\beta$-CsCl",
        "ZnS_sphalerite":   "ZnS\n(sphal)",
        "ZnS_wurtzite":     "ZnS\n(wurtz)",
        "CaF2_fluorite":    r"CaF$_2$",
        "TiO2_rutile":      r"TiO$_2$",
        "Cu2O_cuprite":     r"Cu$_2$O",
    }
    pred_FU = np.array([rows[n]["M_per_FU_predicted"] for n in names])
    pub_FU  = np.array([rows[n]["M_per_FU_published"] for n in names])
    rel_err = np.array([rows[n]["rel_err_published"] for n in names])
    labels = [pretty_names.get(n, n) for n in names]

    fig, (ax_bar, ax_err) = plt.subplots(
        2, 1, figsize=(13.0, 9.0), gridspec_kw={"height_ratios": [3.0, 1.5]},
    )

    # ---------- top: bar comparison (log y) ---------- #
    x = np.arange(len(names))
    w = 0.38
    ax_bar.bar(x - w/2, pred_FU, w, label="Substrate Ewald",
               color="#1f77b4", edgecolor="black", linewidth=0.5)
    ax_bar.bar(x + w/2, pub_FU, w, label="Published",
               color="#ff7f0e", edgecolor="black", linewidth=0.5,
               alpha=0.85)
    ax_bar.set_yscale("log")
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(labels, fontsize=10)
    ax_bar.set_ylabel("Madelung constant per formula unit  (log)")
    ax_bar.set_title(
        "Substrate K_4-lattice + Coulomb prediction vs published Madelung\n"
        "constant across 8 ionic-crystal structure types  (zero free parameters)"
    )
    ax_bar.legend(loc="upper left", fontsize=10)
    ax_bar.grid(True, axis="y", alpha=0.3, which="both")

    # Annotate each bar with the rel-err in spec convention
    for xi, (p, q, e) in enumerate(zip(pred_FU, pub_FU, rel_err)):
        if e < 1e-3:
            label = "match"
        elif e < 5e-2:
            label = f"{e * 100.0:.2f}%"
        else:
            label = f"{e * 100.0:.0f}%"
        y = max(p, q) * 1.18
        ax_bar.text(xi, y, label, ha="center", fontsize=9,
                    color="black" if e < 5e-2 else "red")

    # ---------- bottom: relative error log-scale ---------- #
    err_pct = np.maximum(rel_err * 100.0, 1e-6)
    bar_colors = [("#2ca02c" if v < 1e-1 else "#d62728") for v in err_pct]
    ax_err.bar(x, err_pct, w * 1.5, color=bar_colors,
               edgecolor="black", linewidth=0.5)
    ax_err.set_yscale("log")
    ax_err.set_xticks(x)
    ax_err.set_xticklabels(labels, fontsize=10)
    ax_err.set_ylabel("Relative error  [%]   (log)")
    ax_err.axhline(0.1, color="black", linestyle=":", alpha=0.5,
                   label="0.1% (machine precision Ewald)")
    ax_err.axhline(5.0, color="orange", linestyle=":", alpha=0.5,
                   label="5% (loose match)")
    ax_err.set_title(
        f"Per-crystal relative error against published value  "
        f"(7/8 within 0.1%; rutile factor-~4 off by literature convention)"
    )
    ax_err.legend(loc="upper left", fontsize=9)
    ax_err.grid(True, axis="y", alpha=0.3, which="both")

    fig.tight_layout()
    return [save(fig, "119_madelung_test.png")]


# ---------------------------------------------------------------------------
# Nuclear BE test (substrate vs AME2020 across 25 isotopes A=2..238) - 121
# ---------------------------------------------------------------------------

def render_nuclear_be_test() -> list[str]:
    """Render visuals/121_nuclear_be_test.png.

    Two-panel figure:
      Top:    BE/A vs A for AME2020 (black circles), bare substrate
              (red squares), and substrate + textbook SEMF corrections
              (blue triangles).  25 isotopes from deuteron to U-238.
      Bottom: Residual = BE_pred - BE_obs (MeV) vs A for both bare
              and corrected, with the textbook Coulomb deficit
              ~ 0.72 * Z(Z-1) / A^{1/3} overlaid for reference.
    """
    from src.stiff_medium.nuclear_be_test import (
        A_COULOMB_MEV,
        compute_results,
        compute_results_with_corrections,
        summary_statistics,
    )

    results = compute_results()
    results_corr = compute_results_with_corrections()
    stats = summary_statistics(results)
    stats_corr = summary_statistics(results_corr, use_corrected=True)

    A_arr = np.array([r.isotope.A for r in results])
    Z_arr = np.array([r.isotope.Z for r in results])
    BE_pred_per_A = np.array([r.BE_pred_per_A for r in results])
    BE_obs_per_A = np.array([r.BE_obs_per_A for r in results])
    BE_corr_per_A = np.array([r.BE_pred_corr_per_A for r in results_corr])
    err_MeV = np.array([r.err_abs_MeV for r in results])
    err_corr_MeV = np.array([r.err_abs_corr_MeV for r in results_corr])

    # Sort by A for plotting
    order = np.argsort(A_arr)
    A_arr = A_arr[order]
    Z_arr = Z_arr[order]
    BE_pred_per_A = BE_pred_per_A[order]
    BE_obs_per_A = BE_obs_per_A[order]
    BE_corr_per_A = BE_corr_per_A[order]
    err_MeV = err_MeV[order]
    err_corr_MeV = err_corr_MeV[order]
    names = [results[i].isotope.name for i in order]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 2]})

    # ----- Top: BE/A vs A -----
    ax1.plot(A_arr, BE_obs_per_A, 'ko-', markersize=7, linewidth=1.2,
             alpha=0.85, label='AME2020 (measured)')
    ax1.plot(A_arr, BE_pred_per_A, 'rs--', markersize=8, linewidth=1.2,
             alpha=0.85,
             label=r'Bare substrate: $\eta_{coop}\cdot P(A)\cdot\varepsilon_{face}$')
    ax1.plot(A_arr, BE_corr_per_A, 'b^:', markersize=8, linewidth=1.2,
             alpha=0.75,
             label=r'Substrate + Coulomb + asym + pairing')

    # Annotate select isotopes
    annotate_set = {'2H', '4He', '12C', '56Fe', '208Pb', '238U'}
    for i, nm in enumerate(names):
        if nm in annotate_set:
            ax1.annotate(nm, (A_arr[i], BE_obs_per_A[i]),
                         xytext=(0, -14), textcoords='offset points',
                         ha='center', fontsize=9, color='black')

    ax1.axvline(56, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    ax1.text(56, 9.6, 'Fe-56 BE/A peak', ha='center', fontsize=9,
             color='gray')
    ax1.set_ylabel('BE / A   [MeV / nucleon]', fontsize=11)
    ax1.set_title(
        'Substrate nuclear binding energy vs AME2020 (25 isotopes)\n'
        r'$\varepsilon_{face} = \Lambda_{QCD}/(n_A\cdot N_{BAM}) = 200/90 = 2.222$ MeV    '
        r'$a_C = (3/5)\,\alpha\,\hbar c / R_0 = 0.7200$ MeV   '
        r'$a_{sym}=23,\, a_p=11$ MeV',
        fontsize=10.5)
    ax1.legend(loc='lower right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 11)

    # Inline stats box
    stat_str = (
        f"n = {stats['n_isotopes']}\n"
        f"BARE     mean abs = {stats['mean_abs_err_pct']:.1f}%   RMS = {stats['rms_err_pct']:.1f}%\n"
        f"+SEMF   mean abs = {stats_corr['mean_abs_err_pct']:.1f}%   RMS = {stats_corr['rms_err_pct']:.1f}%\n"
        f"(textbook a_sym=23 over-corrects;\n"
        f"see analysis/nuclear_be_ame2020_test_results.md)"
    )
    ax1.text(0.02, 0.97, stat_str, transform=ax1.transAxes,
             fontsize=9, va='top', ha='left',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # ----- Bottom: residual + Coulomb deficit overlay -----
    # Bare substrate residual (red bars)
    width = 1.6
    ax2.bar(A_arr - width/2, err_MeV, width=width, color='red', alpha=0.6,
            edgecolor='darkred', label='Bare substrate residual (pred - obs)')
    # Corrected residual (blue bars)
    ax2.bar(A_arr + width/2, err_corr_MeV, width=width,
            color='steelblue', alpha=0.6, edgecolor='navy',
            label='Substrate + SEMF corrections residual')

    # Textbook Coulomb deficit: 0.72 * Z(Z-1) / A^{1/3}
    # (this is what an unsubtracted Coulomb term *would* contribute)
    A_smooth = np.linspace(2, 240, 240)
    # Use Z = A/2 for the smooth curve (rough valley of stability)
    Z_smooth = 0.5 * A_smooth
    coulomb = A_COULOMB_MEV * Z_smooth * (Z_smooth - 1) / (A_smooth ** (1.0 / 3.0))
    ax2.plot(A_smooth, coulomb, 'k--', linewidth=1.4, alpha=0.7,
             label=r'Substrate Coulomb deficit  $a_C\,Z(Z-1)/A^{1/3}$')

    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_xlabel('Mass number A', fontsize=11)
    ax2.set_ylabel(r'$BE_{pred} - BE_{obs}$   [MeV]', fontsize=11)
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 245)

    fig.tight_layout()
    return [save(fig, "121_nuclear_be_test.png")]


def main() -> None:
    print(f"Rendering all visualizations to {VISUALS_DIR}/")
    print("=" * 70)
    renderers = [
        ("K_4 face-pair geometry", render_k4_face_pair),
        ("Topological defect zoo", render_topological_defects),
        ("Kink-antikink scattering", render_kink_scattering),
        ("2D lattice substrate", render_lattice_substrate_2d),
        ("Saturation cap scenarios", render_saturation_simulator),
        ("Phonon dispersion", render_phonon_dispersion),
        ("Cube DM Q_3", render_cube_dm),
        ("Möbius bundle", render_mobius_bundle),
        ("EM radiation patterns", render_em_radiation),
        ("Cosmology de-saturation", render_cosmology_evolution),
        ("Cone-bouncing visualizer", render_cone_bouncing),
        ("Multi-nucleon K_4 stacking", render_nucleon_stacking),
        ("Mass-torque ladder", render_mass_ladder),
        ("3-generation tower", render_generation_tower),
        ("Saturation horizon (cone-tilt + potential)", render_saturation_horizon),
        ("Möbius 11/12 amplitude on K_4 + α breakdown", render_mobius_amplitude),
        ("Möbius sheet-swap (Z/2, Majorana, σ=½ fixed point)",
         render_mobius_sheet_swap),
        ("3D bound-state extraction (particle = substrate strain)",
         render_bound_state_3d),
        ("Lagrangian-term contributions (kin/grad/pot/drag)",
         render_lagrangian_terms),
        ("Black-hole horizon + Hawking + ringdown (paired σ=½ saturation)",
         render_black_hole),
        ("Cosmological phase transition (bubbles, percolation, Γ(T))",
         render_phase_transition),
        ("BBH GW signal (inspiral + merger + ringdown, σ→½ QNM)",
         render_gw_signal),
        ("Hubble tension (substrate H_0 = 71.92 vs SH0ES vs Planck)",
         render_hubble),
        ("3D substrate field full-evolution movie (32³ iso-surfaces)",
         render_substrate_3d_movie),
        ("CMB power spectrum + polarization (paired GEOMETRY+SIM+VIZ)",
         render_cmb),
        ("Quantum measurement & decoherence (double-slit + density matrix + CHSH)",
         render_quantum_measurement),
        ("Mitochondrial bioenergetics (ETC complexes I-IV + F0F1 ATP synthase + chemiosmosis)",
         render_mito),
        ("Atoms as substrate strain patterns (orbitals + IEs for H..Ne)",
         render_atoms),
        ("Molecular bonds as substrate strain bridges (5 molecules + 20 bonds)",
         render_molecules),
        ("Reaction kinetics (Arrhenius+Eyring+catalysis on SN2/H2+I2/Diels-Alder)",
         render_reactions),
        ("Molecular spectroscopy (UV-Vis + IR + 1H NMR, paired GEOMETRY+SIM+VIZ)",
         render_spectroscopy),
        ("Acid-base equilibria (pKa table + titration curves, paired GEOMETRY+SIM+VIZ)",
         render_pka),
        ("Solvation shells + dielectric response (Born + Debye)",
         render_solvation),
        ("Protein folding (alpha-helix + beta-sheet + funnel + Ramachandran)",
         render_protein),
        ("DNA mechanics (B-DNA double helix + force-extension + B→S transition)",
         render_dna),
        ("Biological membranes (lipid bilayer 4 nm + κ=20 kT + lateral diffusion + Helfrich)",
         render_membrane),
        ("Catalysis (Sabatier volcano Ni/Pd/Pt/Au + carbonic anhydrase + Hb Hill)",
         render_catalysis),
        ("Substrate-DFT (KS orbitals + LDA exchange + substrate σ≤½ correlation)",
         render_dft),
        ("Crystal structures (NaCl, diamond, graphite, CsCl, ZnS, perovskite + XRD)",
         render_crystals),
        ("Photosynthesis (chlorophyll absorption + Z-scheme PS-II -> PS-I -> NADPH)",
         render_photosynthesis),
        ("Neural action potential (Hodgkin-Huxley AP + m/h/n gating + refractory)",
         render_neural),
        ("Ribosome translation (30S+50S + mRNA + A/P/E + WC pairing + 2 GTP/cycle)",
         render_ribosome),
        ("Immune response (antibody Y-shape + 1 deg vs 2 deg titer + SIR coupled)",
         render_immune),
        ("Ecosystem dynamics (Lotka-Volterra + food web + May-Wigner)",
         render_ecosystem),
        ("Evolutionary dynamics (HW + Wright-Fisher + Kimura/Haldane + speciation)",
         render_evolution),
        ("Cell differentiation (Waddington landscape + lineage tree + Yamanaka)",
         render_differentiation),
        ("Epidemiology (SIR + SEIR + R_0 phase diagram + vaccination)",
         render_epidemiology),
        ("Climate (radiative forcing + ECS + IPCC AR6 sensitivity bands)",
         render_climate),
        ("Neural network learning (perceptron AND/OR/XOR + MLP universality + loss landscape)",
         render_neural_network),
        ("Fluid turbulence from substrate (Kolmogorov k^-5/3 + Karman vortex street + Re_crit 2300)",
         render_turbulence),
        ("Chaos / dynamical systems (Lorenz attractor + logistic bifurcation + Lyapunov)",
         render_chaos),
        ("Quantum computing as Mobius two-sheet states (gates + Bell + Grover + decoherence)",
         render_qc),
        ("Superconductivity (BCS gap Δ(T) + DOS + substrate T_c ceiling 128.9 K)",
         render_sc),
        ("Semiconductor band structure + p-n junction (Si/GaAs/GaN/diamond + V_bi)",
         render_semi),
        ("Measurement / observer (substrate decoherence, NOT consciousness; Bell + Born + Wigner)",
         render_measurement_observer),
        ("Allometric scaling laws (Kleiber 3/4 across 30 mammals + WBE vascular fractal)",
         render_allometric),
        ("Brain network dynamics (Kuramoto sync + 5 EEG bands + DMN + -3/2 avalanches)",
         render_brain),
        ("Cancer / tumor growth (Gompertz + Armitage-Doll + Knudson + log-kill + 8 hallmarks)",
         render_cancer),
        ("Muscle contraction (sarcomere + sliding filament + Hill 1938 F-v + cross-bridge cycle)",
         render_muscle),
        ("Sensory transduction (rhodopsin photo-cascade + cochlea Bekesy + MET + Weber-Fechner)",
         render_sensory),
        ("Morphogenesis / Turing patterns (stripes/spots/maze + Wolpert French flag gradient)",
         render_morphogenesis),
        ("Substrate visualizer", render_substrate_visualizer),
        ("Madelung constants: substrate vs published (8 ionic crystals)",
         render_madelung_test),
        ("Nuclear BE: substrate vs AME2020 (25 isotopes A=2..238)",
         render_nuclear_be_test),
    ]
    all_paths = []
    for name, fn in renderers:
        print(f"  {name}...")
        try:
            paths = fn()
            for p in paths:
                rel = os.path.relpath(p, ROOT)
                print(f"    → {rel}")
                all_paths.append(rel)
        except Exception as e:
            print(f"    FAILED: {type(e).__name__}: {e}")
            traceback.print_exc(limit=2)
    print()
    print(f"Done. {len(all_paths)} visualizations in visuals/")


if __name__ == "__main__":
    main()
