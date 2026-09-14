#!/usr/bin/env python3
"""
SAFE Test Suite

Comprehensive tests for:
1. Source tier classification
2. Reasoning audit fallacy detection
3. Component weight adjustment
4. Integrated ASC scoring
5. End-to-end pipeline
"""

import sys
from typing import Dict, Any, List


# ============================================================================
# TEST 1: Source Tier Classification
# ============================================================================

def test_source_classification_tier_1():
    """Verify Tier 1 (primary peer-reviewed) classification."""
    from engine.source_tier_classifier import classify_source, QualityTier
    
    tier_1_source = {
        "source_type": "peer_reviewed_empirical",
        "peer_review": {
            "is_peer_reviewed": True,
            "venue_tier": "top_10_percent",
        },
        "consensus_metadata": {
            "replication_count": 2,
        },
        "derivation_signal": {
            "is_primary": True,
        },
    }
    
    classification = classify_source(tier_1_source)
    assert "tier_1" in str(classification["quality_tier"]).lower(), \
        f"Expected Tier 1, got {classification['quality_tier']}"
    
    boosts = classification["component_boosts"]
    assert boosts.r_source_reliability >= 20, "Tier 1 should have high R boost"
    assert boosts.e_evidence_quality >= 20, "Tier 1 should have high E boost"
    
    print("✓ Test 1.1 PASSED: Tier 1 (peer-reviewed empirical) classified correctly")


def test_source_classification_tier_2():
    """Verify Tier 2 (consensus/established) classification."""
    from engine.source_tier_classifier import classify_source
    
    tier_2_source = {
        "source_type": "university_curriculum",
        "academic_curriculum_metadata": {
            "curriculum_level": "graduate_masters",
            "accredited_institution": True,
        },
    }
    
    classification = classify_source(tier_2_source)
    assert "tier_2" in str(classification["quality_tier"]).lower(), \
        f"Expected Tier 2, got {classification['quality_tier']}"
    
    print("✓ Test 1.2 PASSED: Tier 2 (advanced curriculum) classified correctly")


def test_source_classification_tier_4():
    """Verify Tier 4 (derivative) penalty."""
    from engine.source_tier_classifier import classify_source
    
    tier_4_source = {
        "source_type": "blog_or_opinion",
        "peer_review": {"is_peer_reviewed": False},
    }
    
    classification = classify_source(tier_4_source)
    assert "tier_4" in str(classification["quality_tier"]).lower(), \
        f"Expected Tier 4, got {classification['quality_tier']}"
    
    boosts = classification["component_boosts"]
    assert boosts.r_source_reliability < 0, "Tier 4 should have negative R boost"
    assert boosts.i_independence < 0, "Tier 4 should have negative I boost"
    
    print("✓ Test 1.3 PASSED: Tier 4 (blog/opinion) classified with penalties")


# ============================================================================
# TEST 2: Reasoning Audit
# ============================================================================

def test_reasoning_audit_single_source():
    """Detect single-source dependence fallacy."""
    from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
    
    claim = "Study X proves Y"
    evidence = [{"id": "1", "type": "blog"}]
    classifications = [{
        "quality_tier": "tier_4_derivative",
        "consensus_metadata": {"contradictions_count": 0},
    }]
    
    audit = analyze_source_hierarchy_in_reasoning(claim, evidence, classifications)
    
    assert audit["single_source_dependence"], "Should detect single-source dependence"
    assert len(audit["fallacies_detected"]) > 0, "Should flag reasoning fallacy"
    assert audit["reasoning_chain_integrity"] < 80, "Chain integrity should be reduced"
    
    print("✓ Test 2.1 PASSED: Single-source dependence detected")


def test_reasoning_audit_tier_inversion():
    """Detect when lower-tier sources dominate reasoning."""
    from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
    
    claim = "Multiple sources show X"
    evidence = [{"id": str(i)} for i in range(4)]
    classifications = [
        {"quality_tier": "tier_4_derivative", "consensus_metadata": {"contradictions_count": 0}},
        {"quality_tier": "tier_4_derivative", "consensus_metadata": {"contradictions_count": 0}},
        {"quality_tier": "tier_4_derivative", "consensus_metadata": {"contradictions_count": 0}},
        {"quality_tier": "tier_1_primary", "consensus_metadata": {"contradictions_count": 0}},
    ]
    
    audit = analyze_source_hierarchy_in_reasoning(claim, evidence, classifications)
    
    # Should detect tier inversion (more Tier 4 than Tier 1)
    assert any("tier" in f.lower() for f in audit["fallacies_detected"]), \
        "Should detect tier-related fallacy"
    
    print("✓ Test 2.2 PASSED: Tier inversion detected")


def test_reasoning_audit_good_hierarchy():
    """Verify no fallacies when hierarchy is sound."""
    from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
    
    claim = "Multiple peer-reviewed studies confirm X"
    evidence = [
        {"id": "1"},
        {"id": "2"},
        {"id": "3"},
    ]
    classifications = [
        {"quality_tier": "tier_1_primary", "consensus_metadata": {"contradictions_count": 0}},
        {"quality_tier": "tier_1_primary", "consensus_metadata": {"contradictions_count": 0}},
        {"quality_tier": "tier_2_consensus", "consensus_metadata": {"contradictions_count": 0}},
    ]
    
    audit = analyze_source_hierarchy_in_reasoning(claim, evidence, classifications)
    
    assert len(audit["fallacies_detected"]) == 0, "Should detect no fallacies with sound hierarchy"
    assert audit["reasoning_chain_integrity"] >= 85, "Chain integrity should be high"
    
    print("✓ Test 2.3 PASSED: Good hierarchy produces no fallacies")


# ============================================================================
# TEST 3: Component Weight Adjustment
# ============================================================================

def test_weight_adjustment_tier_1_dominant():
    """Verify R and E weights increase when Tier 1 dominates."""
    from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext, DEFAULT_WEIGHTS
    
    context = WeightAdjustmentContext(
        source_tier_distribution={"tier_1": 3, "tier_2": 0, "tier_3": 0, "tier_4": 0},
        reasoning_fallacies_count=0,
        single_source_dependence=False,
        independence_score=85,
        replication_count=2,
        contradiction_count=0,
    )
    
    adjusted = compute_weight_adjustments(context)
    
    assert adjusted["R_source_reliability"] > DEFAULT_WEIGHTS["R_source_reliability"], \
        "R weight should increase for Tier 1-dominant evidence"
    assert adjusted["E_evidence_quality"] > DEFAULT_WEIGHTS["E_evidence_quality"], \
        "E weight should increase for Tier 1-dominant evidence"
    assert sum(adjusted.values()) > 0.99 and sum(adjusted.values()) < 1.01, \
        "Weights must sum to 1.0"
    
    print("✓ Test 3.1 PASSED: Weights adjust for Tier 1 dominance")


def test_weight_adjustment_fallacies():
    """Verify E weight increases when reasoning fallacies detected."""
    from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext, DEFAULT_WEIGHTS
    
    context = WeightAdjustmentContext(
        source_tier_distribution={"tier_1": 1, "tier_2": 1, "tier_3": 0, "tier_4": 0},
        reasoning_fallacies_count=3,  # Multiple fallacies
        single_source_dependence=False,
        independence_score=70,
        replication_count=1,
        contradiction_count=0,
    )
    
    adjusted = compute_weight_adjustments(context)
    
    assert adjusted["E_evidence_quality"] > DEFAULT_WEIGHTS["E_evidence_quality"], \
        "E weight should increase when fallacies detected"
    
    print("✓ Test 3.2 PASSED: Weights adjust for reasoning fallacies")


# ============================================================================
# TEST 4: Integrated ASC Scoring
# ============================================================================

def test_asc_source_boost_applied():
    """Verify source quality boosts are applied to ASC."""
    from engine.scoring_integrated import compute_asc_integrated
    
    base_components = {"E": 50, "R": 50, "I": 50, "P": 50, "C": 50, "T": 50, "F": 0, "M": 50}
    
    source_classifications = [{
        "quality_tier": "tier_1_primary",
        "component_boosts": {
            "r_source_reliability": 20,
            "e_evidence_quality": 20,
            "t_temporal_stability": 15,
            "i_independence": 10,
        },
    }]
    
    result = compute_asc_integrated(
        base_components,
        source_classifications=source_classifications,
        include_audit_trace=True,
    )
    
    # Components should have been boosted
    assert result["components"]["R_source_reliability"] > 50, "R should be boosted"
    assert result["components"]["E_evidence_quality"] > 50, "E should be boosted"
    
    print("✓ Test 4.1 PASSED: Source boosts applied to ASC")


def test_asc_reasoning_penalty_applied():
    """Verify reasoning audit penalties reduce ASC."""
    from engine.scoring_integrated import compute_asc_integrated
    
    base_components = {"E": 75, "R": 75, "I": 75, "P": 75, "C": 75, "T": 75, "F": 0, "M": 75}
    
    reasoning_audit = {
        "fallacies_detected": ["tier_inversion", "single_source_dependence"],
        "single_source_dependence": True,
    }
    
    result = compute_asc_integrated(
        base_components,
        reasoning_audit=reasoning_audit,
    )
    
    # Components should be penalized
    assert result["components"]["E_evidence_quality"] < 75, "E should be penalized for fallacies"
    assert result["components"]["I_independence"] < 75, "I should be penalized for single source"
    
    print("✓ Test 4.2 PASSED: Reasoning penalties applied to ASC")


def test_asc_confidence_very_high():
    """Verify VERY_HIGH confidence assigned correctly."""
    from engine.scoring_integrated import compute_asc_integrated
    
    # High, consistent components
    base_components = {"E": 88, "R": 90, "I": 85, "P": 82, "C": 87, "T": 89, "F": 0, "M": 86}
    
    result = compute_asc_integrated(base_components)
    
    assert result["confidence"] == "VERY_HIGH", "Should assign VERY_HIGH confidence"
    assert result["asc_score"] >= 85, "ASC should be ≥85 for VERY_HIGH"
    
    print("✓ Test 4.3 PASSED: VERY_HIGH confidence assigned correctly")


# ============================================================================
# TEST 5: End-to-End Pipeline
# ============================================================================

def test_end_to_end_pipeline():
    """Complete pipeline from claim to ASC score."""
    from engine.source_tier_classifier import classify_source
    from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
    from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext
    from engine.scoring_integrated import compute_asc_integrated
    
    # Setup
    claim = "Peer-reviewed studies support X"
    
    evidence = [
        {
            "source_type": "peer_reviewed_empirical",
            "peer_review": {"is_peer_reviewed": True, "venue_tier": "top_10_percent"},
            "consensus_metadata": {"replication_count": 2, "contradictions_count": 0},
            "derivation_signal": {"is_primary": True},
        },
        {
            "source_type": "peer_reviewed_empirical",
            "peer_review": {"is_peer_reviewed": True, "venue_tier": "top_25_percent"},
            "consensus_metadata": {"replication_count": 1, "contradictions_count": 0},
            "derivation_signal": {"is_primary": True},
        },
    ]
    
    base_components = {"E": 70, "R": 70, "I": 65, "P": 60, "C": 75, "T": 75, "F": 0, "M": 72}
    
    # Step 1: Classify sources
    classifications = [classify_source(ev) for ev in evidence]
    assert len(classifications) == 2
    assert all("tier_1" in str(c["quality_tier"]).lower() for c in classifications), \
        "Both sources should be Tier 1"
    
    # Step 2: Audit reasoning
    audit = analyze_source_hierarchy_in_reasoning(claim, evidence, classifications)
    assert len(audit["fallacies_detected"]) <= 1, "Should have minimal fallacies"
    
    # Step 3: Adjust weights
    tier_dist = {"tier_1": 2, "tier_2": 0, "tier_3": 0, "tier_4": 0}
    context = WeightAdjustmentContext(
        source_tier_distribution=tier_dist,
        reasoning_fallacies_count=len(audit["fallacies_detected"]),
        single_source_dependence=audit["single_source_dependence"],
        independence_score=80,
        replication_count=2,
        contradiction_count=0,
    )
    weights = compute_weight_adjustments(context)
    
    # Step 4: Score
    result = compute_asc_integrated(
        base_components,
        source_classifications=classifications,
        reasoning_audit=audit,
        weights=weights,
    )
    
    # Verify result
    assert result["asc_score"] >= 70, "Should have reasonable score with Tier 1 sources"
    assert result["confidence"] in ["HIGH", "VERY_HIGH"], "Should have high confidence"
    
    print("✓ Test 5.1 PASSED: End-to-end pipeline executed successfully")
    print(f"  Final ASC Score: {result['asc_score']:.1f}")
    print(f"  Confidence: {result['confidence']}")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Execute all tests."""
    tests = [
        # Source Classification
        test_source_classification_tier_1,
        test_source_classification_tier_2,
        test_source_classification_tier_4,
        
        # Reasoning Audit
        test_reasoning_audit_single_source,
        test_reasoning_audit_tier_inversion,
        test_reasoning_audit_good_hierarchy,
        
        # Weight Adjustment
        test_weight_adjustment_tier_1_dominant,
        test_weight_adjustment_fallacies,
        
        # ASC Scoring
        test_asc_source_boost_applied,
        test_asc_reasoning_penalty_applied,
        test_asc_confidence_very_high,
        
        # End-to-End
        test_end_to_end_pipeline,
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 80)
    print("SAFE TEST SUITE")
    print("=" * 80)
    print("")
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("")
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
