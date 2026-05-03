"""Substrate scattering experiment: extract effective fine-structure constant α_eff.

Strategy
--------
Build two N=4 neutrino clusters bound by the back-reaction spring.
Scatter them at various impact parameters b and initial kinetic energies E.
Fit the classical Rutherford / Coulomb-like formula:

    tan(θ/2) = α_eff / (2 E b)

and extract α_eff from the fit.

The force law used is back_reaction.py::back_reaction_force, which produces a
spring-like interaction with minimum at r_eq:

    F ~ k_pull * (d - r_eq)   [attractive,   r_eq < d < r_capture]
    F ~ -k_push * (r_eq - d)  [repulsive,     d < r_eq]

The long-range tail (r_eq < d < r_capture) is attractive by design.  For
like-charge (repulsive) scattering we flip the sign so both regimes push out.

Units: natural (c = 1, r_eq = 1).

Honest purpose
--------------
We are NOT inserting α = 1/137 anywhere.  The coupling constants k_pull and
k_push are substrate parameters.  The α_eff we extract tells us what
effective electromagnetic constant THIS particular substrate dynamics implies.

The output will honestly state whether α_eff matches 1/137.
"""

from __future__ import annotations

import math
import sys
import warnings
from dataclasses import dataclass
from typing import Final

import numpy as np

# ---------------------------------------------------------------------------
# Bring substrate modules onto the path (PYTHONPATH=src already set by runner)
# ---------------------------------------------------------------------------
from stiff_medium.back_reaction import back_reaction_force, vverlet_step

# ---------------------------------------------------------------------------
# Natural-units constants
# ---------------------------------------------------------------------------

C: Final[float] = 1.0          # speed of light = 1
R_EQ: Final[float] = 1.0       # equilibrium radius  [natural units = 1]
R_CAPTURE: Final[float] = 3.0  # capture radius: no force beyond this

# Spring constants — these are the ONLY free parameters that set the force scale.
# k_pull sets the long-range attraction; k_push sets the short-range repulsion.
# We use dimensionless values consistent with a Yukawa-like substrate.
K_PUSH: Final[float] = 10.0    # repulsive spring constant
K_PULL: Final[float] = 1.0     # attractive spring constant (Coulomb analog)

# Cluster composition
N_PER_CLUSTER: Final[int] = 4  # neutrinos per bound cluster

# Simulation parameters
DT: Final[float] = 0.005       # time step
T_MAX_FACTOR: Final[float] = 60.0  # run for T_MAX_FACTOR * r_eq / v_rel steps
SEPARATION_INITIAL: Final[float] = 10.0 * R_EQ  # initial centre-to-centre distance

# Impact parameters to probe (in units of r_eq)
IMPACT_PARAMETERS: Final[list[float]] = [0.1, 0.5, 1.0, 2.0, 5.0]

# Initial relative speed (fraction of c)
V_REL_FRAC: Final[float] = 0.5


# ---------------------------------------------------------------------------
# Cluster builder
# ---------------------------------------------------------------------------

def build_cluster(centre: np.ndarray, n: int = N_PER_CLUSTER) -> list[np.ndarray]:
    """Return n positions arranged in a compact cluster around `centre`.

    Args:
        centre: 3D centre of the cluster.
        n: Number of constituent positions.

    Returns:
        List of n 3D position arrays.
    """
    rng = np.random.default_rng(seed=42)
    # Place constituents on a slightly jittered sphere of radius r_eq/3 so
    # they are all within the equilibrium distance of each other.
    radius = R_EQ * 0.4
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    positions = []
    for phi in angles:
        offset = radius * np.array([np.cos(phi), np.sin(phi), 0.0])
        positions.append(centre + offset)
    return positions


def cluster_centre_of_mass(positions: list[np.ndarray]) -> np.ndarray:
    """Compute centre of mass of a cluster (equal masses)."""
    return np.mean(np.stack(positions), axis=0)


# ---------------------------------------------------------------------------
# Force computation between two clusters
# ---------------------------------------------------------------------------

def inter_cluster_force(
    pos_A: list[np.ndarray],
    pos_B: list[np.ndarray],
    sign: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute total force on cluster A and cluster B from pairwise interactions.

    Args:
        pos_A: Positions of cluster A constituents.
        pos_B: Positions of cluster B constituents.
        sign: +1 for repulsive (like charges), -1 for attractive (opposite charges).
              The back_reaction_force already has its own sign convention for
              the spring potential, so `sign` simply flips the long-range tail.

    Returns:
        (F_on_A, F_on_B): Total 3D force vectors on each cluster.
    """
    F_on_A = np.zeros(3)
    F_on_B = np.zeros(3)

    for pa in pos_A:
        for pb in pos_B:
            diff = pb - pa
            d = float(np.linalg.norm(diff))
            if d < 1e-12 or d > R_CAPTURE:
                continue
            unit = diff / d
            # Spring force from back_reaction_force (returns force on A due to B)
            f_vec = back_reaction_force(pa, pb, R_EQ, R_CAPTURE, K_PUSH, K_PULL)
            # For repulsive (like-charge): flip the attractive tail
            if sign > 0:
                # attractive tail becomes repulsive:
                # when d > r_eq the natural force pulls A toward B;
                # for same-charge we want it to push A away from B.
                if d > R_EQ:
                    f_vec = -f_vec  # flip long-range part
                # short-range (d < r_eq) is already repulsive — keep it
            F_on_A += f_vec
            F_on_B -= f_vec  # Newton 3rd law

    return F_on_A, F_on_B


# ---------------------------------------------------------------------------
# Single scattering simulation
# ---------------------------------------------------------------------------

@dataclass
class ScatterResult:
    """Result of one scattering event."""
    impact_parameter: float
    energy: float
    theta_rad: float
    theta_deg: float
    tan_half_theta: float
    converged: bool
    n_steps: int


def run_scattering(
    b: float,
    v_rel: float,
    sign: float = 1.0,
    dt: float = DT,
    t_max_factor: float = T_MAX_FACTOR,
) -> ScatterResult:
    """Simulate one scattering event and return the asymptotic scattering angle.

    Two clusters (each N=4 neutrinos) approach from separation SEPARATION_INITIAL,
    interact via the substrate back-reaction force, and separate.

    The scattering angle θ is measured from the asymptotic initial and final
    velocity vectors of the centre-of-mass of cluster A.

    Args:
        b: Impact parameter in units of r_eq.
        v_rel: Relative approach speed (natural units, should be < C).
        sign: +1 = repulsive (like charges), -1 = attractive (opposite charges).
        dt: Time step.
        t_max_factor: Simulation time = t_max_factor * SEPARATION_INITIAL / v_rel.

    Returns:
        ScatterResult with angle and metadata.
    """
    # --- Initial positions ---
    # Cluster A approaches from -x, cluster B sits at +x.
    # Impact parameter b is offset in the y direction.
    half_sep = SEPARATION_INITIAL / 2.0
    centre_A0 = np.array([-half_sep, b, 0.0])
    centre_B0 = np.array([+half_sep, 0.0, 0.0])

    pos_A = build_cluster(centre_A0)
    pos_B = build_cluster(centre_B0)

    # --- Initial velocities (centre-of-mass frame) ---
    # Cluster A moves in +x direction, Cluster B moves in -x direction.
    v_half = v_rel / 2.0
    vel_A = [np.array([+v_half, 0.0, 0.0]) for _ in pos_A]
    vel_B = [np.array([-v_half, 0.0, 0.0]) for _ in pos_B]

    # Record initial CM velocities for angle computation
    cm_vel_A_initial = np.mean(np.stack(vel_A), axis=0).copy()

    # --- Simulate ---
    t_max = t_max_factor * SEPARATION_INITIAL / (v_rel + 1e-12)
    n_steps_max = int(t_max / dt) + 1

    for step in range(n_steps_max):
        # Compute pairwise inter-cluster forces
        F_A, F_B = inter_cluster_force(pos_A, pos_B, sign=sign)

        # Mass per constituent = 1/N (cluster has total mass 1)
        mass = 1.0 / N_PER_CLUSTER

        # Update each constituent by giving them the cluster-CM acceleration
        # (the cluster moves rigidly; internal forces are balance separately)
        a_A = F_A / (N_PER_CLUSTER * mass)  # = F_A (since N*mass = 1)
        a_B = F_B / (N_PER_CLUSTER * mass)

        for i in range(len(pos_A)):
            # velocity Verlet (simplified: treat whole cluster as unit mass = 1)
            vel_A[i] = vel_A[i] + a_A * dt
            pos_A[i] = pos_A[i] + vel_A[i] * dt

        for i in range(len(pos_B)):
            vel_B[i] = vel_B[i] + a_B * dt
            pos_B[i] = pos_B[i] + vel_B[i] * dt

        # Check if clusters are well separated and moving apart
        cm_A = cluster_centre_of_mass(pos_A)
        cm_B = cluster_centre_of_mass(pos_B)
        separation = float(np.linalg.norm(cm_A - cm_B))
        cm_vel_A_now = np.mean(np.stack(vel_A), axis=0)

        if step > 100 and separation > SEPARATION_INITIAL * 0.9:
            # Check that A is moving away (dot product of v_A with direction from B to A)
            direction_from_B_to_A = (cm_A - cm_B) / (separation + 1e-12)
            moving_apart = float(np.dot(cm_vel_A_now, direction_from_B_to_A)) > 0
            if moving_apart:
                break

    # --- Measure scattering angle ---
    cm_vel_A_final = np.mean(np.stack(vel_A), axis=0)

    # Normalise
    v_init_norm = cm_vel_A_initial / (np.linalg.norm(cm_vel_A_initial) + 1e-20)
    v_final_norm = cm_vel_A_final / (np.linalg.norm(cm_vel_A_final) + 1e-20)

    cos_theta = float(np.clip(np.dot(v_init_norm, v_final_norm), -1.0, 1.0))
    theta_rad = math.acos(cos_theta)
    theta_deg = math.degrees(theta_rad)
    tan_half = math.tan(theta_rad / 2.0) if theta_rad < math.pi else float("inf")

    converged = step < n_steps_max - 1

    return ScatterResult(
        impact_parameter=b,
        energy=0.5 * v_rel**2,  # kinetic energy per unit mass in CM frame
        theta_rad=theta_rad,
        theta_deg=theta_deg,
        tan_half_theta=tan_half,
        converged=converged,
        n_steps=step,
    )


# ---------------------------------------------------------------------------
# Rutherford fit
# ---------------------------------------------------------------------------

def fit_alpha_eff(
    results: list[ScatterResult],
    label: str = "",
) -> dict:
    """Fit tan(θ/2) = α_eff / (2 E b) to extract α_eff.

    Uses linear regression on:
        tan(θ/2) = α_eff * (1 / (2 E b))
    so slope = α_eff, intercept forced to 0.

    Args:
        results: List of ScatterResult from run_scattering calls.
        label: Human-readable label for the fit group.

    Returns:
        Dict with alpha_eff, fit_quality, and per-point data.
    """
    x_vals = []   # 1 / (2 E b)
    y_vals = []   # tan(θ/2)
    b_vals = []

    for r in results:
        if not r.converged:
            continue
        if r.impact_parameter <= 0:
            continue
        denom = 2.0 * r.energy * r.impact_parameter
        if denom < 1e-15:
            continue
        x = 1.0 / denom
        y = r.tan_half_theta
        if not math.isfinite(y) or not math.isfinite(x):
            continue
        x_vals.append(x)
        y_vals.append(y)
        b_vals.append(r.impact_parameter)

    if len(x_vals) < 2:
        return {
            "label": label,
            "alpha_eff": float("nan"),
            "n_points": len(x_vals),
            "r_squared": float("nan"),
            "comment": "Insufficient converged data points for fit.",
            "points": [],
        }

    x = np.array(x_vals)
    y = np.array(y_vals)

    # Weighted least squares: y = alpha_eff * x, no intercept
    alpha_eff = float(np.dot(x, y) / np.dot(x, x))

    # R^2 for this 0-intercept model
    y_pred = alpha_eff * x
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum(y**2))
    r_squared = 1.0 - ss_res / (ss_tot + 1e-20)

    points = [
        {
            "b": b_vals[i],
            "1/(2Eb)": x_vals[i],
            "tan(theta/2)": y_vals[i],
            "tan_predicted": float(alpha_eff * x_vals[i]),
        }
        for i in range(len(x_vals))
    ]

    return {
        "label": label,
        "alpha_eff": alpha_eff,
        "n_points": len(x_vals),
        "r_squared": r_squared,
        "comment": "",
        "points": points,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(sign: float, label: str, v_rel: float = V_REL_FRAC) -> dict:
    """Run scattering at all impact parameters for a given charge sign.

    Args:
        sign: +1 = repulsive (like-charge), -1 = attractive (opposite-charge).
        label: Human-readable label.
        v_rel: Relative velocity.

    Returns:
        Dict containing individual results and the Rutherford fit.
    """
    print(f"\n  Running {label} scattering...")
    results = []
    for b in IMPACT_PARAMETERS:
        r = run_scattering(b=b, v_rel=v_rel, sign=sign)
        results.append(r)
        status = "OK" if r.converged else "TIMEOUT"
        print(
            f"    b={b:5.2f} r_eq | theta={r.theta_deg:8.3f} deg | "
            f"tan(theta/2)={r.tan_half_theta:10.6f} | steps={r.n_steps:6d} [{status}]"
        )

    fit = fit_alpha_eff(results, label=label)
    return {"results": results, "fit": fit}


def print_fit_summary(fit: dict, alpha_qed: float = 1.0 / 137.036) -> None:
    """Print the α_eff fit summary with honest comparison to QED.

    Args:
        fit: Return value of fit_alpha_eff.
        alpha_qed: QED measured fine-structure constant.
    """
    alpha_eff = fit["alpha_eff"]
    print(f"\n  --- Rutherford fit: {fit['label']} ---")
    print(f"  Points used:  {fit['n_points']}")
    if math.isfinite(alpha_eff):
        print(f"  alpha_eff     = {alpha_eff:.6f}")
        print(f"  1/alpha_eff   = {1/alpha_eff:.2f}" if alpha_eff > 0 else "  1/alpha_eff   = N/A (negative)")
        print(f"  R^2           = {fit['r_squared']:.4f}")
        print(f"\n  alpha_QED     = {alpha_qed:.6f}  (= 1/{1/alpha_qed:.3f})")
        if alpha_eff > 0:
            ratio = alpha_eff / alpha_qed
            print(f"  Ratio alpha_eff / alpha_QED = {ratio:.4f}")
        else:
            print("  alpha_eff <= 0: no Coulomb-like repulsion measured")
    else:
        print("  alpha_eff = NaN (fit failed)")


def honest_assessment(repulsive_fit: dict, attractive_fit: dict, alpha_qed: float) -> None:
    """Print a candid evaluation of what the simulation shows.

    Args:
        repulsive_fit: Fit result from like-charge scattering.
        attractive_fit: Fit result from opposite-charge scattering.
        alpha_qed: Measured QED fine-structure constant 1/137.
    """
    alpha_rep = repulsive_fit["alpha_eff"]
    alpha_att = attractive_fit["alpha_eff"]

    print("\n" + "=" * 70)
    print("HONEST ASSESSMENT: Does the substrate give α_eff = 1/137?")
    print("=" * 70)
    print()
    print("Substrate parameters used:")
    print(f"  k_push (short-range repulsion)  = {K_PUSH}")
    print(f"  k_pull (long-range attraction)  = {K_PULL}")
    print(f"  r_eq (equilibrium distance)     = {R_EQ}")
    print(f"  r_capture (force cutoff)        = {R_CAPTURE}")
    print(f"  N per cluster                   = {N_PER_CLUSTER}")
    print(f"  v_rel (initial)                 = {V_REL_FRAC} c")
    print()

    if math.isfinite(alpha_rep) and alpha_rep > 0:
        ratio = alpha_rep / alpha_qed
        print(f"REPULSIVE scattering:  alpha_eff = {alpha_rep:.6f}  (1/{1/alpha_rep:.1f})")
        print(f"  Compared to 1/137:  ratio = {ratio:.4f}")
        if 0.5 < ratio < 2.0:
            print("  ROUGH order-of-magnitude match (within 2x)")
        else:
            gap_decades = math.log10(ratio) if ratio > 0 else float("nan")
            print(f"  OFF by factor {ratio:.2f}  (= 10^{gap_decades:.2f} decades)")
    else:
        print(f"REPULSIVE scattering:  alpha_eff = {alpha_rep}  (fit failed or non-positive)")

    if math.isfinite(alpha_att) and alpha_att > 0:
        ratio_att = alpha_att / alpha_qed
        print(f"\nATTRACTIVE scattering: alpha_eff = {alpha_att:.6f}  (1/{1/alpha_att:.1f})")
        print(f"  Compared to 1/137:  ratio = {ratio_att:.4f}")
    else:
        print(f"\nATTRACTIVE scattering: alpha_eff = {alpha_att}")

    print()
    print("WHAT THIS RESULT MEANS:")
    print()
    print("  The back_reaction force is a SPRING with free parameters")
    print("  k_push and k_pull.  No physics forces these to any specific value.")
    print("  The 'coupling constant' we extract is:")
    print()
    print("      alpha_eff = k_pull * (some geometric factor involving r_eq,")
    print("                  r_capture, cluster size, and N)")
    print()
    print("  It is NOT an independent prediction of α = 1/137.  To get the")
    print("  measured α from the substrate, you would need to derive k_pull")
    print("  from the substrate Lagrangian L_total (MODEL.md §9).  That")
    print("  derivation requires integrating out the kink zero-modes on the")
    print("  Möbius bundle — a multi-loop computation not yet completed.")
    print()
    print("  The existing alpha_derivation.py module in src/ already documents")
    print("  this honestly: the Coleman bosonization route and RG running give")
    print("  constraints on what β² must be, but the gap between those")
    print("  constraints and 1/137 requires a bundle-field-theory calculation")
    print("  that does not yet exist.")
    print()

    if math.isfinite(alpha_rep) and alpha_rep > 0:
        ratio = alpha_rep / alpha_qed
        if abs(ratio - 1.0) < 0.01:
            print("  NOTE: alpha_eff is suspiciously close to 1/137.  Check whether")
            print("  the coupling constants k_push/k_pull were set to reproduce this")
            print("  value.  A genuine test requires deriving k_pull from the theory.")
        else:
            print(f"  The substrate with k_pull={K_PULL}, k_push={K_PUSH} gives")
            print(f"  alpha_eff = {alpha_rep:.4f}, which differs from 1/137 by")
            print(f"  a factor of {ratio:.2f}.  This confirms the force scale is a")
            print("  free parameter: nothing in the current simulation fixes it.")

    print()
    print("BOTTOM LINE:")
    print("  alpha_eff (from simulation) = WHATEVER k_pull SETS IT TO BE.")
    print("  alpha_QED (measured)        = 1/137.036 = 0.007297...")
    print("  To genuinely test α from the substrate requires:")
    print("    1. Derive k_pull from first principles (L_total → 1-loop on Möbius bundle)")
    print("    2. Show that derived k_pull, when plugged into THIS simulation,")
    print("       gives alpha_eff = 1/137.")
    print("    3. That calculation is open work (MODEL.md §6 item 1).")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full substrate scattering experiment."""
    print("=" * 70)
    print("SUBSTRATE SCATTERING: Effective Fine-Structure Constant")
    print("=" * 70)
    print()
    print(f"Setup: N={N_PER_CLUSTER} neutrinos per cluster, v_rel = {V_REL_FRAC}c")
    print(f"       Impact params b = {IMPACT_PARAMETERS} r_eq")
    print(f"       Initial separation = {SEPARATION_INITIAL} r_eq")
    print()

    alpha_qed = 1.0 / 137.035999084

    # --- Repulsive (like-charge) scattering ---
    print("PART 1: Like-charge (repulsive) scattering")
    print("-" * 50)
    rep_data = run_experiment(sign=+1.0, label="repulsive (like-charge)")
    print_fit_summary(rep_data["fit"], alpha_qed=alpha_qed)

    # --- Attractive (opposite-charge) scattering ---
    print("\nPART 2: Opposite-charge (attractive) scattering")
    print("-" * 50)
    att_data = run_experiment(sign=-1.0, label="attractive (opposite-charge)")
    print_fit_summary(att_data["fit"], alpha_qed=alpha_qed)

    # --- Comparison table ---
    print("\n" + "=" * 70)
    print("SCATTERING ANGLE SUMMARY TABLE")
    print("=" * 70)
    print(f"{'b [r_eq]':>10}  {'theta_rep [deg]':>16}  {'tan(t/2)_rep':>13}  "
          f"{'theta_att [deg]':>16}  {'tan(t/2)_att':>13}")
    print("-" * 75)
    for r_rep, r_att in zip(rep_data["results"], att_data["results"]):
        print(
            f"{r_rep.impact_parameter:>10.2f}  "
            f"{r_rep.theta_deg:>16.3f}  "
            f"{r_rep.tan_half_theta:>13.6f}  "
            f"{r_att.theta_deg:>16.3f}  "
            f"{r_att.tan_half_theta:>13.6f}"
        )

    # --- Rutherford fit points ---
    print("\nRutherford fit data (repulsive):")
    print(f"{'b':>8}  {'1/(2Eb)':>12}  {'tan(t/2)_data':>14}  {'tan(t/2)_fit':>13}")
    print("-" * 55)
    for pt in rep_data["fit"].get("points", []):
        print(
            f"{pt['b']:>8.2f}  "
            f"{pt['1/(2Eb)']:>12.6f}  "
            f"{pt['tan(theta/2)']:>14.6f}  "
            f"{pt['tan_predicted']:>13.6f}"
        )

    # --- Honest assessment ---
    honest_assessment(rep_data["fit"], att_data["fit"], alpha_qed)


if __name__ == "__main__":
    main()
