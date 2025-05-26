from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

class TicketBase(BaseModel):
    movie: str = Field(..., description="Movie name", alias="Movie")
    theatre_seat: str = Field(..., description="Theatre seat identifier", alias="Theatre-Seat")
    price: Optional[Decimal] = Field(None, description="Ticket price", alias="Price")
    customer_name: Optional[str] = Field(None, description="Customer name", alias="CustomerName")
    booking_date: Optional[str] = Field(None, description="Booking date", alias="BookingDate")

    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: float
        }

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    theatre_seat: str = Field(..., description="Theatre seat identifier", alias="Theatre-Seat")
    update_key: str = Field(..., description="Field to update", alias="updateKey")
    update_value: Any = Field(..., description="New value", alias="updateValue")

    class Config:
        populate_by_name = True

class TicketDelete(BaseModel):
    theatre_seat: str = Field(..., description="Theatre seat identifier", alias="Theatre-Seat")

    class Config:
        populate_by_name = True

class TicketResponse(TicketBase):
    previous_price: Optional[Decimal] = Field(None, alias="PreviousPrice")
    last_price_change_timestamp: Optional[str] = Field(None, alias="LastPriceChangeTimestamp")
    discount_percentage: Optional[Decimal] = Field(None, alias="DiscountPercentage")
    is_discounted: Optional[bool] = Field(None, alias="IsDiscounted")

class PriceChangeEvent(BaseModel):
    event_type: str = Field(..., alias="eventType")
    theatre_seat: str = Field(..., alias="theatreSeat")
    movie: str
    old_price: Optional[float] = Field(None, alias="oldPrice")
    new_price: float = Field(..., alias="newPrice")
    timestamp: str
    updated_item: Optional[Dict[str, Any]] = Field(None, alias="updatedItem")
