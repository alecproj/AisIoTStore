from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

from app.domain.entities import Cart, Device, Firmware, Order, Product
from app.ports.repositories import (
    CartRepository,
    DeviceRepository,
    FirmwareRepository,
    InventoryPort,
    OrderRepository,
    ProductRepository,
)


class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[str, Product] = {
            "sensor-001": Product(
                id="sensor-001", name="Temperature Sensor", price=Decimal("49.99")
            ),
            "hub-001": Product(id="hub-001", name="Smart Hub", price=Decimal("129.99")),
            "camera-001": Product(
                id="camera-001", name="Indoor Camera", price=Decimal("89.99")
            ),
        }

    def get_all(self) -> list[Product]:
        return list(self._products.values())

    def get_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)


class InMemoryCartRepository(CartRepository):
    def __init__(self) -> None:
        self._cart = Cart()

    def get(self) -> Cart:
        return deepcopy(self._cart)

    def save(self, cart: Cart) -> Cart:
        self._cart = deepcopy(cart)
        return deepcopy(self._cart)

    def clear(self) -> None:
        self._cart = Cart()


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def save(self, order: Order) -> Order:
        self._orders[order.id] = deepcopy(order)
        return deepcopy(order)

    def get(self, order_id: str) -> Order | None:
        order = self._orders.get(order_id)
        return deepcopy(order) if order else None


class InMemoryInventoryPort(InventoryPort):
    def __init__(self) -> None:
        self._inventory: dict[str, list[str]] = {
            "sensor-001": ["SN-SENSOR-1001", "SN-SENSOR-1002", "SN-SENSOR-1003"],
            "hub-001": ["SN-HUB-2001", "SN-HUB-2002"],
            "camera-001": ["SN-CAM-3001", "SN-CAM-3002"],
        }

    def reserve(self, product_id: str) -> str | None:
        available = self._inventory.get(product_id, [])
        if not available:
            return None
        return available.pop(0)


class InMemoryDeviceRepository(DeviceRepository):
    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}

    def save(self, device: Device) -> Device:
        self._devices[device.id] = device
        return device

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)


class InMemoryFirmwareRepository(FirmwareRepository):
    def __init__(self) -> None:
        self._firmware_by_product: dict[str, Firmware] = {
            "sensor-001": Firmware(
                version="1.2.0",
                download_url="https://example.com/fw/sensor-001/1.2.0.bin",
            ),
            "hub-001": Firmware(
                version="2.5.1", download_url="https://example.com/fw/hub-001/2.5.1.bin"
            ),
            "camera-001": Firmware(
                version="3.1.4",
                download_url="https://example.com/fw/camera-001/3.1.4.bin",
            ),
        }

    def get_latest_for_product(self, product_id: str) -> Firmware | None:
        return self._firmware_by_product.get(product_id)
