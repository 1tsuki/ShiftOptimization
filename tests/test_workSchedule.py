import calendar
import datetime
from unittest import TestCase
from optimizer.workSchedule import WorkSchedule, Role, Section

NIGHT_ASSIGN_LIMIT_ICU = 4
NIGHT_ASSIGN_LIMIT_ER = 7
CONSECUTIVE_WORK_LIMIT = 5
CONSECUTIVE_OFF_LIMIT = 4

year = 2024
month = 4
first_date = datetime.date(year, month, 1)
month_length = calendar.monthrange(year, month)[1]

class TestWorkSchedule(TestCase):
    def test_5連勤はOK(self):
        workSchedule = WorkSchedule("test", Role.ER)
        for date in [first_date + datetime.timedelta(days=x) for x in range(CONSECUTIVE_WORK_LIMIT)]:
            workSchedule.assign(date, Section.ER)
        self.assertTrue(workSchedule.is_valid())

    def test_6連勤はNG(self):
        workSchedule = WorkSchedule("test", Role.ER)
        for date in [first_date + datetime.timedelta(days=x) for x in range(CONSECUTIVE_WORK_LIMIT + 1)]:
            workSchedule.assign(date, Section.ER)
        self.assertFalse(workSchedule.is_valid())

    def test_4連休はOK(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.ER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.ER)
        self.assertTrue(workSchedule.is_valid(False))

    def test_5連休はNG(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.ER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=6), Section.ER)
        self.assertFalse(workSchedule.is_valid(False))

    def test_夜勤ER明けの勤務はNG(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.ER)
        self.assertFalse(workSchedule.is_valid())

    def test_ERは夜勤7回までOK(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=6), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=7), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=8), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=9), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=10), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=11), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=12), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=13), Section.OFF)
        self.assertTrue(workSchedule.is_valid())

    def test_ERは夜勤8回でNG(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=6), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=7), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=8), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=9), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=10), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=11), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=12), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=13), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=14), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=15), Section.OFF)
        self.assertFalse(workSchedule.is_valid())

    def test_ICUは夜勤4回までOK(self):
        workSchedule = WorkSchedule("test", Role.ICU)
        workSchedule.assign(first_date, Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=6), Section.NER)
        self.assertTrue(workSchedule.is_valid())

    def test_ICUは夜勤5回でNG(self):
        workSchedule = WorkSchedule("test", Role.ICU)
        workSchedule.assign(first_date, Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=3), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=4), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=5), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=6), Section.NER)
        workSchedule.assign(first_date + datetime.timedelta(days=7), Section.OFF)
        workSchedule.assign(first_date + datetime.timedelta(days=8), Section.NER)
        self.assertFalse(workSchedule.is_valid())

    def test_ICUはERに配属できない(self):
        workSchedule = WorkSchedule("test", Role.ICU)
        workSchedule.assign(first_date, Section.ER)
        self.assertFalse(workSchedule.is_valid())

    def test_ICUはEICUに配属できない(self):
        workSchedule = WorkSchedule("test", Role.ICU)
        workSchedule.assign(first_date, Section.EICU)
        self.assertFalse(workSchedule.is_valid())

    def test_ICUはICUとNERに配属可能(self):
        workSchedule = WorkSchedule("test", Role.ICU)
        workSchedule.assign(first_date, Section.ICU)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.NER)
        self.assertTrue(workSchedule.is_valid())

    def test_ERはICUに配属できない(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.ICU)
        self.assertFalse(workSchedule.is_valid())

    def test_ERはERとEICUとNERに配属可能(self):
        workSchedule = WorkSchedule("test", Role.ER)
        workSchedule.assign(first_date, Section.ER)
        workSchedule.assign(first_date + datetime.timedelta(days=1), Section.EICU)
        workSchedule.assign(first_date + datetime.timedelta(days=2), Section.NER)
        self.assertTrue(workSchedule.is_valid())