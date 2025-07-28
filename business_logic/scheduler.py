from datetime import datetime
from threading import Lock
from typing import List, Optional

from data_classes.slot_data import SlotData
from enums.doctor_type import DoctorType
from enums.operation_request_status import OperationRequestStatus
from exceptions import InvalidInputError
from logger import logger
from models.operating_room import OperatingRoom
from models.operation_request import OperationRequest


class Scheduler:

    def __init__(self, operating_rooms: List[OperatingRoom]):
        self.operating_rooms = operating_rooms
        self.room_id_to_room = {room.id: room for room in operating_rooms}
        self.waiting_queue: List[OperationRequest] = []
        self.lock = Lock()


    def _schedule_next_available_slot(self, doctor_type: DoctorType) -> Optional[SlotData]:
        now = datetime.now().replace(second=0, microsecond=0)
        best_slot = None

        for room in self.operating_rooms:
            if not room.supports(doctor_type):
                continue
            duration = room.get_surgery_duration(doctor_type)
            slot_info = room.find_earliest_available_slot(start_time=now, duration=duration)
            if slot_info and (best_slot is None or slot_info.start_time < best_slot.start_time):
                best_slot = slot_info

        if best_slot:
            # book the room
            room = self.room_id_to_room[best_slot.room_id]
            room.schedule_slot(slot_data=best_slot)
        return best_slot

    def schedule(self, doctor_type_str: str) -> OperationRequest:
        doctor_type = self._get_doctor_type(doctor_type_str)
        operation_request = OperationRequest(doctor_type=doctor_type, request_time=datetime.now())
        with self.lock:
            self._drain_queue()
            slot_info = self._schedule_next_available_slot(doctor_type=doctor_type)
            if slot_info:
                self._update_request_with_slot_info(operation_request=operation_request, slot_info=slot_info)
                logger.info(f"scheduled {doctor_type}, request_id: {operation_request.id} in room {slot_info.room_id} at {slot_info.start_time}")
            else:
                self.waiting_queue.append(operation_request)
                logger.info(f"No available rooms in the next week, added request id {operation_request.id}, {doctor_type} surgery to queue")
            return operation_request

    def _drain_queue(self):
        new_queue = []
        for request in self.waiting_queue:
            slot_info = self._schedule_next_available_slot(doctor_type=request.doctor_type)
            if slot_info:
                self._update_request_with_slot_info(request, slot_info)
                logger.info(
                    f"Drained & scheduled queued request id {request.id}, type: {request.doctor_type} at {slot_info.start_time} in room {slot_info.room_id}")
            else:
                new_queue.append(request)
        self.waiting_queue = new_queue

    def _update_request_with_slot_info(self, operation_request: OperationRequest, slot_info: SlotData):
        operation_request.status = OperationRequestStatus.SCHEDULED
        operation_request.scheduled_room_id = slot_info.room_id
        operation_request.scheduled_start_time = slot_info.start_time
        operation_request.scheduled_end_time = slot_info.end_time

    def _get_doctor_type(self, doctor_type_str:str) -> DoctorType:
        if doctor_type_str not in DoctorType.__members__:
            raise InvalidInputError(f"Unknown doctor type: {doctor_type_str}")
        return DoctorType[doctor_type_str]
