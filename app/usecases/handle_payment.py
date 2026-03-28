from __future__ import annotations

from uuid import uuid4

from app.domain.entities import Device, OrderStatus
from app.domain.exceptions import ConflictError, NotFoundError, ValidationError
from app.ports.repositories import DeviceRepository, InventoryPort, OrderRepository


class HandlePayment:
    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_port: InventoryPort,
        device_repo: DeviceRepository,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_port = inventory_port
        self._device_repo = device_repo

    def execute(self, order_id: str) -> dict[str, str]:
        order = self._order_repo.get(order_id)
        if order is None:
            raise NotFoundError("Заказ не найден")

        if order.status == OrderStatus.PAID:
            raise ConflictError("Заказ уже оплачен")
        if order.status != OrderStatus.CREATED:
            raise ValidationError("Заказ не может быть оплачен")

        for item in order.items:
            for _ in range(item.quantity):
                serial_number = self._inventory_port.reserve(item.product_id)
                if serial_number is None:
                    raise ConflictError("Невозможно зарезервировать устройство")
                device = Device(
                    id=str(uuid4()),
                    product_id=item.product_id,
                    serial_number=serial_number,
                )
                self._device_repo.save(device)

        order.status = OrderStatus.PAID
        self._order_repo.save(order)
        return {"status": OrderStatus.PAID.value}
