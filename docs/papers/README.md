# AI Debugger Pro research papers

These papers document the project in recommended reading order.

1. [From Stateless Execution to Human-Governed AI Repair: The Evolution of AI Debugger Pro, Versions 0–6](01-system-evolution/system-evolution-v0-v6.pdf)  
   A system-evolution case study covering the path from a stateless code runner to an approval-gated, human-governed repair workflow.

2. [AI Debugger Pro: Current Architecture and Human-Governed Repair Protocol](02-current-architecture/current-architecture-and-repair-protocol.pdf)  
   The authoritative description of the current architecture, trust boundaries, structured diagnosis, approval gate, source mutation, and verification loop.

3. [Empirical Evaluation Protocol for Human-Governed AI-Assisted Repair](03-evaluation-protocol/empirical-evaluation-protocol.pdf)  
   A preregistration-ready evaluation design. The protocol is complete; benchmark results are intentionally pending.

4. [AI Debugger Pro: Security Threat Model for Human-Governed AI-Assisted Repair](04-security-threat-model/security-threat-model.pdf)  
   A repository-grounded threat model covering execution isolation, diagnostic-data exposure, prompt injection, unsafe repair acceptance, verification limits, and prioritized mitigations. The [editable source](04-security-threat-model/security-threat-model.md) is included.

5. [AI Debugger Pro: Repair Verification, Evidence, and Trust](05-repair-verification-and-trust/repair-verification-and-trust.pdf)  
   A technical assurance framework defining scoped verification labels, immutable evidence, independent oracles, regression strategy, provenance, and reviewer decision support. The [editable source](05-repair-verification-and-trust/repair-verification-and-trust.md) is included.

6. [AI Debugger Pro: Multi-Language Execution Architecture](06-multi-language-execution/multi-language-execution-architecture.pdf)  
   A systems paper separating shared lifecycle contracts from language-specific validation, build, runtime, diagnostic, artifact, and verification semantics. The [editable source](06-multi-language-execution/multi-language-execution-architecture.md) is included.

7. [AI Debugger Pro: Human-in-the-Loop UX and Decision-Support Study Protocol](07-human-in-the-loop-ux/human-in-the-loop-ux-study-protocol.pdf)  
   A preregistration-ready human-factors protocol evaluating decision accuracy, unsafe acceptance, automation bias, evidence labels, risky-change warnings, calibration, workload, and accessibility. The [editable source](07-human-in-the-loop-ux/human-in-the-loop-ux-study-protocol.md) is included.

8. [AI Debugger Pro: Benchmark Results and Comparative Evaluation](08-benchmark-results/benchmark-results-and-comparative-evaluation.md)  
   The first measured multi-language baseline: 24/24 execution classifications matched, with latency, diagnostic-evidence coverage, and CI validation. [PDF](08-benchmark-results/benchmark-results-and-comparative-evaluation.pdf) · [raw data](08-benchmark-results/data/frozen-execution-benchmark-raw.csv) · [summary data](08-benchmark-results/data/measured-results.csv)

9. [AI Debugger Pro: Failure Taxonomy for AI-Assisted Debugging](09-failure-taxonomy/failure-taxonomy-for-ai-assisted-debugging.md)  
   A measured taxonomy of syntax/compile, runtime, and timeout failures, including the silent nonzero-exit evidence gap. [PDF](09-failure-taxonomy/failure-taxonomy-for-ai-assisted-debugging.pdf) · [taxonomy data](09-failure-taxonomy/data/failure-taxonomy-data.csv)

10. [AI Debugger Pro: Context Selection and Diagnostic Relevance](10-context-selection/context-selection-and-diagnostic-relevance.md)  
    A repository-grounded context-engineering architecture with typed manifests, failure-directed selection, privacy and injection controls, deterministic budgets, and frozen validation scenarios. [PDF](10-context-selection/context-selection-and-diagnostic-relevance.pdf) · [context matrix](10-context-selection/data/context-source-matrix.csv) · [selection scenarios](10-context-selection/data/selection-scenarios.csv)

11. [AI Debugger Pro: Regression-Test Generation and Independent Oracles](11-regression-test-oracles/regression-test-generation-and-independent-oracles.md)  
    A verification-engineering architecture for oracle provenance, regression-test admission, mutation challenges, independent behavioral evidence, and scoped authority. [PDF](11-regression-test-oracles/regression-test-generation-and-independent-oracles.pdf) · [oracle matrix](11-regression-test-oracles/data/oracle-source-matrix.csv) · [frozen scenarios](11-regression-test-oracles/data/regression-test-scenarios.csv)

12. [AI Debugger Pro: Reproducible Engineering and Release Evidence](12-reproducible-engineering/reproducible-engineering-and-release-evidence.md)  
    Final series paper defining the evidence graph from source commit through independent replication. [PDF](12-reproducible-engineering/reproducible-engineering-and-release-evidence.pdf) · [artifact manifest](12-reproducible-engineering/data/artifact-manifest.csv) · [claim-evidence matrix](12-reproducible-engineering/data/claim-evidence-matrix.csv) · [release checklist](12-reproducible-engineering/data/release-readiness-checklist.csv)

## Historical paper

- [AI Studio Debugger](../AI%20Studio%20Debugger.pdf) documents the earlier V0–V4 project state and is preserved for historical comparison.
