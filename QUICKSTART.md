# SAFE Source Hierarchy System — Quick Start Guide

## Overview

The SAFE system now treats source quality as a first-class epistemic signal. Every claim evaluation flows through:

```
Claim + Evidence → Classify Sources → Audit Reasoning → 
Adjust Weights → Score ASC → Result with Full Audit Trail
```

---

## Installation & Setup

### Step 1: Prepare Evidence Metadata

For each piece of evidence, gather metadata:

```python
evidence_item = {
    # Required: Type of source
    "source_type": "peer_reviewed_empirical",  # or: systematic_review_meta_analysis, 
                                               # consensus_statement, university_curriculum,
                                               # official_statistic, preprint, news_cited, etc.
    
    # Peer-review information (if applicable)
    "peer_review": {
        "is_peer_reviewed": True,
        "review_status": "published",  # or: accepted_pending, under_review, preprint
        "venue_name": "Nature Climate Change",
        "venue_impact_factor": 25.3,
        "venue_tier": "top_10_percent",  # or: top_5_percent, top_25_percent, peer_reviewed_standard
    },
    
    # Consensus metadata (critical: consensus formation date, not just publication)
    "consensus_metadata": {
        "publication_date": "2023-06-01",
        "consensus_formation_date": "2024-01-01",  # When field consensus formed
        "replication_count": 3,  # Independent peer-reviewed replications
        "citation_trajectory": "growing",  # or: stable, declining
        "contradictions_count": 0,  # High-quality contradictions
    },
    
    # University curriculum (if applicable)
    "academic_curriculum_metadata": {
        "curriculum_level": "graduate_masters",  # or: foundational, intermediate, advanced_undergraduate, doctoral
        "institution_type": "research_university",
        "accreditation": ["RAE"],
    },
    
    # News article information (if applicable)
    "news_metadata": {
        "publication_name": "The Guardian",
        "editorial_standards": "established_mainstream",  # or: flagship_reputation, specialized_reputable
        "cited_source_count": 3,
        "cited_source_quality": ["peer_reviewed_study", "official_statistic"],
    },
    
    # Derivation tracking (is this a repost or original?)
    "derivation_signal": {
        "is_primary": True,  # True if original primary source
        "lineage_id": "original_study_X",  # Shared with all derivatives
    },
    
    # Critical flags
    "critical_flags": [],  # or: ["retracted", "ethical_concerns", etc.]
}
```

### Step 2: Run Classification

```python
from engine.source_tier_classifier import classify_source

for evidence in evidence_list:
    classification = classify_source(evidence)
    print(f"Tier: {classification['quality_tier']}")
    print(f"Rationale: {classification['classification_rationale']}")
    # Returns boosts to apply to ASC components
```

**Output:**
```
Tier: tier_1_primary
Rationale: Peer-reviewed empirical with consensus formation and replication
Component boosts:
  R (source reliability): +25
  E (evidence quality): +22
  T (temporal stability): +15
  I (independence): +10
```

### Step 3: Audit Reasoning

```python
from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning

audit = analyze_source_hierarchy_in_reasoning(
    claim="Climate change is anthropogenic",
    evidence_used=evidence_list,
    source_classifications=classification_list,
)

print(f"Chain Integrity: {audit['reasoning_chain_integrity']}/100")
print(f"Fallacies Detected: {audit['fallacies_detected']}")
print(f"Critical Issues: {audit['critical_issues']}")
```

**Output:**
```
Chain Integrity: 95/100
Fallacies Detected: []
Critical Issues: []
```

### Step 4: Adjust Weights

```python
from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext

context = WeightAdjustmentContext(
    source_tier_distribution={"tier_1": 2, "tier_2": 0, "tier_3": 1, "tier_4": 0},
    reasoning_fallacies_count=len(audit['fallacies_detected']),
    single_source_dependence=audit['single_source_dependence'],
    independence_score=85,
    replication_count=3,
    contradiction_count=0,
)

weights = compute_weight_adjustments(context)
print(f"R weight: {weights['R_source_reliability']:.4f}")
print(f"E weight: {weights['E_evidence_quality']:.4f}")
```

**Output:**
```
R weight: 0.1827  (vs default 0.1500 → +0.0327)
E weight: 0.2025  (vs default 0.1800 → +0.0225)
```

### Step 5: Compute ASC Score

```python
from engine.scoring_integrated import compute_asc_integrated

result = compute_asc_integrated(
    base_components={
        "E": 75,  # Evidence quality (0-100)
        "R": 70,  # Source reliability
        "I": 65,  # Independence
        "P": 60,  # Replication
        "C": 75,  # Contradiction resistance
        "T": 80,  # Temporal stability
        "F": 0,   # Fundamental laws (-20 to +20)
        "M": 78,  # Methodology
    },
    source_classifications=classification_list,
    reasoning_audit=audit,
    weights=weights,
    include_audit_trace=True,
)

print(f"ASC Score: {result['asc_score']:.1f}/100")
print(f"Confidence: {result['confidence']}")
print(f"\nAdjustment Trace:")
for line in result['adjustment_trace']:
    print(f"  {line}")
```

**Output:**
```
ASC Score: 82.5/100
Confidence: VERY_HIGH

Adjustment Trace:
  Source 1: Peer-reviewed empirical with consensus → R+25, E+22, T+15, I+10
  Source 2: Peer-reviewed empirical with consensus → R+25, E+22, T+15, I+10
  Source 3: News article (reputable, multiple citations) → R+12, E+10, T+3, I-5
  Applied average boosts: R+20.7, E+14.7, T+11.0, I+5.0
  Reasoning audit: no fallacies detected
  Final weighted ASC: 82.5
```

---

## Common Workflows

### Workflow 1: Evaluate a Single Claim

```python
from engine.orchestrator import SafeEvaluationRequest, evaluate_claim_end_to_end
from engine.source_tier_classifier import classify_source
from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext
from engine.scoring_integrated import compute_asc_integrated

# Create request
request = SafeEvaluationRequest(
    claim="Claim text here",
    claim_type="empirical_causal",
    evidence_items=[...],  # Your evidence with metadata
    base_asc_components={"E": 70, "R": 70, "I": 60, "P": 60, "C": 75, "T": 75, "F": 0, "M": 72},
)

# Evaluate end-to-end
result = evaluate_claim_end_to_end(
    request,
    source_classifier_fn=classify_source,
    reasoning_audit_fn=analyze_source_hierarchy_in_reasoning,
    weight_adjuster_fn=compute_weight_adjustments,
    asc_scorer_fn=compute_asc_integrated,
)

print(f"Status: {result.status}")
print(f"ASC Score: {result.final_asc_score}")
print(result.summary)
```

### Workflow 2: Detect Source Hierarchy Violations

```python
audit = analyze_source_hierarchy_in_reasoning(claim, evidence, classifications)

if audit['reasoning_chain_integrity'] < 70:
    print("⚠ Warning: Reasoning quality concerns")
    for issue in audit['critical_issues']:
        print(f"  - {issue}")
    for rec in audit['recommendations']:
        print(f"  → {rec}")
```

### Workflow 3: Compare Two Claims

```python
# Evaluate Claim A
result_a = evaluate_claim_end_to_end(request_a, ...)

# Evaluate Claim B
result_b = evaluate_claim_end_to_end(request_b, ...)

# Compare
if result_a.final_asc_score > result_b.final_asc_score:
    print(f"Claim A is better supported ({result_a.final_asc_score:.1f} vs {result_b.final_asc_score:.1f})")
else:
    print(f"Claim B is better supported ({result_b.final_asc_score:.1f} vs {result_a.final_asc_score:.1f})")

# Show why
print(f"\nClaim A:")
print(f"  Tiers: {result_a.source_classifications}")
print(f"  Reasoning integrity: {result_a.reasoning_audit['reasoning_chain_integrity']}")

print(f"\nClaim B:")
print(f"  Tiers: {result_b.source_classifications}")
print(f"  Reasoning integrity: {result_b.reasoning_audit['reasoning_chain_integrity']}")
```

---

## Understanding Output

### ASC Score Interpretation

| Range | Confidence | Status | Interpretation |
|-------|-----------|--------|-----------------|
| 85-100 | VERY_HIGH | SUPPORTED | Multiple high-quality, independent sources. Reasoning sound. |
| 70-84 | HIGH | SUPPORTED/CONTESTED | Strong evidence, minor concerns about independence or methodology. |
| 55-69 | MEDIUM | CONTESTED | Evidence exists, but quality or independence concerns. Further investigation warranted. |
| 35-54 | LOW | UNVERIFIED | Weak evidence. Cannot rank among established knowledge. |
| 0-34 | LOW | REFUTED | Strong evidence contradicts claim. Alternative explanation better supported. |

### Reading the Adjustment Trace

```
Source 1: Peer-reviewed empirical with consensus → R+25, E+22, T+15, I+10
│         └─ This source got Tier 1 classification
│            └─ Boosts applied to 4 components
│
Applied average boosts: R+20.7, E+14.7, T+11.0, I+5.0
│
└─ If multiple sources, these are the averaged boosts

Final weighted ASC: 82.5
  Components (after all adjustments):
    E: 92.0 (75 base + 22 boost - 0 reasoning penalty + weighted)
    R: 90.7 (70 base + 20.7 boost - 0 reasoning penalty + weighted)
    ...
```

### Critical Flags

Watch for these warnings:

- **Retraction:** Source has been formally retracted → high unreliability
- **Tier Inversion:** Lower-tier sources dominate reasoning → chain integrity reduced
- **Single-Source Dependence:** Only one source, especially Tier 4 → high risk
- **Cherry-Picking:** High-tier contradictions ignored → reasoning flaws detected
- **Unclassified:** Unknown source type → defaulted to Tier 3, confidence reduced

---

## Best Practices

### 1. Always Provide Consensus Formation Date

**Wrong:**
```python
"consensus_metadata": {"publication_date": "2020-01-01"}
```

**Right:**
```python
"consensus_metadata": {
    "publication_date": "2020-01-01",
    "consensus_formation_date": "2022-06-01",  # When field agreement emerged
}
```

### 2. Track Lineage for Derivatives

**Wrong:**
```python
evidence_1 = {"id": "original_study"}
evidence_2 = {"id": "news_article_citing_study"}
# These appear as 2 independent sources
```

**Right:**
```python
evidence_1 = {
    "id": "original_study",
    "derivation_signal": {"is_primary": True, "lineage_id": "study_X"}
}
evidence_2 = {
    "id": "news_article",
    "derivation_signal": {"is_primary": False, "lineage_id": "study_X"}  # Same lineage
}
# Correctly identified as single lineage with 1 derivative
```

### 3. Evaluate Reasoning First

Flawed reasoning can't be fixed by high-quality sources:

```python
if audit['reasoning_chain_integrity'] < 60:
    print("Stop: Fix the reasoning before scoring")
    print(audit['critical_issues'])
    # Don't proceed to ASC scoring yet
```

### 4. Pay Attention to Dynamic Weights

If your weights changed significantly from defaults:

```python
print(f"R weight change: {weights['R_source_reliability'] - DEFAULT_WEIGHTS['R_source_reliability']:+.4f}")
if abs(change) > 0.05:
    print("⚠ Significant weight adjustment due to epistemic context")
    print("  This reflects the specific composition of sources and reasoning quality")
```

---

## Troubleshooting

### Q: My claim got low ASC even though I used peer-reviewed sources?

**Check:**
1. Are you specifying `consensus_formation_date`? (Recent publication_date alone doesn't guarantee Tier 1)
2. Does `replication_count` >= 1? (Single study, even peer-reviewed, gets Tier 2)
3. Run reasoning audit: `analyze_source_hierarchy_in_reasoning()` — any fallacies?
4. Review critical_issues in audit output

### Q: Sources classified as Tier 4 but I think they should be Tier 1?

**Check:**
1. Is `is_peer_reviewed` set to True?
2. Is `venue_tier` one of: "top_5_percent", "top_10_percent", "top_25_percent"?
3. Is `replication_count` >= 1?
4. Is `is_primary` = True (not a derivative)?
5. Any critical_flags set (retraction, ethical concerns)?

### Q: Confidence is LOW but I expected VERY_HIGH?

**Check:**
1. Component variance: Are E, R, I, P, C, T scores consistent? (Wide spread → lower confidence)
2. ASC score: Is it actually >= 85? (Required for VERY_HIGH)
3. Reasoning fallacies: Any detected in audit? (Each reduces confidence)

### Q: How do I know if the system is working correctly?

Run the test suite:
```bash
python test_suite.py
```

Expected output:
```
✓ Test 1.1 PASSED: Tier 1 classification
✓ Test 1.2 PASSED: Tier 2 classification
✓ Test 1.3 PASSED: Tier 4 penalties
...
RESULTS: 13 passed, 0 failed
```

---

## Next Steps

1. **Integrate with your evidence retrieval** (Consensus API, PubMed, etc.)
   - Adapters return evidence metadata
   - Feed to `classify_source()`

2. **Wire into your user interface**
   - Display ASC score prominently
   - Show adjustment trace for transparency
   - Highlight critical issues and recommendations

3. **Validate on domain test cases**
   - Biomedical claims: Compare against MEDLINE/PubMed consensus
   - Climate: Compare against IPCC assessments
   - Policy: Compare against peer-reviewed policy research

4. **Iterate on weight adjustment rules**
   - Collect feedback from domain experts
   - Refine thresholds and boost values
   - Test sensitivity to parameter changes

---

## Reference

- **Full Documentation:** `docs/SOURCE_HIERARCHY_IMPLEMENTATION.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Example Code:** `example_integration.py`
- **Test Suite:** `test_suite.py`
- **Source Code:** `engine/` directory

---

**Version:** 2.0.0  
**Last Updated:** 2024  
**Status:** Production Ready
