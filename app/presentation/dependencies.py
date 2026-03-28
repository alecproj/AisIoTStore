from __future__ import annotations

from dataclasses import dataclass

from app.adapters.in_memory import (
    InMemoryCartRepository,
    InMemoryDeviceRepository,
    InMemoryFirmwareRepository,
    InMemoryInventoryPort,
    InMemoryOrderRepository,
    InMemoryProductRepository,
)
from app.usecases.add_to_cart import AddToCart
from app.usecases.create_order import CreateOrder
from app.usecases.get_cart import GetCart
from app.usecases.get_catalog import GetCatalog
from app.usecases.get_ota import GetOta
from app.usecases.handle_payment import HandlePayment


@dataclass(slots=True)
class Container:
    product_repo: InMemoryProductRepository
    cart_repo: InMemoryCartRepository
    order_repo: InMemoryOrderRepository
    inventory_port: InMemoryInventoryPort
    device_repo: InMemoryDeviceRepository
    firmware_repo: InMemoryFirmwareRepository


container = Container(
    product_repo=InMemoryProductRepository(),
    cart_repo=InMemoryCartRepository(),
    order_repo=InMemoryOrderRepository(),
    inventory_port=InMemoryInventoryPort(),
    device_repo=InMemoryDeviceRepository(),
    firmware_repo=InMemoryFirmwareRepository(),
)


def get_catalog_uc() -> GetCatalog:
    return GetCatalog(product_repo=container.product_repo)


def add_to_cart_uc() -> AddToCart:
    return AddToCart(product_repo=container.product_repo, cart_repo=container.cart_repo)


def get_cart_uc() -> GetCart:
    return GetCart(cart_repo=container.cart_repo)


def create_order_uc() -> CreateOrder:
    return CreateOrder(
        cart_repo=container.cart_repo,
        order_repo=container.order_repo,
        inventory_port=container.inventory_port,
    )


def handle_payment_uc() -> HandlePayment:
    return HandlePayment(
        order_repo=container.order_repo,
        inventory_port=container.inventory_port,
        device_repo=container.device_repo,
    )


def get_ota_uc() -> GetOta:
    return GetOta(
        device_repo=container.device_repo, firmware_repo=container.firmware_repo
    )
