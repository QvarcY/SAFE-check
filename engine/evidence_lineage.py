"""
SAFE Engine — Deterministic Evidence Lineage Resolution

Conservatively groups evidence items only when they share
an explicitly identifiable source identity.
"""

from __future__ import annotations

from typing import Any, Dict, List


def normalize_doi(value: str) -> str:
    """
    Normalize common DOI representations into a stable identifier.

    Examples
    --------
    10.1000/ABC.123
    https://doi.org/10.1000/abc.123
    doi:10.1000/abc.123

    all normalize to:

    10.1000/abc.123
    """
    doi = value.strip().lower()

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    )

    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
            break

    return doi.strip()


def resolve_evidence_lineages(
    evidence_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Resolve deterministic evidence lineages.

    Current conservative rule:
    - Evidence items with the same normalized DOI belong to one lineage.
    - Evidence without a DOI remains independent.

    No probabilistic or semantic inference is performed.
    """
    lineage_keys = []

    for index, item in enumerate(evidence_items):
        doi = item.get("doi")

        if doi:
            lineage_key = ("doi", normalize_doi(str(doi)))
        else:
            # Missing metadata must never cause an accidental collapse.
            lineage_key = ("item", index)

        lineage_keys.append(lineage_key)

    total_items = len(evidence_items)
    unique_lineages = len(set(lineage_keys))
    derivative_items = total_items - unique_lineages

    independence_ratio = (
        unique_lineages / total_items
        if total_items
        else 0.0
    )

    return {
        "total_items": total_items,
        "unique_lineages": unique_lineages,
        "derivative_items": derivative_items,
        "independence_ratio": independence_ratio,
    }