from enum import Enum
from copy import deepcopy

class Section(Enum):
    ER = 'ER'
    ICU = 'ICU'
    EICU = 'EICU'
    NER = 'NER'
    OFF = NoneOFF = None

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
        self.reset_work_schedule()

    def reset_work_schedule(self):
        self.work_schedule = []

    def can_assign(self, day: int, section: Section, in_progress = False) -> bool:
        # Roleに応じたSection配属可否チェック
        if self.role == Role.ER and section not in [Section.ER, Section.EICU, Section.NER, Section.OFF]:
            return False
        if self.role == Role.ICU and section not in [Section.ICU, Section.NER, Section.OFF]:
            return False

        # シフト整合担保のため、Section割り当て済みの場合はOFF以外許容しない
        if self.assign_of(day) != Section.OFF and section != Section.OFF:
            return False

        # 実際にアサインを試みたうえでシフトが破綻していないかを検証
        after_assign = deepcopy(self)
        after_assign.assign(day, section)
        return after_assign.is_valid_work_schedule(in_progress)

    def assign(self, day: int, section: Section) -> None:
        if len(self.work_schedule) < day:
            self.work_schedule += [Section.OFF] * (day - len(self.work_schedule))
        self.work_schedule[day - 1] = section

    def assign_of(self, day: int) -> Section:
        if len(self.work_schedule) < day:
            return Section.OFF
        return self.work_schedule[day - 1]

    def assign_count(self, section: Section) -> int:
        return len(list(filter(lambda s: s == section, self.work_schedule)))

    def is_day_off(self, day: int) -> bool:
        return self.assign_of(day) == Section.OFF

    def is_valid_work_schedule(self, in_progress = False) -> bool:
        if self.role == Role.ER:
            # ERはICUに配属しない
            if 0 < self.assign_count(Section.ICU):
                return False

            # 夜勤上限チェック
            if NIGHT_ASSIGN_LIMIT_ER < self.assign_count(Section.NER):
                return False

        if self.role == Role.ICU:
            # ICUはER,EICUに配属しない
            if 0 < self.assign_count(Section.ER) + self.assign_count(Section.EICU):
                return False

            # 夜勤上限チェック
            if NIGHT_ASSIGN_LIMIT_ICU < self.assign_count(Section.NER):
                return False

        # 各日付の確認
        consecutive_on_count = 0
        consecutive_off_count = 0
        for day in range(1, len(self.work_schedule) + 1):
            # 夜勤明けに勤務をしていないか
            if 1 < day and self.assign_of(day - 1) == Section.NER and not self.is_day_off(day):
                return False

            # 連続勤務/休暇日数の計算
            if self.is_day_off(day):
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
            print('{0}: {1}'.format(Section.NER.name, self.assign_count(Section.NER)), end='\t')
            print('{0}: {1}'.format(Section.ER.name, self.assign_count(Section.ER)), end='\t')
            print('{0}: {1}'.format(Section.EICU.name, self.assign_count(Section.EICU)), end='\t')
        elif self.role == Role.ICU:
            print('{0}: {1}'.format(Section.NER.name, self.assign_count(Section.NER)), end='\t')
            print('{0}: {1}'.format(Section.ICU.name, self.assign_count(Section.ICU)), end='\t')
        else:
            for section in list(Section):
                print('{0}: {1}'.format(section.name, self.assign_count(section)), end='\t')
        print()

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
