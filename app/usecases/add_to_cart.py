from app.domain.entities import Cart
from app.domain.exceptions import NotFoundError, ValidationError
from app.ports.repositories import CartRepository, ProductRepository


class AddToCart:
    def __init__(
        self, product_repo: ProductRepository, cart_repo: CartRepository
    ) -> None:
        self._product_repo = product_repo
        self._cart_repo = cart_repo

    def execute(self, product_id: str, quantity: int) -> Cart:
        if quantity <= 0:
            raise ValidationError("Количество должно быть больше 0")

        product = self._product_repo.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Товар не найден")

        cart = self._cart_repo.get()
        cart.add_item(product_id=product_id, quantity=quantity)
        return self._cart_repo.save(cart)
