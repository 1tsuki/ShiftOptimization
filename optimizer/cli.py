import calendar
import random
import datetime
from optimizer.evaluator import Evaluator
from optimizer.intern import NIGHT_ASSIGN_LIMIT_ER, NIGHT_ASSIGN_LIMIT_ICU, Role, Section
from optimizer.modifier import Modifier
from optimizer.scheduler import Scheduler


def main():
    debug = True
    year = input('Year: ') if not debug else 2024
    month = input('Month: ') if not debug else 4
    er_count = input('ER count: ') if not debug else 14
    icu_count = input('ICU count: ') if not debug else 6
    max_attempt = input('Max attempt: ') if not debug else 10000

    # 初期シフトの生成
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])

    work_schedule = Scheduler(er_count, icu_count).schedule(start_date, end_date)
    current_score = Evaluator.evaluate(work_schedule)
    print('initial score = {0}'.format(current_score))

    # 進化的アプローチで内容を改善
    attempt, swapped, improved = 0, 0, 0
    while attempt < max_attempt:
        attempt += 1

        # ランダム進化したシフトを生成
        modified = Modifier(work_schedule).modify()
        new_score = Evaluator.evaluate(modified)

        # スコアが同値以上ならば変化を受容
        if current_score <= new_score:
            work_schedule = modified
            swapped += 1

            # スコアが向上するならば向上回数を記録
            if current_score < new_score:
                current_score = new_score
                improved += 1

    print('swapped {0} times and improved {1} times in {2} attempts, final score = {3}'.format(swapped, improved, max_attempt, current_score))

    for intern in work_schedule:
        intern.print_stats()
    print()

    for intern in work_schedule:
        print(intern.name, end='\t')

        for date in intern.get_work_schedule_range():
            section = intern.assign_of(date)

            # 週末は青背景
            if date.weekday() in [5, 6]:
                print('\033[44m', end='')
            # 夜勤は赤文字
            if section == Section.NER:
                print('\033[31m', end='')
            # オフ日は非表示
            if section == Section.OFF:
                print('\033[08m', end='')
            print('{:4}'.format(section.name), end='\t')
            print('\033[0m', end='')
        print()

    print()