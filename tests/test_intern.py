import calendar
import datetime
from unittest import TestCase
from optimizer.intern import Intern, Role, Section

NIGHT_ASSIGN_LIMIT_ICU = 4
NIGHT_ASSIGN_LIMIT_ER = 7
CONSECUTIVE_WORK_LIMIT = 5
CONSECUTIVE_OFF_LIMIT = 4

year = 2024
month = 4
start_date = datetime.date(year, month, 1)
month_length = calendar.monthrange(year, month)[1]

class TestIntern(TestCase):
    def test_5連勤はOK(self):
        intern = Intern("test", Role.ER)
        for date in [start_date + datetime.timedelta(days=x) for x in range(CONSECUTIVE_WORK_LIMIT)]:
            intern.assign(date, Section.ER)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_6連勤はNG(self):
        intern = Intern("test", Role.ER)
        for date in [start_date + datetime.timedelta(days=x) for x in range(CONSECUTIVE_WORK_LIMIT + 1)]:
            intern.assign(date, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_4連休はOK(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.ER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=5), Section.ER)
        self.assertTrue(intern.is_valid_work_schedule(False))

    def test_5連休はNG(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.ER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=5), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=6), Section.ER)
        self.assertFalse(intern.is_valid_work_schedule(False))

    def test_夜勤ER明けの勤務はNG(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.NER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ERは夜勤7回までOK(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.NER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=5), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=6), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=7), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=8), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=9), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=10), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=11), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=12), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=13), Section.OFF)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ERは夜勤8回でNG(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.NER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=5), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=6), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=7), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=8), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=9), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=10), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=11), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=12), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=13), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=14), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=15), Section.OFF)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUは夜勤4回までOK(self):
        intern = Intern("test", Role.ICU)
        intern.assign(start_date, Section.NER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=5), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=6), Section.NER)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ICUは夜勤5回でNG(self):
        intern = Intern("test", Role.ICU)
        intern.assign(start_date, Section.NER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=2), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=3), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=4), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=5), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=6), Section.NER)
        intern.assign(start_date + datetime.timedelta(days=7), Section.OFF)
        intern.assign(start_date + datetime.timedelta(days=8), Section.NER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはERに配属できない(self):
        intern = Intern("test", Role.ICU)
        intern.assign(start_date, Section.ER)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはEICUに配属できない(self):
        intern = Intern("test", Role.ICU)
        intern.assign(start_date, Section.EICU)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ICUはICUとNERに配属可能(self):
        intern = Intern("test", Role.ICU)
        intern.assign(start_date, Section.ICU)
        intern.assign(start_date + datetime.timedelta(days=1), Section.NER)
        self.assertTrue(intern.is_valid_work_schedule())

    def test_ERはICUに配属できない(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.ICU)
        self.assertFalse(intern.is_valid_work_schedule())

    def test_ERはERとEICUとNERに配属可能(self):
        intern = Intern("test", Role.ER)
        intern.assign(start_date, Section.ER)
        intern.assign(start_date + datetime.timedelta(days=1), Section.EICU)
        intern.assign(start_date + datetime.timedelta(days=2), Section.NER)
        self.assertTrue(intern.is_valid_work_schedule())