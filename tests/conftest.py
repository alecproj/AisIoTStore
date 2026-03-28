import pytest
from fastapi.testclient import TestClient

from app.adapters.in_memory import (
    InMemoryCartRepository,
    InMemoryDeviceRepository,
    InMemoryFirmwareRepository,
    InMemoryInventoryPort,
    InMemoryOrderRepository,
    InMemoryProductRepository,
)
from app.main import app
from app.presentation.dependencies import container


@pytest.fixture(autouse=True)
def reset_container_state():
    container.product_repo = InMemoryProductRepository()
    container.cart_repo = InMemoryCartRepository()
    container.order_repo = InMemoryOrderRepository()
    container.inventory_port = InMemoryInventoryPort()
    container.device_repo = InMemoryDeviceRepository()
    container.firmware_repo = InMemoryFirmwareRepository()
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
