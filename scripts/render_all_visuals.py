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
