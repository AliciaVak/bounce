from datetime import datetime, timedelta, time
from typing import List, Dict, Set, Optional

from data_classes.slot_data import SlotData
from enums.doctor_type import DoctorType
from enums.machine_type import MachineType
from exceptions import InvalidInputError


class OperatingRoom:
    def __init__(self, id: int, machines: Set[MachineType]):
        self.id = id
        self.machines = machines
        self.schedule: List[Dict[str, datetime]] = []  # each slot- {"start":, "end":}
        self.start_hour = time(10, 0)
        self.end_hour = time(18, 0)

    def supports(self, doctor_type: DoctorType) -> bool:
        if doctor_type == DoctorType.HEART:
            return MachineType.ECG in self.machines
        if doctor_type == DoctorType.BRAIN:
            return MachineType.MRI in self.machines
        return False

    def get_surgery_duration(self, doctor_type: DoctorType) -> timedelta:
        if doctor_type == DoctorType.HEART:
            return timedelta(hours=3)
        elif doctor_type == DoctorType.BRAIN:
            return timedelta(hours=2) if MachineType.CT in self.machines else timedelta(hours=3)
        raise InvalidInputError(f"Unsupported doctor type: {doctor_type}")

    def schedule_slot(self, slot_data: SlotData) -> None:
        slot = {'start': slot_data.start_time, 'end': slot_data.end_time}
        i = 0
        # for avoid sorting every time, insert in place
        while i < len(self.schedule) and self.schedule[i]['start'] < slot['start']:
            i += 1
        self.schedule.insert(i, slot)

    def is_within_working_hours(self, start: datetime, duration: timedelta) -> bool:
        end = start + duration
        return (self.start_hour <= start.time() <= self.end_hour and self.start_hour <= end.time() <= self.end_hour)

    def _next_working_day_start(self, after: datetime) -> datetime:
        next_day = (after + timedelta(days=1)).date()
        return datetime.combine(next_day, self.start_hour)

    def find_earliest_available_slot(self, start_time: datetime, duration: timedelta, max_days: int = 7) -> Optional[SlotData]:
        current_time = max(start_time, datetime.combine(start_time.date(), self.start_hour))
        max_date = (start_time + timedelta(days=max_days - 1)).date()
        while current_time.date() <= max_date:
            # Skip if outside working hours
            if current_time.time() > self.end_hour or current_time.time() < self.start_hour:
                current_time = self._next_working_day_start(after=current_time)
                continue
            end_time = current_time + duration
            if not self.is_within_working_hours(current_time, duration):
                current_time += timedelta(minutes=15)
                continue
            conflict_found = False
            for entry in self.schedule:
                scheduled_start = entry["start"]
                scheduled_end = entry["end"]
                if scheduled_start < end_time and current_time < scheduled_end:
                    conflict_found = True
                    current_time = scheduled_end  # jump to after this slot
                    break
            if not conflict_found:
                return SlotData(start_time=current_time, end_time=end_time, room_id=self.id)
        return None
