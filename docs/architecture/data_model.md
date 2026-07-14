# Argus Data Model

## Purpose

This document defines the core entities used by Argus and the relationships between them.

The data model separates:

1. observations collected from sources;
2. claims made by people and organizations;
3. reconstructed real-world events;
4. analytical inferences produced by Argus.

Argus does not store an absolute representation of truth. It stores observations, evidence, claims, relationships and explicitly qualified inferences.

---

## Knowledge Layers

Argus represents information through three connected layers.

### Reality Layer

Represents the best currently supported model of real-world entities, events and relationships.

Examples:

- people;
- organizations;
- countries;
- locations;
- agreements;
- elections;
- military actions;
- economic changes;
- historical events.

The Reality Layer must distinguish confirmed information from disputed or uncertain information.

### Information Layer

Represents how the world is described by sources.

It stores:

- documents;
- statements;
- claims;
- quotations;
- frames;
- rhetorical features;
- narratives;
- source attribution.

Multiple incompatible descriptions of the same event may coexist in this layer.

### Reasoning Layer

Represents analyses and hypotheses produced by Argus.

It stores:

- inferred relationships;
- factual consistency assessments;
- possible effects;
- potential beneficiaries;
- communication-function hypotheses;
- competing explanations;
- supporting and contradicting evidence.

Every reasoning object must be traceable to its evidence.

---

## Core Entities

### Source

An origin from which a document is obtained.

Examples:

- newspaper;
- news agency;
- government department;
- international organization;
- research institution;
- individual social-media account.

Important properties:

- name;
- source type;
- jurisdictions and operating countries;
- publication languages;
- ownership;
- affiliations;
- official status;
- known relationships with other sources;
- temporal validity of source metadata.

Country, ownership, affiliation, publication language and intended audience are
separate properties. They may change over time and must not be collapsed into
a single permanent source label.

A source profile provides context. It must not automatically determine whether its claims are true.

---

### Document

A discrete information artifact collected by Argus.

Examples:

- article;
- speech transcript;
- press release;
- treaty;
- report;
- court decision;
- social-media post;
- video transcript.

Important properties:

- source;
- author or speaker;
- publication time or time interval;
- collection time;
- original language using a BCP 47 identifier;
- canonical URL or archive reference;
- raw content;
- normalized content;
- content hash;
- document type.

A document is evidence that particular information was published. It is not evidence that every statement inside it is true.
A translation is a derived artifact. It must retain a relationship to the
original document and record the translation method, model, version, and
creation time. Analytical evidence should reference the original-language
content whenever possible.

---

### Observation

A directly recorded property of a document or external data source.

Examples:

- a sentence appears in a document;
- a word is used 14 times;
- an article was published at a particular time;
- a value appears in an official statistical table;
- a headline changed between archived versions.

Observations should be reproducible and minimally interpretive.

Important properties:

- observation type;
- observed value;
- document or dataset reference;
- exact location within the source;
- extraction method;
- method version;
- timestamp.

---

### Statement

A communicative act attributed to a speaker.

Examples:

- a politician's quotation;
- an official announcement;
- an editorial assertion;
- a spokesperson's response.

Important properties:

- speaker;
- audience;
- venue;
- date;
- quotation or paraphrase;
- surrounding context;
- source document.

A statement may contain one or more claims.

---

### Claim

The smallest independently assessable assertion extracted from a document or statement.

Examples:

- "The agreement was signed on 14 March."
- "Unemployment fell by two percentage points."
- "Country X initiated the attack."

Important properties:

- subject;
- predicate;
- object or value;
- time;
- location;
- modality;
- certainty expressed by the speaker;
- source attribution;
- original text span.

A claim must remain separate from its verification status.

---

### Evidence

Information relevant to evaluating a claim or inference.

Evidence may:

- support;
- contradict;
- contextualize;
- weaken;
- leave unresolved.

Important properties:

- evidence type;
- source;
- referenced claim or inference;
- relationship type;
- strength;
- independence from other evidence;
- exact citation;
- temporal relevance.

A government statement is strong evidence that the government made that statement. It is not automatically strong evidence that the statement's content is true.

---

### Entity

A persistent identifiable object.

Examples:

- person;
- organization;
- country;
- location;
- company;
- political party;
- institution;
- document;
- physical object.

Important properties:

- canonical name;
- aliases;
- entity type;
- active period;
- external identifiers;
- merge history.

Entity resolution must preserve uncertainty when two references may or may not identify the same object.

---

### Event

A time-bounded real-world occurrence or process reconstructed from claims, observations and evidence.

Examples:

- election;
- military strike;
- treaty signing;
- protest;
- policy change;
- market crash;
- diplomatic meeting.

Important properties:

- event type;
- start and end time;
- location;
- participants;
- related claims;
- supporting evidence;
- status;
- confidence;
- alternative interpretations.

An event is not a single article. It is a structured cluster that may evolve as new information arrives.

Possible lifecycle states:

- detected;
- emerging;
- active;
- stabilized;
- historical;
- disputed.

---

### Frame

A recurring way of presenting an event or issue.

A frame determines:

- who is presented as the actor;
- who is presented as the victim;
- which causes are emphasized;
- which consequences are emphasized;
- which information is omitted;
- which moral evaluation is encouraged.

Examples:

- self-defence frame;
- humanitarian-crisis frame;
- external-threat frame;
- economic-necessity frame;
- historical-justice frame.

Frames belong to the Information Layer and must reference observable textual evidence.

---

### Narrative

A recurring explanatory pattern linking actors, events, causes and moral judgments across multiple documents.

A narrative is not a single phrase. It is a pattern detected across time and sources.

Important properties:

- constituent claims;
- frames;
- associated entities and events;
- participating sources;
- first and last observation;
- temporal prevalence;
- geographic distribution;
- competing narratives.

---

### Analysis Result

A versioned output produced by an analytical method.

Examples:

- linguistic metric;
- detected rhetorical technique;
- factual consistency assessment;
- event-cluster assignment;
- narrative similarity score;
- rhetorical-shift measurement.

Important properties:

- analysis type;
- target object;
- method name;
- method version;
- analysis-run identifier;
- model or lexicon version where applicable;
- configuration;
- input object versions;
- software version;
- result;
- confidence;
- evidence chain;
- creation time;
- warnings and execution limitations.

Analysis results must be reproducible where the underlying method is deterministic.

---

### Inference

A conclusion or hypothesis derived from observations, claims, events or other analysis results.

Examples:

- event A may have contributed to rhetoric shift B;
- actor X may receive an economic benefit from event Y;
- several sources may be reproducing the same narrative;
- a statement may be intended to mobilize an audience.

Important properties:

- inference type;
- proposition;
- supporting evidence;
- contradicting evidence;
- required assumptions;
- alternative explanations;
- confidence or evidence strength;
- method version.

An inference must never be stored without an explicit evidence chain.

---

### Potential Effect

A plausible consequence of an event.

Examples:

- oil prices increase;
- public approval changes;
- military spending rises;
- trade routes become less reliable.

Potential effects may be:

- observed;
- projected;
- disputed;
- unsupported.

Argus must distinguish observed effects from hypothetical effects.

---

### Potential Beneficiary

An actor that may benefit from an event or one of its effects.

A potential beneficiary record does not imply responsibility for causing the event.

Required structure:

- actor;
- event or effect;
- benefit type;
- benefit mechanism;
- supporting evidence;
- counterevidence;
- required assumptions;
- alternative explanations;
- evidence strength.

Example:

- Actor: oil-exporting country;
- Effect: increase in oil price;
- Mechanism: higher export revenue;
- Evidence: price and export-volume data;
- Limitation: political or military costs may exceed economic gains.

---

## Core Relationships

### Source and Document

```text
Source
    publishes
        Document
```

### Document and Observation

```text
Document
    contains
        Observation
```

### Document, Statement and Claim

```text
Document
    contains
        Statement

Statement
    expresses
        Claim
```

### Claim and Event

```text
Claim
    refers_to
        Event
```

### Claim and Evidence

```text
Evidence
    supports
        Claim

Evidence
    contradicts
        Claim

Evidence
    contextualizes
        Claim
```

### Documents and Frames

```text
Document
    uses
        Frame
```

### Claims and Narratives

```text
Claim
    contributes_to
        Narrative
```

### Events

```text
Event
    precedes
        Event

Event
    overlaps
        Event

Event
    may_influence
        Event

Event
    has_effect
        Potential Effect
```

The `may_influence` relationship is analytical and must include evidence and confidence. It must not be treated as proven causation.

### Inferences

```text
Inference
    based_on
        Observation

Inference
    based_on
        Claim

Inference
    based_on
        Event

Inference
    supported_by
        Evidence

Inference
    contradicted_by
        Evidence
```

### Potential Beneficiaries

```text
Potential Beneficiary
    may_benefit_from
        Potential Effect
```

---

## Evidence Chain

Every non-trivial conclusion must be traceable through an evidence chain.

Example:

```text
Potential-beneficiary hypothesis
    ↓
Observed increase in oil prices
    ↓
Economic dataset
    ↓
Specific table and timestamp
```

Example:

```text
Appeal-to-fear detection
    ↓
Rhetorical feature
    ↓
Sentence spans
    ↓
Original document
    ↓
Source and publication date
```

The user must be able to inspect every step.

---

## Separation of Fact and Interpretation

Argus must distinguish:

- collected content;
- direct observations;
- attributed claims;
- supported facts;
- disputed reconstructions;
- analytical measurements;
- hypotheses;
- speculative alternatives.

These categories must not be collapsed into a single generic `fact` type.

---

## Versioning

All extracted and derived objects must record:

- creation time;
- method or model identifier;
- method, model or lexicon version;
- analysis-run identifier where applicable;
- relevant configuration;
- input object and source-data versions;
- input content hash where applicable;
- software version;
- superseded or current status.

Historical analysis results should remain available after methods are updated.

---

## Uncertainty

Uncertainty is a first-class property.

Argus must be able to represent:

- unknown;
- disputed;
- partially supported;
- contradictory;
- time-sensitive;
- source-dependent;
- method-dependent.

A missing answer is preferable to unsupported certainty.
