from enum import Enum, auto


class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


class InvitationStatus(AutoName):
    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()


class RequestStatus(AutoName):
    PENDING = auto()
    APPROVED = auto()
    DECLINED = auto()
