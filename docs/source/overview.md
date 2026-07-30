# Overview

Onomasticon centers on a single abstraction: `ImplementationRegistry`. A
registry subclass owns a mapping from normalized names to implementation
classes, validates that each class derives from the expected base type, and
offers helper methods for retrieval and instantiation.

## Core behavior

### Named registration

Each implementation is stored under a normalized name. By default, names are:

- stripped of surrounding whitespace
- converted with `casefold()`
- rejected if empty

That means `"Console"`, `" console "`, and `"CONSOLE"` all resolve to the same
registry entry.

### Subclass isolation

Every subclass of `ImplementationRegistry` gets its own internal storage and
lock. This keeps separate plugin systems from colliding with each other.

```python
from abc import ABC

from onomasticon import ImplementationRegistry


class Renderer(ABC):
    pass


class Exporter(ABC):
    pass


class RendererRegistry(ImplementationRegistry[Renderer]):
    implementation_base = Renderer


class ExporterRegistry(ImplementationRegistry[Exporter]):
    implementation_base = Exporter
```

Registering a renderer does not affect `ExporterRegistry`, and clearing one
registry does not clear the other.

### Thread-safe updates and reads

Registrations and lookups are guarded by a re-entrant lock, which makes the
registry safe to use in multi-threaded applications that perform registration
or discovery from different execution paths.

### Explicit extension points

The `implementation()` decorator makes registration readable at declaration
time and keeps extension code close to the implementation itself.

```python
@RendererRegistry.implementation("console")
class ConsoleRenderer(Renderer):
    pass
```

## When to use it

Onomasticon is a good fit when you want:

- named strategies or backends
- application-internal plugin registries
- testable replacement of implementations by name
- a small alternative to more elaborate plugin frameworks

It is less useful when dynamic discovery from installed packages, entry points,
or remote sources is the main problem. In those cases, Onomasticon can still be
the final registration layer, but not the whole discovery system by itself.
