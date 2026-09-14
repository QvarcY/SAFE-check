"""
SAFE Engine — Component Weight Adjustment Strategy

Dynamically adjusts ASC component weights based on:
1. Composition of source quality tiers (if heavy on Tier 1/2, rely more on R and E)
2. Reasoning audit findings (if fallacies detected, increase E weight)
3. Independence signals (if single source or low independence, reduce I weight)
4. Replication evidence (if strong replication, increase P weight)

This ensures the ASC weighting is responsive to the actual epistemic situation,
not static.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class WeightAdjustmentContext:
    """Context for weight adjustment decisions"""
    source_tier_distribution: Dict[str, int]  # {"tier_1": n, "tier_2": n, ...}
    reasoning_fallacies_count: int
    single_source_dependence: bool
    independence_score: float  # 0-100
    replication_count: int
    contradiction_count: int


# Default weights (baseline)
DEFAULT_WEIGHTS = {
    "E_evidence_quality": 0.18,
    "R_source_reliability": 0.15,
    "I_independence": 0.15,
    "P_replication": 0.12,
    "C_contradiction_resistance": 0.15,
    "T_temporal_stability": 0.10,
    "M_methodology": 0.15,
}


def compute_weight_adjustments(context: WeightAdjustmentContext) -> Dict[str, float]:
    """
    Compute weight adjustments based on epistemic context.
    
    Returns adjusted weights that sum to 1.0.
    
    Parameters
    ----------
    context : WeightAdjustmentContext
        Epistemic situation (tier distribution, reasoning quality, independence, etc.)
    
    Returns
    -------
    dict of adjusted weights (sum to 1.0)
    """
    weights = DEFAULT_WEIGHTS.copy()
    adjustments = {}
    
    # ========================================================================
    # ADJUSTMENT 1: Source Tier Composition
    # ========================================================================
    tier_1_count = context.source_tier_distribution.get("tier_1", 0)
    tier_2_count = context.source_tier_distribution.get("tier_2", 0)
    tier_3_count = context.source_tier_distribution.get("tier_3", 0)
    tier_4_count = context.source_tier_distribution.get("tier_4", 0)
    
    total_sources = sum(context.source_tier_distribution.values())
    
    if total_sources > 0:
        tier_1_ratio = tier_1_count / total_sources
        tier_2_ratio = tier_2_count / total_sources
        tier_34_ratio = (tier_3_count + tier_4_count) / total_sources
        
        # If heavy on Tier 1/2, increase weight on R (source reliability)
        # because the quality signal is clear
        if tier_1_ratio >= 0.5:
            adjustments["R_source_reliability"] = +0.03
            adjustments["E_evidence_quality"] = +0.02
            adjustments["M_methodology"] = +0.01
            adjustments["T_temporal_stability"] = -0.02  # Less weight needed
            adjustments["P_replication"] = -0.02
            adjustments["C_contradiction_resistance"] = -0.02
        
        # If heavy on Tier 3/4, increase weight on I (independence)
        # because we need to ensure sources aren't derivative
        elif tier_34_ratio >= 0.5:
            adjustments["I_independence"] = +0.05
            adjustments["E_evidence_quality"] = +0.03
            adjustments["R_source_reliability"] = -0.03
            adjustments["M_methodology"] = -0.02
            adjustments["P_replication"] = -0.03
    
    # ========================================================================
    # ADJUSTMENT 2: Reasoning Fallacies
    # ========================================================================
    # More fallacies detected → increase E (evidence quality) weight
    # because quality reasoning is more critical
    if context.reasoning_fallacies_count > 0:
        fallacy_weight_boost = min(0.08, context.reasoning_fallacies_count * 0.02)
        adjustments["E_evidence_quality"] = adjustments.get("E_evidence_quality", 0) + fallacy_weight_boost
        adjustments["R_source_reliability"] = adjustments.get("R_source_reliability", 0) + fallacy_weight_boost * 0.5
        adjustments["M_methodology"] = adjustments.get("M_methodology", 0) + fallacy_weight_boost * 0.5
        
        # Reduce weights on components less directly tied to reasoning quality
        adjustments["T_temporal_stability"] = adjustments.get("T_temporal_stability", 0) - fallacy_weight_boost * 0.3
        adjustments["P_replication"] = adjustments.get("P_replication", 0) - fallacy_weight_boost * 0.2
    
    # ========================================================================
    # ADJUSTMENT 3: Single-Source Dependence
    # ========================================================================
    if context.single_source_dependence:
        # Single source → must rely heavily on that source's reliability
        adjustments["R_source_reliability"] = adjustments.get("R_source_reliability", 0) + 0.05
        adjustments["I_independence"] = adjustments.get("I_independence", 0) + 0.05
        
        # Cannot rely on replication or contradiction resistance
        adjustments["P_replication"] = adjustments.get("P_replication", 0) - 0.03
        adjustments["C_contradiction_resistance"] = adjustments.get("C_contradiction_resistance", 0) - 0.03
    
    # ========================================================================
    # ADJUSTMENT 4: Independence Signal
    # ========================================================================
    # Low independence score → increase I weight
    if context.independence_score < 50:
        independence_deficit = (50 - context.independence_score) / 50  # 0-1 scale
        independence_boost = independence_deficit * 0.05
        adjustments["I_independence"] = adjustments.get("I_independence", 0) + independence_boost
        
        # Reduce other weights to compensate
        adjustments["M_methodology"] = adjustments.get("M_methodology", 0) - independence_boost * 0.3
        adjustments["T_temporal_stability"] = adjustments.get("T_temporal_stability", 0) - independence_boost * 0.2
    
    # ========================================================================
    # ADJUSTMENT 5: Replication Evidence
    # ========================================================================
    # High replication count → increase P weight
    if context.replication_count >= 3:
        replication_boost = min(0.04, context.replication_count * 0.01)
        adjustments["P_replication"] = adjustments.get("P_replication", 0) + replication_boost
        
        # Reduce weight on components that matter less when replicated
        adjustments["M_methodology"] = adjustments.get("M_methodology", 0) - replication_boost * 0.5
        adjustments["I_independence"] = adjustments.get("I_independence", 0) - replication_boost * 0.3
    
    elif context.replication_count == 0:
        # No replication → reduce P weight
        adjustments["P_replication"] = adjustments.get("P_replication", 0) - 0.03
        adjustments["M_methodology"] = adjustments.get("M_methodology", 0) + 0.02
    
    # ========================================================================
    # ADJUSTMENT 6: Contradiction Evidence
    # ========================================================================
    # High contradiction count → increase C weight
    if context.contradiction_count >= 2:
        contradiction_weight = min(0.04, context.contradiction_count * 0.01)
        adjustments["C_contradiction_resistance"] = adjustments.get("C_contradiction_resistance", 0) + contradiction_weight
        
        # Reduce other weights
        adjustments["T_temporal_stability"] = adjustments.get("T_temporal_stability", 0) - contradiction_weight * 0.5
        adjustments["P_replication"] = adjustments.get("P_replication", 0) - contradiction_weight * 0.3
    
    # ========================================================================
    # APPLY ADJUSTMENTS WITH NORMALIZATION
    # ========================================================================
    adjusted = {}
    for key, weight in weights.items():
        adj = adjustments.get(key, 0)
        adjusted[key] = weight + adj
    
    # Clamp all weights to reasonable bounds [0.08, 0.25] to prevent over-weighting
    for key in adjusted:
        adjusted[key] = max(0.08, min(0.25, adjusted[key]))
    
    # Normalize to sum to 1.0
    total = sum(adjusted.values())
    normalized = {k: v / total for k, v in adjusted.items()}
    
    return normalized


def get_weight_explanation(
    context: WeightAdjustmentContext,
    adjusted_weights: Dict[str, float],
    default_weights: Dict[str, float] = None,
) -> Dict[str, str]:
    """
    Generate human-readable explanations for weight adjustments.
    
    Returns dict mapping weight names to explanatory text.
    """
    if default_weights is None:
        default_weights = DEFAULT_WEIGHTS
    
    explanations = {}
    
    tier_1_count = context.source_tier_distribution.get("tier_1", 0)
    tier_2_count = context.source_tier_distribution.get("tier_2", 0)
    tier_34_count = context.source_tier_distribution.get("tier_3", 0) + context.source_tier_distribution.get("tier_4", 0)
    total = sum(context.source_tier_distribution.values())
    
    if total > 0:
        if tier_1_count / total >= 0.5:
            explanations["R_source_reliability"] = (
                f"Increased: {tier_1_count} Tier 1 sources detected. "
                "High-quality sources increase weight on venue/peer-review credibility."
            )
            explanations["E_evidence_quality"] = (
                "Increased: Strong evidence base justifies higher weight on quality signals."
            )
        
        elif tier_34_count / total >= 0.5:
            explanations["I_independence"] = (
                f"Increased: {tier_34_count} lower-tier sources detected. "
                "Critical to verify these are independent primaries, not reposts."
            )
            explanations["E_evidence_quality"] = (
                "Increased: Lower-tier sources require more scrutiny on quality."
            )
    
    if context.reasoning_fallacies_count > 0:
        explanations["E_evidence_quality"] = (
            f"Increased: {context.reasoning_fallacies_count} reasoning fallacies detected. "
            "Quality of supporting evidence becomes more critical."
        )
    
    if context.single_source_dependence:
        explanations["R_source_reliability"] = (
            "Increased: Single-source dependence detected. "
            "Credibility of that source is critical."
        )
        explanations["I_independence"] = (
            "Increased: Must verify single source is truly independent."
        )
    
    if context.independence_score < 50:
        explanations["I_independence"] = (
            f"Increased: Independence score {context.independence_score:.0f}/100 is below threshold. "
            "Evidence provenance needs scrutiny."
        )
    
    if context.replication_count >= 3:
        explanations["P_replication"] = (
            f"Increased: {context.replication_count} independent replications. "
            "Strong replication signal increases confidence."
        )
    elif context.replication_count == 0:
        explanations["P_replication"] = (
            "Reduced: No independent replications found. "
            "Cannot lean on replication signal."
        )
    
    if context.contradiction_count >= 2:
        explanations["C_contradiction_resistance"] = (
            f"Increased: {context.contradiction_count} contradictions detected. "
            "Must evaluate how claim handles contrary evidence."
        )
    
    return explanations


if __name__ == "__main__":
    # Example: Adjust weights for Tier 1-heavy evidence with good reasoning
    example_context = WeightAdjustmentContext(
        source_tier_distribution={
            "tier_1": 2,
            "tier_2": 1,
            "tier_3": 0,
            "tier_4": 0,
        },
        reasoning_fallacies_count=0,
        single_source_dependence=False,
        independence_score=85,
        replication_count=3,
        contradiction_count=0,
    )
    
    adjusted = compute_weight_adjustments(example_context)
    explanations = get_weight_explanation(example_context, adjusted)
    
    print("Weight Adjustments (Tier 1-heavy, good reasoning):")
    print("=" * 70)
    for key in sorted(adjusted.keys()):
        default = DEFAULT_WEIGHTS[key]
        adj = adjusted[key]
        change = adj - default
        direction = "↑" if change > 0 else "↓" if change < 0 else "→"
        print(f"  {key:30} {default:.3f} {direction} {adj:.3f} (Δ {change:+.3f})")
    
    print("\nExplanations:")
    print("=" * 70)
    for key, explanation in explanations.items():
        print(f"  {key}:")
        print(f"    {explanation}\n")
    
    print("\nSum of weights:", round(sum(adjusted.values()), 4))
