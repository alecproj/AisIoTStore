from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.domain.exceptions import ConflictError, NotFoundError, ValidationError
from app.presentation.dependencies import (
    add_to_cart_uc,
    create_order_uc,
    get_cart_uc,
    get_catalog_uc,
    get_ota_uc,
    handle_payment_uc,
)
from app.presentation.schemas import (
    AddCartItemRequest,
    CartResponse,
    FirmwareResponse,
    OrderResponse,
    PaymentRequest,
    PaymentResponse,
    ProductResponse,
)
from app.usecases.add_to_cart import AddToCart
from app.usecases.create_order import CreateOrder
from app.usecases.get_cart import GetCart
from app.usecases.get_catalog import GetCatalog
from app.usecases.get_ota import GetOta
from app.usecases.handle_payment import HandlePayment

router = APIRouter()


@router.get("/catalog", response_model=list[ProductResponse])
def get_catalog(uc: GetCatalog = Depends(get_catalog_uc)):
    return uc.execute()


@router.post("/cart/items", response_model=CartResponse)
def add_to_cart(payload: AddCartItemRequest, uc: AddToCart = Depends(add_to_cart_uc)):
    try:
        return uc.execute(product_id=payload.product_id, quantity=payload.quantity)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/cart", response_model=CartResponse)
def get_cart(uc: GetCart = Depends(get_cart_uc)):
    return uc.execute()


@router.post(
    "/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
def create_order(uc: CreateOrder = Depends(create_order_uc)):
    try:
        return uc.execute()
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.post("/payments", response_model=PaymentResponse)
def handle_payment(
    payload: PaymentRequest, uc: HandlePayment = Depends(handle_payment_uc)
):
    try:
        return uc.execute(order_id=payload.order_id)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.get("/ota", response_model=FirmwareResponse)
def get_ota(
    device_id: str = Query(...),
    uc: GetOta = Depends(get_ota_uc),
):
    try:
        return uc.execute(device_id=device_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
