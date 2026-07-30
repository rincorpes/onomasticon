# Quick Start

## Installation

Install the package from PyPI:

```bash
pip install onomasticon
```

For local development with docs and test tooling available:

```bash
poetry install --extras dev --extras docs
```

## Define a base type

Registries enforce that every registered class derives from the configured
`implementation_base`.

```python
from abc import ABC, abstractmethod


class Renderer(ABC):
    @abstractmethod
    def render(self, value: str) -> str:
        """Render a value."""
```

## Create a registry

```python
from onomasticon import ImplementationRegistry


class RendererRegistry(ImplementationRegistry[Renderer]):
    implementation_base = Renderer
```

## Register implementations

You can register classes directly:

```python
class ConsoleRenderer(Renderer):
    def render(self, value: str) -> str:
        return value


RendererRegistry.register("console", ConsoleRenderer)
```

Or use the decorator form:

```python
@RendererRegistry.implementation("json")
class JsonRenderer(Renderer):
    def render(self, value: str) -> str:
        return f'"{value}"'
```

## Retrieve or instantiate by name

```python
renderer_type = RendererRegistry.get("CONSOLE")
renderer = RendererRegistry.instantiate("json")

assert renderer_type is ConsoleRenderer
assert renderer.render("hello") == '"hello"'
assert RendererRegistry.contains(" console ")
```

## Replace registrations deliberately

By default, duplicate names raise `KeyError`. If you want to override an
existing registration, set `replace=True`.

```python
class BetterConsoleRenderer(Renderer):
    def render(self, value: str) -> str:
        return f">>> {value}"


RendererRegistry.register(
    "console",
    BetterConsoleRenderer,
    replace=True,
)
```

## Build the docs locally

After installing the docs dependencies:

```bash
poetry run sphinx-build -n -W --keep-going -b html docs/source docs/_build/html
```

The generated site will be written to `docs/_build/html`.
