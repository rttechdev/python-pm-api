"""
Organization API endpoints.

This module provides endpoints for creating organizations and managing membership.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organization import Organization, Membership
from app.models.user import User
from app.schemas.organization import (
    MembershipCreate,
    MembershipResponse,
    OrganizationCreate,
    OrganizationResponse,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/", response_model=OrganizationResponse, summary="Create an organization")
def create_organization(
    organization: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new organization.

    The authenticated user becomes the owner of the organization.
    """
    org = Organization(name=organization.name, owner_id=current_user.id)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create an owner membership as admin
    membership = Membership(
        user_id=current_user.id,
        organization_id=org.id,
        role="admin",
    )
    db.add(membership)
    db.commit()

    return org

@router.post("/{organization_id}/members", response_model=MembershipResponse, summary="Add a user to an organization")
def add_organization_member(
    organization_id: int,
    membership_in: MembershipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a user to an organization.

    Only the organization owner may add members.
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if organization.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the organization owner can add members")

    user = db.query(User).filter(User.id == membership_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(Membership)
        .filter(
            Membership.user_id == membership_in.user_id,
            Membership.organization_id == organization_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this organization")

    membership = Membership(
        user_id=membership_in.user_id,
        organization_id=organization_id,
        role=membership_in.role,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership