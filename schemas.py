"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# PDAM App Schemas

class Customer(BaseModel):
    """
    Customers collection schema
    Collection name: "customer"
    """
    name: str = Field(..., description="Nama pelanggan")
    address: str = Field(..., description="Alamat pelanggan")
    meter_number: str = Field(..., description="Nomor meter air")
    qrcode_value: str = Field(..., description="Nilai QR unik yang ditanam pada meter / kartu pelanggan")
    phone: Optional[str] = Field(None, description="Nomor telepon pelanggan")
    is_active: bool = Field(True, description="Status aktif pelanggan")

class Reading(BaseModel):
    """
    Readings collection schema
    Collection name: "reading"
    """
    customer_id: str = Field(..., description="ID pelanggan (string ObjectId)")
    current_reading: float = Field(..., ge=0, description="Angka meter saat ini")
    operator_name: Optional[str] = Field(None, description="Nama petugas pencatat")
    notes: Optional[str] = Field(None, description="Catatan tambahan")
    reading_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Tanggal pencatatan")
