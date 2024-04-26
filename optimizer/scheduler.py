import random
import datetime
from enum import Enum
from optimizer.intern import Intern, Role, Section

class Requirements:
    def staff_required(date: datetime.date, section: Section):
        if date.weekday() in [0, 1, 2, 3, 4]:
            if section == Section.ICU:
                return 3
            if section == Section.ER:
                return 3
            if section == Section.EICU:
                return 3
            if section == Section.NER:
                return 3
        else:
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
    def __init__(self, er_count: int, icu_count: int):
        self.interns = list(map(lambda i: Intern("ER.{0}".format(str(i)), Role.ER), range(1, er_count + 1)))
        self.interns += list(map(lambda i: Intern("ICU.{0}".format(str(i)), Role.ICU), range(1, icu_count + 1)))

    def schedule(self, start_date: datetime.date, end_date: datetime.date):
        for intern in self.interns:
            for date in [start_date + datetime.timedelta(days=x) for x in range((end_date-start_date).days + 1)]:
                intern.assign(date, Section.OFF)

        self.assign(start_date, end_date)
        return self.interns

    def assign(self, current_date: datetime.date, end_date: datetime.date, er_idx = 0, icu_idx = 0, ner_idx = 0):
        # 終了条件
        if current_date > end_date:
            return

        # 日勤ER割当
        for i in range(Requirements.staff_required(current_date, Section.ER)):
            assignable = self.get_assignable(current_date, Section.ER)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for date:{0} section: {1}'.format(current_date, Section.ER.name))
            random.choice(assignable).assign(current_date, Section.ER)

        # 日勤EICU割当
        for i in range(Requirements.staff_required(current_date, Section.EICU)):
            assignable = self.get_assignable(current_date, Section.EICU)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for date:{0} section: {1}'.format(current_date, Section.EICU.name))
            random.choice(assignable).assign(current_date, Section.EICU)

        # 日勤ICU割当
        for i in range(Requirements.staff_required(current_date, Section.ICU)):
            assignable = self.get_assignable(current_date, Section.ICU)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for date:{0} section: {1}'.format(current_date, Section.ICU.name))
            random.choice(assignable).assign(current_date, Section.ICU)

        # 夜勤ER担当
        for i in range(Requirements.staff_required(current_date, Section.NER)):
            assignable = self.get_assignable(current_date, Section.NER)
            if len(assignable) == 0:
                raise Exception('No intern can be assigned for date:{0} section: {1}'.format(current_date, Section.NER.name))
            random.choice(assignable).assign(current_date, Section.NER)

        # 翌日分の割当を開始
        return self.assign(current_date + datetime.timedelta(days=1), end_date, er_idx, icu_idx, ner_idx)

    def get_assignable(self, date, section):
        # 当該シフトに勤務可能な次のスタッフを探す
        return [intern for intern in self.interns if intern.can_assign(date, section, True)]