"""
Organization-related database models.

This module defines the Organization and Membership models used to manage
organization ownership and user membership within organizations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class Organization(Base):
    """Organization database model."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="owned_organizations")
    memberships = relationship("Membership", back_populates="organization")

class Membership(Base):
    """Membership database model."""
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(String, nullable=False, default="member")

    user = relationship("User", backref="memberships")
    organization = relationship("Organization", back_populates="memberships")