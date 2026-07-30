"""
Typed, thread-safe, subclass-isolated implementation registries.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any, ClassVar, Generic, TypeVar, cast

ImplementationT = TypeVar("ImplementationT")


class ImplementationRegistry(Generic[ImplementationT]):
    """
    Base class for named registries of implementation classes.

    Every subclass owns an independent registry and must define
    ``implementation_base``.

    Examples:
        Basic registration.

        .. code-block:: python

            from abc import ABC, abstractmethod

            from onomasticon import ImplementationRegistry


            class Renderer(ABC):
                @abstractmethod
                def render(self, value: str) -> None:
                    ...


            class RendererRegistry(ImplementationRegistry[Renderer]):
                implementation_base = Renderer


            @RendererRegistry.implementation("console")
            class ConsoleRenderer(Renderer):
                def render(self, value: str) -> None:
                    print(value)

        Retrieval.

        .. code-block:: python

            renderer_type = RendererRegistry.get("console")
            renderer = RendererRegistry.instantiate("console")

            assert renderer_type is ConsoleRenderer
            assert isinstance(renderer, Renderer)
            assert RendererRegistry.contains("CONSOLE")

        Registry isolation.

        .. code-block:: python

            class Exporter(ABC):
                pass


            class ExporterRegistry(ImplementationRegistry[Exporter]):
                implementation_base = Exporter


            assert RendererRegistry.count() == 1
            assert ExporterRegistry.count() == 0
    """

    implementation_base: ClassVar[type[Any] | None] = None

    # ClassVar cannot accurately express the per-subclass generic parameter.
    # Values are validated when registered and cast at the public boundary.
    _registry: ClassVar[dict[str, type[Any]]] = {}
    _lock: ClassVar[threading.RLock] = threading.RLock()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Give every registry subclass independent storage and synchronization.
        """
        super().__init_subclass__(**kwargs)
        cls._registry = {}
        cls._lock = threading.RLock()

    @classmethod
    def _require_implementation_base(cls) -> type[Any]:
        """
        Return the configured implementation base.

        Raises:
            TypeError: If the registry has no implementation base.
        """
        implementation_base = cls.implementation_base

        if implementation_base is None:
            raise TypeError(
                f"{cls.__qualname__} must define 'implementation_base'"
            )

        return implementation_base

    @classmethod
    def _normalize_name(cls, name: str) -> str:
        """
        Normalize and validate a registry name.

        Subclasses may override this method to provide a different naming
        policy.

        Args:
            name: Registry name to normalize.

        Returns:
            The normalized registry name.

        Raises:
            TypeError: If the name is not a string.
            ValueError: If the normalized name is empty.
        """
        if not isinstance(name, str):
            raise TypeError("Implementation name must be a string")

        normalized = name.strip().casefold()

        if not normalized:
            raise ValueError("Implementation name cannot be empty")

        return normalized

    @classmethod
    def _infer_name(cls, impl_class: type[ImplementationT]) -> str:
        """
        Infer a registration name from an implementation class.
        """
        return cls._normalize_name(impl_class.__name__)

    @classmethod
    def _validate_implementation(
        cls,
        impl_class: type[ImplementationT],
    ) -> None:
        """
        Validate an implementation class before registration.

        Subclasses may override this method to add custom validation.

        Raises:
            TypeError: If the value is not a class or does not derive from
                ``implementation_base``.
        """
        if not isinstance(impl_class, type):
            raise TypeError(
                "Expected an implementation class, "
                f"got {type(impl_class).__qualname__}"
            )

        implementation_base = cls._require_implementation_base()

        if not issubclass(impl_class, implementation_base):
            raise TypeError(
                f"{impl_class.__qualname__} must subclass "
                f"{implementation_base.__qualname__}"
            )

    @classmethod
    def register(
        cls,
        name: str,
        impl_class: type[ImplementationT],
        *,
        replace: bool = False,
    ) -> None:
        """
        Register an implementation class.

        Args:
            name: Name under which the implementation will be registered.
            impl_class: Implementation class to register.
            replace: Replace an existing registration with the same name.

        Raises:
            TypeError: If the implementation is invalid.
            ValueError: If the name is invalid.
            KeyError: If the name is already registered and replacement is
                disabled.
        """
        normalized_name = cls._normalize_name(name)
        cls._validate_implementation(impl_class)

        with cls._lock:
            if not replace and normalized_name in cls._registry:
                raise KeyError(
                    f"Implementation '{normalized_name}' is already registered"
                )

            cls._registry[normalized_name] = impl_class

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> type[ImplementationT] | None:
        """
        Remove an implementation registration.

        Args:
            name: Name of the implementation to remove.

        Returns:
            The removed implementation class, or ``None`` if it was not
            registered.
        """
        normalized_name = cls._normalize_name(name)

        with cls._lock:
            impl_class = cls._registry.pop(normalized_name, None)

        return cast(type[ImplementationT] | None, impl_class)

    @classmethod
    def implementation(
        cls,
        name: str | None = None,
        *,
        replace: bool = False,
    ) -> Callable[
        [type[ImplementationT]],
        type[ImplementationT],
    ]:
        """
        Create an implementation-registration decorator.

        Args:
            name: Optional explicit registration name.
            replace: Replace an existing registration with the same name.
        """

        def decorator(
            impl_class: type[ImplementationT],
        ) -> type[ImplementationT]:
            registration_name = (
                cls._infer_name(impl_class) if name is None else name
            )

            cls.register(
                registration_name,
                impl_class,
                replace=replace,
            )

            return impl_class

        return decorator

    @classmethod
    def get(cls, name: str) -> type[ImplementationT]:
        """
        Retrieve an implementation class.

        Args:
            name: Name of the implementation to retrieve.

        Returns:
            The registered implementation class.

        Raises:
            KeyError: If the implementation is not registered.
        """
        normalized_name = cls._normalize_name(name)

        with cls._lock:
            try:
                impl_class = cls._registry[normalized_name]
            except KeyError as error:
                raise KeyError(
                    f"Unknown implementation '{normalized_name}'"
                ) from error

        return cast(type[ImplementationT], impl_class)

    @classmethod
    def try_get(
        cls,
        name: str,
    ) -> type[ImplementationT] | None:
        """
        Retrieve an implementation class when present.

        Args:
            name: Name of the implementation to retrieve.

        Returns:
            The registered implementation class, or ``None``.
        """
        normalized_name = cls._normalize_name(name)

        with cls._lock:
            impl_class = cls._registry.get(normalized_name)

        return cast(type[ImplementationT] | None, impl_class)

    @classmethod
    def contains(cls, name: str) -> bool:
        """
        Determine whether an implementation is registered.
        """
        normalized_name = cls._normalize_name(name)

        with cls._lock:
            return normalized_name in cls._registry

    @classmethod
    def implementations(
        cls,
    ) -> Mapping[str, type[ImplementationT]]:
        """
        Return an immutable snapshot of registered implementations.
        """
        with cls._lock:
            snapshot = MappingProxyType(dict(cls._registry))

        return cast(
            Mapping[str, type[ImplementationT]],
            snapshot,
        )

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """
        Return an immutable snapshot of registered names.
        """
        with cls._lock:
            return tuple(cls._registry)

    @classmethod
    def count(cls) -> int:
        """
        Return the number of registered implementations.
        """
        with cls._lock:
            return len(cls._registry)

    @classmethod
    def instantiate(
        cls,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> ImplementationT:
        """
        Instantiate a registered implementation.

        Constructor arguments cannot be statically validated because different
        implementations may expose different constructor signatures.
        """
        impl_class = cls.get(name)
        constructor = cast(Callable[..., ImplementationT], impl_class)

        return constructor(*args, **kwargs)

    @classmethod
    def clear(cls) -> None:
        """
        Remove every implementation from this registry.
        """
        with cls._lock:
            cls._registry.clear()
