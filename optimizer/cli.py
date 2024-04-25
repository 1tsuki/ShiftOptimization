from enum import Enum
from functools import reduce
from random import randint, choice, shuffle
from statistics import stdev
from copy import deepcopy
from optimizer.calendar import MonthlyCalendar
from optimizer.staff import Role, Staff, Section


def generate_base_work_schedule(cal, icu_count, er_count):
    staffs_icu = list(map(lambda i: Staff("ICU.{0}".format(str(i+1)), Role.ICU, cal), range(0, icu_count)))
    staffs_er = list(map(lambda i: Staff("ER.{0}".format(str(i+1)), Role.ER, cal), range(0, er_count)))
    return assign(cal, staffs_icu, staffs_er)

def assign(cal, staffs_icu: list, staffs_er: list):
    (staffs_icu, staffs_er) = assign_shift(cal, staffs_icu, staffs_er)
    return staffs_icu + staffs_er

NIGHT_ER_STAFF_REQUIRED = 3
WEEKDAY_DAY_ICU_STAFF_REQUIRED = 3
WEEKDAY_DAY_ER_STAFF_REQUIRED = 3
WEEKDAY_DAY_EICU_STAFF_REQUIRED = 3
WEEKEND_DAY_ICU_STAFF_REQUIRED = 2
WEEKEND_DAY_ER_STAFF_REQUIRED = 3
WEEKEND_DAY_EICU_STAFF_REQUIRED = 3
def assign_shift(cal, staffs_icu, staffs_er, night_idx = 0, icu_idx = 0, er_idx = 0, day = 1):
    # 再起終了条件
    if day > cal.number_of_days():
        return (staffs_icu, staffs_er)

    # 日勤ER割当
    for i in range(WEEKDAY_DAY_ER_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_ER_STAFF_REQUIRED):
        er_idx = find_next_assignable(day, er_idx, staffs_er, Section.ER)
        staffs_er[er_idx].assign(day, Section.ER)
        er_idx = increment_idx(er_idx, len(staffs_er))

    # 日勤EICU割当
    for i in range(WEEKDAY_DAY_EICU_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_EICU_STAFF_REQUIRED):
        er_idx = find_next_assignable(day, er_idx, staffs_er, Section.EICU)
        staffs_er[er_idx].assign(day, Section.EICU)
        er_idx = increment_idx(er_idx, len(staffs_er))

    # 日勤ICU割当
    for i in range(WEEKDAY_DAY_ICU_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_ICU_STAFF_REQUIRED):
        icu_idx = find_next_assignable(day, icu_idx, staffs_icu, Section.ICU)
        staffs_icu[icu_idx].assign(day, Section.ICU)
        icu_idx = increment_idx(icu_idx, len(staffs_icu))

    # 夜勤ER担当
    for i in range(NIGHT_ER_STAFF_REQUIRED):
        night_idx = find_next_assignable(day, night_idx, staffs_er + staffs_icu, Section.NER)
        if night_idx < len(staffs_er):
            staffs_er[night_idx].assign(day, Section.NER)
        else:
            staffs_icu[night_idx - len(staffs_er)].assign(day, Section.NER)
        night_idx = increment_idx(night_idx, len(staffs_er) + len(staffs_icu))

    # 翌日分の割当を開始
    return assign_shift(cal, staffs_icu, staffs_er, night_idx, icu_idx, er_idx, day + 1)

def find_next_assignable(day, idx, staffs, section):
    # 当該シフトに勤務可能な次のスタッフを探す
    count = 0
    while not staffs[idx].can_assign(day, section) and count < len(staffs):
        idx = increment_idx(idx, len(staffs))
        count += 1

    if not staffs[idx].can_assign(day, section):
        print('Error occured at day {0}, section {1}'.format(day, section))
        for staff in staffs:
            staff.print_work_schedule()
        raise Exception('No staff can be assigned')
    return idx

def increment_idx(idx, length):
    return idx + 1 if idx < length - 1 else 0

def evaluate(staffs):
    # シフトの質を評価する評価関数
    # 個人観点のシフトの質
    score = 0
    for staff in staffs:
        # 総夜勤日数は上限より少ないほうが好ましい
        score += staff.role.night_shift_assign_limit() - staff.assignment_count(Section.NER)

        for day in range(1, staff.calendar.number_of_days() + 1):
            # 土日の休暇は加点
            if staff.calendar.is_weekend(day) and staff.is_day_off(day):
                score += 1

            # 連続休暇は加点
            if 2 <= day and staff.is_day_off(day - 1) and staff.is_day_off(day):
                score += 1

            # 同種連日勤務は加点
            if 2 <= day and staff.work_schedule_of(day) in [Section.ICU, Section.EICU] and staff.work_schedule_of(day - 1) == staff.work_schedule_of(day):
                score += 1

    # 全体観点でのシフトの質
    er_staffs = [staff for staff in staffs if staff.role == Role.ER]
    icu_staffs = [staff for staff in staffs if staff.role == Role.ICU]

    er_day_shift_dev = stdev([staff.assignment_count(Section.ER) + staff.assignment_count(Section.ICU) + staff.assignment_count(Section.EICU) for staff in er_staffs])
    er_night_shift_dev = stdev([staff.assignment_count(Section.NER) for staff in er_staffs])
    icu_day_shift_dev = stdev([staff.assignment_count(Section.ER) + staff.assignment_count(Section.ICU) + staff.assignment_count(Section.EICU) for staff in icu_staffs])
    icu_night_shift_dev = stdev([staff.assignment_count(Section.NER) for staff in icu_staffs])

    return score - er_day_shift_dev * len(er_staffs) - er_night_shift_dev * len(er_staffs) - icu_day_shift_dev * len(icu_staffs) - icu_night_shift_dev * len(icu_staffs)

def modify(staffs, cal: MonthlyCalendar):
    # ランダムな日を抽出
    day = randint(1, cal.number_of_days())
    target_section = choice(list(Section))
    swap_shift(staffs, day, target_section)

def get_staff_assigned(staffs, day: int, section: Section):
    return [staff for staff in staffs if staff.work_schedule_of(day) == section]

def get_staffs_unassigned(staffs, day: int, role: Role = None):
    if role == None:
        return [staff for staff in staffs if staff.work_schedule_of(day) == Section.OFF]
    else:
        return [staff for staff in staffs if staff.work_schedule_of(day) == Section.OFF and staff.role == role]

def swap_shift(staffs, day: int, section: Section):
    # 夜勤の人を探す
    assigned = get_staff_assigned(staffs, day, section)
    staff_a = choice(assigned)

    # 勤務に入れる人を探す
    role = Role.ICU if section == Section.ICU else (Role.ER if section in [Section.ER, Section.EICU] else None)
    unassigned = get_staffs_unassigned(staffs, day, role)
    shuffle(unassigned)
    for staff_b in unassigned:
        if staff_b.can_assign(day, section):
            staff_b.assign(day, section)
            staff_a.assign(day, Section.OFF)
            break

def assigned_count(staffs, day, section):
    return len([staff for staff in staffs if staff.work_schedule_of(day) == section])

def main():
    debug = True
    year = input('Year: ') if not debug else 2024
    month = input('Month: ') if not debug else 4
    icu_count = input('ICU count: ') if not debug else 6
    er_count = input('ER count: ') if not debug else 14
    max_attempt = input('Max attempt: ') if not debug else 10000

    cal = MonthlyCalendar(year, month)
    work_schedule = generate_base_work_schedule(cal, icu_count, er_count)
    print('initial score = {0}'.format(evaluate(work_schedule)))

    attempt = 0
    swapped = 0
    improved = 0
    prev_score = evaluate(work_schedule)
    while attempt < max_attempt:
        attempt += 1
        modified = deepcopy(work_schedule)
        modify(modified, cal)

        new_score = evaluate(modified)
        if all([staff.is_valid_work_schedule(False) for staff in modified]) and prev_score <= new_score:
            work_schedule = modified
            swapped += 1
            if prev_score < new_score:
                prev_score = new_score
                improved += 1

    print('swapped {0} and improved {1} times in {2} attempts, final score = {3}'.format(swapped, improved, max_attempt, evaluate(work_schedule)))

    for staff in work_schedule:
        staff.print_stats()
    print()

    cal.print_dates()
    for staff in work_schedule:
        staff.print_work_schedule()
    print()