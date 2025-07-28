import unittest
from datetime import datetime, timedelta, time

from freezegun import freeze_time

from enums.doctor_type import DoctorType
from enums.machine_type import MachineType
from models.operating_room import OperatingRoom
from data_classes.slot_data import SlotData


class TestOperatingRoom(unittest.TestCase):

    def setUp(self):
        self.room = OperatingRoom(id=1, machines={MachineType.ECG, MachineType.MRI, MachineType.CT})
        self.today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    def test_supports_doctor_type(self):
        self.assertTrue(self.room.supports(DoctorType.HEART))
        self.assertTrue(self.room.supports(DoctorType.BRAIN))

        room_without_MRI = OperatingRoom(id=2, machines={MachineType.ECG})
        self.assertFalse(room_without_MRI.supports(DoctorType.BRAIN))

    def test_get_surgery_duration(self):
        self.assertEqual(self.room.get_surgery_duration(DoctorType.HEART), timedelta(hours=3))
        self.assertEqual(self.room.get_surgery_duration(DoctorType.BRAIN), timedelta(hours=2))

        room_without_CT = OperatingRoom(id=3, machines={MachineType.MRI})
        self.assertEqual(room_without_CT.get_surgery_duration(DoctorType.BRAIN), timedelta(hours=3))

    def test_schedule_slot_and_ordering(self):
        later_slot = SlotData(start_time=self.today + timedelta(hours=5),end_time=self.today + timedelta(hours=8), room_id=1)
        earlier_slot = SlotData(start_time=self.today + timedelta(hours=1), end_time=self.today + timedelta(hours=4), room_id=1)

        self.room.schedule_slot(later_slot)
        self.room.schedule_slot(earlier_slot)

        self.assertEqual(len(self.room.schedule), 2)
        self.assertLess(self.room.schedule[0]["start"], self.room.schedule[1]["start"])

    @freeze_time("2025-07-28 10:00:00")
    def test_no_available_slot_within_next_week(self):
        room = OperatingRoom(id=1, machines={MachineType.ECG})
        start_time = datetime(2025, 7, 28, 10, 0)
        duration = timedelta(hours=3)

        for day in range(7):
            for hour_offset in (0, 3, 6):  # 10:00, 13:00, 16:00
                slot_start = start_time + timedelta(days=day, hours=hour_offset)
                slot_end = slot_start + duration
                room.schedule_slot(SlotData(start_time=slot_start, end_time=slot_end, room_id=room.id))

        result = room.find_earliest_available_slot(start_time=datetime.now(), duration=timedelta(hours=3))

        assert result is None


if __name__ == '__main__':
    unittest.main()
