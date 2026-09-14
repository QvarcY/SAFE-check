"""
SAFE Engine — Pipeline Orchestrator

Coordinates the complete evaluation flow:
1. Source Classification (tier assignment)
2. Reasoning Audit (fallacy detection)
3. Weight Adjustment (dynamic weighting based on context)
4. ASC Scoring (integrated calculation)

Produces a complete, auditable epistemic evaluation.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .component_weights import WeightAdjustmentContext


@dataclass
class SafeEvaluationRequest:
    """Request to evaluate a claim with full context"""
    claim: str
    claim_type: str  # "empirical_causal", "observational", "theoretical", "normative"
    evidence_items: List[Dict[str, Any]]  # Raw evidence with source metadata
    base_asc_components: Dict[str, float]  # Initial component scores (E, R, I, P, C, T, F, M)


@dataclass
class SafeEvaluationResult:
    """Complete evaluation result with full audit trail"""
    claim: str
    final_asc_score: float
    confidence: str
    
    # Detailed component scores
    components_initial: Dict[str, float]
    components_after_sources: Dict[str, float]
    components_after_reasoning: Dict[str, float]
    
    # Classifications and audits
    source_classifications: List[Dict[str, Any]]
    reasoning_audit: Dict[str, Any]
    weight_adjustments: Dict[str, float]
    weight_explanations: Dict[str, str]
    
    # Audit trail
    adjustment_trace: List[str]
    critical_flags: List[str]
    
    # Epistemic summary
    status: str  # "supported", "contested", "refuted", "unverified"
    summary: str


def evaluate_claim_end_to_end(
    request: SafeEvaluationRequest,
    source_classifier_fn,
    reasoning_audit_fn,
    weight_adjuster_fn,
    asc_scorer_fn,
) -> SafeEvaluationResult:
    """
    Complete end-to-end evaluation pipeline.
    
    Parameters
    ----------
    request : SafeEvaluationRequest
        The claim and evidence to evaluate
    
    source_classifier_fn : callable
        Function that classifies sources into tiers
    
    reasoning_audit_fn : callable
        Function that audits reasoning quality
    
    weight_adjuster_fn : callable
        Function that adjusts ASC weights based on context
    
    asc_scorer_fn : callable
        Function that computes final ASC score
    
    Returns
    -------
    SafeEvaluationResult with complete audit trail
    """
    
    # ========================================================================
    # STEP 1: CLASSIFY SOURCES
    # ========================================================================
    source_classifications = []
    critical_flags = []
    
    for i, evidence_item in enumerate(request.evidence_items):
        classification = source_classifier_fn(evidence_item)
        source_classifications.append(classification)
        
        # Collect critical flags
        if "critical_flags" in classification:
            for flag in classification["critical_flags"]:
                critical_flags.append(f"Source {i+1}: {flag}")
    
    # ========================================================================
    # STEP 2: AUDIT REASONING
    # ========================================================================
    reasoning_audit = reasoning_audit_fn(
        request.claim,
        request.evidence_items,
        source_classifications,
    )
    
    # Add reasoning issues to critical flags
    for issue in reasoning_audit.get("critical_issues", []):
        critical_flags.append(f"Reasoning: {issue}")
    
    # ========================================================================
    # STEP 3: BUILD WEIGHT ADJUSTMENT CONTEXT
    # ========================================================================
    tier_distribution = {
        "tier_1": 0,
        "tier_2": 0,
        "tier_3": 0,
        "tier_4": 0,
    }
    
    replication_count = 0
    contradiction_count = 0
    
    for classification in source_classifications:
        raw_tier = classification.get("quality_tier", "unknown")
        tier = str(getattr(raw_tier, "value", raw_tier)).lower()
        if "tier_1" in tier:
            tier_distribution["tier_1"] += 1
        elif "tier_2" in tier:
            tier_distribution["tier_2"] += 1
        elif "tier_3" in tier:
            tier_distribution["tier_3"] += 1
        else:
            tier_distribution["tier_4"] += 1
        
        # Aggregate replication and contradiction counts
        consensus_meta = classification.get("consensus_metadata", {})
        replication_count = max(replication_count, consensus_meta.get("replication_count", 0))
        contradiction_count += consensus_meta.get("contradictions_count", 0)
    
    # Get independence score from reasoning audit
    independence_score = reasoning_audit.get("source_tier_analysis", {}).get("independence_score", 60)
    single_source = reasoning_audit.get("single_source_dependence", False)
    fallacy_count = len(reasoning_audit.get("fallacies_detected", []))
    
    # ========================================================================
    # STEP 4: ADJUST WEIGHTS
    # ========================================================================
    weight_adjustment_context = WeightAdjustmentContext(
        source_tier_distribution=tier_distribution,
        reasoning_fallacies_count=fallacy_count,
        single_source_dependence=single_source,
        independence_score=independence_score,
        replication_count=replication_count,
        contradiction_count=contradiction_count,
    )
    
    adjusted_weights = weight_adjuster_fn(weight_adjustment_context)
    weight_explanations = {}  # Would be populated by weight_adjuster_fn explanation method
    
    # ========================================================================
    # STEP 5: COMPUTE ASC SCORE
    # ========================================================================
    asc_result = asc_scorer_fn(
        base_components=request.base_asc_components,
        source_classifications=source_classifications,
        reasoning_audit=reasoning_audit,
        weights=adjusted_weights,
        include_audit_trace=True,
    )
    
    # ========================================================================
    # STEP 6: DETERMINE STATUS
    # ========================================================================
    asc_score = asc_result["asc_score"]
    confidence = asc_result["confidence"]
    
    if asc_score >= 75 and confidence in ["HIGH", "VERY_HIGH"]:
        status = "supported"
    elif asc_score >= 55 and asc_score < 75:
        status = "contested"
    elif asc_score < 35:
        status = "refuted"
    else:
        status = "unverified"
    
    # ========================================================================
    # STEP 7: BUILD SUMMARY
    # ========================================================================
    summary = _build_summary(
        claim=request.claim,
        status=status,
        asc_score=asc_score,
        confidence=confidence,
        tier_distribution=tier_distribution,
        fallacy_count=fallacy_count,
        critical_flags=critical_flags,
    )
    
    # ========================================================================
    # BUILD RESULT
    # ========================================================================
    return SafeEvaluationResult(
        claim=request.claim,
        final_asc_score=asc_score,
        confidence=confidence,
        components_initial=request.base_asc_components,
        components_after_sources=asc_result["source_integration_summary"].get("adjusted_components", {}),
        components_after_reasoning=asc_result["reasoning_audit_integration"].get("adjusted_components", {}),
        source_classifications=source_classifications,
        reasoning_audit=reasoning_audit,
        weight_adjustments=adjusted_weights,
        weight_explanations=weight_explanations,
        adjustment_trace=asc_result.get("adjustment_trace", []),
        critical_flags=critical_flags,
        status=status,
        summary=summary,
    )


def _build_summary(
    claim: str,
    status: str,
    asc_score: float,
    confidence: str,
    tier_distribution: Dict[str, int],
    fallacy_count: int,
    critical_flags: List[str],
) -> str:
    """Generate human-readable summary of evaluation."""
    
    summary_lines = [
        f"CLAIM: {claim}",
        f"STATUS: {status.upper()}",
        f"ASC SCORE: {asc_score:.1f}/100 ({confidence})",
        "",
        "EVIDENCE COMPOSITION:",
        f"  Tier 1 (primary peer-reviewed): {tier_distribution['tier_1']}",
        f"  Tier 2 (consensus/established): {tier_distribution['tier_2']}",
        f"  Tier 3 (secondary/news): {tier_distribution['tier_3']}",
        f"  Tier 4 (derivative/opinion): {tier_distribution['tier_4']}",
    ]
    
    if fallacy_count > 0:
        summary_lines.append(f"\nREASONING AUDIT:")
        summary_lines.append(f"  {fallacy_count} fallacy/fallacies detected in supporting logic")
    
    if critical_flags:
        summary_lines.append(f"\nCRITICAL ISSUES:")
        for flag in critical_flags[:5]:  # Limit to 5
            summary_lines.append(f"  ⚠ {flag}")
        if len(critical_flags) > 5:
            summary_lines.append(f"  ... and {len(critical_flags) - 5} more")
    
    # Status-specific language
    if status == "supported":
        summary_lines.append(
            "\nINTERPRETATION: Multiple high-quality sources provide convergent evidence. "
            "Reasoning chain is sound. Confidence is justified."
        )
    elif status == "contested":
        summary_lines.append(
            "\nINTERPRETATION: Evidence exists but quality or independence concerns remain. "
            "Claim warrants further investigation before strong conviction."
        )
    elif status == "refuted":
        summary_lines.append(
            "\nINTERPRETATION: High-quality evidence contradicts this claim. "
            "Alternative explanation(s) better supported."
        )
    else:  # unverified
        summary_lines.append(
            "\nINTERPRETATION: Insufficient or weak evidence. "
            "Claim cannot yet be ranked among established knowledge."
        )
    
    return "\n".join(summary_lines)


def format_evaluation_report(result: SafeEvaluationResult) -> str:
    """Format a complete evaluation result as a readable report."""
    
    lines = [
        "=" * 80,
        "SAFE CLAIM EVALUATION REPORT",
        "=" * 80,
        "",
        result.summary,
        "",
        "=" * 80,
        "DETAILED COMPONENT ANALYSIS",
        "=" * 80,
        "",
        "Initial Components (Base Assessment):",
    ]
    
    for key, val in result.components_initial.items():
        lines.append(f"  {key:30} {val:6.1f}")
    
    lines.append("")
    lines.append("After Source Quality Adjustment:")
    for key, val in result.components_after_sources.items():
        lines.append(f"  {key:30} {val:6.1f}")
    
    lines.append("")
    lines.append("After Reasoning Audit:")
    for key, val in result.components_after_reasoning.items():
        lines.append(f"  {key:30} {val:6.1f}")
    
    lines.extend([
        "",
        "=" * 80,
        "ADJUSTMENT TRACE",
        "=" * 80,
        "",
    ])
    
    for trace_line in result.adjustment_trace:
        lines.append(f"  {trace_line}")
    
    if result.critical_flags:
        lines.extend([
            "",
            "=" * 80,
            "CRITICAL FLAGS",
            "=" * 80,
            "",
        ])
        for flag in result.critical_flags:
            lines.append(f"  ⚠ {flag}")
    
    lines.extend([
        "",
        "=" * 80,
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    print("SAFE Orchestrator Module")
    print("Provides end-to-end pipeline coordination.")
    print("\nUsage:")
    print("  1. Create SafeEvaluationRequest with claim and evidence")
    print("  2. Call evaluate_claim_end_to_end() with classification/audit/weight/scoring functions")
    print("  3. Receive SafeEvaluationResult with complete audit trail")
    print("  4. Format with format_evaluation_report() for human reading")
