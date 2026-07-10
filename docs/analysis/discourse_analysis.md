# Discourse Analysis

## Purpose

The purpose of discourse analysis is not to determine whether a document is "true" or "false".

Instead, Argus measures linguistic, rhetorical and factual properties of documents in order to provide transparent analytical reports.

The system must distinguish observations from interpretations.

Measurements are considered facts produced by the system.

Interpretations are considered hypotheses and must always include confidence estimates together with supporting evidence.



# Philosophy

Argus never asks:

"Who is right?"

Instead it asks:

"What is being claimed?"

"How is it being presented?"

"How has it changed?"

"How does it compare with other sources?"

"Which measurable evidence supports this conclusion?"



# Pipeline

Document

↓

Language Detection

↓

Text Cleaning

↓

Sentence Segmentation

↓

Entity Extraction

↓

Claim Extraction

↓

Linguistic Measurements

↓

Rhetorical Analysis

↓

Fact Verification

↓

Cross-source Comparison

↓

Narrative Detection

↓

Report Generation



# Layer 1

Linguistic Features

Purpose:

Measure objective properties of language.

Input:

Document

Output:

Feature Vector

Examples:

- word count
- sentence count
- passive voice frequency
- lexical diversity
- emotional vocabulary
- certainty markers
- uncertainty markers
- temporal expressions
- modal verbs
- collective pronouns

Limitations

These measurements are descriptive only.

No interpretation should be made at this stage.



# Layer 2

Purpose

Detect rhetorical techniques.

Examples

Appeal to fear

False dilemma

Heroization

Victimization

Enemy image

Scapegoating

Appeal to authority

Bandwagon

Whataboutism