from __future__ import annotations

import re
from importlib import metadata
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover
        tomllib = None  # type: ignore[assignment]

_PACKAGE_NAME = "onomasticon"
_PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"
_VERSION_PATTERN = re.compile(
    r"""^version\s*=\s*["'](?P<version>[^"']+)["']\s*$"""
)


def _parse_version_from_text(pyproject_text: str, default: str) -> str:
    in_project_section = False

    for raw_line in pyproject_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            in_project_section = line == "[project]"
            continue

        if not in_project_section:
            continue

        match = _VERSION_PATTERN.match(line)
        if match:
            return match.group("version").strip()

    return default


def read_pyproject_version(
    pyproject_path: str | Path = _PYPROJECT_PATH,
    *,
    default: str = "0.0.0",
) -> str:
    path = Path(pyproject_path)

    try:
        pyproject_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default

    if tomllib is not None:
        try:
            project_data = tomllib.loads(pyproject_text)
        except tomllib.TOMLDecodeError:
            pass
        else:
            version_value = project_data.get("project", {}).get("version")
            if isinstance(version_value, str) and version_value.strip():
                return version_value.strip()

    return _parse_version_from_text(pyproject_text, default)


def get_version(
    pyproject_path: str | Path = _PYPROJECT_PATH,
    *,
    package_name: str = _PACKAGE_NAME,
    default: str = "0.0.0",
) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return read_pyproject_version(pyproject_path, default=default)


__version__ = get_version()
