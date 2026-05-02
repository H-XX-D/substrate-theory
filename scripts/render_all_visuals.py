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
