import calendar
from enum import Enum
from copy import deepcopy
import datetime

class Section(Enum):
    ER = 'ER'
    ICU = 'ICU'
    EICU = 'EICU'
    NER = 'NER'
    OFF = None
    PTO = 'PTO'

class Role(Enum):
    ER = 'ER'
    ICU = 'ICU'

NIGHT_ASSIGN_LIMIT_ICU = 4
NIGHT_ASSIGN_LIMIT_ER = 7
CONSECUTIVE_WORK_LIMIT = 5
CONSECUTIVE_OFF_LIMIT = 4
class WorkSchedule:
    def __init__(self, name: str, role: Role, ):
        self.name = name
        self.role = role
        self.work_schedule = {}

    def can_assign(self, date: datetime.date, section: Section, in_progress = False) -> bool:
        # Roleに応じたSection配属可否チェック
        if self.role == Role.ER and section not in [Section.ER, Section.EICU, Section.NER, Section.OFF, Section.PTO]:
            return False
        if self.role == Role.ICU and section not in [Section.ICU, Section.NER, Section.OFF, Section.PTO]:
            return False

        # シフト整合担保のため、Section割り当て済みの場合はOFF以外許容しない
        if self.assign_of(date) != Section.OFF and section != Section.OFF:
            return False

        # 実際にアサインを試みたうえでシフトが破綻していないかを検証
        after_assign = deepcopy(self)
        after_assign.assign(date, section)
        return after_assign.is_valid(in_progress)

    def assign(self, date: datetime.date, section: Section) -> None:
        self.work_schedule[date] = section

    def assign_of(self, date: datetime.date) -> Section:
        if date not in self.work_schedule:
            return Section.OFF
        return self.work_schedule[date]

    def total_assign_count(self, section: Section) -> int:
        return len([date for date, assigned in self.work_schedule.items() if assigned == section])

    def monthly_assign_count(self, year: int, month: int, section: Section) -> int:
        first_date = datetime.date(year, month, 1)
        last_date = first_date + datetime.timedelta(days=calendar.monthrange(year, month)[1])
        return len([date for date, assigned in self.work_schedule.items() if assigned == section and first_date <= date <= last_date ])

    def is_day_off(self, date: datetime.date) -> bool:
        return self.assign_of(date) in [Section.OFF, Section.PTO]

    def get_first_schedule(self):
        if len(self.work_schedule) == 0:
            return None
        return sorted(self.work_schedule.keys())[0]

    def get_last_schedule(self):
        if len(self.work_schedule) == 0:
            return None
        return sorted(self.work_schedule.keys())[-1]

    def get_work_schedule_range(self):
        first_date = self.get_first_schedule()
        last_date = self.get_last_schedule()
        if first_date is None or last_date is None:
            return []
        return [first_date + datetime.timedelta(days=x) for x in range((last_date-first_date).days + 1)]

    def is_valid(self, in_progress = False) -> bool:
        if self.role == Role.ER:
            # ERはICUに配属しない
            if 0 < self.total_assign_count(Section.ICU):
                return False

            # 夜勤上限チェック
            if NIGHT_ASSIGN_LIMIT_ER < self.total_assign_count(Section.NER):
                return False

        if self.role == Role.ICU:
            # ICUはER,EICUに配属しない
            if 0 < self.total_assign_count(Section.ER) + self.total_assign_count(Section.EICU):
                return False

            # 夜勤上限チェック
            if NIGHT_ASSIGN_LIMIT_ICU < self.total_assign_count(Section.NER):
                return False

        # 各日付の確認
        consecutive_on_count = 0
        consecutive_off_count = 0

        for date in self.get_work_schedule_range():
            # 夜勤明けに勤務をしていないか
            if self.assign_of(date - datetime.timedelta(days=1)) == Section.NER and not self.is_day_off(date):
                return False

            # 連続勤務/休暇日数の計算
            if self.is_day_off(date):
                consecutive_on_count = 0
                consecutive_off_count += 1
            else:
                consecutive_on_count += 1
                consecutive_off_count = 0

            # 連続勤務/休暇日数の上限チェック
            if CONSECUTIVE_WORK_LIMIT < consecutive_on_count \
                or (not in_progress and CONSECUTIVE_OFF_LIMIT < consecutive_off_count):
                return False

        return True

    def print_stats(self):
        print(self.name, end='\t')
        print(self.role.name, end='\t')
        if self.role == Role.ER:
            print('{0:4}: {1:2}'.format(Section.NER.name, self.total_assign_count(Section.NER)), end='\t')
            print('{0:4}: {1:2}'.format(Section.ER.name, self.total_assign_count(Section.ER)), end='\t')
            print('{0:4}: {1:2}'.format(Section.EICU.name, self.total_assign_count(Section.EICU)), end='\t')
        elif self.role == Role.ICU:
            print('{0:4}: {1:2}'.format(Section.NER.name, self.total_assign_count(Section.NER)), end='\t')
            print('{0:4}: {1:2}'.format(Section.ICU.name, self.total_assign_count(Section.ICU)), end='\t')
        else:
            for section in list(Section):
                print('{0:4}: {1:2}'.format(section.name, self.total_assign_count(section)), end='\t')
        print()

    def print(self):
        print(self.name, end='\t')
        for date in self.get_work_schedule_range():
            section = self.assign_of(date)
            if date.weekday() in [5, 6]: # 週末は青背景
                print('\033[44m', end='')
            if section == Section.NER: # 夜勤は赤文字
                print('\033[31m', end='')
            if section == Section.PTO: # 有給は青文字
                print('\033[34m', end='')
            if section == Section.OFF: # オフ日は非表示
                print('\033[08m', end='')
            print('{0:4}'.format(section.name), end='\t')
            print('\033[0m', end='')
        print()