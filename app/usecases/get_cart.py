from app.domain.entities import Cart
from app.ports.repositories import CartRepository


class GetCart:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    def execute(self) -> Cart:
        return self._cart_repo.get()
