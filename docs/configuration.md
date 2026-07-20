# Argus Configuration

## Purpose

Application configuration is defined in `argus/config.py`.

The configuration module contains static application settings and must not
perform filesystem, network or database operations during import.

## Project Paths

All runtime paths are derived from `PROJECT_ROOT`.

Configured paths include:

- data directory;
- database directory;
- SQLite database file;
- raw-artifact directory;
- logging directory;
- application log file;
- Alembic configuration file.

The modules responsible for using a path are also responsible for creating its
parent directory.

Importing configuration alone must not create files or directories.

Raw acquisition responses are stored beneath `data/raw_artifacts` by their
SHA-256 content address. The artifact store creates directories only when
bytes are written. Absolute filesystem paths are not persisted as artifact
identities.

Database schema management is described in
[Database Migrations](database_migrations.md).


## RSS Sources

RSS sources are represented by the immutable `RSSFeedConfig` dataclass.

Each feed currently contains:

- display name;
- stable source identifier;
- stable collection-endpoint identifier;
- source type;
- feed URL;
- language;
- country or international context.

If no explicit source identifier is configured, the display name is used as
the initial identifier. An explicit identifier is required before a display
name can be changed independently.

If no explicit endpoint identifier is configured, Argus derives
`rss:<source identifier>`. An explicit endpoint identifier is required when
one source exposes more than one RSS feed or when endpoint identity must remain
stable while its technical URL changes.

The configuration objects and the `RSS_FEEDS` collection are immutable during
application execution.

The normalized persistence model is described in
[Sources](sources.md).

## Source Metadata

Source country and language are contextual metadata.

They must not be interpreted as:

- evidence that a source is reliable;
- evidence that a claim is true or false;
- a political classification;
- a substitute for future source profiling.

Argus stores source context so that future analytical modules can compare
coverage across countries and media ecosystems.

## Current Language Limitation

The current discourse-analysis method uses the English spaCy model
`en_core_web_sm`.

The platform architecture targets Arabic, Chinese, English, French, Russian,
and Spanish. English and Russian are the first implementation targets, while
the current production discourse pipeline remains English-only.

For this reason, the active RSS configuration currently contains only
English-language feeds.

Multilingual sources may be added after language detection and versioned
language-specific processing pipelines are implemented.

## Adding a Source

Before an RSS source is added:

1. the URL must return a readable RSS or Atom document;
2. the feed must contain at least one valid entry;
3. article entries must provide a title and URL;
4. the source language and country context must be recorded;
5. the source identifier must match an existing source when several feeds
   belong to the same publisher;
6. each distinct feed must have a stable endpoint identifier;
7. the source type must describe the origin, not its reliability;
8. the source must use its own feed rather than an unattributed aggregation
   proxy.

Network availability is verified manually because unit tests must not depend on
external services.

The RSS adapter itself is tested with deterministic mocked feed data.
