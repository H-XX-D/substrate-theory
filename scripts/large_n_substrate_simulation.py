"""Large-N substrate simulation: emergent bound-state structure from neutrino dynamics.

This script runs the actual substrate mechanics — NOT imported SM formulas.
It uses the existing back_reaction, three_d, and atomic modules exclusively.

What this measures:
  - Cluster formation from random initial conditions
  - Bound-state sizes, stability, and mass spectrum in substrate units
  - Bouncing (oscillation) frequencies of bound pairs
  - Effective charge asymmetry from medium back-reaction
  - Whether any mass hierarchy emerges

Protocol:
  N neutrinos, random positions in a cubic box, random velocities on the
  45-degree cone. Back-reaction force applied pairwise (push/pull potential
  with equilibrium radius r_eq and capture radius r_capture). Velocity-Verlet
  integrator with cone projection at every step.

All quantities in natural substrate units: length unit L0=1, speed C=1,
time unit T0=L0/C=1. No SM constants imported.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import NamedTuple

import numpy as np

# ---------------------------------------------------------------------------
# Existing substrate modules — ONLY these, no SM imports
# ---------------------------------------------------------------------------
from stiff_medium.neutrino import C
from stiff_medium.three_d import make_on_cone
from stiff_medium.back_reaction import back_reaction_force, project_to_cone

# ---------------------------------------------------------------------------
# Substrate parameters (all in natural units: L0=1, C=1, T0=1)
# These are NOT tuned to match SM values; they define the substrate's rules.
# ---------------------------------------------------------------------------

# Equilibrium distance: where push and pull balance
R_EQ: float = 1.0

# Capture radius: beyond this, no interaction
R_CAPTURE: float = 3.0

# Spring constants for push (repulsive) and pull (attractive) zones
K_PUSH: float = 2.0
K_PULL: float = 1.0

# Time step for Verlet integrator (must be small enough for stability)
DT: float = 0.02

# Box size (particles initialized inside; periodic boundary NOT used — open box)
BOX_SIZE: float = 12.0

# Cluster detection: two particles are "bound" if their separation < r_bound
R_BOUND: float = R_CAPTURE * 1.1

# Stability window: check cluster membership at beginning and end of this window
STABILITY_WINDOW: int = 500  # steps


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    """A single substrate neutrino with mutable state for the simulation loop.

    Attributes:
        pos:  position (3,)
        vel:  velocity on 45-degree cone, |vel| = C
        axis: cone axis unit vector (3,)
        idx:  unique particle index
    """
    pos: np.ndarray
    vel: np.ndarray
    axis: np.ndarray
    idx: int


class ClusterStats(NamedTuple):
    """Summary statistics for one identified cluster."""
    size: int
    center: np.ndarray          # geometric center
    com_velocity: np.ndarray    # mean velocity of members
    mean_separation: float      # mean pairwise separation inside cluster
    kinetic_energy: float       # sum of (1/2)|v|^2 per member (all equal C^2/2)
    binding_energy: float       # negative = bound; sum of pair potential energies
    total_energy: float         # kinetic + binding
    oscillation_freq: float     # bouncing frequency from pairwise motion (rad/step)


@dataclass
class SimulationResult:
    """Everything we measured from one N-particle run."""
    N: int
    n_steps: int
    clusters: list[ClusterStats]
    free_particles: int
    cluster_sizes: list[int]
    mass_spectrum: list[float]   # |total_energy| for each cluster
    run_time_s: float
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Initialization helpers
# ---------------------------------------------------------------------------

def random_unit_vector(rng: np.random.Generator) -> np.ndarray:
    """Draw a uniformly random unit vector on S^2."""
    v = rng.standard_normal(3)
    return v / np.linalg.norm(v)


def initialize_particles(
    N: int,
    box: float,
    rng: np.random.Generator,
) -> list[Particle]:
    """Place N particles with random positions and cone-constrained velocities.

    Positions: uniform in [-box/2, box/2]^3.
    Axes:      random unit vectors.
    Velocities: on the 45-degree cone around each particle's axis, random azimuth,
                speed C — using existing make_on_cone from three_d.py.
    """
    particles: list[Particle] = []
    for i in range(N):
        pos = rng.uniform(-box / 2.0, box / 2.0, 3).astype(float)
        axis = random_unit_vector(rng)
        azimuth = rng.uniform(0.0, 2.0 * math.pi)
        vel = make_on_cone(axis, azimuth, speed=C)
        particles.append(Particle(pos=pos.copy(), vel=vel.copy(), axis=axis.copy(), idx=i))
    return particles


# ---------------------------------------------------------------------------
# Force computation
# ---------------------------------------------------------------------------

def compute_all_forces(particles: list[Particle]) -> list[np.ndarray]:
    """Pairwise back-reaction forces using back_reaction_force from back_reaction.py.

    back_reaction_force(pos_a, pos_b, r_eq, r_capture, k_push, k_pull)
    returns force on A due to B. Force on B is minus that (Newton III).
    """
    N = len(particles)
    forces = [np.zeros(3, dtype=float) for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            f_on_i = back_reaction_force(
                particles[i].pos,
                particles[j].pos,
                r_eq=R_EQ,
                r_capture=R_CAPTURE,
                k_push=K_PUSH,
                k_pull=K_PULL,
            )
            forces[i] += f_on_i
            forces[j] -= f_on_i  # Newton III
    return forces


# ---------------------------------------------------------------------------
# Velocity-Verlet integrator with cone projection
# ---------------------------------------------------------------------------

def vverlet_step_N(particles: list[Particle], dt: float) -> None:
    """One in-place velocity-Verlet step for N particles.

    Velocity-Verlet with cone projection at every velocity update, using
    project_to_cone from back_reaction.py — same integrator as vverlet_step
    but for N > 2 particles simultaneously.

    Modifies particles[i].pos and particles[i].vel in place.
    """
    N = len(particles)

    # Step 1: compute forces at current positions
    forces_0 = compute_all_forces(particles)

    # Step 2: half-step velocity update + cone project, then full-step position
    half_vel = []
    for i in range(N):
        # acceleration = force / mass; mass = 1 (all particles identical)
        v_half = project_to_cone(
            particles[i].vel + 0.5 * forces_0[i] * dt,
            particles[i].axis,
            speed=C,
        )
        half_vel.append(v_half)

    new_pos = []
    for i in range(N):
        new_pos.append(particles[i].pos + half_vel[i] * dt)

    # Step 3: compute forces at new positions
    # Temporarily move particles to new positions
    old_pos = [p.pos.copy() for p in particles]
    for i in range(N):
        particles[i].pos = new_pos[i]

    forces_1 = compute_all_forces(particles)

    # Restore old positions (we'll assign at end)
    for i in range(N):
        particles[i].pos = old_pos[i]

    # Step 4: full velocity update + cone project, then finalize position
    for i in range(N):
        new_vel = project_to_cone(
            half_vel[i] + 0.5 * forces_1[i] * dt,
            particles[i].axis,
            speed=C,
        )
        particles[i].pos = new_pos[i]
        particles[i].vel = new_vel


# ---------------------------------------------------------------------------
# Cluster detection (simple union-find on r < R_BOUND)
# ---------------------------------------------------------------------------

def detect_clusters(particles: list[Particle], r_bound: float) -> list[list[int]]:
    """Union-find cluster detection.

    Two particles are in the same cluster if their separation < r_bound.
    Returns list of clusters, each a list of particle indices.
    """
    N = len(particles)
    parent = list(range(N))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(N):
        for j in range(i + 1, N):
            d = float(np.linalg.norm(particles[i].pos - particles[j].pos))
            if d < r_bound:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(N):
        root = find(i)
        groups.setdefault(root, []).append(i)

    return list(groups.values())


# ---------------------------------------------------------------------------
# Pair potential energy (for binding energy calculation)
# ---------------------------------------------------------------------------

def pair_potential(d: float) -> float:
    """Spring-like potential energy between two particles at distance d.

    Matches the force definition in back_reaction_force:
      d < r_eq:            U = 0.5 * K_PUSH * (r_eq - d)^2   (repulsive well)
      r_eq < d < r_capture: U = -0.5 * K_PULL * (d - r_eq)^2  (attractive well, negative = bound)
      d > r_capture:        U = 0

    The attractive region gives negative potential energy — that's the binding.
    """
    if d < 1e-12 or d > R_CAPTURE:
        return 0.0
    if d < R_EQ:
        return 0.5 * K_PUSH * (R_EQ - d) ** 2
    else:
        return -0.5 * K_PULL * (d - R_EQ) ** 2


def cluster_binding_energy(particles: list[Particle], indices: list[int]) -> float:
    """Total pairwise potential energy for a cluster."""
    total = 0.0
    for ii in range(len(indices)):
        for jj in range(ii + 1, len(indices)):
            i, j = indices[ii], indices[jj]
            d = float(np.linalg.norm(particles[i].pos - particles[j].pos))
            total += pair_potential(d)
    return total


# ---------------------------------------------------------------------------
# Oscillation frequency detection (from relative motion of bound pair)
# ---------------------------------------------------------------------------

def measure_oscillation_freq(
    sep_history: list[float],
    dt: float,
) -> float:
    """Estimate oscillation angular frequency from a separation time series.

    Uses zero-crossing count on the detrended separation signal.
    Returns angular frequency in rad/step (= rad per dt), or 0 if signal is too
    short or has no oscillations.
    """
    if len(sep_history) < 20:
        return 0.0
    arr = np.array(sep_history, dtype=float)
    # Detrend: subtract mean (look at oscillations around equilibrium)
    arr = arr - np.mean(arr)
    # Count zero crossings
    crossings = np.sum(np.diff(np.sign(arr)) != 0)
    if crossings < 2:
        return 0.0
    # Each full oscillation = 2 zero crossings
    n_oscillations = crossings / 2.0
    total_time = len(arr) * dt
    freq_hz = n_oscillations / total_time
    omega = 2.0 * math.pi * freq_hz
    return omega


# ---------------------------------------------------------------------------
# Theoretical oscillation frequency from the spring constants
# ---------------------------------------------------------------------------

def theoretical_omega() -> float:
    """Angular frequency of small oscillations around r_eq.

    Near r_eq, the potential is approximately harmonic. On the attractive side,
    U ~ -0.5 * K_PULL * (d - r_eq)^2, giving effective spring constant K_PULL.
    The reduced mass for two identical unit-mass particles is mu = 0.5.
    So omega_theory = sqrt(K_PULL / mu) = sqrt(2 * K_PULL).
    """
    return math.sqrt(2.0 * K_PULL)


# ---------------------------------------------------------------------------
# Cluster characterization
# ---------------------------------------------------------------------------

def characterize_cluster(
    particles: list[Particle],
    indices: list[int],
    sep_history: dict[tuple[int, int], list[float]],
    dt: float,
) -> ClusterStats:
    """Compute all observable properties of one cluster."""
    size = len(indices)
    members = [particles[i] for i in indices]

    center = np.mean([p.pos for p in members], axis=0)
    com_vel = np.mean([p.vel for p in members], axis=0)

    # All velocities have magnitude C (cone constraint), so KE per particle = C^2/2
    kinetic_energy = size * 0.5 * C ** 2

    binding = cluster_binding_energy(particles, indices)

    # Mean pairwise separation inside cluster
    seps = []
    for ii in range(size):
        for jj in range(ii + 1, size):
            d = float(np.linalg.norm(members[ii].pos - members[jj].pos))
            seps.append(d)
    mean_sep = float(np.mean(seps)) if seps else 0.0

    # Oscillation frequency: use the closest pair's history if available
    omega = 0.0
    for ii in range(size):
        for jj in range(ii + 1, size):
            key = (min(indices[ii], indices[jj]), max(indices[ii], indices[jj]))
            if key in sep_history and len(sep_history[key]) >= 20:
                omega_ij = measure_oscillation_freq(sep_history[key], dt)
                if omega_ij > omega:
                    omega = omega_ij

    return ClusterStats(
        size=size,
        center=center,
        com_velocity=com_vel,
        mean_separation=mean_sep,
        kinetic_energy=kinetic_energy,
        binding_energy=binding,
        total_energy=kinetic_energy + binding,
        oscillation_freq=omega,
    )


# ---------------------------------------------------------------------------
# Main simulation runner
# ---------------------------------------------------------------------------

def run_simulation(
    N: int,
    n_steps: int,
    seed: int = 42,
    progress_every: int = 1000,
) -> SimulationResult:
    """Run the full substrate simulation for N particles, n_steps steps.

    Args:
        N:             Number of neutrinos.
        n_steps:       Total integration steps.
        seed:          RNG seed for reproducibility.
        progress_every: Print progress every this many steps.

    Returns:
        SimulationResult with all measured quantities.
    """
    rng = np.random.default_rng(seed)
    t_start = time.perf_counter()

    print(f"\n{'='*60}")
    print(f"  N={N} particles | {n_steps} steps | dt={DT}")
    print(f"  r_eq={R_EQ}  r_capture={R_CAPTURE}  k_push={K_PUSH}  k_pull={K_PULL}")
    print(f"  Box={BOX_SIZE}^3   omega_theory={theoretical_omega():.4f} rad/step")
    print(f"{'='*60}")

    # Initialize
    particles = initialize_particles(N, BOX_SIZE, rng)

    # Track pairwise separation histories for oscillation measurement
    # Only track pairs that start within capture radius (saves memory for large N)
    sep_history: dict[tuple[int, int], list[float]] = {}
    for i in range(N):
        for j in range(i + 1, N):
            d = float(np.linalg.norm(particles[i].pos - particles[j].pos))
            if d < R_CAPTURE * 2:
                sep_history[(i, j)] = []

    # Cluster snapshots at beginning and end of stability window
    clusters_early: list[list[int]] = []
    clusters_late: list[list[int]] = []

    # Main integration loop
    for step in range(n_steps):
        vverlet_step_N(particles, DT)

        # Record pairwise separations for tracked pairs
        if step % 5 == 0:  # sample every 5 steps to save memory
            for (i, j) in sep_history:
                d = float(np.linalg.norm(particles[i].pos - particles[j].pos))
                sep_history[(i, j)].append(d)

        # Snapshot clusters near end of run
        if step == n_steps - STABILITY_WINDOW:
            clusters_early = detect_clusters(particles, R_BOUND)
        if step == n_steps - 1:
            clusters_late = detect_clusters(particles, R_BOUND)

        # Progress reporting
        if (step + 1) % progress_every == 0:
            n_clusters = len(detect_clusters(particles, R_BOUND))
            free = sum(1 for c in detect_clusters(particles, R_BOUND) if len(c) == 1)
            elapsed = time.perf_counter() - t_start
            print(
                f"  step {step+1:6d}/{n_steps}"
                f"  clusters={n_clusters}"
                f"  free={free}"
                f"  elapsed={elapsed:.1f}s"
            )

    # Final cluster analysis
    final_clusters = detect_clusters(particles, R_BOUND)
    cluster_stats = []
    for cluster_idx_list in final_clusters:
        if len(cluster_idx_list) >= 1:
            stats = characterize_cluster(particles, cluster_idx_list, sep_history, DT)
            cluster_stats.append(stats)

    # Sort by size descending
    cluster_stats.sort(key=lambda s: s.size, reverse=True)

    # Stability check: which clusters from early snapshot still exist at end?
    stable_count = 0
    for early_c in clusters_early:
        early_set = set(early_c)
        for late_c in final_clusters:
            late_set = set(late_c)
            overlap = len(early_set & late_set) / max(len(early_set), 1)
            if overlap > 0.5:
                stable_count += 1
                break

    mass_spectrum = [abs(s.total_energy) for s in cluster_stats if s.size > 1]
    free_count = sum(1 for s in cluster_stats if s.size == 1)

    notes = [
        f"Stable clusters (>50% overlap over last {STABILITY_WINDOW} steps): {stable_count}",
        f"Theoretical omega = {theoretical_omega():.4f} rad/step",
        f"Run wall time: {time.perf_counter() - t_start:.2f}s",
    ]

    result = SimulationResult(
        N=N,
        n_steps=n_steps,
        clusters=cluster_stats,
        free_particles=free_count,
        cluster_sizes=[s.size for s in cluster_stats],
        mass_spectrum=mass_spectrum,
        run_time_s=time.perf_counter() - t_start,
        notes=notes,
    )

    print(f"\n  Done in {result.run_time_s:.1f}s")
    return result


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(result: SimulationResult) -> None:
    """Print a detailed honest report of what emerged."""
    print(f"\n{'='*60}")
    print(f"  RESULTS  N={result.N}  steps={result.n_steps}")
    print(f"{'='*60}")

    # Cluster size distribution
    from collections import Counter
    size_dist = Counter(result.cluster_sizes)
    print(f"\n  Cluster size distribution:")
    for size in sorted(size_dist):
        count = size_dist[size]
        label = "free" if size == 1 else f"size-{size}"
        print(f"    {label:12s}: {count:4d}  ({100*count/len(result.clusters):.1f}%)")

    # Largest clusters
    print(f"\n  Largest clusters (up to 5):")
    for i, s in enumerate(result.clusters[:5]):
        print(f"    Cluster {i+1}: size={s.size}  "
              f"KE={s.kinetic_energy:.4f}  "
              f"BE={s.binding_energy:.4f}  "
              f"E_total={s.total_energy:.4f}  "
              f"mean_sep={s.mean_separation:.4f}  "
              f"omega={s.oscillation_freq:.4f}")

    # Mass spectrum (bound states only)
    bound = [s for s in result.clusters if s.size > 1]
    if bound:
        masses = sorted([abs(s.total_energy) for s in bound])
        print(f"\n  Mass spectrum (|E_total| for bound states, {len(bound)} clusters):")
        for i, m in enumerate(masses[:10]):
            print(f"    m[{i}] = {m:.6f}  (substrate energy units)")

        # Mass ratios relative to smallest bound state
        if len(masses) >= 2:
            m0 = masses[0]
            print(f"\n  Mass ratios m[i]/m[0]:")
            for i, m in enumerate(masses[:8]):
                print(f"    m[{i}]/m[0] = {m/m0:.4f}")

            # Compare to lepton ratios (observed: m_mu/m_e ~ 206.8, m_tau/m_e ~ 3477)
            # We cannot expect exact match — just reporting what emerges
            print(f"\n  Observed lepton ratios for reference (NOT fitted):")
            print(f"    m_mu/m_e  = 206.77")
            print(f"    m_tau/m_e = 3477.2")
            print(f"  Substrate ratios:")
            for i in range(1, min(len(masses), 5)):
                print(f"    m[{i}]/m[0] = {masses[i]/masses[0]:.3f}")

    else:
        print(f"\n  No bound clusters found (all particles free).")

    # Oscillation frequencies
    omegas = [s.oscillation_freq for s in bound if s.oscillation_freq > 0]
    if omegas:
        print(f"\n  Oscillation frequencies (omega in rad/step):")
        print(f"    Measured range: [{min(omegas):.4f}, {max(omegas):.4f}]")
        print(f"    Theoretical:     {theoretical_omega():.4f}")
        print(f"    Ratio measured/theoretical: {np.mean(omegas)/theoretical_omega():.3f}")
    else:
        print(f"\n  No oscillation frequencies measured (pairs too short-lived or not oscillating).")

    # Free particles
    print(f"\n  Free (unbound) particles: {result.free_particles} / {result.N}")

    # Notes
    print(f"\n  Notes:")
    for note in result.notes:
        print(f"    {note}")


def print_comparison(results: list[SimulationResult]) -> None:
    """Compare results across N=20, 50, 100."""
    print(f"\n{'='*60}")
    print(f"  CROSS-N COMPARISON")
    print(f"{'='*60}")

    print(f"\n  {'N':>6}  {'free':>6}  {'bound2':>7}  {'bound3+':>8}  "
          f"{'max_size':>9}  {'mass_range':>22}")
    print(f"  {'-'*6}  {'-'*6}  {'-'*7}  {'-'*8}  {'-'*9}  {'-'*22}")

    for res in results:
        free = sum(1 for s in res.clusters if s.size == 1)
        b2 = sum(1 for s in res.clusters if s.size == 2)
        b3 = sum(1 for s in res.clusters if s.size >= 3)
        max_size = max(res.cluster_sizes) if res.cluster_sizes else 0
        masses = sorted([abs(s.total_energy) for s in res.clusters if s.size > 1])
        if masses:
            mass_str = f"[{masses[0]:.3f}, {masses[-1]:.3f}]"
        else:
            mass_str = "none"
        print(f"  {res.N:>6}  {free:>6}  {b2:>7}  {b3:>8}  {max_size:>9}  {mass_str:>22}")

    # Honest assessment of hierarchy
    print(f"\n  HONEST ASSESSMENT OF MASS HIERARCHY:")

    all_masses: list[float] = []
    for res in results:
        bound = [s for s in res.clusters if s.size > 1]
        all_masses.extend([abs(s.total_energy) for s in bound])

    if not all_masses:
        print("    No bound states formed. No mass hierarchy to report.")
        print("    This means the substrate parameters do not support stable binding")
        print("    at this N and box size — a genuine null result.")
        return

    all_masses.sort()
    print(f"    Total bound states across all runs: {len(all_masses)}")
    print(f"    Mass range: [{min(all_masses):.4f}, {max(all_masses):.4f}]  (substrate units)")

    if len(all_masses) >= 2:
        # Cluster the masses to look for distinct levels
        # Simple: look at ratios between consecutive sorted masses
        ratios = [all_masses[i+1] / all_masses[i] for i in range(len(all_masses)-1)]
        print(f"    Consecutive mass ratios (sorted): {[f'{r:.3f}' for r in ratios[:10]]}")

        # Does the spread look like it could span e/mu/tau (factors ~200 and ~17)?
        total_span = all_masses[-1] / all_masses[0] if all_masses[0] > 0 else 0
        print(f"    Total mass span: {total_span:.2f}x")
        print(f"    Lepton span for comparison: ~3477x (e to tau)")
        print()
        if total_span > 100:
            print("    The mass span is large — consistent with a POSSIBLE hierarchy,")
            print("    but the exact ratios do NOT match lepton masses. The substrate")
            print("    dynamics here produce a spectrum, but it is determined by")
            print("    k_push, k_pull, r_eq, r_capture — not by first-principles SM values.")
        elif total_span > 5:
            print("    Moderate mass spread. Some hierarchy exists but span is much smaller")
            print("    than the 3477x range from electron to tau lepton.")
        else:
            print("    Masses are tightly clustered. No significant hierarchy emerged.")
            print("    The substrate dynamics at these parameters produce near-degenerate")
            print("    bound states, NOT a lepton-like mass spectrum.")

    print()
    print("    CONCLUSION: This simulation shows what the substrate rules actually")
    print("    produce. Any match to real particle masses would require both a")
    print("    physical derivation of k_push/k_pull/r_eq from first principles AND")
    print("    the values happening to produce the correct ratios. Neither is")
    print("    demonstrated here. The simulation is honest about this.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # Parse optional N override from command line (e.g. python3 ... --N 20)
    N_values = [20, 50, 100]
    n_steps_map = {20: 10000, 50: 8000, 100: 5000}

    # For large N the O(N^2) force computation is the bottleneck.
    # N=100 with 5000 steps ~ 100^2/2 * 5000 = 25M force evaluations.
    # Each evaluation is cheap (numpy vector ops), should complete in ~60-120s.

    print("LARGE-N SUBSTRATE SIMULATION")
    print("Real substrate mechanics: back_reaction_force + project_to_cone + vverlet")
    print("No SM formulas imported. All units natural (C=1, L0=1).")
    print(f"\nSubstrate parameters:")
    print(f"  r_eq        = {R_EQ}")
    print(f"  r_capture   = {R_CAPTURE}")
    print(f"  k_push      = {K_PUSH}  (repulsion strength)")
    print(f"  k_pull      = {K_PULL}  (attraction strength)")
    print(f"  dt          = {DT}")
    print(f"  omega_theory= {theoretical_omega():.4f} rad/step  (small-oscillation freq)")

    results: list[SimulationResult] = []

    for N in N_values:
        n_steps = n_steps_map[N]
        result = run_simulation(N=N, n_steps=n_steps, seed=1337, progress_every=2000)
        print_report(result)
        results.append(result)

    print_comparison(results)
