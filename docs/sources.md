# Sources

## Purpose

A source represents the publisher or origin responsible for a collected
document. It is separate from the RSS endpoint used to retrieve that document.

This distinction allows one source to provide multiple feeds, languages,
regional editions, or collection methods without creating unrelated source
identities.

Source metadata provides analytical context. It does not determine whether a
source is reliable or whether its claims are true.

## Current model

The normalized `Source` model stores:

- stable identifier;
- display name;
- high-level source type;
- primary jurisdiction when known;
- default language when known;
- creation time.

Articles reference the normalized source through `Article.source_id`.

RSS discovery is performed through the protocol-independent acquisition
contracts. `RSSConnector` converts feed entries into immutable
`CandidateRecord` objects before the collection service creates articles.

The legacy `fetch_rss_entries()` adapter remains available during the
incremental transition, but the collection service no longer depends on its
RSS-specific dictionary representation.

## Source identity

`Source.identifier` is the stable machine-facing identity.

`Source.name` is a display value and may eventually change without changing
the source identity. Current RSS configuration may omit an explicit
identifier, in which case the configured name is used as the initial
identifier.

Several collection endpoints belonging to the same publisher should use the
same explicit source identifier.

The current `SourceType` vocabulary includes:

- news media;
- news agency;
- government;
- international organization;
- research institution;
- social media;
- other.

Source type describes institutional form. It is not a credibility score or a
political classification.

## Metadata enrichment

Repository lookup is performed by stable identifier.

When an existing source has no jurisdiction or default language, configured
values may fill those missing fields. Existing non-null values are not
silently overwritten.

Ownership, affiliations, audience, jurisdiction, and language may change over
time. Future source profiles must represent temporal validity and provenance
instead of repeatedly overwriting one permanent label.

## Legacy migration

The first normalized-source migration preserves the original string-valued
`Article.source` column and adds nullable `Article.source_id`.

For every distinct non-empty legacy source name, the migration:

1. creates one normalized source;
2. uses the legacy name as its initial identifier and display name;
3. assigns the `news_media` source type;
4. preserves a default language only when legacy articles contain one
   unambiguous language;
5. leaves jurisdiction unknown because it was not stored historically;
6. links all matching legacy articles through `source_id`.

The legacy string remains available for verification and rollback. It will be
removed only after normalized-source usage is complete and independently
verified.

## Current limitations

The current implementation does not yet persist:

- collection endpoints as independent records;
- time-versioned source profiles;
- ownership history;
- source aliases;
- intended audiences;
- evidence supporting source metadata;
- normalized jurisdiction codes.

These are planned extensions. They must not be approximated through
unsupported permanent labels.
