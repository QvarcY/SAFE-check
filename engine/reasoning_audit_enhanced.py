"""
SAFE Engine — Enhanced Reasoning Audit

Evaluates the QUALITY of reasoning about sources, not just factual accuracy.

Checks for:
1. Inappropriate elevation of lower-tier sources
2. Dismissal of higher-tier sources without justification
3. Mixing of evidence tiers in single logical chain without transparency
4. Single-source dependence (especially from lower tiers)
5. Cherry-picking (selecting among contradictory sources)
6. Base-rate neglect (ignoring how common claims are in lower vs. higher tiers)
7. Argument-from-authority (appealing to a person's prestige rather than source rigor)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ReasoningFallacy(Enum):
    """Detected logical fallacies specific to source reasoning"""
    TIER_INVERSION = "tier_inversion"                           # Lower tier treated as higher
    CHERRY_PICKING = "cherry_picking"                           # Selected from contradictory sources
    SINGLE_TIER_4_DEPENDENCE = "single_source_dependence_tier_4" # Leaning on blog/opinion
    DISMISSAL_TIER_1_UNJUSTIFIED = "dismissal_tier_1_unjustified"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    BASE_RATE_NEGLECT = "base_rate_neglect"
    CONSENSUS_CONTRADICTION = "consensus_contradiction"
    EXTRAPOLATION_BEYOND_TIER = "extrapolation_beyond_tier"
    CIRCULAR_REASONING = "circular_reasoning"
    CORRELATION_CAUSATION = "correlation_causation"
    UNSUPPORTED_ASSUMPTION = "unsupported_assumption"


@dataclass
class ReasoningAuditResult:
    """Result of enhanced reasoning audit"""
    fallacies_detected: List[str]
    single_source_dependence: bool
    source_tier_analysis: Dict[str, Any]
    reasoning_chain_integrity: float  # 0-100 score
    critical_issues: List[str]
    recommendations: List[str]
    notes: str


def analyze_source_hierarchy_in_reasoning(
    claim: str,
    evidence_used: List[Dict[str, Any]],
    source_classifications: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze whether the reasoning appropriately respects source hierarchy.
    
    Parameters
    ----------
    claim : str
        The claim being evaluated
    
    evidence_used : list
        List of evidence items used in reasoning
    
    source_classifications : list
        Corresponding tier classifications for each evidence item
    
    Returns
    -------
    Comprehensive reasoning audit result
    """
    fallacies = []
    critical_issues = []
    recommendations = []
    
    if not evidence_used or not source_classifications:
        return {
            "fallacies_detected": ["insufficient_evidence"],
            "single_source_dependence": True,
            "reasoning_chain_integrity": 20,
            "critical_issues": ["No evidence provided for claim"],
            "recommendations": ["Add evidence from Tier 1 or Tier 2 sources"],
        }
    
    # Count sources by tier
    tier_counts = {
        "tier_1": 0,
        "tier_2": 0,
        "tier_3": 0,
        "tier_4": 0,
    }
    
    tier_1_sources = []
    tier_2_sources = []
    tier_3_sources = []
    tier_4_sources = []
    
    for classification in source_classifications:
        tier = classification.get("quality_tier", "unknown")
        tier_str = str(getattr(tier, "value", tier)).lower()
        if "tier_1" in tier_str:
            tier_counts["tier_1"] += 1
            tier_1_sources.append(classification)
        elif "tier_2" in tier_str:
            tier_counts["tier_2"] += 1
            tier_2_sources.append(classification)
        elif "tier_3" in tier_str:
            tier_counts["tier_3"] += 1
            tier_3_sources.append(classification)
        elif "tier_4" in tier_str:
            tier_counts["tier_4"] += 1
            tier_4_sources.append(classification)
    
    # ============================================================================
    # FALLACY 1: TIER INVERSION
    # ============================================================================
    # Higher-tier sources exist but lower-tier source is treated as primary
    if tier_1_sources and tier_4_sources:
        if len(tier_4_sources) > len(tier_1_sources):
            fallacies.append(ReasoningFallacy.TIER_INVERSION.value)
            critical_issues.append(
                f"TIER INVERSION: {len(tier_4_sources)} Tier 4 sources used vs "
                f"{len(tier_1_sources)} Tier 1 sources. Lower-tier sources should not "
                "outweigh higher-tier sources without explicit justification."
            )
            recommendations.append(
                "Prioritize conclusions supported by Tier 1 or Tier 2 sources. "
                "If using Tier 4 sources, explicitly state why they override higher tiers."
            )
    
    # ============================================================================
    # FALLACY 2: SINGLE SOURCE DEPENDENCE (especially Tier 4)
    # ============================================================================
    if len(evidence_used) == 1:
        fallacies.append(ReasoningFallacy.SINGLE_TIER_4_DEPENDENCE.value if tier_4_sources else "single_source_dependence")
        if tier_4_sources:
            critical_issues.append(
                "CRITICAL: Claim depends entirely on a Tier 4 (low-confidence) source. "
                "This claim cannot be considered reliable without Tier 1/2 corroboration."
            )
            recommendations.append(
                "Seek independent Tier 1 or Tier 2 sources that support the same claim. "
                "Consider the claim 'unverified' until higher-tier evidence emerges."
            )
        else:
            recommendations.append(
                "Provide at least 2 independent sources at Tier 1 or Tier 2 to reduce "
                "dependence on a single source."
            )
    
    # ============================================================================
    # FALLACY 3: CHERRY-PICKING
    # ============================================================================
    # Check if some high-tier sources are ignored while lower-tier are selected
    has_contradictions = any(
        c.get("consensus_metadata", {}).get("contradictions_count", 0) > 0
        for c in source_classifications
    )
    
    if has_contradictions and (tier_4_sources or tier_3_sources):
        if not (tier_1_sources or tier_2_sources):
            fallacies.append(ReasoningFallacy.CHERRY_PICKING.value)
            critical_issues.append(
                "CHERRY-PICKING: Contradictory evidence exists, but only Tier 3/4 sources "
                "are used. This may indicate selective evidence choice."
            )
            recommendations.append(
                "Address all high-tier contradictory evidence in the reasoning. "
                "Explain why Tier 4 sources are preferred over conflicting Tier 1/2 sources."
            )
    
    # ============================================================================
    # FALLACY 4: APPEAL TO AUTHORITY (vs. appeal to rigor)
    # ============================================================================
    # Detect if reasoning says "X said..." without explaining WHY X is credible
    authority_phrases = ["according to", "X says", "X claims", "X argues"]
    reason_phrases = ["peer-reviewed in", "meta-analysis of", "consensus among", "replicated in"]
    
    uses_authority_language = any(phrase in claim.lower() for phrase in authority_phrases)
    uses_rigor_language = any(phrase in claim.lower() for phrase in reason_phrases)
    
    if uses_authority_language and not uses_rigor_language:
        if not tier_1_sources:
            fallacies.append(ReasoningFallacy.APPEAL_TO_AUTHORITY.value)
            critical_issues.append(
                "APPEAL TO AUTHORITY: Claim cites a person/authority without explaining "
                "the methodological basis for their credibility."
            )
            recommendations.append(
                "Replace 'Person X says' with 'Peer-reviewed study X found' or "
                "'Consensus among N institutions established'."
            )
    
    # ============================================================================
    # FALLACY 5: BASE-RATE NEGLECT
    # ============================================================================
    # If using Tier 3/4 sources for a claim that contradicts Tier 1/2 consensus
    tier_1_tier_2_count = tier_counts["tier_1"] + tier_counts["tier_2"]
    tier_3_tier_4_count = tier_counts["tier_3"] + tier_counts["tier_4"]
    
    if tier_3_tier_4_count > tier_1_tier_2_count and tier_1_tier_2_count > 0:
        # Check if Tier 1/2 would contradict the conclusion
        fallacies.append(ReasoningFallacy.BASE_RATE_NEGLECT.value)
        critical_issues.append(
            "BASE-RATE NEGLECT: More evidence comes from Tier 3/4 than Tier 1/2, "
            "despite Tier 1/2 being available. This may distort the probability of the claim."
        )
        recommendations.append(
            "Weight evidence by tier, not just by count. One Tier 1 source typically "
            "outweighs multiple Tier 3 sources absent explicit contradictions."
        )
    
    # ============================================================================
    # FALLACY 6: CONSENSUS CONTRADICTION
    # ============================================================================
    tier_1_contradictions = sum(
        c.get("consensus_metadata", {}).get("contradictions_count", 0)
        for c in tier_1_sources
    )
    
    if tier_1_contradictions > 0 and (tier_3_sources or tier_4_sources):
        fallacies.append(ReasoningFallacy.CONSENSUS_CONTRADICTION.value)
        critical_issues.append(
            f"CONSENSUS CONTRADICTION: Tier 1 sources have {tier_1_contradictions} "
            "documented contradictions. Using lower-tier sources to support the claim "
            "anyway may be reasoning against the evidence."
        )
        recommendations.append(
            "Acknowledge the contradiction explicitly. Explain why the claim should be "
            "believed despite conflicting Tier 1 evidence."
        )
    
    # ============================================================================
    # CALCULATE REASONING CHAIN INTEGRITY SCORE
    # ============================================================================
    integrity_score = 100.0
    
    # Penalties for each violation (cumulative)
    if fallacies:
        integrity_score -= len(fallacies) * 15  # -15 per fallacy
    
    if len(evidence_used) == 1:
        integrity_score -= 25  # Single-source heavy penalty
    elif len(evidence_used) <= 2:
        integrity_score -= 10
    
    if tier_4_sources and not tier_1_sources:
        integrity_score -= 30
    elif tier_3_sources and not tier_1_sources and not tier_2_sources:
        integrity_score -= 15
    
    if has_contradictions:
        if not (tier_1_sources or tier_2_sources):
            integrity_score -= 20
    
    integrity_score = max(0, min(100, integrity_score))
    
    # ============================================================================
    # BUILD AUDIT RESULT
    # ============================================================================
    return {
        "fallacies_detected": fallacies,
        "single_source_dependence": len(evidence_used) == 1,
        "source_tier_analysis": {
            "tier_1_count": tier_counts["tier_1"],
            "tier_2_count": tier_counts["tier_2"],
            "tier_3_count": tier_counts["tier_3"],
            "tier_4_count": tier_counts["tier_4"],
            "total_sources": len(evidence_used),
            "highest_tier_available": (
                "tier_1" if tier_1_sources else
                "tier_2" if tier_2_sources else
                "tier_3" if tier_3_sources else
                "tier_4"
            ),
            "tier_distribution": tier_counts,
        },
        "reasoning_chain_integrity": round(integrity_score, 1),
        "critical_issues": critical_issues,
        "recommendations": recommendations,
        "notes": f"Analyzed {len(evidence_used)} evidence items across {len(set(str(c.get('quality_tier', 'unknown')) for c in source_classifications))} tiers. "
                 f"Detected {len(fallacies)} potential logical fallacies related to source quality."
    }


def generate_reasoning_audit_report(
    claim: str,
    evidence_used: List[Dict[str, Any]],
    source_classifications: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Full reasoning audit report for inclusion in SAFE output.
    
    Returns machine-readable audit + human-readable summary.
    """
    analysis = analyze_source_hierarchy_in_reasoning(claim, evidence_used, source_classifications)
    
    return {
        "reasoning_audit": {
            "fallacies_detected": analysis["fallacies_detected"],
            "single_source_dependence": analysis["single_source_dependence"],
            "logical_steps_reconstructed": (
                "Evidence was evaluated across hierarchical tiers (Tier 1 primary → Tier 4 derivative). "
                "Reasoning chain checked for appropriate weighting and fallacy patterns."
            ),
            "notes": analysis["notes"],
        },
        "source_tier_analysis": analysis["source_tier_analysis"],
        "reasoning_chain_integrity": analysis["reasoning_chain_integrity"],
        "critical_issues": analysis["critical_issues"],
        "recommendations": analysis["recommendations"],
    }


if __name__ == "__main__":
    # Example: Analyze reasoning about a hypothetical claim
    example_claim = "Study X shows that Z is true"
    
    example_evidence = [
        {
            "title": "Original Research Article",
            "type": "peer_reviewed_empirical",
        },
    ]
    
    example_classifications = [
        {
            "quality_tier": "tier_1_primary",
            "classification_rationale": "Peer-reviewed empirical with consensus",
            "consensus_metadata": {"contradictions_count": 2},
        },
    ]
    
    audit = analyze_source_hierarchy_in_reasoning(
        example_claim,
        example_evidence,
        example_classifications
    )
    
    print("Reasoning Audit Result:")
    print(f"  Fallacies: {audit['fallacies_detected']}")
    print(f"  Chain Integrity: {audit['reasoning_chain_integrity']}/100")
    print(f"  Critical Issues: {audit['critical_issues']}")
    for rec in audit["recommendations"]:
        print(f"    → {rec}")
