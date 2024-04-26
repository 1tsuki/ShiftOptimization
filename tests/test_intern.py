from unittest import TestCase
from optimizer.calendar import MonthlyCalendar
from optimizer.intern import Intern, Role, Section

NIGHT_ASSIGN_LIMIT_ICU = 4
NIGHT_ASSIGN_LIMIT_ER = 7
CONSECUTIVE_WORK_LIMIT = 5
CONSECUTIVE_OFF_LIMIT = 4
class TestIntern(TestCase):
    def test_5連勤はOK(self):
        intern = Intern("test", Role.ER)
        for day in range(1, CONSECUTIVE_WORK_LIMIT + 1):
            intern.assign(day, Section.ER)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_6連勤はNG(self):
        intern = Intern("test", Role.ER)
        for day in range(1, CONSECUTIVE_WORK_LIMIT + 2):
            intern.assign(day, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_4連休はOK(self):
        cal = MonthlyCalendar(2024, 4)
        intern = Intern("test", Role.ER)

        for day in range(1, cal.number_of_days() + 1):
            if day % (CONSECUTIVE_WORK_LIMIT + CONSECUTIVE_OFF_LIMIT) in range(0, CONSECUTIVE_OFF_LIMIT):
                intern.assign(day, Section.OFF)
            else:
                intern.assign(day, Section.ER)
        self.assertTrue(intern.is_valid_work_schedule(False))

    def test_5連休はNG(self):
        cal = MonthlyCalendar(2024, 4)
        intern = Intern("test", Role.ER)
        for day in range(1, cal.number_of_days() + 1):
            if day % (CONSECUTIVE_WORK_LIMIT + CONSECUTIVE_OFF_LIMIT) in range(0, CONSECUTIVE_OFF_LIMIT + 1):
                intern.assign(day, Section.OFF)
            else:
                intern.assign(day, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule(False))

    def test_夜勤ER明けの勤務はNG(self):
        intern = Intern("test", Role.ER)
        intern.assign(1, Section.NER)
        intern.assign(2, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ERは夜勤7回までOK(self):
        intern = Intern("test", Role.ER)
        for day in range(1, NIGHT_ASSIGN_LIMIT_ER + 1):
            intern.assign(day * 2 - 1, Section.NER)
            intern.assign(day * 2, Section.OFF)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ERは夜勤8回でNG(self):
        intern = Intern("test", Role.ER)
        for i in range(1, NIGHT_ASSIGN_LIMIT_ER + 2):
            intern.assign(i * 2 - 1, Section.NER)
            intern.assign(i * 2, Section.OFF)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUは夜勤3回までOK(self):
        intern = Intern("test", Role.ICU)
        for i in range(1, NIGHT_ASSIGN_LIMIT_ICU + 1):
            intern.assign(i * 2 - 1, Section.NER)
            intern.assign(i * 2, Section.OFF)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ICUは夜勤5回でNG(self):
        intern = Intern("test", Role.ICU)
        for i in range(1, NIGHT_ASSIGN_LIMIT_ICU + 2):
            intern.assign(i * 2 - 1, Section.NER)
            intern.assign(i * 2, Section.OFF)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはERに配属できない(self):
        intern = Intern("test", Role.ICU)
        intern.assign(1, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはEICUに配属できない(self):
        intern = Intern("test", Role.ICU)
        intern.assign(1, Section.EICU)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはICUとNERに配属可能(self):
        intern = Intern("test", Role.ICU)
        intern.assign(1, Section.ICU)
        intern.assign(2, Section.NER)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ERはICUに配属できない(self):
        intern = Intern("test", Role.ER)
        intern.assign(1, Section.ICU)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ERはERとEICUとNERに配属可能(self):
        intern = Intern("test", Role.ER)
        intern.assign(1, Section.ER)
        intern.assign(2, Section.EICU)
        intern.assign(2, Section.NER)
        self.assertTrue(intern.is_valid_work_schedule())