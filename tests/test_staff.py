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

    def test_4連休はOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)

        for i in range(cal.number_of_days()):
            if i % (5+4) in range(0, 4):
                staff.assign(i+1, Section.OFF)
            else:
                staff.assign(i+1, Section.ER)
        self.assertTrue(staff.is_valid_work_schedule(False))

    def test_5連休はNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        for i in range(cal.number_of_days()):
            if i % (5+4) in range(0, 5):
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

    def test_ICUは夜勤3回までOK(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        for i in range(3):
            staff.assign(i * 2 + 1, Section.NER)
            staff.assign(i * 2 + 2, Section.OFF)
        self.assertTrue(staff.is_valid_work_schedule())

    def test_ICUは夜勤5回でNG(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        for i in range(5):
            staff.assign(i * 2 + 1, Section.NER)
            staff.assign(i * 2 + 2, Section.OFF)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ICUはERに配属できない(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        staff.assign(1, Section.ER)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ICUはEICUに配属できない(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        staff.assign(1, Section.EICU)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ICUはICUとNERに配属可能(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ICU, cal)
        staff.assign(1, Section.ICU)
        staff.assign(2, Section.NER)
        self.assertTrue(staff.is_valid_work_schedule())

    def test_ERはICUに配属できない(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        staff.assign(1, Section.ICU)
        self.assertFalse(staff.is_valid_work_schedule())

    def test_ERはERとEICUとNERに配属可能(self):
        cal = MonthlyCalendar(2024, 4)
        staff = Staff("test", Role.ER, cal)
        staff.assign(1, Section.ER)
        staff.assign(2, Section.EICU)
        staff.assign(2, Section.NER)
        self.assertTrue(staff.is_valid_work_schedule())