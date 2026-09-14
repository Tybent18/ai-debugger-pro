# AI Debugger Pro: Foundation Overview

> Historical foundation paper · [Publication catalog](../README.md) · [Paper 1: System Evolution →](../01-system-evolution/system-evolution-v0-v6.pdf)

---

**T. R. Bentley**  
Foundation Overview | Historical edition  
Repository: Tybent18/ai-debugger-pro

## Abstract

AI Debugger Pro began as AI Studio Debugger: a practical attempt to shorten the distance between a failing program, an understandable diagnosis, and a repair the developer could evaluate. This foundation overview preserves that origin while placing it inside the project's completed research series. It describes the initial problem, early workflow, core architectural ideas, human role, safety boundaries, and the questions that motivated later work on verification, multi-language execution, human factors, measured evaluation, context selection, test independence, and reproducibility.

This document is the navigable companion to the archived foundation PDF. It records the project's conceptual starting point rather than claiming that every current capability existed in the earliest implementation.

## 1. The original problem

Debugging tools traditionally expose symptoms: error messages, stack traces, compiler output, and exit codes. Those artifacts are essential, but they often leave the developer to translate low-level evidence into a repair strategy alone.

AI Studio Debugger explored a tighter loop:

1. accept source code;
2. execute or validate it;
3. capture the failure evidence;
4. ask an AI system for a structured explanation;
5. present a proposed correction;
6. keep the developer in control of whether the change is accepted.

The enduring idea was not merely “AI writes a fix.” It was that execution evidence and human judgment should surround the model.

## 2. Foundation workflow

The early system joined four concerns that are often separated:

- code editing;
- execution;
- diagnostic interpretation;
- repair guidance.

A user could move from a failing example to an explanation without leaving the workspace. This reduced tool switching and made the debugging session itself the unit of interaction.

The modern project retains that loop but strengthens its boundaries with structured diagnoses, visible diffs, explicit approval, rerun evidence, history, sandboxing, project context, and multiple language adapters.

## 3. Why execution comes first

The foundation treats an actual run as more valuable than speculation about code in isolation. Runtime output supplies concrete evidence: exception type, traceback, standard output, standard error, return code, and timing behavior.

That principle later became central to AI Debugger Pro's evidence model. A model response may interpret evidence or propose an experiment, but it does not replace the observation that produced the diagnosis.

## 4. AI as diagnostic assistance

The AI component is positioned as an interpreter and proposal generator. Useful output should identify:

- what failed;
- where the failure surfaced;
- the likely cause;
- the evidence supporting that explanation;
- a candidate repair;
- a way to test whether the repair addresses the problem.

This division matters. Language models can produce plausible but unsupported explanations. The interface therefore needs to show the underlying execution evidence and keep suggestions distinguishable from verified outcomes.

## 5. Human control

The developer remains the decision-maker. A proposed repair can be reviewed, rejected, edited, or approved. Approval is meaningful only when the user can inspect what will change.

This foundation led directly to the later human-governed repair protocol:

```text
Execute → Capture → Diagnose → Preview → Approve or reject → Rerun → Record
```

The approval gate prevents an AI suggestion from silently becoming source code. The rerun then produces scoped evidence about the accepted candidate.

## 6. Early architecture

The conceptual architecture contains five layers:

| Layer | Responsibility |
| --- | --- |
| Interface | Collect code and display execution, diagnosis, and repair information |
| Analyzer | Detect syntax and structural problems before execution |
| Executor | Run code and capture observable results |
| AI assistant | Convert bounded evidence into structured diagnostic guidance |
| Review loop | Preserve user authority over source mutation and follow-up verification |

Later versions separated these responsibilities into dedicated modules and added persistent history, language routing, sandbox policy, context discovery, CLI access, and editor integration.

## 7. Safety and trust boundaries

Executing arbitrary code and sending diagnostic material to an external model create different risk classes.

Execution risks include filesystem access, process spawning, network access, excessive resource consumption, and hostile code. AI risks include sensitive-data exposure, prompt injection, fabricated explanations, unsafe patches, and excessive user trust.

The foundation paper should therefore be read as the beginning of the safety argument, not its conclusion. The current project uses restricted Docker execution by default and documents remaining limitations explicitly.

## 8. From prototype to research program

Questions raised by the original implementation became the subjects of the twelve-paper AI Debugger Pro series:

| Question | Later treatment |
| --- | --- |
| How did the system evolve? | Paper 1 |
| What is the authoritative architecture? | Paper 2 |
| How should effectiveness be evaluated? | Paper 3 |
| What can attack or misuse the system? | Paper 4 |
| What counts as verification? | Paper 5 |
| How should languages share one lifecycle? | Paper 6 |
| How does the interface affect human decisions? | Paper 7 |
| What has been measured? | Paper 8 |
| Which failures and evidence gaps occur? | Paper 9 |
| Which context should reach the model? | Paper 10 |
| Can generated tests independently verify repairs? | Paper 11 |
| How are claims tied to reproducible release evidence? | Paper 12 |

The historical artifact is therefore valuable because it shows the seed before the branches grew.

## 9. Historical scope

This foundation overview describes the project's original direction and early assumptions. It should not be used as the authoritative specification of the current repository.

For current behavior, consult the main README and Papers 1–12. For measured results, consult Paper 8 and its frozen datasets. Architecture proposals and study protocols are labeled separately from completed measurements throughout the catalog.

## 10. Lasting contribution

The original contribution was a workflow idea with teeth: debugging assistance should begin with observable failure evidence, explain its reasoning, preserve human choice, and return to execution after a repair.

The implementation has changed substantially, but that spine remains intact. AI Studio Debugger was the sketch; AI Debugger Pro became the engineered system and the research record around it.

## Source artifact

- [Download the foundation overview PDF](ai-debugger-pro-foundation-overview.pdf)
- [Browse the complete publication catalog](../README.md)
- [Continue to Paper 1: System Evolution](../01-system-evolution/system-evolution-v0-v6.pdf)

---

[Publication catalog](../README.md) · [Paper 1: System Evolution →](../01-system-evolution/system-evolution-v0-v6.pdf)
