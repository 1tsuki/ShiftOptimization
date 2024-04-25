from unittest import TestCase
from optimizer.calendar import MonthlyCalendar
from optimizer.staff import Staff, Role, Section

class TestStaff(TestCase):
    def test_5連勤はOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(5):
            staff.assign(i+1, Section.ER)
        self.assertTrue(staff.is_valid_work_schedule())

    def test_6連勤はNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(6):
            staff.assign(i+1, Section.ER)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_6連休はOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)

        for i in range(cal.number_of_days()):
            if i % 10 in range(0, 6):
                staff.assign(i+1, Section.OFF)
            else:
                staff.assign(i+1, Section.ER)
        self.assertTrue(staff.is_valid_work_schedule(False))

    def test_7連休はNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(cal.number_of_days()):
            if i % 10 in range(0, 7):
                staff.assign(i+1, Section.OFF)
            else:
                staff.assign(i+1, Section.ER)
        self.assertFalse(staff.is_valid_work_schedule(False))

    def test_夜勤ER明けの勤務はNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        staff.assign(1, Section.NER)
        staff.assign(2, Section.ER)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ERは夜勤7回までOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(7):
            staff.assign(i * 2 + 1, Section.NER)
            staff.assign(i * 2 + 2, Section.OFF)
        self.assertTrue(staff.is_valid_work_schedule())

    def test_ERは夜勤8回でNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(8):
            staff.assign(i * 2 + 1, Section.NER)
            staff.assign(i * 2 + 2, Section.OFF)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ICUは夜勤4回までOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        for i in range(5):
            if i % 2 == 0:
                staff.assign(i+1, Section.NER)
        self.assertTrue(staff.is_valid_work_schedule())

    def test_ICUは夜勤5回でNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        for i in range(5):
            staff.assign(i * 2 + 1, Section.NER)
            staff.assign(i * 2 + 2, Section.OFF)
        self.assertFalse(staff.is_valid_work_schedule())