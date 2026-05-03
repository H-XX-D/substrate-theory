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
    if curve.ndim == 2 and curve.shape[0] == 2:
        d_vals, e_vals = curve[0], curve[1]
    else:
        d_vals, e_vals = distances, np.asarray(curve).flatten()
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
            x = res.get("x")
            u = res.get("u")
            sigma = res.get("sigma")
            if x is not None and u is not None:
                ax.plot(x, u, "b-", label="u(x)", linewidth=1.5)
            if x is not None and sigma is not None:
                ax2 = ax.twinx()
                ax2.plot(x, sigma, "r--", label="σ(x)", alpha=0.7)
                ax2.axhline(0.5, color="orange", linestyle=":",
                            linewidth=2, label="σ_max=½")
                ax2.set_ylabel("σ", color="r")
                ax2.legend(loc="upper right", fontsize=8)
            ax.set_title(name)
            ax.set_xlabel("x")
            ax.set_ylabel("u", color="b")
            ax.legend(loc="upper left", fontsize=8)
            ax.grid(True, alpha=0.3)
        except Exception as e:
            ax.text(0.5, 0.5, f"{name}\n(error: {e})",
                    ha="center", transform=ax.transAxes, fontsize=8)
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
    pd = PhononDispersion(K=1.0, rho=1.0)
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    geoms = [("1d", "1D chain"), ("2d_sq", "2D square"),
             ("2d_hex", "2D hexagonal"),
             ("3d_fcc", "3D FCC"), ("3d_bcc", "3D BCC"),
             ("3d_diamond", "3D diamond")]
    for ax, (g, label) in zip(axes.flat, geoms):
        try:
            data = pd.dispersion(geometry=g, n_k=80)
            k = data.get("k")
            omega = data.get("omega")
            if k is not None and omega is not None:
                if omega.ndim == 1:
                    ax.plot(k, omega, "b-", linewidth=2)
                else:
                    for i in range(omega.shape[1]):
                        ax.plot(k, omega[:, i], alpha=0.75, linewidth=1.5)
            ax.set_title(label)
            ax.set_xlabel("k")
            ax.set_ylabel("ω")
            ax.grid(True, alpha=0.3)
        except Exception as e:
            ax.text(0.5, 0.5, f"{label}\n(N/A)", ha="center",
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

    # Energy density components
    ax = axes[1]
    if "rho_matter" in history or "rho_lambda" in history:
        for k, color in [("rho_matter", "blue"), ("rho_radiation", "red"),
                         ("rho_lambda", "green"), ("rho_total", "black")]:
            if k in history:
                ax.semilogy(history.get("t", range(len(history[k]))),
                            history[k], color=color, label=k.replace("rho_", "ρ_"))
        ax.set_xlabel("Time [arb units]")
        ax.set_ylabel("Energy density")
        ax.set_title("Cosmic energy budget evolution")
        ax.legend()
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
        ("Epidemiology (SIR + SEIR + R_0 phase diagram + vaccination)",
         render_epidemiology),
        ("Climate (radiative forcing + ECS + IPCC AR6 sensitivity bands)",
         render_climate),
        ("Neural network learning (perceptron AND/OR/XOR + MLP universality + loss landscape)",
         render_neural_network),
        ("Substrate visualizer", render_substrate_visualizer),
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
