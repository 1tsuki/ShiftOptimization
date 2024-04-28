from copy import deepcopy
import random
import datetime
from enum import Enum
from optimizer.workSchedule import WorkSchedule, Role, Section

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

class PaidTimeOffRequest:
    def __init__(self, role: Role, dates: list[datetime.date]):
        self.role = role
        self.dates = dates

class Scheduler:
    def __init__(self, er_count: int, icu_count: int, pto_requests: list[PaidTimeOffRequest]):
        self.workSchedules = list(map(lambda i: WorkSchedule("ER.{0}".format(str(i+1)), Role.ER), range(er_count)))
        self.workSchedules += list(map(lambda i: WorkSchedule("ICU.{0}".format(str(i+1)), Role.ICU), range(icu_count)))
        self.pto_requests = pto_requests

    def schedule(self, first_date: datetime.date, last_date: datetime.date):
        # 初期スケジュールの生成に失敗する事があるため、10回上限でリトライを行う
        for i in range(0, 10):
            try:
                # 有給取得希望日を先んじて割り当て
                pto_requests = deepcopy(self.pto_requests)
                er_pto_requests = [request for request in pto_requests if request.role == Role.ER]
                icu_pto_requests = [request for request in pto_requests if request.role == Role.ICU]
                for workSchedule in self.workSchedules:
                    requests = []
                    if workSchedule.role == Role.ER and len(er_pto_requests) > 0:
                        requests = er_pto_requests.pop().dates
                    if workSchedule.role == Role.ICU and len(icu_pto_requests) > 0:
                        requests = icu_pto_requests.pop().dates

                    for date in [first_date + datetime.timedelta(days=x) for x in range((last_date - first_date).days + 1)]:
                        if date in requests:
                            workSchedule.assign(date, Section.PTO)
                        else:
                            workSchedule.assign(date, Section.OFF)

                # 初期スケジュールを生成
                self.assign(first_date, last_date)

            except Exception:
                print('failed to generate initial work schedule, retrying... count:{0}'.format(i + 1))
                continue
            break

        return self.workSchedules

    def assign(self, current_date: datetime.date, last_date: datetime.date, er_idx = 0, icu_idx = 0, ner_idx = 0):
        # 終了条件
        if current_date > last_date:
            return

        # 日勤ER割当
        for _ in range(Requirements.staff_required(current_date, Section.ER)):
            assignable = self.get_assignable(current_date, Section.ER)
            if len(assignable) == 0:
                raise Exception('No workSchedule can be assigned for date:{0} section: {1}'.format(current_date, Section.ER.name))
            random.choice(assignable).assign(current_date, Section.ER)

        # 日勤EICU割当
        for _ in range(Requirements.staff_required(current_date, Section.EICU)):
            assignable = self.get_assignable(current_date, Section.EICU)
            if len(assignable) == 0:
                raise Exception('No workSchedule can be assigned for date:{0} section: {1}'.format(current_date, Section.EICU.name))
            random.choice(assignable).assign(current_date, Section.EICU)

        # 日勤ICU割当
        for _ in range(Requirements.staff_required(current_date, Section.ICU)):
            assignable = self.get_assignable(current_date, Section.ICU)
            if len(assignable) == 0:
                raise Exception('No workSchedule can be assigned for date:{0} section: {1}'.format(current_date, Section.ICU.name))
            random.choice(assignable).assign(current_date, Section.ICU)

        # 夜勤ER担当
        for _ in range(Requirements.staff_required(current_date, Section.NER)):
            assignable = self.get_assignable(current_date, Section.NER)
            if len(assignable) == 0:
                raise Exception('No workSchedule can be assigned for date:{0} section: {1}'.format(current_date, Section.NER.name))
            random.choice(assignable).assign(current_date, Section.NER)

        # 翌日分の割当を開始
        return self.assign(current_date + datetime.timedelta(days=1), last_date, er_idx, icu_idx, ner_idx)

    def get_assignable(self, date, section):
        # 当該シフトに勤務可能な次のスタッフを探す
        return [workSchedule for workSchedule in self.workSchedules if workSchedule.can_assign(date, section, True)]