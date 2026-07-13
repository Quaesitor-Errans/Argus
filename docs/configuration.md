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
- logging directory;
- application log file.

The modules responsible for using a path are also responsible for creating its
parent directory.

Importing configuration alone must not create files or directories.

## RSS Sources

RSS sources are represented by the immutable `RSSFeedConfig` dataclass.

Each source currently contains:

- name;
- feed URL;
- language;
- country or international context.

The configuration objects and the `RSS_FEEDS` collection are immutable during
application execution.

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
5. the source must use its own feed rather than an unattributed aggregation
   proxy.

Network availability is verified manually because unit tests must not depend on
external services.

The RSS adapter itself is tested with deterministic mocked feed data.