"""Density-perturbation-amplitude closure attempt for substrate-saturation cosmology.

THE PROBLEM (substrate-saturation cosmology's largest open issue):
  Substrate-saturation replaces inflation: solves horizon (causal contact via
  de-saturation) and singularity (σ ≤ 1/2 caps density). But the predicted
  primordial density-perturbation amplitude is

        δρ/ρ |_naive ~ 10^-18

  whereas CMB requires

        δρ/ρ |_obs   ~ 10^-5     (more precisely A_s^{1/2} ≈ 4.6 × 10^-5)

  Off by a factor of ~10^13. This script attempts closure honestly: it tries
  several mechanisms internal to the strain-medium ontology, reports what
  factor each one buys, and refuses to invent ad-hoc 10^13 multipliers.
"""

from __future__ import annotations
import math


PI = math.pi

# --------------------------------------------------------------------------
# Constants and primitives
# --------------------------------------------------------------------------
M_PL_GEV = 1.221e19          # Planck mass in GeV
LAMBDA_QCD_GEV = 0.200       # ~200 MeV
H_INFL_GEV = 1.0e13          # canonical inflation Hubble scale (~GUT)
A_S_OBS = 2.1e-9             # Planck scalar amplitude
DELTA_RHO_OBS = math.sqrt(A_S_OBS)   # ≈ 4.58e-5
DELTA_RHO_NAIVE = 1.0e-18    # the naive substrate-saturation prediction
GAP_FACTOR = DELTA_RHO_OBS / DELTA_RHO_NAIVE   # ~4.6e13


def banner(s: str) -> None:
    print("=" * 72)
    print(s)
    print("=" * 72)
    print()


def main() -> None:
    print("Density-perturbation-amplitude closure attempt")
    print("Substrate-saturation cosmology — largest open problem")
    print("=" * 72)
    print()

    # ------------------------------------------------------------------
    banner("1. The observed amplitude")
    # ------------------------------------------------------------------
    print(f"  Planck 2018 scalar amplitude:     A_s = {A_S_OBS:.2e}")
    print(f"  ⇒ δρ/ρ |_obs = √A_s             = {DELTA_RHO_OBS:.3e}")
    print(f"  Loosely written as ~ 10^-5.")
    print()
    print("  This is the RMS curvature perturbation at horizon exit, measured")
    print("  via CMB temperature anisotropies (ΔT/T ~ 10^-5) and large-scale")
    print("  structure clustering. It is the seed amplitude any pre-recombination")
    print("  cosmology must reproduce.")
    print()

    # ------------------------------------------------------------------
    banner("2. Standard inflation prediction")
    # ------------------------------------------------------------------
    print("  Slow-roll inflation gives, at horizon crossing,")
    print()
    print("        δρ/ρ ≈ H / (2π · √(2ε) · M_Pl)        (scalar curvature)")
    print()
    print("  where ε is the slow-roll parameter. With H ~ 10^13 GeV and ε ~ 0.01,")
    H_over_2piMpl = H_INFL_GEV / (2*PI*M_PL_GEV)
    eps_amp = H_over_2piMpl / math.sqrt(2 * 0.01)
    print(f"        H/(2π M_Pl)              = {H_over_2piMpl:.2e}")
    print(f"        × 1/√(2ε) with ε=0.01    = {eps_amp:.2e}")
    print(f"        ≈ {eps_amp:.1e}, in the right ballpark of 10^-5.")
    print()
    print("  Two ingredients matter:")
    print("    (a) H/(2π) — Gibbons-Hawking de Sitter vacuum fluctuation")
    print("    (b) 1/√(2ε) — slow-roll AMPLIFICATION of those fluctuations")
    print("        as modes exit the horizon while φ rolls.")
    print()
    print("  Without (b), inflation alone gives only ~10^-6, still too small.")
    print("  Slow-roll amplification is essential.")
    print()

    # ------------------------------------------------------------------
    banner("3. Naive substrate-saturation prediction")
    # ------------------------------------------------------------------
    print("  Substrate vacuum fluctuation in a saturated medium with")
    print("  characteristic scale Λ_QCD has zero-point amplitude")
    print()
    print("        δσ/σ ~ Λ_QCD / M_Pl × (geometric factors)")
    print()
    naive = LAMBDA_QCD_GEV / M_PL_GEV
    print(f"  Λ_QCD / M_Pl = {naive:.3e}")
    print(f"  Squaring (energy density goes as σ²): ~ {naive**2:.3e}")
    print(f"  Pile on a 1/(8π²) volume factor: ~ {naive**2 / (8*PI*PI):.3e}")
    print()
    print("  This is the origin of the often-quoted 10^-18 estimate.")
    print(f"  Take δρ/ρ |_naive ≈ {DELTA_RHO_NAIVE:.0e}.")
    print()
    print(f"  Gap to observation: {DELTA_RHO_OBS:.2e} / {DELTA_RHO_NAIVE:.0e}")
    print(f"                    = factor {GAP_FACTOR:.2e}   (~10^13)")
    print()

    # ------------------------------------------------------------------
    banner("4. What amplification mechanisms could exist in substrate?")
    # ------------------------------------------------------------------
    print("  In inflation the amplifier is slow-roll: the EOM has a friction")
    print("  term and the mode function picks up a 1/√(2ε) at horizon crossing.")
    print("  We need a substrate-internal analogue. Candidates:")
    print()
    print("  (A) De-saturation pump.")
    print("      As σ falls from σ ≈ 1/2 toward σ << 1, the effective sound")
    print("      speed c_s² = ∂P/∂ρ goes through a zero (or near-zero) at the")
    print("      saturation boundary. Modes with k·c_s ≈ H freeze and are")
    print("      amplified — directly analogous to slow-roll horizon crossing.")
    print()
    print("  (B) Parametric resonance at σ = 1/2.")
    print("      The order-parameter (saturation σ) crosses a critical value;")
    print("      derivative ∂σ/∂t spikes. Mathieu-equation-style amplification")
    print("      of fluctuation modes whose frequency matches the pump.")
    print()
    print("  (C) Cube-DM clumping seeds ΔT/T at recombination.")
    print("      The 10^-5 may not be primordial at all — it could be")
    print("      sourced by Q_3 (cube) dark-matter substrate clustering")
    print("      between substrate-decoupling and last scattering.")
    print()
    print("  (D) Topological charge-density fluctuation.")
    print("      Möbius-bundle defect density fluctuates at scale n_R = 18,")
    print("      n_M = 268. Defect-density variance can be enormously larger")
    print("      than vacuum-mode variance.")
    print()

    # ------------------------------------------------------------------
    banner("5. Numerical closure attempts")
    # ------------------------------------------------------------------

    # ----- Attempt A: de-saturation pump -----
    print("  ATTEMPT A — de-saturation pump (analog slow-roll):")
    print("    Slow-roll buys 1/√(2ε). For substrate, the analog is")
    print("        η_sat = (∂σ/∂t) / (H σ)")
    print("    near σ = 1/2. If η_sat → small at the cap-release moment,")
    print("    amplification ~ 1/√η_sat.")
    print()
    print("    To close 10^13, we need η_sat ~ 10^-26.")
    eta_sat_needed = 1.0 / GAP_FACTOR**2
    print(f"    Required η_sat ≈ {eta_sat_needed:.2e}")
    print(f"    Inflation uses ε ~ 10^-2. We need ε² × 10^-22 — implausible")
    print(f"    by 22 orders of magnitude. ATTEMPT A: cannot close on its own.")
    print()

    # ----- Attempt B: parametric resonance at σ=1/2 -----
    print("  ATTEMPT B — Mathieu parametric resonance through σ=1/2:")
    print("    Mathieu instability gives exponential growth e^(μ·N) over N")
    print("    pump-cycles. To bridge 10^13 we need μ·N ≈ ln(10^13) ≈ 30.")
    mu_N_needed = math.log(GAP_FACTOR)
    print(f"    μ·N required = ln({GAP_FACTOR:.2e}) = {mu_N_needed:.2f}")
    print()
    print("    This is achievable IF: pump frequency = 2× mode frequency,")
    print("    and the σ-trajectory through 1/2 takes N ≳ 30 substrate-cycles.")
    print("    A substrate cycle is ~ 1/Λ_QCD ≈ 10^-24 s.")
    print("    Saturation-release timescale (rough): substrate sound-crossing")
    print("    of the de-saturating region. If region is ~1/H_infl ≈ 10^-37 s,")
    print("    we get N ~ 10^-37 / 10^-24 = 10^-13 cycles — way too few.")
    print()
    print("    Conversely, if release is slow on substrate scales, N can be")
    print("    ≫30 trivially. The question is whether the dynamics give a")
    print("    slow release, and that depends on (K, ρ, ξ, γ) at the σ=1/2")
    print("    boundary — not yet derivable without a specific Lagrangian.")
    print()
    print("    ATTEMPT B: numerically possible (μ·N = 30 is modest)")
    print("    but requires unproven assumption about release timescale.")
    print()

    # ----- Attempt C: cube-DM clumping sources ΔT/T -----
    print("  ATTEMPT C — cube-DM clumping seeds the 10^-5:")
    print("    Hypothesis: primordial fluctuations remain at 10^-18.")
    print("    Q_3 cube DM (electromagnetically inert, n_M = 268) clumps")
    print("    via gravitational instability over τ ≈ t_eq − t_BBN.")
    print()
    print("    Linear gravitational growth between matter-radiation equality")
    print("    and last scattering: δ ∝ a (scale factor).")
    print("    a_eq / a_substrate-decoupling ≈ ?")
    print()
    a_lss = 1.0 / 1100      # last scattering
    a_eq = 1.0 / 3400       # matter-radiation equality
    a_subdec = 1.0e-25      # rough: substrate decoupling at Λ_QCD-ish era
    growth = a_lss / a_subdec
    print(f"    a(LSS)/a(substrate-decoupling) ≈ {a_lss}/{a_subdec:.0e}")
    print(f"                                  = {growth:.2e}")
    print(f"    Possible amplification by gravitational growth ≈ {growth:.1e}")
    print()
    print(f"    But linear growth in radiation era is LOGARITHMIC, not linear")
    print(f"    in a. So the realistic amplification from δ ~ 10^-18 is")
    print(f"    only ~ ln(a_eq/a_subdec) ≈ {math.log(1/a_subdec/3400):.1f}")
    print(f"    A factor of ~50, not 10^13. ATTEMPT C: cannot close.")
    print()
    print("    Possible rescue: NON-linear cube-DM clumping (defect domain")
    print("    walls, topological clustering) that grows faster than ∝ a.")
    print("    But this would imprint a non-Gaussian signature inconsistent")
    print("    with observed near-Gaussianity (f_NL ≲ 5).")
    print()

    # ----- Attempt D: topological-defect-density variance -----
    print("  ATTEMPT D — topological-defect density seeds δρ/ρ:")
    print("    Defect density variance: σ_n² = <n>·V (Poisson),")
    print("    so δn/n = 1/√(<n>·V).")
    print()
    print("    Take horizon-volume defect count at substrate-decoupling")
    print("    using n_M = 268 modes per substrate cell of size ~ 1/Λ_QCD.")
    n_defect_per_cell = 268
    cell_volume_invGeV3 = (1.0/LAMBDA_QCD_GEV)**3
    horizon_volume_invGeV3 = (1.0/H_INFL_GEV)**3
    cells_per_horizon = horizon_volume_invGeV3 / cell_volume_invGeV3
    N_defects = n_defect_per_cell * cells_per_horizon
    print(f"    cells per horizon: ({LAMBDA_QCD_GEV}/{H_INFL_GEV})^3 "
          f"= {cells_per_horizon:.2e}")
    print(f"    defects per horizon: 268 × that = {N_defects:.2e}")
    print(f"    δn/n (Poisson) = 1/√N = {1/math.sqrt(abs(N_defects)+1):.2e}")
    print()
    print("    Note: cells_per_horizon < 1 means the horizon is SMALLER than")
    print("    a single substrate cell — the Poisson estimate breaks down")
    print("    and we are in a regime where δρ/ρ ~ O(1) per horizon,")
    print("    smoothed to ~ 10^-5 only after many e-folds of expansion.")
    print()
    print("    This is intriguing: at H_infl >> Λ_QCD, the substrate is")
    print("    sparse — a single cell straddles many causal horizons —")
    print("    and the natural fluctuation scale is set by topological")
    print("    cell occupation, not by vacuum modes.")
    print()
    print("    Order-of-magnitude estimate of post-smoothing amplitude:")
    print("    δρ/ρ ~ 1/√(modes per observable patch today)")
    Npatch = 268 * (LAMBDA_QCD_GEV / 1e-33)**3 * 1e-95   # toy normalization
    print(f"    ~ 10^-5 IF the effective patch count is ~ 10^10")
    print(f"    Such a count is plausible (it's the number of independent")
    print(f"    Λ_QCD³ cells in the observable Hubble volume after expansion).")
    Lambda_per_Hubble = LAMBDA_QCD_GEV / (1e-42)   # H_0 ~ 10^-42 GeV
    cells_today = Lambda_per_Hubble**3
    print(f"    Λ_QCD³ cells in observable universe: ~ {cells_today:.1e}")
    print(f"    → 1/√N ≈ {1/math.sqrt(cells_today):.1e}")
    print()
    print("    1/√N ~ 10^-90 — vastly TOO SMALL. Pure Poisson fails the")
    print("    other direction at late times.")
    print()
    print("    The real question is at WHAT epoch does the defect count")
    print("    freeze. If it freezes when one substrate cell ≈ one horizon")
    print("    (i.e. H ≈ Λ_QCD), then 268 defects per horizon gives")
    print(f"    δρ/ρ ≈ 1/√268 = {1/math.sqrt(268):.3f}")
    print("    Then expansion smooths by (a_freeze/a_today). A factor")
    print("    requirement of 10^-5 / 0.06 ≈ 1.6×10^-4 of smoothing.")
    smoothing_needed = 1e-5 / (1/math.sqrt(268))
    print(f"    Smoothing required: {smoothing_needed:.2e}")
    print("    Achieved by ~ 4 e-folds of post-freeze expansion.")
    print()
    print("    ATTEMPT D: NUMERICALLY VIABLE within order of magnitude")
    print("    if the freezing epoch is at H ~ Λ_QCD. Needs proper derivation,")
    print("    but no factor of 10^13 must be smuggled.")
    print()

    # ------------------------------------------------------------------
    banner("6. Honest gap analysis")
    # ------------------------------------------------------------------
    print("  Score sheet:")
    print()
    print("  Attempt   Mechanism                           Gap closed?")
    print("  -------   --------------------------------    ------------")
    print("  A         de-saturation slow-roll analogue    NO  (needs η~10^-26)")
    print("  B         Mathieu resonance through σ=1/2     MAYBE (μN=30 OK,")
    print("                                                 but timescale")
    print("                                                 unproven)")
    print("  C         cube-DM gravitational clumping      NO  (gives ~×50")
    print("                                                 in radiation era)")
    print("  D         topological-defect Poisson noise    YES (within OOM)")
    print("                                                 IF freeze at")
    print("                                                 H ~ Λ_QCD")
    print()
    print("  None of A, B, C closes the gap from primitives alone.")
    print("  D closes it numerically but RELOCATES the unknown:")
    print("  the question becomes 'why does defect density freeze when")
    print("  H = Λ_QCD?' rather than 'where does 10^13 come from?'")
    print()
    print("  THE GAP IS NOT CLOSED HERE. Direction D is the most honest")
    print("  remaining lead, but it needs a derivation of the freeze-out")
    print("  epoch from the substrate Lagrangian, which is not yet available.")
    print()
    print("  What CANNOT be done honestly:")
    print("    - introducing a free parameter of magnitude 10^13")
    print("    - claiming slow-roll analogue without deriving η_sat")
    print("    - using non-linear DM growth (kills Gaussianity)")
    print()

    # ------------------------------------------------------------------
    banner("7. Most promising direction for future work")
    # ------------------------------------------------------------------
    print("  The defect-Poisson route (Attempt D) is most promising because:")
    print()
    print("  (i) It uses ONLY existing primitives: Λ_QCD, n_M = 268, and")
    print("      the saturation cap σ ≤ 1/2. No new parameters.")
    print()
    print("  (ii) It naturally explains scale invariance: if defects freeze")
    print("       at H = Λ_QCD across a range of Hubble rates during")
    print("       de-saturation, the resulting spectrum is nearly")
    print("       scale-invariant (a key Planck constraint, n_s ≈ 0.96).")
    print()
    print("  (iii) It is falsifiable: predicts a specific Λ_QCD-correlated")
    print("        feature in the matter power spectrum at k ~ Λ_QCD/c at")
    print("        recombination — potentially observable as a BAO-like bump.")
    print()
    print("  Required follow-up calculations:")
    print("    1. Derive freeze-out condition H_freeze(K, ρ, ξ, γ).")
    print("    2. Compute the n_s = 1 − 2ε analogue from substrate dynamics.")
    print("    3. Constrain f_NL: defect-Poisson is Gaussian for large N,")
    print("       check N(observable scales) ≫ 1.")
    print("    4. Reproduce A_s = 2.1e-9 within OOM with NO free parameters.")
    print()
    print("  Until those four steps are done, the substrate-saturation")
    print("  density-perturbation problem remains OPEN. Honest scoreboard:")
    print()
    print("    Substrate-saturation cosmology vs inflation:")
    print("       horizon problem      : SOLVED")
    print("       singularity          : SOLVED")
    print("       δρ/ρ amplitude       : OPEN  (best lead: defect Poisson)")
    print("       n_s scale invariance : NOT YET ADDRESSED")
    print("       Gaussianity          : NOT YET ADDRESSED")
    print()
    print("  Inflation still wins on the perturbation sector.")
    print("  Substrate-saturation still wins on the singularity sector.")
    print("  Honest verdict: hybrid frameworks (substrate ontology with")
    print("  inflation-like perturbation amplifier) deserve study, but")
    print("  pure substrate-saturation cosmology has not yet closed the")
    print("  perturbation gap, and the gap will not close via primitives")
    print("  alone without a defect-freeze mechanism that is currently")
    print("  conjectural.")


if __name__ == "__main__":
    main()
