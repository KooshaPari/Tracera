"""SQLAlchemy ORM models for domain entities.

These models map domain entities to database tables while maintaining the separation
between domain and infrastructure.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserModel(Base):
    """
    SQLAlchemy model for User entity.
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email})>"


class DeploymentModel(Base):
    """
    SQLAlchemy model for Deployment entity.
    """

    __tablename__ = "deployments"

    id = Column(String(36), primary_key=True)
    environment = Column(String(50), nullable=False, index=True)
    strategy = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<DeploymentModel(id={self.id}, environment={self.environment}, status={self.status})>"
        )


class ServiceModel(Base):
    """
    SQLAlchemy model for Service entity.
    """

    __tablename__ = "services"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    port = Column(Integer, nullable=False)
    protocol = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ServiceModel(id={self.id}, name={self.name}, status={self.status})>"


class ConfigurationModel(Base):
    """
    SQLAlchemy model for Configuration entity.
    """

    __tablename__ = "configurations"

    key = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=False)
    value_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ConfigurationModel(key={self.key})>"
