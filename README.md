# Onomasticon

> Typed, safe, and subclass-isolated implementation registry.

[![CI](https://github.com/rincorpes/onomasticon/actions/workflows/ci.yml/badge.svg)](https://github.com/rincorpes/onomasticon/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/rincorpes/onomasticon)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/onomasticon)](https://pypi.org/project/onomasticon/)
[![Docs](https://img.shields.io/badge/docs-in%20repo-blue)](./docs)

Onomasticon provides a small but strongly structured foundation for building
named registries of implementation classes. It is useful when an application
needs to discover, validate, and instantiate interchangeable components such
as renderers, exporters, adapters, strategies, or service backends by name.

The library focuses on a few practical guarantees: type-aware APIs,
subclass-isolated registries, thread-safe registration and lookup, normalized
names for predictable retrieval, and decorator-based registration for clean,
readable extension points. The result is a lightweight pattern for plugin-like
architectures without bringing in a larger dependency or framework.

## Table of Contents

- [Built With](#built-with)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## Built With

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/packaging-poetry-60A5FA?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![Typing](https://img.shields.io/badge/typing-supported-009688)](https://docs.python.org/3/library/typing.html)

## Getting Started

Onomasticon has no runtime dependencies and is designed to be quick to adopt in
small libraries, internal tools, or larger applications that need explicit
registration of concrete implementations.

### Prerequisites

- Python 3.10 or newer
- `pip` for package installation, or `poetry` for local development

### Installation

Install from PyPI:

```bash
pip install onomasticon
```

Install for local development with Poetry:

```bash
poetry install --extras dev
```

Run the test suite locally:

```bash
poetry run pytest -s tests
```

## Usage

Create a base interface or abstract class, then define a registry whose
`implementation_base` points to that type.

```python
from abc import ABC, abstractmethod

from onomasticon.onomasticon import ImplementationRegistry


class Renderer(ABC):
    @abstractmethod
    def render(self, value: str) -> str:
        """Render a string value."""


class RendererRegistry(ImplementationRegistry[Renderer]):
    implementation_base = Renderer


@RendererRegistry.implementation("console")
class ConsoleRenderer(Renderer):
    def render(self, value: str) -> str:
        return f"console:{value}"
```

Retrieve registered implementations by name:

```python
renderer_type = RendererRegistry.get("console")
renderer = RendererRegistry.instantiate("console")

assert renderer_type is ConsoleRenderer
assert isinstance(renderer, Renderer)
assert RendererRegistry.contains("CONSOLE")
```

Useful behaviors built into the registry:

- Registration names are normalized with `strip()` and `casefold()`
- Each registry subclass keeps its own isolated storage
- Lookups and updates are protected by a re-entrant lock
- `implementations()`, `names()`, and `count()` expose the current registry
  state
- `register(..., replace=True)` and `@registry.implementation(..., replace=True)`
  support controlled overrides

## License

This project is distributed under the MIT License. See [LICENSE](./LICENSE) for
the full text.

## Contact

Santiago Rincón  
Email: [rincorpes@gmail.com](mailto:rincorpes@gmail.com)  
GitHub: [@rincorpes](https://github.com/rincorpes)

## Acknowledgments

- The Python standard library, especially `typing` and `threading`
- `pytest` for straightforward test coverage during development
- Poetry for packaging and dependency management
