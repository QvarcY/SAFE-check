# SAFE Source Quality Hierarchy Implementation

## Overview

This document describes how SAFE incorporates your source prioritization hierarchy:

1. **Academic studies & research papers** (newest peer-review consensus)
2. **University curriculum knowledge** (by complexity level)
3. **Scientific publication consensus**
4. **News articles** (with clear references)

into the Argument Strength Coefficient (ASC) scoring system.

---

## 1. Architecture Layer: Source Quality Tiers

### 1.1 Source Classification (Tier Assignment)

All evidence sources are classified into 4 tiers based on quality signals:

**TIER 1 (Primary)** — Highest confidence
- Peer-reviewed empirical studies with ≥1 independent replication
- Systematic reviews / meta-analyses (top-tier venues)
- Formal consensus statements (multiple institutions)

**TIER 2 (Consensus)** — Established knowledge
- Peer-reviewed studies in standard venues
- Advanced university curriculum (graduate+) from accredited institutions
- Official statistics with transparent methodology

**TIER 3 (Secondary)** — Lower confidence
- Preprints (not yet peer-reviewed)
- News articles from reputable sources with ≥2 citations
- Foundational curriculum knowledge (undergraduate level)

**TIER 4 (Derivative)** — Lowest confidence
- Blog posts, opinion columns, personal websites
- News with minimal citations or unnamed sources
- Derivative reposts of primary studies (same lineage_id)

**Implementation**: `engine/source_tier_classifier.py` → `classify_source(metadata)`

---

## 2. How Your Hierarchy Maps to Tiers

### Academic Papers → Tier 1 or 2

**Tier 1 (Primary):**
- Published in top-5%, top-10%, or top-25% venues (impact factor, citation trajectory)
- Has ≥1 independent peer-reviewed replication
- Consensus formation date established (not just publication date)
- No major retractions or ethical concerns

**Example:**
```python
{
  "source_type": "peer_reviewed_empirical",
  "peer_review": {
    "is_peer_reviewed": True,
    "venue_tier": "top_10_percent",
  },
  "consensus_metadata": {
    "replication_count": 2,
    "consensus_formation_date": "2022-06-01",
  },
  "derivation_signal": {"is_primary": True},
}
→ TIER 1 (Primary)
```

**Tier 2 (Standard):**
- Peer-reviewed but not in top venues
- May lack independent replications
- Stable citation trajectory

**Recency Handling:**
Your requirement: "newest information is priority"
- We track **consensus_formation_date** (when field consensus formed)
- NOT just publication_date
- This allows new evidence to gradually enter consensus
- But doesn't overweight preliminary findings

### University Curriculum Knowledge → Tier 2 or 3

**Tier 2 (Consensus):**
- Advanced level (Graduate Masters, Doctoral)
- From accredited research university
- Represents well-established, peer-validated knowledge
- Provides theoretical foundation

**Example:**
```python
{
  "source_type": "university_curriculum",
  "academic_curriculum_metadata": {
    "curriculum_level": "graduate_masters",
    "institution_type": "research_university",
    "accreditation": ["RAE", "ABET"],
  },
}
→ TIER 2 (Consensus)
```

**Tier 3 (Secondary):**
- Foundational level (undergraduate, technicum)
- From accredited institution
- Provides established definitions, not cutting-edge research

### Scientific Consensus → Tier 1 (via Consensus Statements)

Consensus statements (IPCC, WHO, professional societies) are **Tier 1** because they:
- Aggregate multiple peer-reviewed studies
- Represent field consensus (multiple institution endorsement)
- Are themselves peer-reviewed

### News Articles → Tier 3 or 4

**Tier 3 (Secondary):**
- Flagship/established mainstream publication
- ≥2 citations to peer-reviewed studies or official statistics
- No retractions or major corrections

**Tier 4 (Derivative):**
- ≤1 citation
- Citations to press releases or unnamed sources
- Has retraction/correction history

---

## 3. Component Influence: How Tiers Adjust ASC

### 3.1 Component Boosts by Tier

Each tier applies boosts to ASC components (R, E, T, I):

| Tier | R (Reliability) | E (Quality) | T (Temporal) | I (Independence) |
|------|-----------------|------------|--------------|------------------|
| T1   | +25 to +30      | +22 to +28 | +15 to +20   | +10 to +15       |
| T2   | +10 to +20      | +8 to +18  | +5 to +12    | -3 to +8         |
| T3   | -5 to +12       | -10 to +10 | -12 to +3    | -15 to +2        |
| T4   | -15 to -8       | -18 to -10 | -12 to -8    | -20 to -15       |

**Example: Tier 1 Peer-Reviewed Study**
```
R (source reliability):   65 + 25 = 90
E (evidence quality):     70 + 22 = 92
T (temporal stability):   75 + 15 = 90
I (independence):         60 + 10 = 70
```

### 3.2 Independence Handling: Lineage vs. Count

Your hierarchy emphasizes **independent convergence** over repeated citations.

**Evidence Provenance Graph:**
```
❌ Single study cited 5 times (same lineage_id)
   ↓ I_independence penalty

✓ Five independent studies reaching same conclusion (different lineage_ids)
   ↑ I_independence boost
```

**Implementation**: `consensus_metadata.lineage_id` shared across derivatives.

---

## 4. Reasoning Audit Layer

The Enhanced Reasoning Audit (`engine/reasoning_audit_enhanced.py`) checks:

### 4.1 Source Hierarchy Violations

**TIER INVERSION:** Lower-tier sources outweigh higher-tier
```
BAD:  3x Tier 4 sources + 1x Tier 1 source → conclusion from Tier 4
GOOD: 1x Tier 1 source + 3x Tier 3 sources → conclusion prioritizes Tier 1
```

**SINGLE-SOURCE DEPENDENCE:** Especially critical for lower tiers
```
CRITICAL: Claim depends entirely on Tier 4 blog post
ACCEPTABLE: Claim depends on single Tier 1 peer-reviewed study
```

**CHERRY-PICKING:** Selecting lower-tier sources while ignoring higher-tier contradictions
```
BAD: Tier 1 consensus contradicts claim, but reasoning uses only Tier 3 news
GOOD: Directly addresses why Tier 1 consensus may be incomplete/incorrect
```

### 4.2 Reasoning Penalties

Each fallacy detected reduces component scores:
- **E (Evidence Quality)**: -5 per fallacy
- **R (Source Reliability)**: -3 per fallacy
- **I (Independence)**: -15 if single-source dependence

---

## 5. Dynamic Weight Adjustment

Component weights are NOT fixed. They adjust based on epistemic context.

### 5.1 Weight Adjustment Rules

**When Tier 1/2 sources dominate (≥50%):**
```
R_source_reliability:  +0.03  (venue/peer-review becomes clearer signal)
E_evidence_quality:    +0.02
T_temporal_stability:  -0.02
P_replication:         -0.02
C_contradiction_resistance: -0.02
```

**Rationale:** High-quality sources make source reliability and evidence quality more informative; replication is less critical.

**When Tier 3/4 sources dominate (≥50%):**
```
I_independence:        +0.05  (must verify these aren't all reposts)
E_evidence_quality:    +0.03
R_source_reliability:  -0.03
M_methodology:         -0.02
P_replication:         -0.03
```

**Rationale:** Lower-tier sources demand stronger independence verification.

**When reasoning fallacies detected:**
```
E_evidence_quality:    +boost  (quality of reasoning becomes critical)
R_source_reliability:  +boost * 0.5
M_methodology:         +boost * 0.5
T_temporal_stability:  -boost * 0.3
P_replication:         -boost * 0.2
```

**Rationale:** Flawed reasoning shifts weight toward higher-quality evidence and away from signals that don't directly support reasoning quality.

**Implementation**: `engine/component_weights.py` → `compute_weight_adjustments(context)`

---

## 6. End-to-End Pipeline

### Flow Diagram

```
CLAIM + EVIDENCE
       ↓
       └─→ [Source Classification]
           (TIER assignment: 1-4)
           ↓
           └─→ [Reasoning Audit]
               (Fallacy detection, tier hierarchy check)
               ↓
               └─→ [Weight Adjustment]
                   (Dynamic weighting based on tier distribution + reasoning)
                   ↓
                   └─→ [ASC Integration]
                       (Apply source boosts + reasoning penalties + weighted average)
                       ↓
                       └─→ ASC Score + Confidence + Status
```

### Example Trace

**Claim:** "Rapid climate change is anthropogenic"

**Evidence:**
- Tier 1: IPCC Report (consensus statement)
- Tier 1: Nature Climate Change paper (replicated)
- Tier 3: Guardian news article (cites above)

**Source Classification:**
```
IPCC        → Tier 1 (consensus statement)
             → R+30, E+28, T+20, I+15
Nature CC   → Tier 1 (peer-reviewed, top-tier, replicated)
             → R+25, E+22, T+15, I+10
Guardian    → Tier 3 (news, multiple citations)
             → R+12, E+10, T+3, I-5
```

**Reasoning Audit:**
```
Tier distribution: 2 Tier 1, 0 Tier 2, 1 Tier 3, 0 Tier 4
Fallacies detected: 0
Single-source dependence: No
→ Chain Integrity: 95/100
```

**Weight Adjustment:**
```
Tier 1 dominant (67%) → Boost R (+0.03), boost E (+0.02)
No fallacies → No penalty adjustments
→ Final weights: R=0.18, E=0.20, I=0.13, P=0.10, C=0.13, T=0.08, M=0.13
```

**ASC Scoring:**
```
Base components: E=75, R=70, I=60, P=65, C=80, T=75, F=0, M=76
After source boosts: E=95, R=92, I=80, P=65, C=80, T=85, F=0, M=76
After reasoning audit: (no changes—no fallacies)
Weighted sum: (0.20×95 + 0.18×92 + 0.13×80 + 0.10×65 + 0.13×80 + 0.08×85 + 0.13×76) = 82.4
→ ASC = 82.4/100, Confidence: VERY_HIGH, Status: SUPPORTED
```

---

## 7. Key Design Decisions

### 7.1 Why Consensus Formation Date, Not Publication Date?

New research must prove itself before entering "established knowledge":
- Week 1: Interesting preprint (Tier 3, low T boost)
- Month 6: Published in top venue (Tier 2, medium T boost)
- Year 2: Replicated 5 times (Tier 1, high T boost)

This prevents preliminary findings from dominating while allowing rapid incorporation of genuine breakthroughs.

### 7.2 Why Lineage-Based Independence, Not Citation Count?

Citation counts can be gamed or create echo chambers:
```
BAD:  News→Blog→Wikipedia→AI summary = 4 "sources" (same lineage)
      Independence score = 25/100 (derivative)

GOOD: Study A + Study B + Study C = 3 independent lineages
      Independence score = 85/100
```

### 7.3 Why Dynamic Weighting?

Static weights assume all epistemic situations are alike. They're not:
- High Tier 1 composition → Source reliability signal is clear → increase R weight
- High Tier 4 composition → Independence signal critical → increase I weight
- Reasoning fallacies → Evidence quality must carry more weight → increase E

---

## 8. Practical Workflow: From Claim to Score

### Step 1: Metadata Preparation

For each evidence source, gather:
```python
{
  "source_type": "peer_reviewed_empirical",  # required
  "peer_review": {
    "is_peer_reviewed": True,
    "venue_tier": "top_10_percent",
    "venue_name": "Nature",
  },
  "consensus_metadata": {
    "publication_date": "2023-06-01",
    "consensus_formation_date": "2024-01-01",  # When consensus formed
    "replication_count": 3,
    "contradictions_count": 0,
  },
  "derivation_signal": {
    "is_primary": True,
    "lineage_id": "primary_study_X",  # Shared with derivatives
  },
}
```

### Step 2: Classification

```python
from engine.source_tier_classifier import classify_source

classification = classify_source(evidence_metadata)
# Returns: quality_tier, component_boosts, rationale, critical_flags
```

### Step 3: Reasoning Audit

```python
from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning

audit = analyze_source_hierarchy_in_reasoning(
    claim, 
    evidence_items, 
    source_classifications
)
# Returns: fallacies_detected, chain_integrity, critical_issues
```

### Step 4: Weight Adjustment

```python
from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext

context = WeightAdjustmentContext(
    source_tier_distribution={...},
    reasoning_fallacies_count=len(audit["fallacies_detected"]),
    ...
)
weights = compute_weight_adjustments(context)
# Returns: normalized weights dict summing to 1.0
```

### Step 5: ASC Scoring

```python
from engine.scoring_integrated import compute_asc_integrated

result = compute_asc_integrated(
    base_components=initial_scores,
    source_classifications=classifications,
    reasoning_audit=audit,
    weights=weights,
)
# Returns: asc_score, confidence, components, adjustment_trace
```

---

## 9. Testing & Validation

### 9.1 Unit Tests (Each Component)

- Source classifier: Does Tier 1 consensus statement get assigned correctly?
- Reasoning audit: Are fallacies detected?
- Weight adjuster: Do Tier 1-heavy sources increase R weight?
- ASC scorer: Do source boosts apply correctly?

### 9.2 Integration Tests

- Full pipeline: Claim → Evidence → Score matches expected range
- Fallacy injection: Add reasoning flaws, verify score decreases
- Tier inversion: Use only Tier 4 sources for claim, verify penalty

### 9.3 Sensitivity Analysis

- Weight permutations: Run ASC with 10,000 random weight distributions
- Source swaps: Replace Tier 1 with Tier 3, verify score spread
- Contamination signal: Inject derivative sources, verify detection

---

## 10. Future Extensions

### 10.1 Machine Learning for Tier Assignment

Current classifier uses hand-coded rules. Future versions could use:
- Venue classification model (trained on impact factors, citation patterns)
- Derivation detection (linguistic similarity to earlier work)
- Consensus formation timing (citation velocity model)

### 10.2 Domain-Specific Tiers

Biology evidence hierarchy differs from physics differs from sociology.
Could add domain-aware tier definitions (e.g., "in vitro vs. in vivo").

### 10.3 Temporal Weighting Strategy

Track how T (temporal stability) evolves:
- Consensus formation date → T score increases
- Major correction published → T score decreases
- Contradictory replication → T score adjusts

---

## References

- Safe.PDF Section 12: Research Adapters (priority ranking)
- Safe.PDF Section 4: Source Hierarchy (lineage deduplication)
- Safe.PDF Section 6: Reasoning Audit (fallacy patterns)
- Safe.PDF Section 13: Self-Auditing (transparency requirements)

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** Implementation Complete (v2.0 ASC scoring system)
