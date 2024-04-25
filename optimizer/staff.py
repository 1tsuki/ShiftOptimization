from enum import Enum
from copy import deepcopy

from optimizer.calendar import MonthlyCalendar

class Section(Enum):
    ER = 'ER'
    ICU = 'ICU'
    EICU = 'EICU'
    NER = 'NER'
    OFF = None

class Role(Enum):
    ER = 'ER'
    ICU = 'ICU'

    def day_shift_assign_limit(self) -> int:
        if self == Role.ER:
            return 15
        elif self == Role.ICU:
            return 18

    def night_shift_assign_limit(self) -> int:
        if self == Role.ER:
            return 7
        elif self == Role.ICU:
            return 4

CONSECUTIVE_WORK_MAX = 5
CONSECUTIVE_OFF_MAX = 6
class Staff:
    def __init__(self, name: str, role: Role, calendar: MonthlyCalendar):
        self.name = name
        self.role = role
        self.calendar = calendar
        self.work_schedule = {}
        self.work_schedule = [Section.OFF] * calendar.number_of_days()

    def assign(self, day: int, section: Section) -> None:
        self.work_schedule[day - 1] = section

    def can_assign(self, day: int, section: Section) -> bool:
        if self.work_schedule_of(day) != Section.OFF:
            return False
        after_assign = deepcopy(self)
        after_assign.assign(day, section)
        return after_assign.is_valid_work_schedule()

    def assignment_count(self, section: Section) -> int:
        return len(list(filter(lambda s: s == section, self.work_schedule)))

    def work_schedule_of(self, day: int) -> Section:
        return self.work_schedule[day - 1]

    def is_day_off(self, day: int) -> bool:
        # 当日昼夜及び前日夜にシフトがない場合、休暇として扱う
        return self.work_schedule_of(day) == Section.OFF

    def is_valid_work_schedule(self, ignore_consecutive_off_check = True) -> bool:
        # シフト生成初期は全日程が休日扱いのため、シフト生成中は連休上限チェックをスキップする必要がある

        # 日勤夜勤回数上限チェック
        if self.role.night_shift_assign_limit() < self.assignment_count(Section.NER):
            return False
        if self.role.day_shift_assign_limit() < (self.assignment_count(Section.ER) + self.assignment_count(Section.ICU) + self.assignment_count(Section.EICU)):
            return False

        # 連勤/連休上限チェック + 夜勤明け勤務チェック
        consecutive_on_count = 0 if self.is_day_off(1) else 1
        consecutive_off_count = 1 if self.is_day_off(1) else 0
        for day in range(2, self.calendar.number_of_days() + 1):
            # 日またぎ制約を扱うため2日目から処理を行う
            # 夜勤明けに勤務をしていないか
            if self.work_schedule_of(day - 1) == Section.NER and not self.is_day_off(day):
                return False

            # 連続勤務/休暇日数の計算
            if 0 < consecutive_on_count:
                if self.is_day_off(day): # 勤務→休み
                    consecutive_off_count = 1
                    consecutive_on_count = 0
                else: # 勤務→勤務
                    consecutive_off_count = 0
                    consecutive_on_count += 1
            else:
                if self.is_day_off(day): # 休み→休み
                    consecutive_off_count += 1
                    consecutive_on_count = 0
                else: # 休み→勤務
                    consecutive_off_count = 1
                    consecutive_on_count = 0

            if CONSECUTIVE_WORK_MAX <= consecutive_on_count \
                or (not ignore_consecutive_off_check and CONSECUTIVE_OFF_MAX <= consecutive_off_count):
                return False
        return True

    def print_stats(self):
        print("{0}\tRole:{1}\tday_assignment_count:{2}\tnight_assignment_count:{3}".format(
            self.name, 
            self.role.name, 
            self.assignment_count(Section.ER) + self.assignment_count(Section.ICU) + self.assignment_count(Section.EICU), 
            self.assignment_count(Section.NER)))

    def print_work_schedule(self):
        print(self.name, end='\t')

        day = 1
        for section in self.work_schedule:
            if self.calendar.is_weekend(day):
                print('\033[44m', end='')
            if section == Section.OFF:
                print('\033[08m', end='')
            if section == Section.NER:
                print('\033[31m', end='')
            print(section.name, end='\t')
            print('\033[0m', end='')

            day += 1
        print()
