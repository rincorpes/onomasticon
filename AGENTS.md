# AGENTS.md

## Scope

This guide applies to `packages/python/onomasticon`.

## Purpose

Onomasticon is a published typed registry library for named implementation
registration and lookup.

This file is intended to stay useful even when `onomasticon` is worked on as an
independent package repository.

## Maintainer Priorities

- Protect public API stability.
- Preserve normalized lookup behavior.
- Preserve subclass-isolated registries.
- Keep the library small, explicit, and dependency-light.

## Working Rules

- Protect public API stability unless the task explicitly calls for a breaking
  change.
- Be careful with normalization rules, thread safety, and subclass registry
  isolation.
- Update tests and docs whenever registration behavior changes.
- Avoid turning the library into a larger plugin framework than it needs to be.

## Sensitive Areas

- registration name normalization
- subclass-local registry storage
- `replace=True` override behavior
- thread-safety around registration and lookup
- type-facing APIs used by downstream libraries

Changes to these behaviors should include regression tests.

## Commands

Run from this package root:

```bash
poetry install --extras dev --extras docs
poetry run pytest tests
poetry run mypy src
poetry run pylint src/onomasticon
poetry run sphinx-build -n -W --keep-going -b html docs/source docs/_build/html
```

## API Change Rules

- Registration and lookup semantics are part of the public contract.
- If name normalization changes, document it clearly and add direct tests.
- If subclass isolation or override behavior changes, assume downstream users
  may depend on the previous semantics.
- Breaking changes should be rare and called out explicitly in docs and release
  notes.
