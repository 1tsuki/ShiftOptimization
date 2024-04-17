from enum import Enum
from functools import reduce
from random import randint, choice, shuffle
from statistics import stdev
from copy import deepcopy
from optimizer.calendar import MonthlyCalendar
from optimizer.staff import Role, Staff, Section, Shift


def generate_base_work_schedule(cal, icu_count, er_count):
    staffs_icu = list(map(lambda i: Staff("Dr.{0}".format(str(i)), Role.ICU, cal), range(0, icu_count)))
    staffs_er = list(map(lambda i: Staff("Dr.{0}".format(str(i)), Role.ER, cal), range(0, er_count)))
    return assign(cal, staffs_icu, staffs_er)

def assign(cal, staffs_icu: list, staffs_er: list):
    (staffs_icu, staffs_er) = assign_night_shift(cal, staffs_icu, staffs_er)
    (staffs_icu, staffs_er) = assign_day_shift(cal, staffs_icu, staffs_er)
    return staffs_icu + staffs_er

NIGHT_ER_STAFF_REQUIRED = 3
def assign_night_shift(cal, staffs_icu, staffs_er, idx = 0, day = 1):
    # 再起終了条件
    if day > cal.number_of_days():
        return (staffs_icu, staffs_er)

    # 夜勤ER割当
    for i in range(NIGHT_ER_STAFF_REQUIRED):
        idx = find_next_assignable(day, idx, staffs_icu + staffs_er, Shift.NIGHT, Section.ER)
        staff = staffs_icu[idx] if idx < len(staffs_icu) else staffs_er[idx - len(staffs_icu)]
        staff.assign(day, Shift.NIGHT, Section.ER)
        idx = increment_idx(idx, len(staffs_icu) + len(staffs_er))

    # 翌日分の割当を開始
    return assign_night_shift(cal, staffs_icu, staffs_er, idx, day + 1)

WEEKDAY_DAY_ICU_STAFF_REQUIRED = 3
WEEKDAY_DAY_ER_STAFF_REQUIRED = 3
WEEKDAY_DAY_EICU_STAFF_REQUIRED = 3
WEEKEND_DAY_ICU_STAFF_REQUIRED = 2
WEEKEND_DAY_ER_STAFF_REQUIRED = 3
WEEKEND_DAY_EICU_STAFF_REQUIRED = 3
def assign_day_shift(cal, staffs_icu, staffs_er, icu_idx = 0, er_idx = 0, day = 1):
    # 再起終了条件
    if day > cal.number_of_days():
        return (staffs_icu, staffs_er)

    # 日勤ER割当
    for i in range(WEEKDAY_DAY_ER_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_ER_STAFF_REQUIRED):
        er_idx = find_next_assignable(day, er_idx, staffs_er, Shift.DAY, Section.ER)
        staffs_er[er_idx].assign(day, Shift.DAY, Section.ER)
        er_idx = increment_idx(er_idx, len(staffs_er))

    # 日勤EICU割当
    for i in range(WEEKDAY_DAY_EICU_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_EICU_STAFF_REQUIRED):
        er_idx = find_next_assignable(day, er_idx, staffs_er, Shift.DAY, Section.EICU)
        staffs_er[er_idx].assign(day, Shift.DAY, Section.EICU)
        er_idx = increment_idx(er_idx, len(staffs_er))

    # 日勤ICU割当
    for i in range(WEEKDAY_DAY_ICU_STAFF_REQUIRED if cal.is_weekday(day) else WEEKEND_DAY_ICU_STAFF_REQUIRED):
        icu_idx = find_next_assignable(day, icu_idx, staffs_icu, Shift.DAY, Section.ICU)
        staffs_icu[icu_idx].assign(day, Shift.DAY, Section.ICU)
        icu_idx = increment_idx(icu_idx, len(staffs_icu))

    # 翌日分の割当を開始
    return assign_day_shift(cal, staffs_icu, staffs_er, icu_idx, er_idx, day + 1)


def find_next_assignable(day, idx, staffs, shift, section):
    # 当該シフトに勤務可能な次のスタッフを探す
    count = 0
    while not staffs[idx].can_assign(day, shift, section) and count < len(staffs):
        idx = increment_idx(idx, len(staffs))
        count += 1

    if not staffs[idx].can_assign(day, shift, section):
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
        score += staff.role.night_shift_assign_limit() - staff.assignment_count(Shift.NIGHT)

        for day in range(1, staff.calendar.number_of_days()):
            # 土日の休暇は加点
            if staff.calendar.is_weekend(day) and staff.is_day_off(day):
                score += 1

            # 連続休暇は加点
            if 2 <= day and staff.is_day_off(day - 1) and staff.is_day_off(day):
                score += 1

            # 同種連日勤務は加点
            if 2 <= day and staff.work_schedule_of(day, Shift.DAY) in [Section.ICU, Section.EICU] and staff.work_schedule_of(day - 1, Shift.DAY) == staff.work_schedule_of(day, Shift.DAY):
                score += 1
        return score

    # 全体観点でのシフトの質
    day_shift_dev = stdev([staff.assignment_count(Shift.DAY) for staff in staffs])
    night_shift_dev = stdev([staff.assignment_count(Shift.NIGHT) for staff in staffs])

    return score - day_shift_dev * 10 - night_shift_dev * 10

def modify(staffs, cal: MonthlyCalendar):
    # ランダムな日を抽出
    day = randint(1, cal.number_of_days())
    swap_night_shift(staffs, day)
    swap_day_shift(staffs, day)

    return staffs

def get_random_staff_assigned(staffs, day: int, shift:Shift):
    assigned = [staff for staff in staffs if staff.work_schedule_of(day, shift) != Section.OFF]
    return choice(assigned)

def get_staffs_unassigned(staffs, day: int, shift:Shift, role: Role = None):
    if role == None:
        return [staff for staff in staffs if staff.work_schedule_of(day, shift) == Section.OFF]
    else:
        return [staff for staff in staffs if staff.work_schedule_of(day, shift) == Section.OFF and staff.role == role]

def swap_night_shift(staffs, day):
    # 夜勤の人を探す
    staff_a = get_random_staff_assigned(staffs, day, Shift.NIGHT)

    # 夜勤に入れる人を探す
    unassigned = get_staffs_unassigned(staffs, day, Shift.NIGHT)
    shuffle(unassigned)
    for staff_b in unassigned:
        if staff_b.can_assign(day, Shift.NIGHT, Section.ER):
            staff_b.assign(day, Shift.NIGHT, Section.ER)
            staff_a.assign(day, Shift.NIGHT, Section.OFF)
            break

def swap_day_shift(staffs, day):
    # 日勤の人を探す
    staff_a = get_random_staff_assigned(staffs, day, Shift.DAY)
    assignment = staff_a.work_schedule_of(day, Shift.DAY)

    # 同一シフトの別人物を探す
    unassigned = get_staffs_unassigned(staffs, day, Shift.DAY, staff_a.role)
    shuffle(unassigned)
    for staff_b in unassigned:
        if staff_b.can_assign(day, Shift.DAY, assignment):
            staff_b.assign(day, Shift.DAY, assignment)
            staff_a.assign(day, Shift.DAY, Section.OFF)
            break

def assigned_count(staffs, day, shift, section):
    return len([staff for staff in staffs if staff.work_schedule_of(day, shift) == section])

def main():
    debug = True
    year = input('Year: ') if not debug else 2024
    month = input('Month: ') if not debug else 4
    icu_count = input('ICU count: ') if not debug else 5
    er_count = input('ER count: ') if not debug else 20
    attempts = input('Attempt count: ') if not debug else 10000

    cal = MonthlyCalendar(year, month)
    work_schedule = generate_base_work_schedule(cal, icu_count, er_count)
    print('initial score = {0}'.format(evaluate(work_schedule)))

    count = 0
    improved = 0
    while count < attempts:
        count += 1
        # deep copy base_shift
        modified = modify(deepcopy(work_schedule), cal)
        if evaluate(modified) > evaluate(work_schedule) and all([staff.is_valid_work_schedule(False) for staff in modified]):
            improved += 1
            work_schedule = modified
    print('improved {0} times in {1} attempts, final score = {2}'.format(improved, attempts, evaluate(work_schedule)))

    for staff in work_schedule:
        staff.print_work_schedule()
    print()

    day_icu_counts = []
    day_er_counts = []
    day_eicu_counts = []
    night_er_counts = []
    for day in range(1, cal.number_of_days() + 1):
        day_icu_counts.append(assigned_count(work_schedule, day, Shift.DAY, Section.ICU))
        day_er_counts.append(assigned_count(work_schedule, day, Shift.DAY, Section.ER))
        day_eicu_counts.append(assigned_count(work_schedule, day, Shift.DAY, Section.EICU))
        night_er_counts.append(assigned_count(work_schedule, day, Shift.NIGHT, Section.ER))

    print('D ICU', end='\t')
    for count in day_icu_counts:
        print(count, end='\t')
    print()

    print('D ER', end='\t')
    for count in day_er_counts:
        print(count, end='\t')
    print()

    print('D EICU', end='\t')
    for count in day_eicu_counts:
        print(count, end='\t')
    print()

    print('N ER', end='\t')
    for count in night_er_counts:
        print(count, end='\t')
    print()


    for staff in work_schedule:
        staff.print_stats()

    print('Validity: {0}'.format(all([staff.is_valid_work_schedule(True) for staff in work_schedule])))