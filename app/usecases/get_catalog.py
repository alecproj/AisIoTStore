from app.domain.entities import Product
from app.ports.repositories import ProductRepository


class GetCatalog:
    def __init__(self, product_repo: ProductRepository) -> None:
        self._product_repo = product_repo

    def execute(self) -> list[Product]:
        return self._product_repo.get_all()
