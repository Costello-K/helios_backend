from enum import StrEnum, auto


# enums for InvitationToCompany model
class InvitationStatus(StrEnum):
    PENDING = auto()
    ACCEPTED = auto()
    DECLINED = auto()
    REVOKED = auto()


# enums for RequestToCompany model
class RequestStatus(StrEnum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    CANCELLED = auto()
