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
# 11. Mass torque ladder
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
        out.append(save(fig, "17_mass_torque_ladder.png"))
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
        ("Mass-torque ladder", render_mass_ladder),
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
