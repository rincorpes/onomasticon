# Onomasticon

Onomasticon is a small Python library for building named registries of
implementation classes with explicit validation, predictable lookup, and
subclass-level isolation.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Quick Start
:link: quickstart
:link-type: doc

Install the package, define a registry, and register implementations in a few
lines.
:::

:::{grid-item-card} API Reference
:link: api
:link-type: doc

Browse the public API for `ImplementationRegistry` and its registration and
lookup helpers.
:::

::::

```{button-link} quickstart.html
:color: primary
:shadow:

Get Started
```

```{button-link} api.html
:color: secondary
:shadow:

Read the API
```

## What Onomasticon solves

When a project needs to map names like `"console"`, `"json"`, or `"redis"` to
concrete implementation classes, it is easy to end up with ad hoc dictionaries,
hidden import side effects, or registries that leak state across tests and
subsystems.

Onomasticon gives that pattern a dedicated abstraction:

- typed lookup and instantiation helpers
- isolated registries per subclass
- normalized names for consistent matching
- thread-safe registration and retrieval
- decorator-based registration for plugin-like extension points

## Design goals

- Keep the implementation small and dependency-free at runtime.
- Make registration failures obvious and early.
- Support extension-heavy code without sacrificing readability.
- Fit equally well in applications, internal tools, and reusable libraries.

```{toctree}
:hidden:
:caption: Start Here

Overview <overview>
Quick Start <quickstart>
API Reference <api>
```
