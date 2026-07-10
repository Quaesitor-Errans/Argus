# Argus Architecture Overview

## What is Argus?

Argus is an explainable information-space analysis platform.

Unlike traditional news aggregators or Large Language Models, Argus does not aim to answer questions directly.

Its goal is to continuously observe the global information space, extract measurable information from it, compare different narratives and provide transparent analytical reports.

Argus is designed as a research platform rather than a chatbot.

---

# Mission

To create a transparent, explainable and reproducible system capable of analysing how information spreads, changes and influences society.

---

# Core Principles

## Explainability

Every conclusion produced by Argus must be traceable to measurable evidence.

The user should always be able to understand why the system reached a particular conclusion.

---

## Measurements before conclusions

Argus measures language first.

Interpretation comes only after enough measurable evidence has been collected.

---

## Evidence over authority

No statement is accepted as true solely because of its source.

Every claim must be evaluated using available evidence.

---

## Events are primary

Articles are not the main object of the system.

They are evidence describing real-world events.

---

## Claims are atomic

Every document should be decomposed into independent factual claims whenever possible.

---

## Reproducibility

Running the same analysis on the same data should produce identical results.

---

## Transparency

Argus should avoid black-box decisions whenever possible.

Every score should be decomposable into intermediate calculations.

---

## Modularity

Every subsystem should solve exactly one problem.

Communication between modules should happen through clearly defined interfaces.

---

# High-Level Workflow

Internet

↓

Collectors

↓

Raw Documents

↓

Storage

↓

Parsing

↓

Linguistic Analysis

↓

Fact Verification

↓

Event Detection

↓

Narrative Detection

↓

Cross-source Comparison

↓

Reports