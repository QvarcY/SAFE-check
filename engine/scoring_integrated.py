"""
SAFE Engine — Integrated Argument Strength Coefficient (ASC) Calculator v2.0

Version: 2.0.0 — Source Quality Tier Integration
Incorporates source hierarchy, reasoning audit, and component boosts.

Transparent, versioned, pure function.
Ethical desirability never enters the calculation.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import math
from dataclasses import dataclass


ASC_VERSION = "2.0.0"

# Default weights for the seven 0-100 components.
# F is treated as a signed adjustment outside the weighted average.
DEFAULT_WEIGHTS = {
    "E_evidence_quality": 0.18,
    "R_source_reliability": 0.15,
    "I_independence": 0.15,
    "P_replication": 0.12,
    "C_contradiction_resistance": 0.15,
    "T_temporal_stability": 0.10,
    "M_methodology": 0.15,
}

F_SCALE = 1.0  # multiplier applied to F before adding


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


@dataclass
class ComponentBoosts:
    """Component boost adjustments from source classification"""
    r_source_reliability: float
    e_evidence_quality: float
    t_temporal_stability: float
    i_independence: float


def compute_asc_integrated(
    base_components: Dict[str, float],
    source_classifications: Optional[List[Dict[str, Any]]] = None,
    reasoning_audit: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
    include_sensitivity: bool = True,
    include_audit_trace: bool = True,
) -> Dict[str, Any]:
    """
    Compute the Argument Strength Coefficient with source quality and reasoning integration.

    Parameters
    ----------
    base_components : dict
        Base ASC component scores (E, R, I, P, C, T, F, M) or long form.
        These are pre-audit scores; source quality adjustments will be applied.

    source_classifications : optional list
        List of source classification results (from source_tier_classifier).
        Each item should have:
        - quality_tier
        - component_boosts (R, E, T, I adjustments)
        - critical_flags

    reasoning_audit : optional dict
        Result from reasoning_audit_enhanced module.
        Contains fallacies_detected, single_source_dependence, etc.

    weights : optional dict
        Override default weights. Must sum to ~1.0 for the seven 0-100 components.

    include_sensitivity : bool
        Include sensitivity analysis notes.

    include_audit_trace : bool
        Include detailed trace of adjustments made.

    Returns
    -------
    dict with:
        - asc_score (0-100)
        - confidence (LOW/MEDIUM/HIGH/VERY_HIGH)
        - components (all 8, adjusted)
        - version
        - adjustment_trace (what was modified and why)
        - source_integration_summary
        - reasoning_audit_integration
        - sensitivity_note (optional)
    """
    # Normalize short keys to long form
    key_map = {
        "E": "E_evidence_quality",
        "R": "R_source_reliability",
        "I": "I_independence",
        "P": "P_replication",
        "C": "C_contradiction_resistance",
        "T": "T_temporal_stability",
        "F": "F_fundamental_laws",
        "M": "M_methodology",
    }
    norm: Dict[str, float] = {}
    for k, v in base_components.items():
        long_key = key_map.get(k, k)
        norm[long_key] = float(v)

    required = [
        "E_evidence_quality",
        "R_source_reliability",
        "I_independence",
        "P_replication",
        "C_contradiction_resistance",
        "T_temporal_stability",
        "F_fundamental_laws",
        "M_methodology",
    ]
    missing = [k for k in required if k not in norm]
    if missing:
        raise ValueError(f"Missing required component(s): {missing}")

    w = weights if weights is not None else DEFAULT_WEIGHTS.copy()
    
    # ========================================================================
    # STEP 1: Apply source quality tier boosts
    # ========================================================================
    adjustment_trace = []
    source_integration_summary = {
        "sources_classified": 0,
        "tiers_represented": [],
        "component_boosts_applied": {},
    }
    
    if source_classifications:
        r_adjustments = []
        e_adjustments = []
        t_adjustments = []
        i_adjustments = []
        tiers_found = []
        
        for i, classification in enumerate(source_classifications):
            boosts = classification.get("component_boosts")
            if boosts:
                if isinstance(boosts, dict):
                    r_adj = boosts.get("r_source_reliability", 0)
                    e_adj = boosts.get("e_evidence_quality", 0)
                    t_adj = boosts.get("t_temporal_stability", 0)
                    i_adj = boosts.get("i_independence", 0)
                else:
                    # ComponentBoosts dataclass
                    r_adj = boosts.r_source_reliability
                    e_adj = boosts.e_evidence_quality
                    t_adj = boosts.t_temporal_stability
                    i_adj = boosts.i_independence
                
                r_adjustments.append(r_adj)
                e_adjustments.append(e_adj)
                t_adjustments.append(t_adj)
                i_adjustments.append(i_adj)
                
                tier = classification.get("quality_tier", "unknown")
                tiers_found.append(str(tier))
                
                adjustment_trace.append(
                    f"Source {i+1}: {classification.get('classification_rationale', 'unclassified')} "
                    f"→ R+{r_adj:.1f}, E+{e_adj:.1f}, T+{t_adj:.1f}, I+{i_adj:.1f}"
                )
        
        # Average boosts
        avg_r_boost = sum(r_adjustments) / len(r_adjustments) if r_adjustments else 0
        avg_e_boost = sum(e_adjustments) / len(e_adjustments) if e_adjustments else 0
        avg_t_boost = sum(t_adjustments) / len(t_adjustments) if t_adjustments else 0
        avg_i_boost = sum(i_adjustments) / len(i_adjustments) if i_adjustments else 0
        
        # Apply boosts with clamping
        norm["R_source_reliability"] = _clamp(norm["R_source_reliability"] + avg_r_boost)
        norm["E_evidence_quality"] = _clamp(norm["E_evidence_quality"] + avg_e_boost)
        norm["T_temporal_stability"] = _clamp(norm["T_temporal_stability"] + avg_t_boost)
        norm["I_independence"] = _clamp(norm["I_independence"] + avg_i_boost)
        
        source_integration_summary["sources_classified"] = len(source_classifications)
        source_integration_summary["tiers_represented"] = list(set(tiers_found))
        source_integration_summary["component_boosts_applied"] = {
            "R_source_reliability": round(avg_r_boost, 1),
            "E_evidence_quality": round(avg_e_boost, 1),
            "T_temporal_stability": round(avg_t_boost, 1),
            "I_independence": round(avg_i_boost, 1),
        }
        
        adjustment_trace.append(
            f"Applied average boosts: R+{avg_r_boost:.1f}, E+{avg_e_boost:.1f}, "
            f"T+{avg_t_boost:.1f}, I+{avg_i_boost:.1f}"
        )
    
    # ========================================================================
    # STEP 2: Apply reasoning audit penalties
    # ========================================================================
    reasoning_audit_integration = {
        "audit_applied": False,
        "fallacies_detected": [],
        "integrity_penalty": 0,
    }
    
    if reasoning_audit:
        reasoning_audit_integration["audit_applied"] = True
        fallacies = reasoning_audit.get("fallacies_detected", [])
        reasoning_audit_integration["fallacies_detected"] = fallacies
        
        # Penalty: each fallacy reduces E and R components
        fallacy_penalty_e = len(fallacies) * 5  # -5 per fallacy to E
        fallacy_penalty_r = len(fallacies) * 3  # -3 per fallacy to R
        
        if reasoning_audit.get("single_source_dependence", False):
            fallacy_penalty_i = 15  # Heavy penalty to independence
        else:
            fallacy_penalty_i = 0
        
        norm["E_evidence_quality"] = _clamp(norm["E_evidence_quality"] - fallacy_penalty_e)
        norm["R_source_reliability"] = _clamp(norm["R_source_reliability"] - fallacy_penalty_r)
        norm["I_independence"] = _clamp(norm["I_independence"] - fallacy_penalty_i)
        
        reasoning_audit_integration["integrity_penalty"] = (
            round(fallacy_penalty_e, 1),
            round(fallacy_penalty_r, 1),
            round(fallacy_penalty_i, 1),
        )
        
        adjustment_trace.append(
            f"Reasoning audit penalties: E-{fallacy_penalty_e}, R-{fallacy_penalty_r}, I-{fallacy_penalty_i}"
        )
    
    # ========================================================================
    # STEP 3: Compute weighted average ASC (unchanged from v1.0)
    # ========================================================================
    weighted_sum = 0.0
    weight_total = 0.0
    for key, weight in w.items():
        if key not in norm:
            continue
        weighted_sum += norm[key] * weight
        weight_total += weight

    if weight_total <= 0:
        raise ValueError("Sum of weights must be positive")

    base = weighted_sum / weight_total

    # Apply F as signed adjustment
    f_adj = norm["F_fundamental_laws"] * F_SCALE
    asc = _clamp(base + f_adj)

    # ========================================================================
    # STEP 4: Compute confidence band
    # ========================================================================
    vals = [norm[k] for k in required if k != "F_fundamental_laws"]
    mean = sum(vals) / len(vals)
    variance = sum((x - mean) ** 2 for x in vals) / len(vals)
    std = math.sqrt(variance)

    if asc >= 85 and std < 12:
        confidence = "VERY_HIGH"
    elif asc >= 70 and std < 18:
        confidence = "HIGH"
    elif asc >= 50:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # ========================================================================
    # STEP 5: Build result
    # ========================================================================
    result: Dict[str, Any] = {
        "asc_score": round(asc, 2),
        "confidence": confidence,
        "components": {
            "E_evidence_quality": round(norm["E_evidence_quality"], 2),
            "R_source_reliability": round(norm["R_source_reliability"], 2),
            "I_independence": round(norm["I_independence"], 2),
            "P_replication": round(norm["P_replication"], 2),
            "C_contradiction_resistance": round(norm["C_contradiction_resistance"], 2),
            "T_temporal_stability": round(norm["T_temporal_stability"], 2),
            "F_fundamental_laws": round(norm["F_fundamental_laws"], 2),
            "M_methodology": round(norm["M_methodology"], 2),
        },
        "version": ASC_VERSION,
        "source_integration_summary": source_integration_summary,
        "reasoning_audit_integration": reasoning_audit_integration,
    }

    if include_audit_trace:
        result["adjustment_trace"] = adjustment_trace

    if include_sensitivity:
        result["sensitivity_note"] = (
            f"ASC {asc:.1f} under integrated model v{ASC_VERSION} with source quality "
            f"and reasoning audit. Component std≈{std:.1f}. "
            "Re-run with alternative weights or different source classifications for robustness."
        )

    return result


def validate_claim_object(claim: Dict[str, Any]) -> bool:
    """
    Validate claim object against expected schema.
    """
    required_top = ["claim", "type", "status", "argument_strength", "fundamental_gate"]
    for k in required_top:
        if k not in claim:
            return False

    asc = claim.get("argument_strength", {})
    if "asc_score" not in asc or "components" not in asc or "version" not in asc:
        return False

    comps = asc.get("components", {})
    needed = [
        "E_evidence_quality", "R_source_reliability", "I_independence",
        "P_replication", "C_contradiction_resistance", "T_temporal_stability",
        "F_fundamental_laws", "M_methodology"
    ]
    return all(k in comps for k in needed)


if __name__ == "__main__":
    # Example: Compute ASC with source quality and reasoning audit
    example_components = {
        "E": 70,  # Start with moderate evidence quality
        "R": 65,  # Moderate source reliability
        "I": 60,  # Some independence concerns
        "P": 50,  # Limited replication
        "C": 75,  # Some contradiction resistance
        "T": 80,  # Temporal stability present
        "F": 0,   # No fundamental conflicts
        "M": 72,  # Reasonable methodology
    }
    
    example_sources = [
        {
            "quality_tier": "tier_1_primary",
            "classification_rationale": "Peer-reviewed empirical with consensus",
            "component_boosts": {
                "r_source_reliability": 25,
                "e_evidence_quality": 22,
                "t_temporal_stability": 15,
                "i_independence": 10,
            },
            "critical_flags": [],
        },
        {
            "quality_tier": "tier_2_consensus",
            "classification_rationale": "Advanced curriculum knowledge",
            "component_boosts": {
                "r_source_reliability": 18,
                "e_evidence_quality": 16,
                "t_temporal_stability": 10,
                "i_independence": 6,
            },
            "critical_flags": [],
        },
    ]
    
    example_audit = {
        "fallacies_detected": [],
        "single_source_dependence": False,
        "source_tier_analysis": {"tier_1_count": 1, "tier_2_count": 1},
    }
    
    result = compute_asc_integrated(
        example_components,
        source_classifications=example_sources,
        reasoning_audit=example_audit,
        include_audit_trace=True,
    )
    
    print("Integrated ASC Result (v2.0):")
    print(f"  ASC Score: {result['asc_score']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Components:")
    for k, v in result['components'].items():
        print(f"    {k}: {v}")
    print(f"  Sources classified: {result['source_integration_summary']['sources_classified']}")
    print(f"  Tiers used: {result['source_integration_summary']['tiers_represented']}")
    print(f"  Reasoning audit applied: {result['reasoning_audit_integration']['audit_applied']}")
    print(f"\n  Adjustment trace:")
    for line in result.get('adjustment_trace', []):
        print(f"    {line}")
