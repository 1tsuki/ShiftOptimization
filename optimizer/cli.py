import calendar
import datetime
from optimizer.evaluator import Evaluator
from optimizer.intern import NIGHT_ASSIGN_LIMIT_ER, NIGHT_ASSIGN_LIMIT_ICU, Role, Section
from optimizer.modifier import Modifier
from optimizer.scheduler import PaidTimeOffRequest, Scheduler


def main(year: int, month: int, er_count: int, icu_count: int, max_attempt: int, pto_requests: list[PaidTimeOffRequest]):
    # 初期シフトの生成
    start_date = datetime.date(year, month, 1)
    end_date = start_date + datetime.timedelta(days=calendar.monthrange(year, month)[1])
    print(start_date.strftime('Start optimizing shift for %Y/%m'))
    print('ER interns:{0}, ICU interns:{1}'.format(er_count, icu_count))
    print('Requested PTOs:')
    for request in pto_requests:
        print('  {0} : {1}'.format(request.role.name, ', '.join([date.strftime('%Y/%m/%d') for date in request.dates])))
    print('========================================')

    work_schedule = Scheduler(er_count, icu_count, pto_requests).schedule(start_date, end_date)
    current_score = Evaluator.evaluate(work_schedule)

    # 初期値を出力
    print('initial score = {0}'.format(current_score))

    # 進化的アプローチで内容を改善
    attempt, swapped, improved = 0, 0, 0
    while attempt < max_attempt:
        attempt += 1

        # ランダム進化したシフトを生成
        modified = Modifier(work_schedule).modify()
        new_score = Evaluator.evaluate(modified)
        print('\rattempt:{0}/{1}, current score:{2}'.format(attempt, max_attempt, current_score), end='')

        # スコアが同値以上ならば変化を受容
        if current_score <= new_score:
            work_schedule = modified
            swapped += 1

            # スコアが向上するならば向上回数を記録
            if current_score < new_score:
                current_score = new_score
                improved += 1

    # 実行結果を出力
    print()
    print('========================================')
    print('swapped {0} times and improved {1} times in {2} attempts\n'.format(swapped, improved, max_attempt))
    print_stats(work_schedule)
    print_calendar(work_schedule)

def print_stats(work_schedule):
    print('Shift stats')
    for intern in work_schedule:
        intern.print_stats()
    print()

def print_calendar(work_schedule):
    print('Shift calendar')
    # 日付一覧
    is_first = True
    for date in work_schedule[0].get_work_schedule_range():
        if is_first:
            print(date.strftime('%b'), end='\t')
            is_first = False

        print(date.strftime('%d(%a)'), end='\t')
    print()

    # シフト一覧
    for intern in work_schedule:
        print(intern.name, end='\t')

        for date in intern.get_work_schedule_range():
            section = intern.assign_of(date)
            if date.weekday() in [5, 6]: # 週末は青背景
                print('\033[44m', end='')
            if section == Section.NER: # 夜勤は赤文字
                print('\033[31m', end='')
            if section == Section.PTO: # 有給は青文字
                print('\033[34m', end='')
            if section == Section.OFF: # オフ日は非表示
                print('\033[08m', end='')
            print('{:4}'.format(section.name), end='\t')
            print('\033[0m', end='')
        print()