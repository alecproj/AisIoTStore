from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


@dataclass(frozen=True, slots=True)
class Product:
    id: str
    name: str
    price: Decimal


@dataclass(slots=True)
class CartItem:
    product_id: str
    quantity: int


@dataclass(slots=True)
class Cart:
    items: list[CartItem] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def add_item(self, product_id: str, quantity: int) -> None:
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product_id=product_id, quantity=quantity))

    def clear(self) -> None:
        self.items.clear()


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"


@dataclass(slots=True)
class Order:
    id: str
    items: list[CartItem]
    status: OrderStatus = OrderStatus.CREATED


@dataclass(frozen=True, slots=True)
class Device:
    id: str
    product_id: str
    serial_number: str


@dataclass(frozen=True, slots=True)
class Firmware:
    version: str
    download_url: str
