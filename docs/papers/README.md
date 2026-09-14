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

## Historical paper

- [AI Studio Debugger](../AI%20Studio%20Debugger.pdf) documents the earlier V0–V4 project state and is preserved for historical comparison.
