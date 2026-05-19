from enum import StrEnum


class SystemRole(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    PLN = "PLN"


class EntityStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_NEGOTIATION = "in_negotiation"
    CONTRACTED = "contracted"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class OfferStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ContractStatus(StrEnum):
    PENDING_CONFIRMATION = "pending_confirmation"
    ACTIVE = "active"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
