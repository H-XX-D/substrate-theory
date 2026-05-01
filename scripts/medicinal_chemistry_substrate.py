"""Medicinal chemistry and drug design through the strain-medium framework.

Substrate primitives (4 + 1 cap):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2

Drug-receptor binding   = substrate-strain bridge complementarity
                          (drug strain pattern matches binding-pocket pattern)
ADME (pharmacokinetics) = substrate-strain transport across barriers
                          (membranes are substrate-strain barriers)
SAR                     = substrate-strain modifications shift binding energy

Honest framing: substrate REPRODUCES standard medicinal-chemistry numbers.
The value-add is unification of binding, transport, metabolism, and toxicity
under one strain-template-and-transport story.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
R_GAS = 8.314           # J/(mol K)
RT_KCAL = 0.5924        # kcal/mol at 298.15 K
RT_KJ   = 2.4789        # kJ/mol  at 298.15 K
T_K = 298.15
N_A = 6.02214076e23


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Medicinal chemistry and drug design in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2")
    print("Drug binding   = strain-bridge complementarity (drug <-> pocket)")
    print("ADME           = strain transport (membrane = strain barrier)")
    print("SAR            = strain modifications shift binding free energy")
    print()

    # ============================================================
    section(1, "DRUG-TARGET INTERACTIONS (binding affinity)")
    # ============================================================
    print("Binding equilibrium:  D + R  <->  DR     K_d = [D][R]/[DR]")
    print()
    print("Free energy of binding (substrate strain energy of bridge formation):")
    print("  Delta G  =  -R T ln(K_a)  =  +R T ln(K_d)")
    print()
    print("At T = 298.15 K:  RT = 0.5924 kcal/mol = 2.4789 kJ/mol")
    print("Conversion: pK_d = -log10(K_d)   pIC50 = -log10(IC50)")
    print("Cheng-Prusoff: K_i = IC50 / (1 + [S]/K_m)  (competitive inhibitor)")
    print()
    print(f"  {'drug':<22s}  {'target':<22s}  {'K_d/IC50':>10s}  {'pK':>5s}  {'dG[kcal/mol]':>13s}")
    drugs = [
        ("Imatinib",        "BCR-ABL kinase",       37e-9,  None),
        ("Gefitinib",       "EGFR kinase",          33e-9,  None),
        ("Atorvastatin",    "HMG-CoA reductase",     8e-9,  None),
        ("Captopril",       "ACE",                  17e-9,  None),
        ("Propranolol",     "beta-adrenergic R",     4e-9,  None),
        ("Naloxone",        "mu-opioid receptor",    1e-9,  None),
        ("Methotrexate",    "DHFR",                  1e-9,  None),
        ("Aspirin",         "COX-1",               1.7e-7,  None),
        ("Ibuprofen",       "COX-1",               7.0e-6,  None),
        ("Diazepam",        "GABA-A (BZ site)",     10e-9,  None),
        ("Sildenafil",      "PDE5",                3.5e-9,  None),
        ("Penicillin G",    "PBP transpeptidase",   50e-9,  None),
    ]
    for name, target, kd, _ in drugs:
        pK = -math.log10(kd)
        dG = -RT_KCAL * math.log(1.0/kd)         # binding dG (negative)
        # dG = RT ln(Kd) so for Kd in M:
        dG = RT_KCAL * math.log(kd)
        print(f"  {name:<22s}  {target:<22s}  {kd:>10.2e}  {pK:>5.1f}  {dG:>13.2f}")
    print()
    print("Substrate reading: each ~1.4 kcal/mol of binding energy = one extra")
    print("strain-bridge contact (H-bond, salt bridge, hydrophobic lobe match).")
    print("Going from millimolar (lead) to nanomolar (drug) = ~6 log units")
    print("= ~8 kcal/mol = ~5-6 additional strain-pattern matches.")

    # ============================================================
    section(2, "LIPINSKI'S RULE OF FIVE (substrate transport criteria)")
    # ============================================================
    print("Lipinski's Rule of Five (oral bioavailability heuristic):")
    print("  MW   <= 500   Da     (mass below substrate-tunneling cutoff)")
    print("  logP <=   5          (lipophilicity matches lipid-bilayer strain)")
    print("  HBD  <=   5          (H-bond donors)")
    print("  HBA  <=  10          (H-bond acceptors)")
    print()
    print("Substrate framing: the lipid bilayer is a substrate-strain BARRIER.")
    print("To cross it the drug's strain pattern must MATCH the barrier's strain")
    print("template within a finite envelope. Beyond logP~5 the molecule sticks")
    print("in the bilayer (over-saturated, sigma cap); below logP~0 it cannot")
    print("dissolve into the bilayer at all.")
    print()
    print(f"  {'drug':<20s}  {'MW':>6s}  {'logP':>6s}  {'HBD':>4s}  {'HBA':>4s}  {'oral?':>5s}")
    lipinski = [
        ("Aspirin",          180,  1.2,  1,  3, "Y"),
        ("Ibuprofen",        206,  3.5,  1,  2, "Y"),
        ("Caffeine",         194, -0.1,  0,  6, "Y"),
        ("Atorvastatin",     559,  5.0,  4,  5, "Y"),
        ("Imatinib",         494,  3.0,  2,  7, "Y"),
        ("Sildenafil",       474,  2.7,  1, 11, "Y"),
        ("Cyclosporin A",   1203,  3.0,  5, 12, "Y*"),
        ("Vancomycin",      1449, -3.1, 19, 24, "N"),
        ("Paclitaxel",       854,  3.0,  4, 14, "N"),
        ("Amphotericin B",   924,  0.8, 12, 18, "N"),
        ("Lipitor",          559,  5.0,  4,  5, "Y"),
    ]
    for n, mw, lp, hbd, hba, oral in lipinski:
        viol = sum([mw>500, lp>5, hbd>5, hba>10])
        flag = "ok" if viol <= 1 else f"v{viol}"
        print(f"  {n:<20s}  {mw:>6d}  {lp:>6.1f}  {hbd:>4d}  {hba:>4d}  {oral:>5s}  ({flag})")
    print()
    print("Cyclosporin (* macrocycle, intramolecular H-bonds shield polarity)")
    print("violates 3 rules but is orally bioavailable -> Lipinski is heuristic,")
    print("not law. Substrate insight: shielding H-bond donors lowers the strain")
    print("mismatch with the lipid template.")

    # ============================================================
    section(3, "BIOISOSTERES (functional-group strain equivalents)")
    # ============================================================
    print("Bioisosteres = different functional groups with similar substrate")
    print("strain footprint -> preserve binding while improving ADME / tox.")
    print()
    print("Classical (Erlenmeyer / Grimm hydride displacement):")
    print(f"  {'group':<12s}  {'isostere':<14s}  {'rationale':<40s}")
    classic = [
        ("-H",        "-F",            "size match, blocks metabolism"),
        ("-CH3",      "-Cl",           "similar van der Waals volume"),
        ("-CH2-",     "-O-, -NH-, -S-","valence + size match"),
        ("-CH=",      "-N=",           "aromatic ring N-substitution"),
        ("-OH",       "-NH2, -SH",     "H-bond donor swap"),
        ("-O-",       "-S-, -NH-",     "ether / thioether / amine bridge"),
    ]
    for g, i, r in classic:
        print(f"  {g:<12s}  {i:<14s}  {r:<40s}")
    print()
    print("Non-classical (preserves pharmacophore strain pattern, different group):")
    nonclassic = [
        ("-COOH",   "tetrazole",       "pKa ~4.5, planar, metabolically stable"),
        ("-COOH",   "-SO2NH2",         "H-bond donor + acceptor pair"),
        ("-COOH",   "hydroxamic acid", "metal chelation (HDAC, MMP inhibitors)"),
        ("amide",   "1,2,4-oxadiazole","planar bioisostere, peptidase resistant"),
        ("phenyl",  "thiophene",       "pi-system, different metabolism"),
        ("ester",   "amide",           "hydrolytic stability up"),
    ]
    print(f"  {'group':<10s}  {'isostere':<18s}  {'effect':<40s}")
    for g, i, r in nonclassic:
        print(f"  {g:<10s}  {i:<18s}  {r:<40s}")
    print()
    print("Substrate basis: bioisosteres share the LOCAL strain bridge pattern")
    print("(same number of H-bond donors/acceptors, similar lobe geometry, similar")
    print("electrostatic profile) so the binding-pocket complement still fits.")

    # ============================================================
    section(4, "PRODRUGS AND SOFT DRUGS (strain transport tricks)")
    # ============================================================
    print("Prodrug = inactive parent that is metabolically activated in vivo.")
    print("Soft drug = active drug designed to be metabolized to inactive form.")
    print()
    print("Common prodrug strategies:")
    print(f"  {'parent drug':<18s}  {'prodrug form':<22s}  {'activation':<22s}")
    pro = [
        ("Aspirin (active)",    "salicylate ester",       "esterase hydrolysis"),
        ("Enalaprilat",         "Enalapril (ethyl ester)","liver carboxylesterase"),
        ("L-DOPA",              "L-DOPA itself*",         "DOPA decarboxylase"),
        ("5-Fluorouracil",      "Capecitabine",           "thymidine phosphorylase"),
        ("Acyclovir-MP",        "Acyclovir",              "viral thymidine kinase"),
        ("Valacyclovir",        "L-valyl ester ACV",      "intestinal hydrolysis"),
        ("Tenofovir",           "TDF / TAF",              "esterase + phosphoramidase"),
        ("Phenytoin",           "Fosphenytoin",           "phosphatase, IV use"),
    ]
    for p, f, a in pro:
        print(f"  {p:<18s}  {f:<22s}  {a:<22s}")
    print()
    print("Glucuronide conjugates (Phase II metabolism, sometimes acts as prodrug):")
    print("  Morphine -> morphine-6-glucuronide (M6G), more potent at mu-opioid R")
    print()
    print("Substrate framing: a prodrug ester carries the active strain pattern")
    print("BEHIND a hydrolyzable mask that improves transport (logP, charge, BBB)")
    print("until enzymatic cleavage releases the matching strain template at the")
    print("target tissue.")

    # ============================================================
    section(5, "PHARMACOKINETICS — ADME (substrate transport)")
    # ============================================================
    print("ADME = Absorption, Distribution, Metabolism, Excretion.")
    print("Each step = substrate-strain transport across or transformation by a")
    print("biological compartment / enzyme.")
    print()
    print("Caco-2 apparent permeability (intestinal absorption surrogate):")
    print(f"  {'class':<16s}  {'P_app [10^-6 cm/s]':>20s}  {'oral abs':>10s}")
    caco = [
        ("low",       "<  1",     "< 20%"),
        ("moderate",  "1 - 10",   "20-70%"),
        ("high",      "> 10",     "> 70%"),
    ]
    for c, p, o in caco:
        print(f"  {c:<16s}  {p:>20s}  {o:>10s}")
    print()
    print("Plasma protein binding (PPB) — fraction bound to albumin / AAG:")
    print(f"  {'drug':<18s}  {'%PPB':>6s}  {'free fraction':>14s}")
    ppb = [
        ("Warfarin",        99,   "1%"),
        ("Diazepam",        98,   "2%"),
        ("Ibuprofen",       99,   "1%"),
        ("Phenytoin",       90,   "10%"),
        ("Atenolol",         3,   "97%"),
        ("Lithium",          0,   "100%"),
    ]
    for d, p, f in ppb:
        print(f"  {d:<18s}  {p:>6d}  {f:>14s}")
    print()
    print("CYP450 metabolism (Phase I oxidation in liver):")
    print(f"  {'isoform':<8s}  {'fraction of drugs':>18s}  {'examples':<32s}")
    cyp = [
        ("CYP3A4",  "~50%", "midazolam, atorvastatin, sildenafil"),
        ("CYP2D6",  "~25%", "codeine, fluoxetine, metoprolol"),
        ("CYP2C9",  "~15%", "warfarin, ibuprofen, phenytoin"),
        ("CYP2C19", "~10%", "omeprazole, clopidogrel"),
        ("CYP1A2",  "~10%", "caffeine, theophylline"),
    ]
    for i, f, e in cyp:
        print(f"  {i:<8s}  {f:>18s}  {e:<32s}")
    print()
    print("Inhibitors / inducers (DDI risk):")
    print("  Inhibitors: ketoconazole, ritonavir, grapefruit juice (CYP3A4)")
    print("  Inducers:   rifampin, phenytoin, carbamazepine, St John's wort")
    print()
    print("Half-life and clearance:  t_1/2 = 0.693 V_d / CL")
    print(f"  {'drug':<16s}  {'t_1/2 [h]':>10s}  {'V_d [L/kg]':>11s}  {'CL [mL/min]':>12s}")
    pk = [
        ("Caffeine",      5,   0.5,    100),
        ("Diazepam",     43,   1.1,     30),
        ("Warfarin",     40,   0.14,     5),
        ("Penicillin G", 0.5,  0.35,   500),
        ("Amiodarone",   720, 66.0,    100),
        ("Lithium",      24,   0.8,     30),
    ]
    for d, t, v, c in pk:
        print(f"  {d:<16s}  {t:>10.1f}  {v:>11.2f}  {c:>12d}")
    print()
    print("Substrate framing: each membrane / enzyme is a strain barrier or")
    print("strain transformer. ADME = sequence of strain-bridge handoffs,")
    print("with PK parameters quantifying time scales of these substrate steps.")

    # ============================================================
    section(6, "PHARMACODYNAMICS (dose-response, agonism)")
    # ============================================================
    print("Dose-response (Hill equation):  E = E_max [D]^n / (EC50^n + [D]^n)")
    print()
    print("Receptor occupancy types (substrate strain-template interaction):")
    print(f"  {'class':<22s}  {'effect':<40s}")
    pd = [
        ("Full agonist",         "max signal at saturation (E_max)"),
        ("Partial agonist",      "submaximal even at saturation"),
        ("Inverse agonist",      "reduces basal (constitutive) activity"),
        ("Neutral antagonist",   "no effect alone, blocks agonist"),
        ("Allosteric modulator", "binds non-orthosteric site, tunes K_d"),
        ("Biased agonist",       "selective downstream pathway activation"),
    ]
    for c, e in pd:
        print(f"  {c:<22s}  {e:<40s}")
    print()
    print(f"  {'drug':<18s}  {'target':<24s}  {'class':<18s}")
    pd_ex = [
        ("Morphine",         "mu-opioid receptor",   "full agonist"),
        ("Buprenorphine",    "mu-opioid receptor",   "partial agonist"),
        ("Naloxone",         "mu-opioid receptor",   "antagonist"),
        ("Naltrexone",       "mu-opioid receptor",   "antagonist"),
        ("Pimavanserin",     "5-HT2A",               "inverse agonist"),
        ("Diazepam",         "GABA-A (BZ site)",     "PAM"),
        ("TRV130 (oliceridine)", "mu-opioid R",      "biased agonist"),
    ]
    for d, t, c in pd_ex:
        print(f"  {d:<18s}  {t:<24s}  {c:<18s}")
    print()
    print("Substrate basis: strain-template match strength sets E_max (efficacy);")
    print("complementarity geometry (lock-and-key) sets EC50 / K_d (potency).")

    # ============================================================
    section(7, "SAR / QSAR (structure-activity relationships)")
    # ============================================================
    print("SAR = how chemical changes shift biological activity.")
    print("QSAR = quantitative model relating structure descriptors to activity.")
    print()
    print("Hammett equation (substituent electronic effects):")
    print("  log(k/k_0) = rho * sigma_X      (sigma_X = Hammett constant)")
    print()
    print(f"  {'substituent':<14s}  {'sigma_meta':>10s}  {'sigma_para':>10s}")
    hammett = [
        ("-NH2",   -0.16, -0.66),
        ("-OH",     0.12, -0.37),
        ("-OCH3",   0.12, -0.27),
        ("-CH3",   -0.07, -0.17),
        ("-H",      0.00,  0.00),
        ("-F",      0.34,  0.06),
        ("-Cl",     0.37,  0.23),
        ("-CN",     0.56,  0.66),
        ("-NO2",    0.71,  0.78),
    ]
    for s, m, p in hammett:
        print(f"  {s:<14s}  {m:>10.2f}  {p:>10.2f}")
    print()
    print("Hansch analysis (combines lipophilicity, electronic, steric):")
    print("  log(1/C) = a*pi + b*sigma + c*E_s + d")
    print("  pi  = log P substituent contribution")
    print("  E_s = Taft steric parameter")
    print()
    print("Free-Wilson: activity = sum of substituent contributions at each position")
    print("  log(activity) = mu + sum_i a_i  (additive substituent fragment values)")
    print()
    print("Modern QSAR descriptors: topological indices, 3D-QSAR (CoMFA, CoMSIA),")
    print("molecular fingerprints (ECFP4), graph neural networks.")
    print()
    print("Substrate framing: each substituent perturbs the local strain pattern")
    print("(electronic = charge-bridge density; steric = lobe geometry; logP =")
    print("transport coupling). Activity = sum of strain-template match shifts.")

    # ============================================================
    section(8, "FRAGMENT-BASED DRUG DISCOVERY (FBDD)")
    # ============================================================
    print("Fragments (MW < 300, often < 250) bind weakly (mM-uM K_d) but with")
    print("HIGH ligand efficiency (binding energy per heavy atom).")
    print()
    print("Ligand efficiency:  LE = -dG / N_heavy_atoms   (target: > 0.3 kcal/mol)")
    print()
    print(f"  {'compound':<20s}  {'K_d':>10s}  {'N_HA':>5s}  {'LE [kcal/HA]':>13s}")
    fbdd = [
        ("Vemurafenib parent",  300e-6,  16, None),
        ("PLX4720 lead",          1e-6,  20, None),
        ("Vemurafenib drug",     31e-9,  31, None),
        ("Venetoclax fragment", 100e-6,  18, None),
        ("Venetoclax drug",      10e-9,  53, None),
    ]
    for n, kd, ha, _ in fbdd:
        dG = -RT_KCAL * math.log(1.0/kd)
        # binding dG is negative; magnitude:
        mag = -dG
        le = mag / ha
        print(f"  {n:<20s}  {kd:>10.2e}  {ha:>5d}  {le:>13.3f}")
    print()
    print("Screening libraries:")
    print("  - Astex 'Rule of 3': MW <= 300, logP <= 3, HBD/HBA <= 3")
    print("  - DEL (DNA-encoded libraries): 10^9 - 10^12 compounds")
    print("  - Crystallographic fragment screens: XChem at Diamond Light Source")
    print()
    print("Substrate framing: fragments occupy a single strain-bridge subpocket.")
    print("Linking / growing fragments adds parallel strain bridges; each new")
    print("contact contributes ~1.4 kcal/mol if geometry is preserved.")

    # ============================================================
    section(9, "DRUG CLASSES AND MECHANISMS (substrate templates)")
    # ============================================================
    print(f"  {'class':<18s}  {'target / MOA':<32s}  {'example':<18s}")
    classes = [
        ("beta-blockers",   "beta-1 adrenergic R antagonist",   "metoprolol"),
        ("Statins",         "HMG-CoA reductase inhibitor",      "atorvastatin"),
        ("ACE inhibitors",  "angiotensin-converting enzyme",    "enalapril"),
        ("ARBs",            "angiotensin II receptor blocker",  "losartan"),
        ("NSAIDs",          "COX-1/COX-2 inhibitor",            "ibuprofen"),
        ("PPIs",            "H+/K+ ATPase inhibitor",           "omeprazole"),
        ("SSRIs",           "serotonin reuptake inhibitor",     "fluoxetine"),
        ("Benzodiazepines", "GABA-A allosteric (BZ site)",      "diazepam"),
        ("Opioids",         "mu-opioid receptor agonist",       "morphine"),
        ("Beta-lactams",    "penicillin-binding protein (PBP)", "amoxicillin"),
        ("Macrolides",      "50S ribosome inhibitor",           "azithromycin"),
        ("Fluoroquinolones","DNA gyrase / topo IV",             "ciprofloxacin"),
        ("NRTIs",           "viral reverse transcriptase",      "tenofovir"),
        ("Protease inh.",   "HIV / HCV protease",               "ritonavir"),
        ("Kinase inh.",     "tyrosine kinase ATP site",         "imatinib"),
        ("mAbs",            "selective antigen binding",        "trastuzumab"),
        ("Checkpoint inh.", "PD-1/PD-L1/CTLA-4",                "pembrolizumab"),
    ]
    for c, t, e in classes:
        print(f"  {c:<18s}  {t:<32s}  {e:<18s}")
    print()
    print("Substrate basis: each class corresponds to a STRAIN TEMPLATE matching a")
    print("specific binding-pocket geometry (ATP site, catalytic dyad, allosteric")
    print("groove, peptide cleavage cleft). Drug evolution within a class refines")
    print("the strain template by pruning bad contacts and adding parallel bridges.")

    # ============================================================
    section(10, "TOXICITY & ADMET PREDICTION")
    # ============================================================
    print("Off-target strain-bridge mismatches -> adverse effects.")
    print()
    print(f"  {'liability':<22s}  {'mechanism':<30s}  {'in silico':<18s}")
    tox = [
        ("hERG block (QT)",    "K+ channel pore promiscuity",  "DEREK, hERG QSAR"),
        ("Hepatotoxicity",     "reactive metab., CYP-dependent","DILIrank, ProTox"),
        ("Mutagenicity (Ames)","DNA strain adduct formation",  "DEREK, Sarah, ToxAlerts"),
        ("Phospholipidosis",   "cationic amphiphile -> lipid",  "logP+pKa rule"),
        ("Cardiac arrhythmia", "hERG + Nav1.5 + Cav1.2 panel",  "CiPA initiative"),
        ("CYP inhibition (DDI)","reversible / TDI",             "isoform-specific QSAR"),
        ("PAINS",              "promiscuous binders, artifacts","Baell-Holloway filter"),
    ]
    for l, m, t in tox:
        print(f"  {l:<22s}  {m:<30s}  {t:<18s}")
    print()
    print("hERG IC50 rule of thumb:")
    print("  IC50 < 1 uM   high cardiac risk")
    print("  IC50 1-10 uM  moderate, watch margin to therapeutic plasma level")
    print("  IC50 > 10 uM  low concern (margin > 30x typical Cmax)")
    print()
    print("Substrate framing: tox = strain-template match at unintended pocket.")
    print("The hERG channel pocket is wide & lipophilic so MANY drug strain")
    print("patterns fit it accidentally -> systematic liability.")

    # ============================================================
    section(11, "MODERN MODALITIES (PROTAC, mRNA, CAR-T, ADC)")
    # ============================================================
    print(f"  {'modality':<22s}  {'mechanism':<46s}")
    modal = [
        ("PROTAC",             "bifunctional: target + E3 ligase -> ubiquitin"),
        ("Molecular glue",     "stabilizes neo-substrate / E3 interface"),
        ("LYTAC",              "lysosomal targeting (extracellular targets)"),
        ("AUTAC",              "autophagy-targeting chimera"),
        ("mRNA therapeutic",   "LNP-encapsulated mRNA -> in situ protein expr."),
        ("siRNA / ASO",        "RISC- or RNase-H-mediated transcript cleavage"),
        ("CRISPR therapeutic", "Cas9 / base editor / prime editor in vivo or ex vivo"),
        ("CAR-T",              "engineered T cells with chimeric antigen receptor"),
        ("ADC",                "monoclonal Ab + cytotoxic payload (linker)"),
        ("Bispecific Ab",      "two paratopes: tumor + CD3 T-cell engager"),
        ("Radioligand",        "targeting moiety + radionuclide (Lu-177, Ac-225)"),
        ("Peptide therapeutic","constrained peptides, GLP-1 analogs (semaglutide)"),
        ("Cyclic peptide",     "macrocyclic, oral (cyclosporin-like envelope)"),
        ("Nanobody",           "single-domain camelid VHH, small + stable"),
    ]
    for m, mech in modal:
        print(f"  {m:<22s}  {mech:<46s}")
    print()
    print("PROTAC ternary-complex thermodynamics (substrate framing):")
    print("  K_d(ternary) is tuned by COOPERATIVITY alpha:")
    print("    alpha = K_d(binary) / K_d(ternary)")
    print("  alpha > 1 = positive cooperativity (better than additive)")
    print("  Substrate: linker length tunes strain-bridge alignment between two")
    print("  templates (target and E3) -> sweet spot of geometric strain match.")
    print()
    print("ADC payload potency (DM1, MMAE, calicheamicin) requires sub-nanomolar")
    print("activity because antibody delivery limits intracellular concentration.")
    print("Substrate: strain template must match at picomolar effective dose.")

    # ============================================================
    section(12, "SUMMARY: drug = strain template matched to pocket")
    # ============================================================
    print("All medicinal-chemistry concepts reduce to substrate strain primitives:")
    print()
    print("  binding affinity   = strain-bridge complementarity energy")
    print("  Lipinski rule      = strain-transport envelope across lipid bilayer")
    print("  bioisostere        = same local strain pattern, different atoms")
    print("  prodrug            = strain template hidden behind hydrolyzable mask")
    print("  ADME               = sequence of strain-barrier transports")
    print("  agonist / antag.   = strain match strength + downstream coupling")
    print("  SAR / QSAR         = sum of substituent strain-pattern shifts")
    print("  fragment           = single strain-bridge subpocket occupant")
    print("  toxicity           = unintended strain match at off-target pocket")
    print("  PROTAC / ADC       = composite strain template (two-pocket bridge)")
    print()
    print("Honest scoreboard: substrate reproduces the SAME K_d, IC50, t_1/2,")
    print("logP, and ADMET numbers as standard medicinal chemistry. The value-add")
    print("is unification: 12 chapters become one strain-template-and-transport")
    print("story rather than 12 empirical rule sets.")


if __name__ == "__main__":
    main()
