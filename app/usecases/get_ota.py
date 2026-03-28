from app.domain.entities import Firmware
from app.domain.exceptions import NotFoundError
from app.ports.repositories import DeviceRepository, FirmwareRepository


class GetOta:
    def __init__(
        self, device_repo: DeviceRepository, firmware_repo: FirmwareRepository
    ) -> None:
        self._device_repo = device_repo
        self._firmware_repo = firmware_repo

    def execute(self, device_id: str) -> Firmware:
        device = self._device_repo.get(device_id)
        if device is None:
            raise NotFoundError("Устройство не найдено")

        firmware = self._firmware_repo.get_latest_for_product(device.product_id)
        if firmware is None:
            raise NotFoundError("Прошивка не найдена")
        return firmware
