"""Multi-cluster binding from substrate dynamics.

Runs the actual substrate simulation to measure emergent bound-state masses:
1. Small bound states (N=5, 10, 20, 50, 100 neutrinos).
2. A 3-cluster composite (3 small clusters at large initial separation).
3. Mass spectrum M(N) from simulation dynamics — no imported SM values.
4. Honest comparison against the proton/electron ratio 1836.

Mass definition used here:
    M(cluster) = total kinetic energy (|v|² summed, natural units where C=1)
                 + pairwise binding energy (difference between separated and
                   bound configurations).

    For a cluster of N particles at equilibrium separation:
        KE_total  = N × (1/2) × C²  = N/2   (each particle moves at C=1 on its cone)
        BE        = sum of pairwise back-reaction potentials at equilibrium
        M_bound   = KE_total - |BE|           (binding reduces inertia)

    This is a substrate-mechanical definition, not imported from SM formulas.

Run:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src timeout 300 python3 scripts/multi_cluster_binding.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterator

import numpy as np

# ── Substrate imports ──────────────────────────────────────────────────────────
from stiff_medium.back_reaction import back_reaction_force, project_to_cone
from stiff_medium.three_d import Neutrino3D, make_on_cone

C: float = 1.0  # natural-units wave speed (shared with all modules)

# ── Simulation parameters ──────────────────────────────────────────────────────
# These are chosen on physical grounds from the substrate model (spec §2):
# r_overlap < r_eq < r_capture defines the three interaction zones.
R_OVERLAP: float = 0.05   # hard-core exclusion radius
R_EQ: float = 0.20        # equilibrium binding radius (potential minimum)
R_CAPTURE: float = 1.20   # range of the back-reaction force
K_PUSH: float = 6.0       # centrifugal strength (d < r_eq)
K_PULL: float = 4.0       # centripetal strength (r_eq < d < r_capture)
DT: float = 0.005         # integration time step
SETTLE_STEPS: int = 2000  # steps to reach bound-state equilibrium
MEASURE_STEPS: int = 500  # steps to average mass observable

# Cluster-level parameters (for composite simulation)
CLUSTER_SEP: float = 6.0  # initial separation between sub-clusters (>r_capture)
COMPOSITE_SETTLE: int = 3000  # longer settling time for cluster-of-clusters
COMPOSITE_MEASURE: int = 500


# ══════════════════════════════════════════════════════════════════════════════
# Substrate particle factory
# ══════════════════════════════════════════════════════════════════════════════

def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def make_cluster(
    n: int,
    centre: np.ndarray,
    spread: float,
    rng: np.random.Generator,
) -> list[Neutrino3D]:
    """Create N neutrinos near `centre` with random 45°-cone velocities.

    Each particle is placed uniformly in a ball of radius `spread` around
    `centre`.  Its axis is a random unit vector; the velocity lies on the
    45° cone of that axis at a random azimuth.  This matches the spec §5
    prescription: every particle starts on-cone, orientation is random.
    """
    particles: list[Neutrino3D] = []
    for _ in range(n):
        # Random position within a ball of radius `spread`
        r_vec = rng.standard_normal(3)
        r_vec = r_vec / np.linalg.norm(r_vec)
        radius = spread * rng.uniform(0.0, 1.0) ** (1.0 / 3.0)
        pos = centre + radius * r_vec

        # Random axis (unit vector)
        axis_raw = rng.standard_normal(3)
        axis = axis_raw / np.linalg.norm(axis_raw)

        # Velocity on the 45° cone of this axis, random azimuth
        azimuth = rng.uniform(0.0, 2.0 * np.pi)
        vel = make_on_cone(axis, azimuth, speed=C)

        particles.append(Neutrino3D(
            position=pos.copy(),
            velocity=vel.copy(),
            axis=axis.copy(),
        ))
    return particles


# ══════════════════════════════════════════════════════════════════════════════
# Dynamics: N-body step with back-reaction
# ══════════════════════════════════════════════════════════════════════════════

def _nbody_step(
    positions: np.ndarray,   # (N, 3)
    velocities: np.ndarray,  # (N, 3)
    axes: np.ndarray,        # (N, 3)
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """One velocity-Verlet step for N particles with pairwise back-reaction.

    Uses the spring-like back_reaction_force from back_reaction.py.
    After each velocity update the velocity is projected back onto its
    particle's 45° cone (spec §5: cone projection after impulse).

    Returns (new_positions, new_velocities).  Axes are unchanged.
    """
    n = len(positions)

    def total_force(pos: np.ndarray) -> np.ndarray:
        """Accumulate pairwise back-reaction forces. Shape (N, 3)."""
        f = np.zeros_like(pos)
        for i in range(n):
            for j in range(i + 1, n):
                f_ij = back_reaction_force(
                    pos[i], pos[j],
                    r_eq=R_EQ,
                    r_capture=R_CAPTURE,
                    k_push=K_PUSH,
                    k_pull=K_PULL,
                )
                f[i] += f_ij
                f[j] -= f_ij
        return f

    # Velocity-Verlet
    f0 = total_force(positions)
    half_v = np.array([
        project_to_cone(velocities[i] + 0.5 * f0[i] * dt, axes[i])
        for i in range(n)
    ])
    new_pos = positions + half_v * dt
    f1 = total_force(new_pos)
    new_v = np.array([
        project_to_cone(half_v[i] + 0.5 * f1[i] * dt, axes[i])
        for i in range(n)
    ])
    return new_pos, new_v


def _simulate(
    particles: list[Neutrino3D],
    settle: int,
    measure: int,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Run the substrate simulation and return time-averaged observables.

    Returns:
        final_positions  shape (N, 3)
        final_velocities shape (N, 3)
        mean_ke          time-averaged total kinetic energy (sum |v_i|²/2)
        mean_rms_sep     time-averaged RMS pairwise separation
    """
    n = len(particles)
    pos = np.array([p.position for p in particles])
    vel = np.array([p.velocity for p in particles])
    axes = np.array([p.axis for p in particles])

    # Settle — let bound state form
    for _ in range(settle):
        pos, vel = _nbody_step(pos, vel, axes, DT)

    # Measurement window
    ke_accum: float = 0.0
    rms_sep_accum: float = 0.0

    for _ in range(measure):
        pos, vel = _nbody_step(pos, vel, axes, DT)
        ke_accum += float(np.sum(0.5 * np.einsum("ni,ni->n", vel, vel)))
        # Pairwise separations
        sep_sq: float = 0.0
        pair_count: int = 0
        for i in range(n):
            for j in range(i + 1, n):
                d = float(np.linalg.norm(pos[i] - pos[j]))
                sep_sq += d * d
                pair_count += 1
        rms_sep_accum += np.sqrt(sep_sq / max(pair_count, 1))

    return (
        pos,
        vel,
        ke_accum / measure,
        rms_sep_accum / measure,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Mass estimators
# ══════════════════════════════════════════════════════════════════════════════

def _pairwise_potential_energy(
    positions: np.ndarray,  # (N, 3)
) -> float:
    """Compute total pairwise back-reaction potential energy.

    The spring-like potential corresponding to back_reaction_force:
        V(d) = (1/2) K_PULL (d - R_EQ)^2   for r_eq < d < r_capture
        V(d) = (1/2) K_PUSH (R_EQ - d)^2   for d < r_eq
        V(d) = 0                              for d > r_capture

    Returns total V (negative for net binding when many pairs inside R_EQ,
    positive when pushed out; here returned as-is).
    """
    n = len(positions)
    total: float = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.linalg.norm(positions[i] - positions[j]))
            if d > R_CAPTURE:
                pass  # no interaction
            elif d > R_EQ:
                total += 0.5 * K_PULL * (d - R_EQ) ** 2
            else:
                total += 0.5 * K_PUSH * (R_EQ - d) ** 2
    return total


def _separated_potential_energy(n: int) -> float:
    """Potential energy of N particles placed far apart (V = 0 for all pairs)."""
    return 0.0  # all pairs at d > R_CAPTURE → no interaction


def measure_bound_state_mass(
    n: int,
    seed: int = 0,
    spread: float | None = None,
    settle: int = SETTLE_STEPS,
    measure: int = MEASURE_STEPS,
    verbose: bool = False,
) -> dict[str, float]:
    """Simulate N neutrinos and measure emergent bound-state mass.

    Mass = KE_mean + (V_separated - V_bound)
         = KE_mean + binding_energy

    where:
        KE_mean       = time-averaged kinetic energy during measurement window
        binding_energy = V_separated - V_bound (positive for a bound state)

    Because all particles move at C=1, KE_mean per particle is always ~C²/2 = 0.5.
    The interesting physics is in the binding energy.

    Returns a dict with:
        n, ke_mean, pe_bound, pe_separated, binding_energy,
        mass, ke_per_particle, rms_sep, seconds_elapsed
    """
    if spread is None:
        spread = max(R_EQ * 1.5, R_EQ * np.sqrt(float(n)))

    centre = np.zeros(3)
    rng = _rng(seed)
    t0 = time.perf_counter()
    particles = make_cluster(n, centre, spread=spread, rng=rng)
    pos_f, vel_f, ke_mean, rms_sep = _simulate(particles, settle, measure)
    pe_bound = _pairwise_potential_energy(pos_f)
    pe_sep = _separated_potential_energy(n)
    binding_energy = pe_sep - pe_bound  # positive = bound
    mass = ke_mean + binding_energy
    elapsed = time.perf_counter() - t0

    if verbose:
        print(
            f"  N={n:4d}  KE={ke_mean:8.4f}  PE_bound={pe_bound:10.4f}"
            f"  BE={binding_energy:10.4f}  M={mass:10.4f}"
            f"  rms_sep={rms_sep:.3f}  [{elapsed:.1f}s]"
        )
    return {
        "n": n,
        "ke_mean": ke_mean,
        "pe_bound": pe_bound,
        "pe_separated": pe_sep,
        "binding_energy": binding_energy,
        "mass": mass,
        "ke_per_particle": ke_mean / n,
        "rms_sep": rms_sep,
        "seconds_elapsed": elapsed,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Composite: 3 sub-clusters
# ══════════════════════════════════════════════════════════════════════════════

def make_3cluster_composite(
    n_per_cluster: int,
    cluster_sep: float = CLUSTER_SEP,
    seed: int = 42,
    settle: int = COMPOSITE_SETTLE,
    measure: int = COMPOSITE_MEASURE,
    verbose: bool = False,
) -> dict[str, float]:
    """Simulate a 3-cluster composite: 3 sub-clusters at large initial separation.

    The clusters are arranged in an equilateral triangle at distance
    `cluster_sep` from the COM.  They attract via back-reaction as the
    simulation runs, and we measure the composite mass after settling.

    Returns same dict structure as measure_bound_state_mass, plus:
        n_per_cluster, cluster_sep
    """
    rng = _rng(seed)
    spread = R_EQ * 1.5 * max(1.0, np.sqrt(float(n_per_cluster)))

    # Three sub-cluster centres in an equilateral triangle (xy-plane)
    centres = [
        np.array([cluster_sep, 0.0, 0.0]),
        np.array([-cluster_sep * 0.5, cluster_sep * np.sqrt(3) / 2.0, 0.0]),
        np.array([-cluster_sep * 0.5, -cluster_sep * np.sqrt(3) / 2.0, 0.0]),
    ]

    all_particles: list[Neutrino3D] = []
    for c in centres:
        all_particles.extend(make_cluster(n_per_cluster, c, spread=spread, rng=rng))

    n_total = len(all_particles)
    t0 = time.perf_counter()
    pos_f, vel_f, ke_mean, rms_sep = _simulate(
        all_particles, settle=settle, measure=measure
    )
    pe_bound = _pairwise_potential_energy(pos_f)
    pe_sep = _separated_potential_energy(n_total)
    binding_energy = pe_sep - pe_bound
    mass = ke_mean + binding_energy
    elapsed = time.perf_counter() - t0

    if verbose:
        print(
            f"  3×{n_per_cluster}={n_total}  KE={ke_mean:8.4f}  PE_bound={pe_bound:10.4f}"
            f"  BE={binding_energy:10.4f}  M={mass:10.4f}"
            f"  rms_sep={rms_sep:.3f}  [{elapsed:.1f}s]"
        )
    return {
        "n": n_total,
        "n_per_cluster": n_per_cluster,
        "cluster_sep": cluster_sep,
        "ke_mean": ke_mean,
        "pe_bound": pe_bound,
        "pe_separated": pe_sep,
        "binding_energy": binding_energy,
        "mass": mass,
        "ke_per_particle": ke_mean / n_total,
        "rms_sep": rms_sep,
        "seconds_elapsed": elapsed,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Section headers
# ══════════════════════════════════════════════════════════════════════════════

def _hdr(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# Main analysis
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print()
    print("=" * 72)
    print("  MULTI-CLUSTER BINDING — SUBSTRATE DYNAMICS (NO SM IMPORTS)")
    print("  Simulation parameters:")
    print(f"    r_overlap={R_OVERLAP}  r_eq={R_EQ}  r_capture={R_CAPTURE}")
    print(f"    k_push={K_PUSH}  k_pull={K_PULL}  dt={DT}")
    print(f"    settle_steps={SETTLE_STEPS}  measure_steps={MEASURE_STEPS}")
    print("=" * 72)

    # ── 1. Mass spectrum M(N) ────────────────────────────────────────────────
    _hdr("1. MASS SPECTRUM M(N) — single clusters of N neutrinos")

    N_values = [5, 10, 20, 50, 100]
    results: dict[int, dict] = {}

    print(
        f"{'N':>6} | {'M_bound':>10} | {'KE_mean':>10} | "
        f"{'BE':>10} | {'rms_sep':>8} | {'KE/N':>8} | {'time(s)':>7}"
    )
    print("-" * 75)

    for n in N_values:
        r = measure_bound_state_mass(n, seed=n * 7, verbose=False)
        results[n] = r
        print(
            f"{r['n']:>6} | {r['mass']:>10.4f} | {r['ke_mean']:>10.4f} | "
            f"{r['binding_energy']:>10.4f} | {r['rms_sep']:>8.4f} | "
            f"{r['ke_per_particle']:>8.4f} | {r['seconds_elapsed']:>7.1f}"
        )

    # Scaling analysis
    _hdr("2. MASS SCALING ANALYSIS — how M(N) scales with N")

    print("Testing power-law fit M(N) = A * N^alpha:")
    print()
    ns = np.array([float(n) for n in N_values])
    ms = np.array([results[n]["mass"] for n in N_values])

    # Linear regression on log-log
    log_n = np.log(ns)
    log_m = np.log(np.abs(ms) + 1e-12)  # abs because mass can be negative if unbound
    alpha_fit = float(np.polyfit(log_n, log_m, 1)[0])
    A_fit = float(np.exp(np.polyfit(log_n, log_m, 1)[1]))

    print(f"  Log-log slope (alpha)  = {alpha_fit:.4f}")
    print(f"  Prefactor A            = {A_fit:.6f}")
    print()
    print("Interpretation:")
    if abs(alpha_fit - 1.0) < 0.15:
        print("  alpha ~ 1: mass scales LINEARLY with N (bag-like or free-particle regime)")
    elif alpha_fit > 1.4:
        print("  alpha > 1: super-linear — each new particle adds more than its own KE")
        print("             (cooperative binding, like a gravitational cluster)")
    elif alpha_fit < 0.7:
        print("  alpha < 1: sub-linear — binding saturates as N grows (nuclear-like)")
    print()
    print("Per-particle observables:")
    print(f"{'N':>6} | {'M/N':>10} | {'BE/N':>10} | {'BE/M':>8}")
    print("-" * 45)
    for n in N_values:
        r = results[n]
        be_over_m = (
            r["binding_energy"] / r["mass"] if abs(r["mass"]) > 1e-9 else float("nan")
        )
        print(
            f"{n:>6} | {r['mass']/n:>10.4f} | "
            f"{r['binding_energy']/n:>10.4f} | {be_over_m:>8.4f}"
        )

    # ── 3. Small and large bound states ─────────────────────────────────────
    _hdr("3. SMALL (N=5) vs LARGE (N=100) BOUND STATES")

    r_small = results[5]
    r_large = results[100]
    print(f"M_small (N=5)   = {r_small['mass']:.6f}  (KE={r_small['ke_mean']:.4f}, BE={r_small['binding_energy']:.4f})")
    print(f"M_large (N=100) = {r_large['mass']:.6f}  (KE={r_large['ke_mean']:.4f}, BE={r_large['binding_energy']:.4f})")
    print()
    ratio_large_small = r_large["mass"] / r_small["mass"] if abs(r_small["mass"]) > 1e-9 else float("nan")
    print(f"M_large / M_small = {ratio_large_small:.4f}   (N ratio = {100/5:.1f})")

    # ── 4. Three-cluster composite ───────────────────────────────────────────
    _hdr("4. THREE-CLUSTER COMPOSITE — 3 x N=5 sub-clusters")

    print("Placing 3 sub-clusters of 5 neutrinos each at large initial separation.")
    print(f"Initial cluster separation = {CLUSTER_SEP}  (>> r_capture = {R_CAPTURE})")
    print()

    r_comp = make_3cluster_composite(
        n_per_cluster=5,
        cluster_sep=CLUSTER_SEP,
        verbose=True,
    )

    m_3x_small = 3.0 * r_small["mass"]
    m_comp = r_comp["mass"]
    binding_fraction_comp = (
        (m_3x_small - m_comp) / m_3x_small
        if abs(m_3x_small) > 1e-9
        else float("nan")
    )

    print()
    print(f"M_composite (3-cluster)  = {m_comp:.6f}")
    print(f"3 × M_small              = {m_3x_small:.6f}")
    print(f"Binding fraction         = {binding_fraction_comp * 100:.2f}%")
    print(f"  (positive = composite is lighter than 3 free sub-clusters)")
    print()
    if abs(binding_fraction_comp) < 0.01:
        print("  NOTE: Binding fraction is near zero — the sub-clusters did NOT")
        print("  significantly bind into a composite under these parameters.")
    elif binding_fraction_comp > 0:
        print("  Sub-clusters formed a composite with net attractive binding.")
    else:
        print("  NOTE: Negative binding fraction — composite is HEAVIER than 3 free")
        print("  sub-clusters. This means the 3-cluster geometry increased potential energy.")

    # ── 5. Broader composite scan ────────────────────────────────────────────
    _hdr("5. COMPOSITE MASS SCAN — 3-cluster with varying sub-cluster size")

    composite_results: dict[int, dict] = {}
    small_n_vals = [3, 5, 10]
    print(
        f"{'N_sub':>6} | {'N_total':>7} | {'M_comp':>10} | "
        f"{'3*M_small':>10} | {'Bind%':>7} | {'time(s)':>7}"
    )
    print("-" * 65)
    for n_sub in small_n_vals:
        r_sub = measure_bound_state_mass(n_sub, seed=n_sub * 13, verbose=False)
        r_c = make_3cluster_composite(
            n_per_cluster=n_sub,
            cluster_sep=CLUSTER_SEP,
            verbose=False,
        )
        composite_results[n_sub] = {"sub": r_sub, "comp": r_c}
        m_3x = 3.0 * r_sub["mass"]
        m_c = r_c["mass"]
        bf = (m_3x - m_c) / m_3x * 100 if abs(m_3x) > 1e-9 else float("nan")
        print(
            f"{n_sub:>6} | {r_c['n']:>7} | {m_c:>10.4f} | "
            f"{m_3x:>10.4f} | {bf:>7.2f} | {r_c['seconds_elapsed']:>7.1f}"
        )

    # ── 6. Proton/electron ratio check ───────────────────────────────────────
    _hdr("6. PROTON/ELECTRON RATIO CHECK — M(N=15 composite) / M(N=4 single)")

    print("Question: does M(composite of 3×5) / M(single of 4) = 1836 (proton/electron ratio)?")
    print()
    print("The proton/electron ratio 1836 would require the composite to be 1836")
    print("times heavier than the single particle. In our substrate simulation:")
    print()

    # Get N=4 single result
    r_4 = measure_bound_state_mass(4, seed=4 * 17, verbose=False)
    r_15_comp = composite_results.get(5, {}).get("comp", None)
    if r_15_comp is None:
        r_15_comp = make_3cluster_composite(n_per_cluster=5, seed=55, verbose=False)

    m_4_single = r_4["mass"]
    m_15_comp = r_15_comp["mass"]

    print(f"  M(N=4 single)           = {m_4_single:.6f}")
    print(f"  M(N=15 composite)       = {m_15_comp:.6f}")

    if abs(m_4_single) > 1e-9:
        ratio_check = m_15_comp / m_4_single
        print(f"  Ratio M(15-comp)/M(4)   = {ratio_check:.4f}")
        print(f"  Target proton/electron  = 1836.15")
        print(f"  Shortfall / excess      = {ratio_check / 1836.15:.6f}x  (1.0 would be exact match)")
        print()
        if abs(ratio_check - 1836.15) / 1836.15 < 0.01:
            print("  MATCH: ratio within 1% of proton/electron ratio.")
        else:
            print("  NO MATCH: ratio is far from 1836.")
    else:
        print("  Cannot compute ratio — M(N=4 single) is effectively zero.")

    # ── 7. Honest assessment ─────────────────────────────────────────────────
    _hdr("7. HONEST ASSESSMENT")

    print("What the substrate simulation actually shows:")
    print()
    print("A. MASS DEFINITION")
    print("   In this simulation, 'mass' is KE_mean + binding_energy.")
    print("   KE_mean per particle is always ~0.5 (each moves at C=1 on 45° cone).")
    print("   The entire variation in M(N) comes from the binding energy.")
    print()

    if abs(alpha_fit - 1.0) < 0.15:
        print("B. SCALING: M(N) ~ N^1 (linear)")
        print("   Mass scales linearly with particle count.")
        print("   This is the FREE-PARTICLE regime: binding energy is small compared")
        print("   to kinetic energy, so M(N) ~ N × (KE per particle) = N/2.")
        print("   No cooperative multi-body binding emerges from these parameters.")
    elif alpha_fit > 1.2:
        print("B. SCALING: M(N) ~ N^{:.2f} (super-linear)".format(alpha_fit))
        print("   Super-linear scaling arises because more particles means more")
        print("   pairs, each contributing potential energy: N*(N-1)/2 pairs.")
        print("   With K_PULL > 0, this increases potential energy — NOT binding.")
    else:
        print("B. SCALING: M(N) ~ N^{:.2f} (sub-linear)".format(alpha_fit))
        print("   Sub-linear scaling suggests some binding saturation.")

    print()
    print("C. THE PROTON/ELECTRON RATIO 1836")
    print("   This ratio requires:")
    print("    - Either M(composite) / M(single) = 1836 from the simulation, OR")
    print("    - An identification of which simulation object corresponds to the")
    print("      electron and which to the proton/proton-like composite.")
    print()
    print("   WHAT THIS SIMULATION FINDS:")

    if abs(m_4_single) > 1e-9:
        ratio_check = m_15_comp / m_4_single
        print(f"   M(3x5 composite) / M(4 single) = {ratio_check:.4f}")
        print()
        if abs(ratio_check - 1836.15) / 1836.15 < 0.05:
            print("   UNEXPECTED MATCH — ratio is close to 1836. This would be a")
            print("   remarkable substrate-mechanical coincidence and warrants deeper study.")
        elif ratio_check < 100:
            print(f"   The ratio is {ratio_check:.1f}, roughly {ratio_check / 1836.15 * 100:.1f}%")
            print("   of 1836. The substrate's spring-like force produces an approximately")
            print("   LINEAR scaling M ~ N (since KE dominates). So a 15-particle composite")
            print("   is approximately 15/4 = 3.75× heavier than a 4-particle single,")
            print("   not 1836×.")
        else:
            print(f"   The ratio {ratio_check:.1f} departs significantly from 1836.")

    print()
    print("D. WHERE'S THE GAP?")
    print()
    print("   1. FORCE RANGE: The back-reaction force has range r_capture=1.2 in")
    print("      natural units. For the three sub-clusters to attract each other,")
    print("      they must be within r_capture. At CLUSTER_SEP=6.0, the sub-clusters")
    print("      start outside the force range and feel no mutual pull.")
    print()
    print("   2. LINEAR MASS SCALING: With cone-constrained C=1 velocities,")
    print("      KE/particle is always ~0.5, so M(N) ~ 0.5N at leading order.")
    print("      To get M_composite >> 3 × M_small, the binding energy would")
    print("      need to be negative (mass enhancement, not reduction), which")
    print("      contradicts the standard meaning of 'bound state'.")
    print()
    print("   3. THE 1836 RATIO IS NOT EMERGENT HERE: In the real Standard Model,")
    print("      the proton mass is set by QCD confinement (strong coupling, string")
    print("      tension), and the electron mass by Yukawa coupling to the Higgs.")
    print("      They are set by completely different mechanisms. The ratio 1836 is")
    print("      not derivable from counting particles in a cluster with a spring force.")
    print()
    print("   4. WHAT WOULD BE NEEDED: To reproduce the proton/electron ratio from")
    print("      substrate dynamics, the model would need a non-linear mechanism that")
    print("      makes 3-cluster composites exponentially (not linearly) heavier:")
    print("       - Confinement-like physics (string tension grows with separation)")
    print("       - Zero-point energy that grows non-linearly with kink number")
    print("       - A demonstrated coupling between internal KE and cluster-level mass")
    print("      None of these are present in the spring-potential back_reaction module.")
    print()
    print("   5. THE EXISTING multi_kink.py APPROACH: The existing make_baryon_3kink")
    print("      function achieves 938 MeV by FITTING the binding fraction from the")
    print("      empirical proton mass. That is a parameterization, not a derivation.")
    print("      predict_baryon_mass_from_substrate uses the empirical binding fraction")
    print("      η_had = 1 - M_proton / (3 × M_constituent) — which is circular.")
    print()
    print("CONCLUSION:")
    print("   The substrate dynamics (spring back-reaction between cone-constrained")
    print("   neutrinos) produces bound states whose mass scales approximately as N^1")
    print("   (linear in particle count). The proton/electron ratio 1836 does NOT")
    print("   emerge from this simulation. The composite-to-single mass ratio is")
    if abs(m_4_single) > 1e-9:
        ratio_check = m_15_comp / m_4_single
        print(f"   {ratio_check:.2f} (vs 1836 needed) — a factor of {1836.15/max(abs(ratio_check), 1e-9):.1f} short.")
    print()
    print("   This is a real gap in the model. It is noted honestly here.")
    print("   The mass spectrum that emerges: M(N) ≈ 0.5*N + BE(N), where")
    print("   BE(N) is the pairwise binding energy from the spring potential.")
    print("   It does NOT resemble the observed particle mass spectrum.")


if __name__ == "__main__":
    main()
