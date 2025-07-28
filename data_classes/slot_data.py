from datetime import datetime

from attr import dataclass


@dataclass
class SlotData:
    start_time: datetime
    end_time: datetime
    room_id: int
