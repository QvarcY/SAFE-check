#!/usr/bin/env python3
"""
SAFE Integration Example

Demonstrates the complete flow:
  claim → evidence → source classification → reasoning audit → 
  weight adjustment → ASC scoring → result

Shows how source hierarchy influences every stage.
"""

from typing import Dict, Any, List


# ============================================================================
# EXAMPLE: Scientific Claim with Multiple Evidence Sources
# ============================================================================

EXAMPLE_CLAIM = "Rapid climate change is primarily driven by human CO2 emissions"

# Three pieces of evidence at different quality tiers
EXAMPLE_EVIDENCE = [
    {
        "id": "ev_1",
        "title": "IPCC 6th Assessment Report - Climate Change 2021",
        "source_type": "consensus_statement",
        "peer_review": {
            "is_peer_reviewed": True,
            "review_status": "published",
            "venue_name": "Intergovernmental Panel on Climate Change",
            "venue_tier": "top_5_percent",
        },
        "consensus_metadata": {
            "publication_date": "2021-08-09",
            "consensus_formation_date": "2021-08-09",
            "replication_count": 50,  # Thousands of studies synthesized
            "citation_trajectory": "growing",
            "contradictions_count": 0,
        },
        "derivation_signal": {
            "is_primary": True,
            "lineage_id": "ipcc_primary",
        },
        "critical_flags": [],
    },
    {
        "id": "ev_2",
        "title": "The Role of Anthropogenic Forcing in Recent Warming",
        "source_type": "peer_reviewed_empirical",
        "peer_review": {
            "is_peer_reviewed": True,
            "review_status": "published",
            "venue_name": "Nature Climate Change",
            "venue_impact_factor": 25.3,
            "venue_tier": "top_5_percent",
        },
        "consensus_metadata": {
            "publication_date": "2020-03-15",
            "consensus_formation_date": "2020-06-01",
            "replication_count": 12,
            "citation_trajectory": "stable",
            "contradictions_count": 1,
        },
        "derivation_signal": {
            "is_primary": True,
            "lineage_id": "ncc_empirical_primary",
        },
        "critical_flags": [],
    },
    {
        "id": "ev_3",
        "title": "News Summary: Scientists Confirm Human Impact on Climate",
        "source_type": "news_cited",
        "news_metadata": {
            "publication_name": "The Guardian",
            "editorial_standards": "established_mainstream",
            "cited_source_count": 3,
            "cited_source_quality": ["peer_reviewed_study", "official_statistic", "expert_quote"],
            "retraction_or_correction": False,
        },
        "derivation_signal": {
            "is_primary": False,
            "likely_root_source": "ev_1 (IPCC)",
            "derivation_confidence": "high",
            "lineage_id": "ipcc_primary",  # Shared with IPCC
        },
        "critical_flags": [],
    },
]

# Initial ASC component scores (before source/reasoning adjustments)
EXAMPLE_BASE_COMPONENTS = {
    "E": 80,  # Strong evidence base
    "R": 75,  # Reasonable source reliability
    "I": 65,  # Multiple independent lineages
    "P": 70,  # Some replication
    "C": 85,  # Good contradiction resistance
    "T": 80,  # Temporally stable
    "F": 0,   # No fundamental conflicts
    "M": 78,  # Sound methodology
}


def run_integration_example():
    """Execute the complete pipeline with example data."""
    
    print("=" * 80)
    print("SAFE INTEGRATION EXAMPLE")
    print("=" * 80)
    print("")
    print(f"CLAIM: {EXAMPLE_CLAIM}")
    print("")
    
    # ========================================================================
    # STEP 1: Source Classification
    # ========================================================================
    print("STEP 1: SOURCE CLASSIFICATION")
    print("-" * 80)
    
    from engine.source_tier_classifier import classify_source
    
    source_classifications = []
    for i, evidence in enumerate(EXAMPLE_EVIDENCE):
        classification = classify_source(evidence)
        source_classifications.append(classification)
        
        print(f"Source {i+1}: {evidence['title'][:50]}...")
        print(f"  Type: {evidence['source_type']}")
        print(f"  Tier: {classification['quality_tier']}")
        print(f"  Rationale: {classification['classification_rationale']}")
        boosts = classification['component_boosts']
        print(f"  Component Boosts:")
        print(f"    R: +{boosts.r_source_reliability:.1f}")
        print(f"    E: +{boosts.e_evidence_quality:.1f}")
        print(f"    T: +{boosts.t_temporal_stability:.1f}")
        print(f"    I: +{boosts.i_independence:.1f}")
        print("")
    
    # ========================================================================
    # STEP 2: Reasoning Audit
    # ========================================================================
    print("")
    print("STEP 2: REASONING AUDIT")
    print("-" * 80)
    
    from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
    
    reasoning_audit = analyze_source_hierarchy_in_reasoning(
        EXAMPLE_CLAIM,
        EXAMPLE_EVIDENCE,
        source_classifications,
    )
    
    print(f"Chain Integrity Score: {reasoning_audit['reasoning_chain_integrity']}/100")
    print(f"Single-Source Dependence: {reasoning_audit['single_source_dependence']}")
    print(f"Tier Distribution:")
    tier_analysis = reasoning_audit['source_tier_analysis']
    print(f"  Tier 1: {tier_analysis['tier_1_count']}")
    print(f"  Tier 2: {tier_analysis['tier_2_count']}")
    print(f"  Tier 3: {tier_analysis['tier_3_count']}")
    print(f"  Tier 4: {tier_analysis['tier_4_count']}")
    
    print(f"Fallacies Detected: {len(reasoning_audit['fallacies_detected'])}")
    if reasoning_audit['fallacies_detected']:
        for fallacy in reasoning_audit['fallacies_detected']:
            print(f"  - {fallacy}")
    
    print(f"Critical Issues: {len(reasoning_audit['critical_issues'])}")
    if reasoning_audit['critical_issues']:
        for issue in reasoning_audit['critical_issues'][:3]:
            print(f"  ⚠ {issue}")
    
    # ========================================================================
    # STEP 3: Weight Adjustment
    # ========================================================================
    print("")
    print("STEP 3: WEIGHT ADJUSTMENT")
    print("-" * 80)
    
    from engine.component_weights import (
        compute_weight_adjustments,
        WeightAdjustmentContext,
        DEFAULT_WEIGHTS,
    )
    
    weight_context = WeightAdjustmentContext(
        source_tier_distribution={
            "tier_1": tier_analysis['tier_1_count'],
            "tier_2": tier_analysis['tier_2_count'],
            "tier_3": tier_analysis['tier_3_count'],
            "tier_4": tier_analysis['tier_4_count'],
        },
        reasoning_fallacies_count=len(reasoning_audit['fallacies_detected']),
        single_source_dependence=reasoning_audit['single_source_dependence'],
        independence_score=reasoning_audit.get('independence_score', 70),
        replication_count=max(
            ev.get('consensus_metadata', {}).get('replication_count', 0)
            for ev in EXAMPLE_EVIDENCE
        ),
        contradiction_count=sum(
            ev.get('consensus_metadata', {}).get('contradictions_count', 0)
            for ev in EXAMPLE_EVIDENCE
        ),
    )
    
    adjusted_weights = compute_weight_adjustments(weight_context)
    
    print("Weight Changes (Tier 1-heavy composition):")
    print(f"{'Component':<30} {'Default':>10} {'Adjusted':>10} {'Change':>10}")
    print("-" * 60)
    for key in sorted(adjusted_weights.keys()):
        default = DEFAULT_WEIGHTS.get(key, 0)
        adjusted = adjusted_weights[key]
        change = adjusted - default
        print(f"{key:<30} {default:>10.4f} {adjusted:>10.4f} {change:>+10.4f}")
    
    # ========================================================================
    # STEP 4: Integrated ASC Scoring
    # ========================================================================
    print("")
    print("STEP 4: INTEGRATED ASC SCORING")
    print("-" * 80)
    
    from engine.scoring_integrated import compute_asc_integrated
    
    asc_result = compute_asc_integrated(
        base_components=EXAMPLE_BASE_COMPONENTS,
        source_classifications=source_classifications,
        reasoning_audit=reasoning_audit,
        weights=adjusted_weights,
        include_audit_trace=True,
        include_sensitivity=True,
    )
    
    print(f"Final ASC Score: {asc_result['asc_score']:.1f}/100")
    print(f"Confidence: {asc_result['confidence']}")
    print("")
    print("Component Scores (After All Adjustments):")
    print(f"{'Component':<30} {'Score':>10}")
    print("-" * 42)
    for key, val in sorted(asc_result['components'].items()):
        print(f"{key:<30} {val:>10.1f}")
    
    print("")
    print("Source Integration Summary:")
    src_summary = asc_result['source_integration_summary']
    print(f"  Sources Classified: {src_summary['sources_classified']}")
    print(f"  Tiers Represented: {src_summary['tiers_represented']}")
    print(f"  Component Boosts Applied:")
    for key, val in src_summary['component_boosts_applied'].items():
        print(f"    {key}: {val:+.1f}")
    
    print("")
    print("Reasoning Audit Integration:")
    reason_summary = asc_result['reasoning_audit_integration']
    print(f"  Audit Applied: {reason_summary['audit_applied']}")
    print(f"  Fallacies Detected: {reason_summary['fallacies_detected']}")
    if reason_summary['fallacies_detected']:
        for fallacy in reason_summary['fallacies_detected']:
            print(f"    - {fallacy}")
    
    # ========================================================================
    # STEP 5: Interpretation
    # ========================================================================
    print("")
    print("STEP 5: INTERPRETATION")
    print("-" * 80)
    
    asc_score = asc_result['asc_score']
    
    if asc_score >= 75:
        status = "SUPPORTED"
        interpretation = (
            "Multiple high-quality, independent sources provide convergent evidence. "
            "Reasoning chain is sound. Strong confidence justified."
        )
    elif asc_score >= 55:
        status = "CONTESTED"
        interpretation = (
            "Evidence exists but concerns about independence or quality remain. "
            "Claim warrants further investigation."
        )
    elif asc_score >= 35:
        status = "UNVERIFIED"
        interpretation = (
            "Weak or insufficient evidence. Cannot rank among established knowledge."
        )
    else:
        status = "REFUTED"
        interpretation = (
            "Strong evidence contradicts this claim. "
            "Alternative explanation(s) better supported."
        )
    
    print(f"Status: {status}")
    print(f"Interpretation: {interpretation}")
    
    # ========================================================================
    # STEP 6: Audit Trail
    # ========================================================================
    print("")
    print("STEP 6: AUDIT TRAIL")
    print("-" * 80)
    
    print("Adjustment Trace:")
    for trace_line in asc_result.get('adjustment_trace', []):
        print(f"  {trace_line}")
    
    print("")
    print(asc_result.get('sensitivity_note', ''))
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("")
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Claim: {EXAMPLE_CLAIM}")
    print(f"Status: {status}")
    print(f"ASC Score: {asc_result['asc_score']:.1f}/100")
    print(f"Confidence: {asc_result['confidence']}")
    print("")
    print("Key Insight:")
    print(f"  Evidence hierarchy: {tier_analysis['tier_1_count']} Tier 1 (primary consensus),")
    print(f"                      {tier_analysis['tier_2_count']} Tier 2 (established),")
    print(f"                      {tier_analysis['tier_3_count']} Tier 3 (secondary)")
    print(f"  Reasoning quality: {reasoning_audit['reasoning_chain_integrity']:.0f}/100")
    print(f"  Source reliability weight: {adjusted_weights['R_source_reliability']:.4f} (vs default {DEFAULT_WEIGHTS['R_source_reliability']:.4f})")
    print(f"  Evidence quality weight: {adjusted_weights['E_evidence_quality']:.4f} (vs default {DEFAULT_WEIGHTS['E_evidence_quality']:.4f})")
    print("")


if __name__ == "__main__":
    run_integration_example()
