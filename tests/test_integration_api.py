from app.domain.entities import Device, OrderStatus
from app.presentation.dependencies import container


def test_full_user_journey_from_health_to_ota_and_internal_side_effects(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    catalog = client.get("/catalog")
    assert catalog.status_code == 200
    catalog_payload = catalog.json()
    assert len(catalog_payload) == 3
    assert {item["id"] for item in catalog_payload} == {
        "sensor-001",
        "hub-001",
        "camera-001",
    }
    assert {item["name"] for item in catalog_payload} == {
        "Temperature Sensor",
        "Smart Hub",
        "Indoor Camera",
    }

    empty_cart = client.get("/cart")
    assert empty_cart.status_code == 200
    assert empty_cart.json() == {"items": []}

    add_sensor = client.post(
        "/cart/items", json={"product_id": "sensor-001", "quantity": 2}
    )
    assert add_sensor.status_code == 200
    assert add_sensor.json() == {"items": [{"product_id": "sensor-001", "quantity": 2}]}

    add_same_sensor = client.post(
        "/cart/items", json={"product_id": "sensor-001", "quantity": 1}
    )
    assert add_same_sensor.status_code == 200
    assert add_same_sensor.json() == {
        "items": [{"product_id": "sensor-001", "quantity": 3}]
    }

    add_hub = client.post("/cart/items", json={"product_id": "hub-001", "quantity": 1})
    assert add_hub.status_code == 200
    assert add_hub.json() == {
        "items": [
            {"product_id": "sensor-001", "quantity": 3},
            {"product_id": "hub-001", "quantity": 1},
        ]
    }

    cart = client.get("/cart")
    assert cart.status_code == 200
    assert cart.json() == {
        "items": [
            {"product_id": "sensor-001", "quantity": 3},
            {"product_id": "hub-001", "quantity": 1},
        ]
    }

    create_order = client.post("/orders")
    assert create_order.status_code == 201
    order_payload = create_order.json()
    assert order_payload["id"]
    assert order_payload["items"] == [
        {"product_id": "sensor-001", "quantity": 3},
        {"product_id": "hub-001", "quantity": 1},
    ]
    order_id = order_payload["id"]

    assert client.get("/cart").json() == {"items": []}
    assert container.order_repo.get(order_id).status == OrderStatus.CREATED
    assert len(container.device_repo._devices) == 0

    payment = client.post("/payments", json={"order_id": order_id})
    assert payment.status_code == 200
    assert payment.json() == {"status": "PAID"}
    assert container.order_repo.get(order_id).status == OrderStatus.PAID

    devices = list(container.device_repo._devices.values())
    assert len(devices) == 4
    assert sorted(device.product_id for device in devices) == [
        "hub-001",
        "sensor-001",
        "sensor-001",
        "sensor-001",
    ]
    assert sorted(device.serial_number for device in devices) == [
        "SN-HUB-2001",
        "SN-SENSOR-1001",
        "SN-SENSOR-1002",
        "SN-SENSOR-1003",
    ]
    assert container.inventory_port._inventory["sensor-001"] == []
    assert container.inventory_port._inventory["hub-001"] == ["SN-HUB-2002"]

    paid_again = client.post("/payments", json={"order_id": order_id})
    assert paid_again.status_code == 409
    assert paid_again.json() == {"detail": "Заказ уже оплачен"}

    first_device = devices[0]
    ota = client.get("/ota", params={"device_id": first_device.id})
    assert ota.status_code == 200
    if first_device.product_id == "sensor-001":
        assert ota.json() == {
            "version": "1.2.0",
            "download_url": "https://example.com/fw/sensor-001/1.2.0.bin",
        }
    else:
        assert ota.json() == {
            "version": "2.5.1",
            "download_url": "https://example.com/fw/hub-001/2.5.1.bin",
        }


def test_api_error_paths_cover_validation_not_found_and_conflict_branches(client):
    empty_order = client.post("/orders")
    assert empty_order.status_code == 400
    assert empty_order.json() == {"detail": "Корзина пуста"}

    invalid_quantity = client.post(
        "/cart/items", json={"product_id": "sensor-001", "quantity": 0}
    )
    assert invalid_quantity.status_code == 422
    assert invalid_quantity.json()["detail"][0]["loc"] == ["body", "quantity"]

    unknown_product = client.post(
        "/cart/items", json={"product_id": "ghost-999", "quantity": 1}
    )
    assert unknown_product.status_code == 404
    assert unknown_product.json() == {"detail": "Товар не найден"}

    missing_payment_order = client.post("/payments", json={"order_id": "missing-order"})
    assert missing_payment_order.status_code == 404
    assert missing_payment_order.json() == {"detail": "Заказ не найден"}

    missing_ota_query = client.get("/ota")
    assert missing_ota_query.status_code == 422
    assert missing_ota_query.json()["detail"][0]["loc"] == ["query", "device_id"]

    unknown_device = client.get("/ota", params={"device_id": "missing-device"})
    assert unknown_device.status_code == 404
    assert unknown_device.json() == {"detail": "Устройство не найдено"}

    add_camera = client.post(
        "/cart/items", json={"product_id": "camera-001", "quantity": 1}
    )
    assert add_camera.status_code == 200

    create_order = client.post("/orders")
    assert create_order.status_code == 201
    broken_order_id = create_order.json()["id"]

    container.order_repo._orders[broken_order_id].status = "BROKEN"
    invalid_status_payment = client.post(
        "/payments", json={"order_id": broken_order_id}
    )
    assert invalid_status_payment.status_code == 400
    assert invalid_status_payment.json() == {"detail": "Заказ не может быть оплачен"}

    custom_device = Device(
        id="device-without-firmware",
        product_id="unknown-product",
        serial_number="SN-NO-FW-1",
    )
    container.device_repo.save(custom_device)
    missing_firmware = client.get("/ota", params={"device_id": custom_device.id})
    assert missing_firmware.status_code == 404
    assert missing_firmware.json() == {"detail": "Прошивка не найдена"}


def test_payment_failure_on_inventory_shortage_keeps_order_unpaid_and_exposes_partial_side_effects(
    client,
):
    add_hubs = client.post("/cart/items", json={"product_id": "hub-001", "quantity": 3})
    assert add_hubs.status_code == 200
    assert add_hubs.json() == {"items": [{"product_id": "hub-001", "quantity": 3}]}

    create_order = client.post("/orders")
    assert create_order.status_code == 201
    order_id = create_order.json()["id"]

    payment = client.post("/payments", json={"order_id": order_id})
    assert payment.status_code == 409
    assert payment.json() == {"detail": "Невозможно зарезервировать устройство"}

    stored_order = container.order_repo.get(order_id)
    assert stored_order.status == OrderStatus.CREATED

    created_devices = list(container.device_repo._devices.values())
    assert len(created_devices) == 2
    assert [device.serial_number for device in created_devices] == [
        "SN-HUB-2001",
        "SN-HUB-2002",
    ]
    assert container.inventory_port._inventory["hub-001"] == []
