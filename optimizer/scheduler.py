import random
from enum import Enum
from optimizer.calendar import MonthlyCalendar
from optimizer.intern import Intern, Role, Section

class Requirements:
    def staff_required(cal: MonthlyCalendar, day: int, section: Section):
        if cal.is_weekday(day):
            if section == Section.ICU:
                return 3
            if section == Section.ER:
                return 3
            if section == Section.EICU:
                return 3
            if section == Section.NER:
                return 3

        if cal.is_weekend(day):
            if section == Section.ICU:
                return 2
            if section == Section.ER:
                return 3
            if section == Section.EICU:
                return 3
            if section == Section.NER:
                return 3

        return 0

class Scheduler:
    def __init__(self, calendar: MonthlyCalendar, er_count: int, icu_count: int):
        self.calendar = calendar
        self.interns = list(map(lambda i: Intern("ER.{0}".format(str(i)), Role.ER), range(1, er_count + 1)))
        self.interns += list(map(lambda i: Intern("ICU.{0}".format(str(i)), Role.ICU), range(1, icu_count + 1)))

    def schedule(self):
        for intern in self.interns:
            intern.work_schedule = []

        self.assign()
        return self.interns

    def assign(self, er_idx = 0, icu_idx = 0, ner_idx = 0, day = 1):
        # 終了条件
        if day > self.calendar.number_of_days():
            return

        # 日勤ER割当
        for i in range(Requirements.staff_required(self.calendar, day, Section.ER)):
            assignable = self.get_assignable(day, Section.ER)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for day:{0} section: {1}'.format(day, Section.ER.name))
            random.choice(assignable).assign(day, Section.ER)

        # 日勤EICU割当
        for i in range(Requirements.staff_required(self.calendar, day, Section.EICU)):
            assignable = self.get_assignable(day, Section.EICU)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for day:{0} section: {1}'.format(day, Section.EICU.name))
            random.choice(assignable).assign(day, Section.EICU)

        # 日勤ICU割当
        for i in range(Requirements.staff_required(self.calendar, day, Section.ICU)):
            assignable = self.get_assignable(day, Section.ICU)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for day:{0} section: {1}'.format(day, Section.ICU.name))
            random.choice(assignable).assign(day, Section.ICU)

        # 夜勤ER担当
        for i in range(Requirements.staff_required(self.calendar, day, Section.NER)):
            assignable = self.get_assignable(day, Section.NER)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for day:{0} section: {1}'.format(day, Section.NER.name))
            random.choice(assignable).assign(day, Section.NER)

        # 翌日分の割当を開始
        return self.assign(er_idx, icu_idx, ner_idx, day + 1)

    def get_assignable(self, day, section):
        # 当該シフトに勤務可能な次のスタッフを探す
        return [intern for intern in self.interns if intern.can_assign(day, section)]