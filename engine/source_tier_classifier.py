"""
SAFE Engine — Source Quality Tier Classifier

Maps evidence sources to reliability tiers based on:
1. Peer-review consensus formation (not just publication date)
2. University curriculum knowledge (by complexity level)
3. Scientific publication consensus
4. News articles (with clear references)

Outputs ASC component influence boosts for R, E, T, I.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass


class SourceType(Enum):
    """Source type categories matching hierarchical priority"""
    PEER_REVIEWED_EMPIRICAL = "peer_reviewed_empirical"
    PEER_REVIEWED_THEORETICAL = "peer_reviewed_theoretical"
    SYSTEMATIC_REVIEW_META = "systematic_review_meta_analysis"
    CONSENSUS_STATEMENT = "consensus_statement"
    UNIVERSITY_CURRICULUM = "university_curriculum"
    OFFICIAL_STATISTIC = "official_statistic"
    INSTITUTIONAL_REPORT = "institutional_report"
    PREPRINT = "preprint"
    NEWS_CITED = "news_cited"
    GREY_LITERATURE = "grey_literature"
    BLOG_OPINION = "blog_or_opinion"


class QualityTier(Enum):
    """Hierarchical reliability tier"""
    TIER_1_PRIMARY = "tier_1_primary"           # Highest confidence
    TIER_2_CONSENSUS = "tier_2_consensus"       # Peer-review consensus formed
    TIER_3_SECONDARY = "tier_3_secondary"       # Derivative or secondary
    TIER_4_DERIVATIVE = "tier_4_derivative"     # Low-reliability derivative


class VenueTier(Enum):
    """Journal/venue quality classification"""
    TOP_5_PERCENT = "top_5_percent"
    TOP_10_PERCENT = "top_10_percent"
    TOP_25_PERCENT = "top_25_percent"
    PEER_REVIEWED_STANDARD = "peer_reviewed_standard"
    NON_PEER_REVIEWED = "non_peer_reviewed"


class CurriculumLevel(Enum):
    """University curriculum complexity"""
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED_UNDERGRADUATE = "advanced_undergraduate"
    GRADUATE_MASTERS = "graduate_masters"
    DOCTORAL = "doctoral"


@dataclass
class ComponentBoosts:
    """ASC component influence adjustments from source classification"""
    r_source_reliability: float  # -20 to +30
    e_evidence_quality: float    # -20 to +30
    t_temporal_stability: float  # -20 to +30
    i_independence: float        # -10 to +20


# TIER 1: Primary research with peer-review consensus
TIER_1_RULES = {
    "peer_reviewed_empirical": {
        "conditions": {
            "is_peer_reviewed": True,
            "venue_tier": ["top_5_percent", "top_10_percent", "top_25_percent"],
            # replication_count is NOT a gate here -- see REPLICATION_BONUS_PER_UNIT.
            # A top-venue peer-reviewed paper qualifies for Tier 1 on venue rigor alone;
            # replication_count (if any) adds incremental weight on top.
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+25,
            e_evidence_quality=+22,
            t_temporal_stability=+15,
            i_independence=+10,
        ),
        "description": "Peer-reviewed empirical in a top-tier venue",
    },
    "systematic_review_meta": {
        "conditions": {
            "is_peer_reviewed": True,
            "aggregates_multiple_studies_min": 3,
            "venue_tier": ["top_5_percent", "top_10_percent", "top_25_percent"],
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+30,  # Highest: aggregates across studies
            e_evidence_quality=+28,
            t_temporal_stability=+20,
            i_independence=+15,
        ),
        "description": "Systematic review/meta-analysis (highest evidence tier)",
    },
    "consensus_statement": {
        "conditions": {
            "represents_field_consensus": True,
            "multiple_institutions_endorsing_min": 3,
            "published_by": ["professional_society", "research_institution"],
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+28,
            e_evidence_quality=+25,
            t_temporal_stability=+22,
            i_independence=+12,
        ),
        "description": "Formal consensus statement from peer group",
    },
}

# TIER 2: Established peer-review with active validation
TIER_2_RULES = {
    "peer_reviewed_standard": {
        "conditions": {
            "is_peer_reviewed": True,
            "venue_tier": ["peer_reviewed_standard"],
            "replication_count_min": 0,
            "citation_trajectory": "stable",
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+16,
            e_evidence_quality=+14,
            t_temporal_stability=+8,
            i_independence=+5,
        ),
        "description": "Peer-reviewed in standard venue, not top-tier",
    },
    "university_curriculum_advanced": {
        "conditions": {
            "curriculum_level": ["advanced_undergraduate", "graduate_masters", "doctoral"],
            "accredited_institution": True,
            "represents_established_knowledge": True,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+18,
            e_evidence_quality=+16,
            t_temporal_stability=+10,
            i_independence=+6,
        ),
        "description": "Advanced curriculum knowledge from accredited institution",
    },
    "official_statistic": {
        "conditions": {
            "published_by": ["government", "international_organization", "statistical_bureau"],
            "methodology_transparent": True,
            "contradictions_count": 0,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+20,
            e_evidence_quality=+18,
            t_temporal_stability=+12,
            i_independence=+8,
        ),
        "description": "Official statistic with transparent methodology",
    },
}

# TIER 3: Secondary sources, news, or lower-confidence primary
TIER_3_RULES = {
    "preprint": {
        "conditions": {
            "peer_reviewed": False,
            "published_on": ["arxiv", "biorxiv", "medrxiv"],
            "later_published_in_peer_review": False,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+8,
            e_evidence_quality=+6,
            t_temporal_stability=-5,
            i_independence=+2,
        ),
        "description": "Preprint (not yet peer-reviewed)",
    },
    "news_cited_quality": {
        "conditions": {
            "publication_tier": ["flagship_reputation", "established_mainstream"],
            "cited_source_count_min": 2,
            "cited_source_quality_includes": ["peer_reviewed_study", "official_statistic"],
            "retraction_or_correction": False,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+12,
            e_evidence_quality=+10,
            t_temporal_stability=+3,
            i_independence=-5,  # Derivative of primary source
        ),
        "description": "News article from reputable source with multiple citations",
    },
    "university_curriculum_foundational": {
        "conditions": {
            "curriculum_level": ["foundational", "intermediate"],
            "accredited_institution": True,
            "knowledge_widely_accepted": True,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=+10,
            e_evidence_quality=+8,
            t_temporal_stability=+5,
            i_independence=-3,
        ),
        "description": "Foundational curriculum knowledge (less specificity)",
    },
}

# TIER 4: Derivative, low-confidence, or unverified
TIER_4_RULES = {
    "news_low_citation": {
        "conditions": {
            "cited_source_count_max": 1,
            "cited_source_quality_includes": ["press_release", "unnamed_source"],
        },
        "boosts": ComponentBoosts(
            r_source_reliability=-8,
            e_evidence_quality=-10,
            t_temporal_stability=-12,
            i_independence=-15,
        ),
        "description": "News with minimal or low-quality citations",
    },
    "blog_opinion": {
        "conditions": {
            "peer_reviewed": False,
            "published_by": ["blog", "opinion_column", "personal_website"],
        },
        "boosts": ComponentBoosts(
            r_source_reliability=-15,
            e_evidence_quality=-18,
            t_temporal_stability=-10,
            i_independence=-20,
        ),
        "description": "Blog, opinion, or unvetted personal source",
    },
    "derivative_repost": {
        "conditions": {
            "is_primary": False,
            "lineage_distance_from_primary_min": 2,
            "adds_no_new_analysis": True,
        },
        "boosts": ComponentBoosts(
            r_source_reliability=-12,
            e_evidence_quality=-10,
            t_temporal_stability=-8,
            i_independence=-20,
        ),
        "description": "Derivative repost of primary source (high independence penalty)",
    },
}


# Replication/corroboration is treated as incremental weight on top of a source's
# base tier boosts, not as a gate for tier membership. Each independent replication
# lands hardest on independence (a second team confirming the result is the clearest
# independence signal), then evidence quality, then reliability; temporal stability
# barely moves per-replication since that's driven by consensus formation over time.
# Diminishing returns: only the first REPLICATION_BONUS_MAX_COUNT replications count.
REPLICATION_BONUS_PER_UNIT = ComponentBoosts(
    r_source_reliability=1.5,
    e_evidence_quality=2.0,
    t_temporal_stability=0.5,
    i_independence=3.0,
)
REPLICATION_BONUS_MAX_COUNT = 4

# Valid range for each ASC component boost (see ComponentBoosts docstring).
_BOOST_RANGES = {
    "r_source_reliability": (-20, 30),
    "e_evidence_quality": (-20, 30),
    "t_temporal_stability": (-20, 30),
    "i_independence": (-10, 20),
}


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _with_replication_bonus(boosts: ComponentBoosts, replication_count: int) -> ComponentBoosts:
    """Add replication/corroboration weight to a base tier boost, clamped to valid ranges."""
    n = max(0, min(replication_count, REPLICATION_BONUS_MAX_COUNT))
    if n == 0:
        return boosts
    return ComponentBoosts(
        r_source_reliability=_clamp(
            boosts.r_source_reliability + n * REPLICATION_BONUS_PER_UNIT.r_source_reliability,
            *_BOOST_RANGES["r_source_reliability"],
        ),
        e_evidence_quality=_clamp(
            boosts.e_evidence_quality + n * REPLICATION_BONUS_PER_UNIT.e_evidence_quality,
            *_BOOST_RANGES["e_evidence_quality"],
        ),
        t_temporal_stability=_clamp(
            boosts.t_temporal_stability + n * REPLICATION_BONUS_PER_UNIT.t_temporal_stability,
            *_BOOST_RANGES["t_temporal_stability"],
        ),
        i_independence=_clamp(
            boosts.i_independence + n * REPLICATION_BONUS_PER_UNIT.i_independence,
            *_BOOST_RANGES["i_independence"],
        ),
    )


def classify_source(source_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a source into tier + quality category.
    
    Parameters
    ----------
    source_metadata : dict
        Must contain at minimum:
        - source_type (from SourceType enum)
        - venue details (if peer-reviewed)
        - publication date
        - peer_review status
        - Optional: replication_count, consensus_formation_date
    
    Returns
    -------
    dict with:
        - quality_tier (TIER_1 through TIER_4)
        - classification_rationale (human-readable explanation)
        - component_boosts (ComponentBoosts)
        - critical_flags (list of warnings)
    """
    source_type = source_metadata.get("source_type")
    is_peer_reviewed = source_metadata.get("peer_review", {}).get("is_peer_reviewed", False)
    venue_tier = source_metadata.get("peer_review", {}).get("venue_tier")
    replication_count = source_metadata.get("consensus_metadata", {}).get("replication_count", 0)
    consensus_formation_date = source_metadata.get("consensus_metadata", {}).get("consensus_formation_date")
    is_primary = source_metadata.get("derivation_signal", {}).get("is_primary", True)
    contradictions = source_metadata.get("consensus_metadata", {}).get("contradictions_count", 0)
    
    critical_flags = source_metadata.get("critical_flags", [])
    
    # TIER 1 classification
    if source_type in ["systematic_review_meta_analysis", "consensus_statement"]:
        if is_peer_reviewed and venue_tier in ["top_5_percent", "top_10_percent", "top_25_percent"]:
            return {
                "quality_tier": QualityTier.TIER_1_PRIMARY,
                "classification_rationale": TIER_1_RULES.get(source_type, {}).get("description", "Tier 1 primary"),
                "component_boosts": TIER_1_RULES[source_type]["boosts"],
                "critical_flags": critical_flags,
            }
    
    if source_type == "peer_reviewed_empirical":
        if is_peer_reviewed and venue_tier in ["top_5_percent", "top_10_percent", "top_25_percent"] and is_primary is not False:
            rationale = TIER_1_RULES["peer_reviewed_empirical"]["description"]
            if replication_count >= 1:
                rationale += (
                    f" (+{min(replication_count, REPLICATION_BONUS_MAX_COUNT)} independent "
                    f"replication{'s' if replication_count != 1 else ''} weighted in)"
                )
            return {
                "quality_tier": QualityTier.TIER_1_PRIMARY,
                "classification_rationale": rationale,
                "component_boosts": _with_replication_bonus(
                    TIER_1_RULES["peer_reviewed_empirical"]["boosts"], replication_count
                ),
                "critical_flags": critical_flags,
            }
    
    # TIER 2 classification
    if is_peer_reviewed and venue_tier == "peer_reviewed_standard":
        return {
            "quality_tier": QualityTier.TIER_2_CONSENSUS,
            "classification_rationale": TIER_2_RULES["peer_reviewed_standard"]["description"],
            "component_boosts": TIER_2_RULES["peer_reviewed_standard"]["boosts"],
            "critical_flags": critical_flags,
        }
    
    if source_type == "university_curriculum":
        curriculum_level = source_metadata.get("academic_curriculum_metadata", {}).get("curriculum_level")
        if curriculum_level in ["advanced_undergraduate", "graduate_masters", "doctoral"]:
            return {
                "quality_tier": QualityTier.TIER_2_CONSENSUS,
                "classification_rationale": TIER_2_RULES["university_curriculum_advanced"]["description"],
                "component_boosts": TIER_2_RULES["university_curriculum_advanced"]["boosts"],
                "critical_flags": critical_flags,
            }
    
    if source_type == "official_statistic":
        rationale = TIER_2_RULES["official_statistic"]["description"]
        if replication_count >= 1:
            rationale += (
                f" (+{min(replication_count, REPLICATION_BONUS_MAX_COUNT)} independent "
                f"corroboration{'s' if replication_count != 1 else ''} weighted in)"
            )
        return {
            "quality_tier": QualityTier.TIER_2_CONSENSUS,
            "classification_rationale": rationale,
            "component_boosts": _with_replication_bonus(
                TIER_2_RULES["official_statistic"]["boosts"], replication_count
            ),
            "critical_flags": critical_flags,
        }
    
    # TIER 3 classification
    if source_type == "preprint":
        return {
            "quality_tier": QualityTier.TIER_3_SECONDARY,
            "classification_rationale": TIER_3_RULES["preprint"]["description"],
            "component_boosts": TIER_3_RULES["preprint"]["boosts"],
            "critical_flags": critical_flags,
        }
    
    if source_type == "news_cited":
        cited_count = source_metadata.get("news_metadata", {}).get("cited_source_count", 0)
        if cited_count >= 2:
            return {
                "quality_tier": QualityTier.TIER_3_SECONDARY,
                "classification_rationale": TIER_3_RULES["news_cited_quality"]["description"],
                "component_boosts": TIER_3_RULES["news_cited_quality"]["boosts"],
                "critical_flags": critical_flags,
            }
    
    # TIER 4 classification (fallback for low-confidence sources)
    if source_type == "blog_or_opinion":
        return {
            "quality_tier": QualityTier.TIER_4_DERIVATIVE,
            "classification_rationale": TIER_4_RULES["blog_opinion"]["description"],
            "component_boosts": TIER_4_RULES["blog_opinion"]["boosts"],
            "critical_flags": critical_flags,
        }
    
    if not is_primary and is_primary is not None:
        return {
            "quality_tier": QualityTier.TIER_4_DERIVATIVE,
            "classification_rationale": TIER_4_RULES["derivative_repost"]["description"],
            "component_boosts": TIER_4_RULES["derivative_repost"]["boosts"],
            "critical_flags": critical_flags,
        }
    
    # Default: unclassified → tier 3
    return {
        "quality_tier": QualityTier.TIER_3_SECONDARY,
        "classification_rationale": "Unclassified source (defaulting to Tier 3)",
        "component_boosts": ComponentBoosts(
            r_source_reliability=0,
            e_evidence_quality=0,
            t_temporal_stability=0,
            i_independence=0,
        ),
        "critical_flags": critical_flags + ["unclassified_source"],
    }


def apply_component_boosts_to_asc(
    base_components: Dict[str, float],
    source_classifications: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Adjust ASC components based on source quality classifications.
    
    For each source, apply its component boosts. Average across multiple sources,
    clamping to valid ranges.
    
    Parameters
    ----------
    base_components : dict
        Original ASC component scores (E, R, I, P, C, T, F, M)
    
    source_classifications : list
        List of classification results from classify_source()
    
    Returns
    -------
    dict with:
        - adjusted_components
        - boost_trace (what was adjusted and why)
        - dominant_tier (most reliable source used)
    """
    if not source_classifications:
        return {
            "adjusted_components": base_components,
            "boost_trace": [],
            "dominant_tier": None,
        }
    
    # Accumulate boosts
    r_adjustments = []
    e_adjustments = []
    t_adjustments = []
    i_adjustments = []
    tiers_found = []
    
    for classification in source_classifications:
        boosts: ComponentBoosts = classification.get("component_boosts")
        if boosts:
            r_adjustments.append(boosts.r_source_reliability)
            e_adjustments.append(boosts.e_evidence_quality)
            t_adjustments.append(boosts.t_temporal_stability)
            i_adjustments.append(boosts.i_independence)
            tiers_found.append(classification.get("quality_tier"))
    
    # Average boosts (favor tier 1 if mixed)
    avg_r = sum(r_adjustments) / len(r_adjustments) if r_adjustments else 0
    avg_e = sum(e_adjustments) / len(e_adjustments) if e_adjustments else 0
    avg_t = sum(t_adjustments) / len(t_adjustments) if t_adjustments else 0
    avg_i = sum(i_adjustments) / len(i_adjustments) if i_adjustments else 0
    
    # Determine dominant tier
    tier_priority = {
        QualityTier.TIER_1_PRIMARY: 4,
        QualityTier.TIER_2_CONSENSUS: 3,
        QualityTier.TIER_3_SECONDARY: 2,
        QualityTier.TIER_4_DERIVATIVE: 1,
    }
    dominant_tier = max(tiers_found, key=lambda t: tier_priority.get(t, 0)) if tiers_found else None
    
    # Apply boosts with clamping
    def clamp_component(base: float, adj: float) -> float:
        return max(0, min(100, base + adj))
    
    adjusted = {
        "E_evidence_quality": clamp_component(base_components.get("E_evidence_quality", 0), avg_e),
        "R_source_reliability": clamp_component(base_components.get("R_source_reliability", 0), avg_r),
        "I_independence": clamp_component(base_components.get("I_independence", 0), avg_i),
        "T_temporal_stability": clamp_component(base_components.get("T_temporal_stability", 0), avg_t),
        "P_replication": base_components.get("P_replication", 0),  # Not directly adjusted by source tier
        "C_contradiction_resistance": base_components.get("C_contradiction_resistance", 0),  # Not directly adjusted
        "F_fundamental_laws": base_components.get("F_fundamental_laws", 0),  # Not directly adjusted
        "M_methodology": base_components.get("M_methodology", 0),  # Not directly adjusted (handled separately)
    }
    
    boost_trace = [
        f"R (source reliability): +{avg_r:.1f} → {adjusted['R_source_reliability']:.0f}",
        f"E (evidence quality): +{avg_e:.1f} → {adjusted['E_evidence_quality']:.0f}",
        f"T (temporal stability): +{avg_t:.1f} → {adjusted['T_temporal_stability']:.0f}",
        f"I (independence): +{avg_i:.1f} → {adjusted['I_independence']:.0f}",
    ]
    
    return {
        "adjusted_components": adjusted,
        "boost_trace": boost_trace,
        "dominant_tier": dominant_tier,
    }


if __name__ == "__main__":
    # Example usage
    example_source = {
        "source_type": "peer_reviewed_empirical",
        "peer_review": {
            "is_peer_reviewed": True,
            "venue_tier": "top_10_percent",
        },
        "consensus_metadata": {
            "replication_count": 2,
            "contradictions_count": 0,
        },
        "derivation_signal": {
            "is_primary": True,
        },
    }
    
    classification = classify_source(example_source)
    print("Source Classification:")
    print(f"  Tier: {classification['quality_tier'].value}")
    print(f"  Rationale: {classification['classification_rationale']}")
    print(f"  Boosts: R={classification['component_boosts'].r_source_reliability}, "
          f"E={classification['component_boosts'].e_evidence_quality}, "
          f"T={classification['component_boosts'].t_temporal_stability}, "
          f"I={classification['component_boosts'].i_independence}")
