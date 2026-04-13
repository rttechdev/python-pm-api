"""
Pydantic schemas for organization and membership operations.

This module defines the request and response schemas used by the organization API.
"""

from pydantic import BaseModel, Field

class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""
    name: str = Field(..., min_length=1, description="Organization name")

class OrganizationResponse(BaseModel):
    """Schema for returning organization data."""
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True

class MembershipCreate(BaseModel):
    """Schema for creating a membership in an organization."""
    user_id: int
    role: str = Field("member", pattern="^(admin|member)$")

class MembershipResponse(BaseModel):
    """Schema for returning membership data."""
    id: int
    user_id: int
    organization_id: int
    role: str

    class Config:
        from_attributes = True