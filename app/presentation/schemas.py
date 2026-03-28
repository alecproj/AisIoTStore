from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    price: float


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    quantity: int


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[CartItemResponse]


class AddCartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    items: list[CartItemResponse]


class PaymentRequest(BaseModel):
    order_id: str


class PaymentResponse(BaseModel):
    status: str


class FirmwareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version: str
    download_url: str
