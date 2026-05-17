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
