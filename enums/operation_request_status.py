from enum import Enum


class OperationRequestStatus(str, Enum):
    IN_QUEUE = "IN_QUEUE"
    SCHEDULED = "SCHEDULED"
