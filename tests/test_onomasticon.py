from __future__ import annotations

from abc import ABC

import pytest

from onomasticon import ImplementationRegistry as PublicImplementationRegistry
from onomasticon.onomasticon import ImplementationRegistry


class Animal(ABC):
    pass


class Vehicle(ABC):
    pass


class AnimalRegistry(ImplementationRegistry[Animal]):
    implementation_base = Animal


class VehicleRegistry(ImplementationRegistry[Vehicle]):
    implementation_base = Vehicle


class Dog(Animal):
    def __init__(self, name: str) -> None:
        self.name = name


class Wolf(Animal):
    pass


class Car(Vehicle):
    pass


@pytest.fixture(autouse=True)
def clear_test_registries() -> None:
    AnimalRegistry.clear()
    VehicleRegistry.clear()
    yield
    AnimalRegistry.clear()
    VehicleRegistry.clear()


def test_register_normalizes_name_and_retrieves_implementation() -> None:
    AnimalRegistry.register("  DOG  ", Dog)

    assert AnimalRegistry.get("dog") is Dog
    assert AnimalRegistry.get("DOG") is Dog
    assert AnimalRegistry.contains(" dog ")


def test_package_root_exports_implementation_registry() -> None:
    assert PublicImplementationRegistry is ImplementationRegistry


def test_register_rejects_duplicate_name_without_replace() -> None:
    AnimalRegistry.register("dog", Dog)

    with pytest.raises(
        KeyError,
        match="Implementation 'dog' is already registered",
    ):
        AnimalRegistry.register("DOG", Wolf)


def test_register_replace_overwrites_existing_registration() -> None:
    AnimalRegistry.register("dog", Dog)
    AnimalRegistry.register("DOG", Wolf, replace=True)

    assert AnimalRegistry.get("dog") is Wolf


def test_register_rejects_non_string_and_empty_names() -> None:
    with pytest.raises(TypeError, match="Implementation name must be a string"):
        AnimalRegistry.register(123, Dog)  # type: ignore[arg-type]

    with pytest.raises(
        ValueError,
        match="Implementation name cannot be empty",
    ):
        AnimalRegistry.register("   ", Dog)


def test_register_rejects_non_class_and_wrong_subclass() -> None:
    with pytest.raises(
        TypeError,
        match="Expected an implementation class, got function",
    ):
        AnimalRegistry.register("dog", lambda: None)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Car must subclass Animal"):
        AnimalRegistry.register("car", Car)  # type: ignore[arg-type]


def test_implementation_decorator_infers_class_name() -> None:
    @AnimalRegistry.implementation()
    class Fox(Animal):
        pass

    assert AnimalRegistry.get("fox") is Fox


def test_implementation_decorator_supports_explicit_name_and_replace() -> None:
    @AnimalRegistry.implementation("dog")
    class FirstDog(Animal):
        pass

    @AnimalRegistry.implementation("DOG", replace=True)
    class SecondDog(Animal):
        pass

    assert AnimalRegistry.get("dog") is SecondDog
    assert AnimalRegistry.try_get("DOG") is SecondDog
    assert AnimalRegistry.try_get("missing") is None


def test_get_raises_for_unknown_implementation() -> None:
    with pytest.raises(KeyError, match="Unknown implementation 'dog'"):
        AnimalRegistry.get("dog")


def test_unregister_returns_removed_class_and_none_when_missing() -> None:
    AnimalRegistry.register("dog", Dog)

    assert AnimalRegistry.unregister("DOG") is Dog
    assert AnimalRegistry.unregister("dog") is None


def test_implementations_returns_immutable_snapshot() -> None:
    AnimalRegistry.register("dog", Dog)
    snapshot = AnimalRegistry.implementations()

    AnimalRegistry.register("wolf", Wolf)

    assert dict(snapshot) == {"dog": Dog}
    assert AnimalRegistry.implementations()["wolf"] is Wolf

    with pytest.raises(TypeError):
        snapshot["wolf"] = Wolf  # type: ignore[index]


def test_names_and_count_reflect_current_registry_state() -> None:
    AnimalRegistry.register("dog", Dog)
    AnimalRegistry.register("wolf", Wolf)

    assert AnimalRegistry.names() == ("dog", "wolf")
    assert AnimalRegistry.count() == 2

    AnimalRegistry.clear()

    assert AnimalRegistry.names() == ()
    assert AnimalRegistry.count() == 0


def test_instantiate_constructs_registered_implementation() -> None:
    AnimalRegistry.register("dog", Dog)

    instance = AnimalRegistry.instantiate("dog", "Fido")

    assert isinstance(instance, Dog)
    assert instance.name == "Fido"


def test_subclasses_have_isolated_registries() -> None:
    AnimalRegistry.register("dog", Dog)
    VehicleRegistry.register("car", Car)

    assert AnimalRegistry.contains("dog")
    assert not AnimalRegistry.contains("car")
    assert VehicleRegistry.contains("car")
    assert not VehicleRegistry.contains("dog")


def test_registry_without_implementation_base_raises_when_used() -> None:
    class MissingBaseRegistry(ImplementationRegistry[Animal]):
        pass

    with pytest.raises(
        TypeError,
        match="MissingBaseRegistry must define 'implementation_base'",
    ):
        MissingBaseRegistry.register("dog", Dog)
