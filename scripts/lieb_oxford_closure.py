"""Lieb-Oxford bound closure attempt from substrate σ ≤ ½ saturation.

Goal: tighten the earlier substrate-medium derivation of the Lieb-Oxford
constant C_LO ≈ 1.804 (Lewin-Lieb-Seiringer 2019) past the ~4% window
that quantum_chemistry_substrate.py left open.

Honest scoreboard: report what works, what's still gappy, and how far
off we are. No fudge factors.
"""

from __future__ import annotations
import math


PI = math.pi


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    print("Lieb-Oxford closure attempt from substrate σ ≤ ½")
    print("Target: C_LO ≤ 1.804  (Lewin-Lieb-Seiringer 2019)")
    print()

    # =========================================================
    section("1. Lieb-Oxford bound: rigorous statement")
    # =========================================================
    print("""
For any N-electron antisymmetric wavefunction ψ with density ρ_ψ,
the exchange-correlation energy obeys

    E_xc[ρ_ψ]  ≥  - C_LO · ∫ ρ(r)^(4/3) d³r .

History of the constant:
    Lieb-Oxford (1981)        : C_LO ≤ 1.68  (loose original)
    Chan-Handy (1999)         : C_LO ≤ 1.6358 numerically
    Lewin-Lieb-Seiringer 2019 : C_LO ≤ 1.804 (current rigorous)
    Lower bound (uniform gas) : C_LO ≥ 1.4442
    Best known lower (LDA)    : C_LO ≥ 1.41

The "right" value (the supremum of -E_xc / ∫ρ^(4/3) over all densities)
is conjectured to lie near the lower-bound side; the LLS 2019 proof
gives 1.804 as the current rigorous upper certificate.

This script asks: can a substrate with σ ≤ ½ saturation reproduce
1.804 from first principles?
""")

    # =========================================================
    section("2. DFT exchange-correlation context")
    # =========================================================
    C_x_dirac = (3.0 / 4.0) * (3.0 / PI) ** (1.0 / 3.0)
    C_TF = (3.0 / 10.0) * (3.0 * PI ** 2) ** (2.0 / 3.0)
    print(f"""
Dirac exchange (1930) — local density approximation (LDA-x):
    E_x^LDA[ρ] = - C_x · ∫ ρ^(4/3) d³r,    C_x = (3/4)(3/π)^(1/3) = {C_x_dirac:.6f}

This is exchange of the uniform electron gas. It corresponds to
σ_eff = 1 (full saturation of one spin channel; pair correlation g(0)=1/2
for parallel spins). The Lieb-Oxford bound includes correlation as well,
so C_LO > C_x. The ratio

    C_LO / C_x = {1.804/C_x_dirac:.4f}

is the "correlation enhancement" the substrate must reproduce.

Thomas-Fermi kinetic constant (for orientation, not used in C_LO):
    C_TF = (3/10)(3π²)^(2/3) = {C_TF:.4f}
""")

    # =========================================================
    section("3. Substrate derivation attempt — the chain")
    # =========================================================
    print("""
Earlier attempt (quantum_chemistry_substrate.py):

    C_LO ≈ (1/σ_max) · (3/2)(3/π)^(1/3) · η_edge
         = 2 · 1.4774   · η_edge       (with σ_max = 1/2)

with η_edge ∈ [1, 4/3] giving the window [1.4774, 1.9698],
midpoint 1.7236, ~4.5% off 1.804.

Ad-hoc parts to fix:
  (a) Where exactly does (3/2)(3/π)^(1/3) come from?  Is it 2·C_x?
      Yes: 2 · (3/4)(3/π)^(1/3) = (3/2)(3/π)^(1/3) — this is
      Dirac × 2.  The factor 2 is the σ ≤ ½ inverse.  So the bracket
      hides a structural double-count.
  (b) Edge correction [1, 4/3] was guessed.  Need to derive from
      substrate strain at boundary.
  (c) Saturation σ ≤ ½ enters as 1/σ_max = 2; this is rigorous
      from antisymmetry (Pauli: half-occupation per spatial mode).
""")

    # =========================================================
    section("4. Geometric factor breakdown")
    # =========================================================
    print(f"""
Re-derivation of (3/2)(3/π)^(1/3):

Step 1.  Uniform electron gas exchange energy density per electron:
            ε_x(ρ) = - C_x · ρ^(1/3),     C_x = (3/4)(3/π)^(1/3)

Step 2.  C_x can be written
            C_x = (3/4) · k_F / π · (something dimensionless)
         where k_F = (3π²ρ)^(1/3) is the Fermi momentum.  In fact
            C_x = (3/4) (3/π)^(1/3) follows from
            C_x = (1/(2π³)) · ∫_0^k_F ∫_0^k_F  d³k d³k' / |k-k'|² · ρ^(-4/3)
         which evaluates to the standard Dirac result.

Step 3.  Pauli enforcement: the Slater determinant fills each spatial
         mode at half-density per spin.  σ_max = 1/2 per spin channel.
         The exchange hole integral is over PAIRS within one spin,
         giving the exchange energy ≈ - C_x ρ^(4/3) per spin,
         × 2 spins ⇒ the standard Dirac formula already has the spin
         sum baked in.  So 1/σ_max = 2 is NOT a free additional factor —
         it is already inside C_x.

→  This kills the "× 2 from saturation" in the earlier script.
   The bracket (3/2)(3/π)^(1/3) was double-counting the spin doubling.

Corrected geometric base:
    C_geom = C_x = (3/4)(3/π)^(1/3) = {C_x_dirac:.6f}

The rest must come from CORRELATION beyond exchange.
""")

    # =========================================================
    section("5. Edge mode correction — derive bounds rigorously")
    # =========================================================
    # Substrate edge-strain: gradient correction to LDA.
    # For a half-space with density profile ρ(z) = ρ_bulk · θ(-z) smoothed
    # over correlation length ξ, the boundary contribution to the
    # exchange-correlation integral is proportional to ∫|∇ρ|² ρ^(-4/3).
    # In the substrate medium, σ ≤ ½ caps the relative density gradient
    # at the same scale: |∇ρ|/ρ ≤ 1/ξ, with ξ ≈ k_F^(-1).
    #
    # The LLS 2019 proof breaks E_xc into bulk + boundary; the boundary
    # piece carries a factor that can be bounded by the GGA-type
    # enhancement F_x(s) at the maximally inhomogeneous limit.
    #
    # PBE GGA gives F_x(s→∞) = 1 + κ with κ = 0.804 (PBE Lieb-Oxford
    # saturation).  This is NOT a coincidence — Perdew-Burke-Ernzerhof
    # set κ = 0.804 specifically so that the GGA exchange respects
    # the LO bound everywhere.  So κ_PBE = C_LO/C_x − 1 by construction:
    kappa_pbe = 1.804 / C_x_dirac - 1.0
    print(f"""
PBE GGA enhancement saturates at  F_x(∞) = 1 + κ  with κ = 0.804.
Cross-check:  κ = C_LO/C_x − 1 = {kappa_pbe:.4f}.
Match to PBE κ=0.804 at  {abs(kappa_pbe-0.804)/0.804*100:.2f}%.

This is circular for "deriving" C_LO from PBE (PBE was fit to LO),
but it gives the SHAPE we must reproduce: a multiplicative enhancement
F = 1 + κ of the Dirac base.

Substrate ansatz: edge enhancement comes from σ = ½ saturation of
the strain gradient.  The most-inhomogeneous limit is a single
electron density (Hartree self-interaction limit), where exchange
exactly cancels Hartree, forcing F_x ≥ 1 + κ_min.

Known rigorous bounds on the enhancement at s→∞:
    Lower (LDA limit, s=0)              :  F = 1
    Upper (single-electron, s→∞)         :  F = C_LO/C_x ≈ 2.450

Our substrate gives no independent prediction of κ_max — we can only
say κ_max ≥ κ_min from saturation, where

    κ_min  =  σ_max · (some integer)  =  (1/2) · 1.608  =  0.804  ?

The "1.608" is what we need to derive.  Without it, this is fitted.
""")

    # =========================================================
    section("6. Saturation cap σ ≤ ½ — rigorous inclusion")
    # =========================================================
    # σ ≤ ½ comes from Pauli (one fermion per spin-mode). In the strain
    # picture it is the maximal local strain density before mode collapse.
    #
    # In the LO context, σ_max enters via the on-top pair density:
    #   g(0) ≥ 1/2  for parallel spins (forced by antisymmetry)
    # which is exactly Pauli; and
    #   g(0) ≥ 0    for antiparallel (Hartree-Fock allows full)
    # The LO constant comes from bounding correlation hole depth, and
    # the strongest hole is the antiparallel-spin one — there σ has no
    # rigorous lower cap from Pauli, only from charge-positivity of
    # the on-top pair density.
    #
    # So σ_max = ½ alone does NOT pin C_LO. It pins the EXCHANGE part.

    sigma_max = 0.5
    base = C_x_dirac
    # Best bracket we can put up rigorously:
    # Lower: pure exchange = C_x = 0.7386
    # Upper: 1.804 (LLS rigorous bound)
    # Substrate adds nothing beyond restating Pauli.
    print(f"""
σ ≤ ½ is Pauli rephrased as a strain cap.  It pins the exchange piece
(Dirac, C_x = {C_x_dirac:.4f}) but is silent on the correlation piece.
The gap

    C_LO − C_x = {1.804 - C_x_dirac:.4f}

is pure correlation enhancement.  Substrate σ ≤ ½ does not give a
zero-parameter prediction for this gap.

Earlier script's "× 2 from σ_max" was double-counting:
    Dirac C_x already integrates over both spin channels.
    Multiplying by 2 = 1/σ_max gives 2·C_x = {2*C_x_dirac:.4f},
    accidentally close to C_LO = 1.804 but for the wrong reason.
""")

    # =========================================================
    section("7. Numerical result + comparison + honest gap")
    # =========================================================
    C_LO_target = 1.804

    # Honest decomposition the substrate CAN justify:
    #   (a) Dirac exchange base = (3/4)(3/π)^(1/3)
    #   (b) σ_max=1/2 spin-doubling: ALREADY IN (a). No extra factor.
    #   (c) correlation enhancement κ: NOT derived from substrate.
    #
    # If we naively multiply by 1/σ_max we get 2·C_x — close, but a coincidence:
    naive_substrate = (1.0 / sigma_max) * C_x_dirac
    naive_gap = (naive_substrate - C_LO_target) / C_LO_target * 100
    # Honest bracket: lower = C_x (exchange-only), upper = LLS 1.804.
    bracket_lo = C_x_dirac
    bracket_hi = 1.804
    bracket_mid = 0.5 * (bracket_lo + bracket_hi)
    bracket_gap_mid = (bracket_mid - C_LO_target) / C_LO_target * 100

    # Edge-mode "1 to 4/3" attempt — reframed as PBE-style enhancement
    # bounded by saturation:
    eta_lo, eta_hi = 1.0, 4.0 / 3.0
    edge_lo = (1.0 / sigma_max) * C_x_dirac * eta_lo
    edge_hi = (1.0 / sigma_max) * C_x_dirac * eta_hi
    edge_mid = 0.5 * (edge_lo + edge_hi)
    edge_gap = (edge_mid - C_LO_target) / C_LO_target * 100

    print(f"""
Comparison table:

    Dirac exchange base  C_x                    = {C_x_dirac:.4f}
    Naive substrate (2·C_x, no edge)            = {naive_substrate:.4f}    Δ = {naive_gap:+.2f}%
    Honest bracket [C_x, 1.804] midpoint        = {bracket_mid:.4f}    Δ = {bracket_gap_mid:+.2f}%
    Earlier window 2·C_x·[1, 4/3] midpoint       = {edge_mid:.4f}    Δ = {edge_gap:+.2f}%
    LLS 2019 rigorous upper                     = {C_LO_target:.4f}    (target)

The earlier ~4% match (1.7236 vs 1.804) was real, but the chain
contained ONE rigorous step and TWO ad-hoc steps:
    rigorous : Pauli σ≤½ doubling → 2·C_x = 1.4774   (off by ~18%)
    ad hoc   : edge factor [1, 4/3] (no derivation)
    ad hoc   : pick midpoint of window
""")

    # =========================================================
    section("8. What's still missing for a rigorous derivation")
    # =========================================================
    print("""
To CLOSE the gap to 1.804 from substrate primitives we need:

  (1) Derivation of the correlation enhancement κ = C_LO/C_x − 1 ≈ 1.443
      from substrate ξ, K, ρ, γ.  This is NOT contained in σ ≤ ½ alone.
      It must come from substrate response at finite gradient — i.e.
      a substrate analogue of the Lindhard / RPA correlation function.

  (2) Proof that the on-top pair density bound g(0) ≥ 0 saturates at
      the LLS value when the substrate strain saturates.  This is the
      antiparallel-spin contribution and is the actually-hard part of
      the LLS 2019 proof.

  (3) A substrate "scaling" argument that the 4/3 power is forced.
      In LO this comes from dimensional analysis on the exchange hole;
      in the substrate it should come from the 3D scaling of strain
      under uniform compression.  The earlier script implicitly assumed
      this without proof.

None of (1), (2), (3) is closed by the σ ≤ ½ cap.

Conclusion: σ ≤ ½ rigorously gives  C_x = 0.7386, NOT 1.804.
The ~4% match in the earlier script was a numerical coincidence
between (1/σ_max)·C_x · midpoint(1, 4/3) ≈ 1.72 and C_LO ≈ 1.80.
""")

    # =========================================================
    section("9. Possible directions to close the gap")
    # =========================================================
    print("""
Three honest paths forward:

  A.  Substrate response function approach.
      Build the substrate density-density response χ(q,ω) from the
      4 primitives (K, ρ, ξ, γ).  In the limit q → 0 it must reduce
      to Lindhard; at finite q the strain-saturation σ ≤ ½ caps the
      correlation hole depth.  Compute - ∫ χ(q,0) · v_C(q) d³q / ρ^(4/3)
      and check whether the σ-saturated answer is 1.804.

  B.  Explicit LO test functional.
      LLS 2019 proof uses a particular trial state (a "uniform
      neutralized scaling" construction).  Reproduce it as a substrate
      strain configuration and evaluate the substrate energy density.
      Match to 1.804 from substrate primitives only.

  C.  Bound from Möbius bundle topology.
      In B3 / strain-medium, the closest analogue of the LO scaling
      4/3 is the bundle amplitude squared on K_4 = 11/12.  Worth
      checking whether 11/12 · 2 · C_x has a structural meaning:
                  2 · 11/12 · 0.7386 = 1.354    ← off, no.
      Or 4π/9 · 2 · C_x ?   4π/9 = 1.396, gives 2.063 — also off.
      No obvious topological closure.  Path A or B is more promising.

Bottom line for the strain-medium scoreboard:

    Lieb-Oxford C_LO ≈ 1.804  is currently NOT a clean substrate result.
    The earlier 4% match was midpoint-of-fitted-window, not derivation.
    Substrate σ ≤ ½ rigorously gives only the Dirac exchange C_x =
    0.7386, off by 59% from C_LO = 1.804.

    Status: OPEN.  Demote from "matched at ~4%" to "exchange piece
    matched, correlation enhancement still gappy."
""")

    # final summary numbers for the tail
    print()
    print("=" * 72)
    print("FINAL NUMERICAL SCORECARD")
    print("=" * 72)
    print(f"  C_LO target (LLS 2019)             : 1.8040")
    print(f"  Substrate rigorous (= C_x Dirac)   : {C_x_dirac:.4f}    gap {(C_x_dirac-1.804)/1.804*100:+.1f}%")
    print(f"  Substrate naive (2·C_x)            : {naive_substrate:.4f}    gap {naive_gap:+.1f}%")
    print(f"  Earlier ad-hoc window midpoint     : {edge_mid:.4f}    gap {edge_gap:+.1f}%")
    print(f"  Honest verdict: exchange piece OK; correlation enhancement")
    print(f"                  κ ≈ 1.443 NOT derived from σ ≤ ½ alone.")
    print(f"  Closure status: OPEN. Best honest gap from substrate-only: ~59%.")


if __name__ == "__main__":
    main()
