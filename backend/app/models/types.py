"""Portable column types for Postgres + SQLite (tests)."""

from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
import uuid
from sqlalchemy import Uuid as SA_UUID


class PortableJSON(TypeDecorator):
    """JSONB on PostgreSQL, generic JSON elsewhere (e.g. SQLite tests)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class PortableUUID(TypeDecorator):
    """UUID that works on SQLite and PostgreSQL."""

    impl = SA_UUID
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(SA_UUID(as_uuid=True))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
