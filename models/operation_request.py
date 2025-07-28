
from datetime import datetime
from typing import Optional
from enums.doctor_type import DoctorType
from enums.operation_request_status import OperationRequestStatus
import itertools

class OperationRequest:
    _id_counter = itertools.count(1)  # class-level generator

    def __init__(self, doctor_type: DoctorType, request_time: datetime):
        self.id = next(OperationRequest._id_counter)
        self.doctor_type = doctor_type
        self.request_time = request_time
        self.status = OperationRequestStatus.IN_QUEUE
        self.scheduled_room_id: Optional[int] = None
        self.scheduled_start_time: Optional[datetime] = None
        self.scheduled_end_time: Optional[datetime] = None
