import calendar
from enum import Enum
from copy import deepcopy
from datetime import date, datetime, timedelta

class Section(Enum):
    ER = 'ER'
    ICU = 'ICU'
    EICU = 'EICU'
    NER = 'NER'
    OFF = None

class Role(Enum):
    ER = 'ER'
    ICU = 'ICU'

NIGHT_ASSIGN_LIMIT_ICU = 4
NIGHT_ASSIGN_LIMIT_ER = 7
CONSECUTIVE_WORK_LIMIT = 5
CONSECUTIVE_OFF_LIMIT = 4
class Intern:
    def __init__(self, name: str, role: Role):
        self.name = name
        self.role = role
        self.work_schedule = {}

    def can_assign(self, date: date, section: Section, in_progress = False) -> bool:
        # Roleに応じたSection配属可否チェック
        if self.role == Role.ER and section not in [Section.ER, Section.EICU, Section.NER, Section.OFF]:
            return False
        if self.role == Role.ICU and section not in [Section.ICU, Section.NER, Section.OFF]:
            return False

        # シフト整合担保のため、Section割り当て済みの場合はOFF以外許容しない
        if self.assign_of(date) != Section.OFF and section != Section.OFF:
            return False

        # 実際にアサインを試みたうえでシフトが破綻していないかを検証
        after_assign = deepcopy(self)
        after_assign.assign(date, section)
        return after_assign.is_valid_work_schedule(in_progress)

    def assign(self, date: date, section: Section) -> None:
        self.work_schedule[date] = section

    def assign_of(self, date: date) -> Section:
        if date not in self.work_schedule:
            return Section.OFF
        return self.work_schedule[date]

    def total_assign_count(self, section: Section) -> int:
        return len([date for date, assigned in self.work_schedule.items() if assigned == section])

    def monthly_assign_count(self, year: int, month: int, section: Section) -> int:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1])

        count = 0
        for date in [start_date + timedelta(days=x) for x in range((end_date-start_date).days)]: 
            count += 1 if self.assign_of(date) == section else 0

        return count

    def is_day_off(self, date: date) -> bool:
        return self.assign_of(date) == Section.OFF

    def get_first_schedule(self):
        return sorted(self.work_schedule.keys())[0]

    def get_last_schedule(self):
        return sorted(self.work_schedule.keys())[-1]

    def get_work_schedule_range(self):
        start_date = self.get_first_schedule()
        last_date = self.get_last_schedule()
        return [start_date + timedelta(days=x) for x in range((last_date-start_date).days)]

    def is_valid_work_schedule(self, in_progress = False) -> bool:
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
            if self.assign_of(date - timedelta(days=1)) == Section.NER and not self.is_day_off(date):
                return False

            # 連続勤務/休暇日数の計算
            if self.is_day_off(date):
                consecutive_on_count = 0
                consecutive_off_count += 1
            else:
                consecutive_on_count += 1
                consecutive_off_count = 0

            if CONSECUTIVE_WORK_LIMIT < consecutive_on_count \
                or (not in_progress and CONSECUTIVE_OFF_LIMIT < consecutive_off_count):
                return False

        return True


    def print_stats(self):
        print(self.name, end='\t')
        print(self.role.name, end='\t')
        if self.role == Role.ER:
            print('{0}: {1}'.format(Section.NER.name, self.total_assign_count(Section.NER)), end='\t')
            print('{0}: {1}'.format(Section.ER.name, self.total_assign_count(Section.ER)), end='\t')
            print('{0}: {1}'.format(Section.EICU.name, self.total_assign_count(Section.EICU)), end='\t')
        elif self.role == Role.ICU:
            print('{0}: {1}'.format(Section.NER.name, self.total_assign_count(Section.NER)), end='\t')
            print('{0}: {1}'.format(Section.ICU.name, self.total_assign_count(Section.ICU)), end='\t')
        else:
            for section in list(Section):
                print('{0}: {1}'.format(section.name, self.total_assign_count(section)), end='\t')
        print()