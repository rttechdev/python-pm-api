"""
Pydantic schemas for BigQuery sales data operations.

This module defines the data models for sales data retrieved from BigQuery,
including validation and response models for various analytics endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime


class SalesData(BaseModel):
    """Schema for individual sales record."""
    order_id: Union[str, int] = Field(..., description="Order ID (can be string or integer)")
    product: str
    category: str
    price: float
    quantity: int
    order_date: datetime

    class Config:
        from_attributes = True


class SalesDataResponse(BaseModel):
    """Response model for sales data queries."""
    data: List[SalesData]
    total_records: int


class RevenuePerProduct(BaseModel):
    """Schema for revenue per product analytics."""
    product: str
    total_revenue: float
    total_quantity: int


class CategorySales(BaseModel):
    """Schema for category-wise sales analytics."""
    category: str
    total_revenue: float
    total_quantity: int
    product_count: int


class TopSellingProduct(BaseModel):
    """Schema for top selling products analytics."""
    product: str
    category: str
    total_quantity: int
    total_revenue: float


class AnalyticsResponse(BaseModel):
    """Generic response model for analytics endpoints."""
    data: List[dict]
    total_records: int