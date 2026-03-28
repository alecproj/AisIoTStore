from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from app.domain.entities import Order
from app.domain.exceptions import ValidationError
from app.ports.repositories import CartRepository, InventoryPort, OrderRepository


class CreateOrder:
    def __init__(
        self,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        inventory_port: InventoryPort,
    ) -> None:
        self._cart_repo = cart_repo
        self._order_repo = order_repo
        self._inventory_port = inventory_port

    def execute(self) -> Order:
        cart = self._cart_repo.get()
        if cart.is_empty():
            raise ValidationError("Корзина пуста")

        # Схема включает InventoryPort в качестве зависимости для данного use case, поэтому порт был внедрен.
        # Логика резервации была упрощена в учебных целях, поэтому не используется в данной реализации.
        # Резервация выполняется во время оплаты.
        _ = self._inventory_port

        order = Order(id=str(uuid4()), items=deepcopy(cart.items))
        saved = self._order_repo.save(order)
        self._cart_repo.clear()
        return saved
