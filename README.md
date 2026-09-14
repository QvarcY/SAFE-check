# SAFE: Source-aware Argument Fidelity & Evidence

> An open, vendor-neutral protocol for scoring and auditing AI-generated claims against source hierarchies and reasoning quality.

**Current Version:** 2.0.0 (Source Hierarchy Integration)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-13%2F13%20passing-green.svg)](#testing)
[![License](https://img.shields.io/badge/license-Unlicense-blue.svg)](LICENSE)

---

## 🎯 Overview

SAFE treats model output as **claims**, never as evidence. Every substantive claim is extracted, classified, provenance-tracked, scored against a transparent source hierarchy, audited for reasoning quality, and returned as a machine-readable object that any model or human can consume.

This repository implements **Version 2.0**, which adds comprehensive source quality tier integration to the Argument Strength Coefficient (ASC) scoring engine:

- **Source Classification** (Tier 1-4 based on peer-review consensus, venue quality, replication)
- **Reasoning Audit** (detects 6 types of hierarchy violations: tier inversion, cherry-picking, single-source dependence, etc.)
- **Dynamic Weighting** (ASC component weights adjust based on source composition and reasoning quality)
- **Integrated Scoring** (source boosts + reasoning penalties applied transparently)

### Why SAFE?

**The Problem:** LLM outputs are often treated as authoritative even when unsupported by evidence. Citation counts create false consensus. Preliminary research dominates established knowledge.

**The Solution:** SAFE enforces a source hierarchy that mirrors scientific practice:

1. **Peer-reviewed academic papers** with peer-review consensus formation date (not just publication date)
2. **University curriculum knowledge** by complexity level (foundational → doctoral)
3. **Scientific consensus statements** (aggregates across peer-reviewed evidence)
4. **News articles** graded by editorial standards and citation quality

Every claim is scored transparently—no "black box," no ethical inflation of scores, full audit trail.

---

## ✨ Key Features

### Source Quality Hierarchy

| Tier | Category | Reliability | Examples |
|------|----------|------------|----------|
| **1** | Primary peer-reviewed consensus | Very High | Peer-reviewed empirical + replication, systematic reviews, consensus statements |
| **2** | Established knowledge | High | Standard-venue peer-review, advanced curriculum, official statistics |
| **3** | Secondary sources | Medium | Preprints, mainstream news (2+ citations), foundational curriculum |
| **4** | Derivative/Opinion | Low | Blog posts, minimal-citation news, reposts |

### Reasoning Quality Audit

Detects and flags:
- **Tier Inversion** — Lower-tier sources outweigh higher-tier
- **Single-Source Dependence** — Especially critical for Tier 4
- **Cherry-Picking** — Ignoring high-tier contradictions
- **Appeal to Authority** — Prestige without methodological rigor
- **Base-Rate Neglect** — Wrong weighting across tiers
- **Consensus Contradiction** — Disagreeing with Tier 1 consensus without justification

### Dynamic ASC Weighting

Component weights (R, E, I, P, C, T, M) adjust automatically based on:
- **Tier distribution** (Tier 1-heavy → boost R/E; Tier 3/4-heavy → boost I)
- **Reasoning fallacies** (more fallacies → boost E)
- **Independence signals** (low independence → boost I)
- **Replication evidence** (high replication → boost P)
- **Contradiction counts** (high contradictions → boost C)

### Transparency by Design

Every ASC result includes:
- Complete component breakdown (8 scored dimensions)
- Source integration summary (tiers represented, boosts applied)
- Reasoning audit findings (fallacies, chain integrity, critical issues)
- Adjustment trace (what changed and why)
- Weight explanation (why weights were adjusted)

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/stirnas/SAFE.git
cd SAFE

# No external dependencies required
# Python 3.9+ only
python --version  # Verify 3.9 or later
```

### Basic Usage

```python
from engine.source_tier_classifier import classify_source
from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext
from engine.scoring_integrated import compute_asc_integrated

# 1. Classify evidence source
evidence = {
    "source_type": "peer_reviewed_empirical",
    "peer_review": {
        "is_peer_reviewed": True,
        "venue_tier": "top_10_percent",
    },
    "consensus_metadata": {
        "publication_date": "2023-06-01",
        "consensus_formation_date": "2024-01-01",  # When consensus formed
        "replication_count": 2,
    },
    "derivation_signal": {"is_primary": True},
}

classification = classify_source(evidence)
print(f"Tier: {classification['quality_tier']}")
# Output: tier_1_primary

# 2. Audit reasoning
claim = "Peer-reviewed studies support X"
audit = analyze_source_hierarchy_in_reasoning(claim, [evidence], [classification])
print(f"Chain Integrity: {audit['reasoning_chain_integrity']}/100")
# Output: Chain Integrity: 95/100

# 3. Adjust weights
context = WeightAdjustmentContext(
    source_tier_distribution={"tier_1": 1, "tier_2": 0, "tier_3": 0, "tier_4": 0},
    reasoning_fallacies_count=0,
    single_source_dependence=False,
    independence_score=85,
    replication_count=2,
    contradiction_count=0,
)
weights = compute_weight_adjustments(context)

# 4. Score with integrated ASC
result = compute_asc_integrated(
    base_components={"E": 75, "R": 70, "I": 65, "P": 60, "C": 75, "T": 75, "F": 0, "M": 72},
    source_classifications=[classification],
    reasoning_audit=audit,
    weights=weights,
)

print(f"ASC: {result['asc_score']:.1f}/100 ({result['confidence']})")
print(result.get('sensitivity_note'))
# Output: ASC: 82.5/100 (VERY_HIGH)
#         ASC 82.5 under integrated model v2.0.0 with source quality and reasoning audit...
```

### End-to-End Pipeline

```python
from engine.orchestrator import SafeEvaluationRequest, evaluate_claim_end_to_end
from engine.source_tier_classifier import classify_source
from engine.reasoning_audit_enhanced import analyze_source_hierarchy_in_reasoning
from engine.component_weights import compute_weight_adjustments, WeightAdjustmentContext
from engine.scoring_integrated import compute_asc_integrated

request = SafeEvaluationRequest(
    claim="Climate change is anthropogenic",
    claim_type="empirical_causal",
    evidence_items=[...],
    base_asc_components={"E": 75, "R": 70, "I": 65, "P": 60, "C": 75, "T": 75, "F": 0, "M": 72},
)

result = evaluate_claim_end_to_end(
    request,
    source_classifier_fn=classify_source,
    reasoning_audit_fn=analyze_source_hierarchy_in_reasoning,
    weight_adjuster_fn=lambda ctx: compute_weight_adjustments(WeightAdjustmentContext(**ctx)),
    asc_scorer_fn=compute_asc_integrated,
)

print(f"Status: {result.status}")
print(f"ASC: {result.final_asc_score}")
print(result.summary)
```

---

## 📁 Repository Structure

```
SAFE/
├── README.md                           # This file
├── LICENSE                             # Unlicense (public domain)
├── INDEX.md                            # Deliverables overview
├── QUICKSTART.md                       # Practical guide with examples
├── IMPLEMENTATION_SUMMARY.md           # Architecture and design decisions
│
├── protocol/                           # JSON schemas (single source of truth)
│   ├── claims.schema.json
│   ├── evidence.schema.json
│   ├── audit.schema.json
│   └── source_quality_classifier.schema.json  [NEW]
│
├── engine/                             # Core scoring & pipeline
│   ├── __init__.py
│   ├── claim_extractor.py
│   ├── provenance.py
│   ├── scoring.py                      # Original ASC v1.0
│   ├── physics_gate.py
│   ├── source_tier_classifier.py       [NEW] Source hierarchy
│   ├── reasoning_audit_enhanced.py     [NEW] Reasoning quality audit
│   ├── component_weights.py            [NEW] Dynamic weight adjustment
│   ├── scoring_integrated.py           [NEW] Integrated ASC v2.0
│   └── orchestrator.py                 [NEW] Pipeline coordination
│
├── adapters/                           # Model integration layers
│   ├── grok/
│   ├── openai/
│   ├── gemini/
│   ├── anthropic/
│   └── generic_api/
│
├── sources/                            # Evidence fetchers
│   ├── scholarly/
│   ├── statistics/
│   ├── biomedical/
│   ├── retractions/
│   └── general_web/
│
├── docs/                               # Extended documentation
│   ├── architecture/
│   ├── scoring/
│   └── SOURCE_HIERARCHY_IMPLEMENTATION.md  [NEW] Complete reference
│
├── benchmarks/                         # Test suites & epistemic stress tests
│   ├── hallucination/
│   ├── contradiction/
│   ├── misinformation/
│   ├── physics/
│   └── ethical_reasoning/
│
├── web/                                # Duda-compatible web runtime
│   ├── safe.js
│   └── embed.html
│
├── example_integration.py              [NEW] Runnable end-to-end example
├── test_suite.py                       [NEW] 13 comprehensive tests
└── .github/
    └── workflows/
        └── python-package.yml          # CI/CD
```

---

## 🏗️ Architecture

### Component Hierarchy

```
Raw Claims/Evidence
    │
    ├─→ Claim Extraction & Typing
    │
    ├─→ Source Classification [NEW]
    │   ├─ Tier 1-4 assignment
    │   ├─ Component boost calculation
    │   └─ Derivation tracking
    │
    ├─→ Reasoning Audit [NEW]
    │   ├─ Fallacy detection (6 types)
    │   ├─ Tier hierarchy validation
    │   └─ Chain integrity scoring
    │
    ├─→ Evidence Provenance Graph
    │   └─ Independence/lineage analysis
    │
    ├─→ Weight Adjustment [NEW]
    │   ├─ Tier distribution analysis
    │   ├─ Reasoning quality assessment
    │   └─ Context-sensitive weighting
    │
    ├─→ Integrated ASC Scoring [NEW]
    │   ├─ Apply source boosts
    │   ├─ Apply reasoning penalties
    │   ├─ Weighted average calculation
    │   ├─ F (fundamental laws) gate
    │   └─ Confidence assignment
    │
    └─→ Machine-Readable Output
        ├─ ASC score (0-100)
        ├─ Component breakdown
        ├─ Source integration summary
        ├─ Reasoning audit findings
        └─ Complete audit trail
```

### ASC Components

| Code | Name | Min | Max | Notes |
|------|------|-----|-----|-------|
| E | Evidence Quality | 0 | 100 | Strength, directness, relevance of supporting data |
| R | Source Reliability | 0 | 100 | Venue quality, peer-review status, track record |
| I | Independence | 0 | 100 | # of independent primary lineages (not reposts) |
| P | Replication | 0 | 100 | Existence and quality of independent replications |
| C | Contradiction Resistance | 0 | 100 | How well claim survives high-quality contradictions |
| T | Temporal Stability | 0 | 100 | Consistency of evidence base over time |
| F | Fundamental Laws | -20 | +20 | Consistency with repeatedly validated constraints |
| M | Methodology | 0 | 100 | Soundness of methods used to generate evidence |

**ASC** = weighted average of E, R, I, P, C, T, M (normalized 0-100) + F adjustment

---

## 📊 Source Tiers

### Tier 1 (Primary) — Highest Confidence

**Includes:**
- Peer-reviewed empirical studies with ≥1 independent replication
- Systematic reviews / meta-analyses (top-5%, top-10%, top-25% venues)
- Formal consensus statements (multiple institutions, peer-reviewed)

**Component Boosts:**
- R: +25-30 (source reliability)
- E: +22-28 (evidence quality)
- T: +15-20 (temporal stability)
- I: +10-15 (independence)

**Example:** Nature Climate Change empirical study with 2 independent replications

### Tier 2 (Consensus) — Established Knowledge

**Includes:**
- Peer-reviewed studies (standard venues, not top-tier)
- Advanced university curriculum (graduate masters, doctoral level)
- Official statistics with transparent methodology

**Component Boosts:**
- R: +10-20
- E: +8-18
- T: +5-12
- I: -3 to +8

**Example:** Graduate-level climate science textbook from accredited research university

### Tier 3 (Secondary) — Lower Confidence

**Includes:**
- Preprints (not yet peer-reviewed)
- News articles (≥2 quality citations, reputable outlet)
- Foundational curriculum (undergraduate level)

**Component Boosts:**
- R: -5 to +12
- E: -10 to +10
- T: -12 to +3
- I: -15 to +2

**Example:** Guardian article citing multiple peer-reviewed studies

### Tier 4 (Derivative) — Lowest Confidence

**Includes:**
- Blog posts, opinion columns, personal websites
- News with ≤1 citation or unnamed sources
- Derivative reposts of primary studies

**Component Boosts:**
- R: -8 to -15 (source reliability penalty)
- E: -10 to -18 (evidence quality penalty)
- T: -8 to -12 (temporal stability penalty)
- I: -15 to -20 (independence penalty for reposts)

**Example:** Opinion blog post about climate research with no citations

---

## 🧪 Testing

### Run Full Test Suite

```bash
python test_suite.py

# Expected output:
# ✓ Test 1.1 PASSED: Tier 1 (peer-reviewed empirical) classified correctly
# ✓ Test 1.2 PASSED: Tier 2 (advanced curriculum) classified correctly
# ✓ Test 1.3 PASSED: Tier 4 (blog/opinion) classified with penalties
# ✓ Test 2.1 PASSED: Single-source dependence detected
# ✓ Test 2.2 PASSED: Tier inversion detected
# ✓ Test 2.3 PASSED: Good hierarchy produces no fallacies
# ✓ Test 3.1 PASSED: Weights adjust for Tier 1 dominance
# ✓ Test 3.2 PASSED: Weights adjust for reasoning fallacies
# ✓ Test 4.1 PASSED: Source boosts applied to ASC
# ✓ Test 4.2 PASSED: Reasoning penalties applied to ASC
# ✓ Test 4.3 PASSED: VERY_HIGH confidence assigned correctly
# ✓ Test 5.1 PASSED: End-to-end pipeline executed successfully
#
# RESULTS: 13 passed, 0 failed
```

### Run Integration Example

```bash
python example_integration.py

# Complete walkthrough with climate change claim:
# Shows: Classification → Reasoning Audit → Weight Adjustment → ASC Scoring
# Outputs reasoning trace and final result
```

### Test Coverage

- **13 automated tests** across classification, audit, weighting, scoring
- **Unit tests** for each module
- **Integration tests** for complete pipeline
- **Sensitivity tests** for weight adjustment logic

---

## 📖 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **README.md** | Overview, quick start, architecture | 15 min |
| **QUICKSTART.md** | Practical guide with code examples | 20 min |
| **docs/SOURCE_HIERARCHY_IMPLEMENTATION.md** | Complete reference (9 sections) | 45 min |
| **IMPLEMENTATION_SUMMARY.md** | Architecture & design decisions | 25 min |
| **example_integration.py** | Runnable code example | Run it |
| **INDEX.md** | Directory of all deliverables | 10 min |

---

## 🎯 Use Cases

### 1. Evaluate AI Claims Against Research

```
Claim: "Recent studies show X causes Y"
Evidence: Mix of peer-reviewed, news, and opinion sources
Result: ASC score reflects both evidence quality AND reasoning quality
```

### 2. Detect Reasoning Fallacies

```
Claim: Supported by single Tier 4 blog post
Result: Flagged as single-source dependence → Chain Integrity: 20/100
```

### 3. Compare Two Competing Claims

```
Claim A: Tier 1 consensus + sound reasoning → ASC 85/100 (SUPPORTED)
Claim B: Tier 4 opinion only → ASC 15/100 (REFUTED)
Result: Clear winner with full audit trail
```

### 4. Validate Model Outputs

```
Model generates: "Study X shows Z"
SAFE scores it against source hierarchy
Returns: ASC + reasoning audit + source tier assignments
→ Can reject low-confidence outputs before exposing to users
```

---

## 🔄 How It Works: Step by Step

### Input
```python
{
  "claim": "Statement to evaluate",
  "evidence": [
    {
      "source_type": "peer_reviewed_empirical",
      "peer_review": {...},
      "consensus_metadata": {...},
      "derivation_signal": {...}
    },
    ...
  ],
  "base_components": {"E": 70, "R": 70, ...}
}
```

### Processing

**Step 1: Source Classification**
- Evaluate peer-review status, venue tier, replication count
- Assign Tier 1-4
- Calculate component boosts

**Step 2: Reasoning Audit**
- Check for 6 types of hierarchy violations
- Calculate reasoning chain integrity (0-100)
- Identify critical issues

**Step 3: Weight Adjustment**
- Analyze tier distribution of sources
- Count reasoning fallacies
- Adjust component weights dynamically
- Normalize to sum to 1.0

**Step 4: ASC Calculation**
- Apply source boosts to components
- Apply reasoning penalties
- Compute weighted average
- Apply F (fundamental laws) gate
- Assign confidence band

### Output
```python
{
  "asc_score": 82.5,
  "confidence": "VERY_HIGH",
  "status": "SUPPORTED",
  "components": {...},
  "source_integration_summary": {...},
  "reasoning_audit_integration": {...},
  "adjustment_trace": [...],
  "sensitivity_note": "..."
}
```

---

## 🔗 Integration Points

### With Evidence Adapters

Adapters (Consensus, PubMed, etc.) provide structured evidence metadata → feeds into `classify_source()`

### With Web Runtime

Frontend receives classifications and audit results → displays with full transparency

### With Model Integration

Adapters (Grok, OpenAI, Gemini) pipe claims through orchestrator → get scored output

---

## 🛠️ Contributing

### How to Contribute

1. **Report Issues**
   - Found a bug? Submit with reproducible example
   - Suggest improvements? Open an issue with rationale

2. **Improve Tier Classifications**
   - Test tier assignment logic against domain experts
   - Propose refinements with evidence

3. **Extend Reasoning Audit**
   - Identify new fallacy types
   - Implement detection logic
   - Add tests

4. **Enhance Documentation**
   - Clarify existing docs
   - Add examples for common use cases
   - Translate to other languages

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes
# ... edit files ...

# 3. Run tests
python test_suite.py

# 4. Commit with clear message
git commit -m "feat: Add new feature with tests and docs"

# 5. Push and create PR
git push origin feature/your-feature
# Create pull request on GitHub
```

### Code Style

- Python 3.9+ compatibility
- Clear docstrings for all functions
- Type hints where practical
- Test coverage for new logic
- Minimal external dependencies

---

## 📋 Constitutional Filter

Every contribution is evaluated against:

1. **Civilisational Continuation** — Does this enhance long-term epistemic integrity?
2. **Planetary Restoration** — Is this environmentally responsible?
3. **Abundance for Future Generations** — Does this leave systems better than we found them?

Contributions that systematically trade long-term integrity for short-term convenience will be declined.

---

## 📜 License

This work is released into the **public domain** under the Unlicense. You are free to copy, modify, publish, use, compile, and distribute this software for any purpose, commercial or non-commercial.

See [LICENSE](LICENSE) for full terms.

---

## 🔗 References

- **SAFE Architecture Spec**: See `Safe.PDF` (original design)
- **Peer-Review Consensus Formation**: [Kuhn, T. (1962) - The Structure of Scientific Revolutions](https://en.wikipedia.org/wiki/The_Structure_of_Scientific_Revolutions)
- **Source Credibility**: [Fogg, B.J. (2003) - Persuasive Technology](https://captology.stanford.edu/)
- **Reasoning Quality**: [Sperber & Wilson (1986) - Relevance Theory](https://en.wikipedia.org/wiki/Relevance_theory)

---

## 🙏 Acknowledgments

This work builds on:
- Project Utopia research architecture (distinguishing evidence, hypotheses, speculation, synthesis)
- Open-source epistemic infrastructure principles
- Scientific consensus methodologies (IPCC, WHO, professional societies)
- Reasoning quality assessment frameworks

---

## 📞 Contact & Support

### Getting Help

- **Quick Questions?** → See [QUICKSTART.md](QUICKSTART.md)
- **Need Full Details?** → See [docs/SOURCE_HIERARCHY_IMPLEMENTATION.md](docs/SOURCE_HIERARCHY_IMPLEMENTATION.md)
- **Want Examples?** → Run [example_integration.py](example_integration.py)
- **Found a Bug?** → Open an issue on GitHub

### Reporting Issues

Include:
1. Minimal reproducible example
2. Expected vs. actual behavior
3. Python version and environment
4. Full error traceback if applicable

---

## 📈 Roadmap

### Phase 1 (Current) ✅
- ✅ Tier classification system
- ✅ Reasoning audit with hierarchy checks
- ✅ Dynamic weight adjustment
- ✅ Integrated ASC v2.0
- ✅ Complete documentation

### Phase 2 (Planned)
- ML-based venue classification
- Derivation detection model
- Domain-specific tier definitions
- Evidence adapter integrations

### Phase 3 (Proposed)
- Temporal weighting evolution
- Contradiction search automation
- Information contamination detection
- Large-scale validation benchmarks

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| Total Lines of Code | ~2,958 |
| Documentation Lines | ~1,400 |
| Test Cases | 13 |
| Engine Modules | 5 |
| Tiers Implemented | 4 |
| Fallacy Types | 6 |
| Time to Score | <100ms |
| Python Version | 3.9+ |
| External Dependencies | 0 |
| License | Unlicense (Public Domain) |

---

## 🎓 Learning Path

1. **Start Here**: Read [README.md](README.md) (this file)
2. **Get Practical**: Follow [QUICKSTART.md](QUICKSTART.md)
3. **Run Examples**: Execute `python example_integration.py`
4. **Validate**: Run `python test_suite.py`
5. **Understand Deep**: Read [docs/SOURCE_HIERARCHY_IMPLEMENTATION.md](docs/SOURCE_HIERARCHY_IMPLEMENTATION.md)
6. **Understand Design**: Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## ⭐ Key Innovations

1. **Consensus Formation Date** — Tracks when field agreement emerged, not just publication date
2. **Lineage-Based Independence** — Avoids false consensus from repeated citations
3. **Hierarchy-Aware Reasoning Audit** — 6 fallacy types specific to source tiers
4. **Dynamic ASC Weighting** — Weights adjust to epistemic context
5. **Full Transparency** — Every decision explained in audit trail

---

**Made with ❤️ for epistemic integrity.**

Maintained by the SAFE community. Contributions welcome.
