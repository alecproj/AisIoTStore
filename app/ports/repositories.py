from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Cart, Device, Firmware, Order, Product


class ProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product | None:
        raise NotImplementedError


class CartRepository(ABC):
    @abstractmethod
    def get(self) -> Cart:
        raise NotImplementedError

    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    def get(self, order_id: str) -> Order | None:
        raise NotImplementedError


class InventoryPort(ABC):
    @abstractmethod
    def reserve(self, product_id: str) -> str | None:
        """Резервация одной единицы устройства и возврат его серийного номера."""
        raise NotImplementedError


class DeviceRepository(ABC):
    @abstractmethod
    def save(self, device: Device) -> Device:
        raise NotImplementedError

    @abstractmethod
    def get(self, device_id: str) -> Device | None:
        raise NotImplementedError


class FirmwareRepository(ABC):
    @abstractmethod
    def get_latest_for_product(self, product_id: str) -> Firmware | None:
        raise NotImplementedError
