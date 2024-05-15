import argparse
import datetime

from optimizer.workSchedule import Role
from optimizer.scheduler import PaidTimeOffRequest

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year', type=int, default=datetime.datetime.now().year, help='target year to generate shift')
parser.add_argument('-m', '--month', type=int, default=datetime.datetime.now().month, help='target month to generate shift')
parser.add_argument('-e', '--er_count', type=int, default=15, help='number of ER interns')
parser.add_argument('-i', '--icu_count', type=int, default=5, help='number of ICU interns')
parser.add_argument('-a', '--max_attempt', type=int, default=5000, help='max attempt to improve shift')

args = parser.parse_args()

if __name__ == '__main__':
    from .cli import main
    # 有給取得希望日を設定
    pto_requests = [
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 8), datetime.date(2024, 6, 9), datetime.date(2024, 6, 7), datetime.date(2024, 6, 21), datetime.date(2024, 6, 22), datetime.date(2024, 6, 28)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 7), datetime.date(2024, 6, 14), datetime.date(2024, 6, 8), datetime.date(2024, 6, 9), datetime.date(2024, 6, 15), datetime.date(2024, 6, 16), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 8), datetime.date(2024, 6, 15), datetime.date(2024, 6, 22), datetime.date(2024, 6, 23), datetime.date(2024, 6, 29), datetime.date(2024, 6, 9)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 23), datetime.date(2024, 6, 8), datetime.date(2024, 6, 15), datetime.date(2024, 6, 22), datetime.date(2024, 6, 1), datetime.date(2024, 6, 5), datetime.date(2024, 6, 12)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 27), datetime.date(2024, 6, 28), datetime.date(2024, 6, 29), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 8), datetime.date(2024, 6, 15), datetime.date(2024, 6, 22), datetime.date(2024, 6, 23)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 2), datetime.date(2024, 6, 26), datetime.date(2024, 6, 27), datetime.date(2024, 6, 28), datetime.date(2024, 6, 29), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 8), datetime.date(2024, 6, 22), datetime.date(2024, 6, 23)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 2), datetime.date(2024, 6, 13), datetime.date(2024, 6, 20)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 15), datetime.date(2024, 6, 16), datetime.date(2024, 6, 17), datetime.date(2024, 6, 18), datetime.date(2024, 6, 19), datetime.date(2024, 6, 2)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 24), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 2), datetime.date(2024, 6, 9), datetime.date(2024, 6, 15), datetime.date(2024, 6, 16), datetime.date(2024, 6, 22), datetime.date(2024, 6, 23), datetime.date(2024, 6, 29)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 2), datetime.date(2024, 6, 3), datetime.date(2024, 6, 8), datetime.date(2024, 6, 9), datetime.date(2024, 6, 16), datetime.date(2024, 6, 21)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 3), datetime.date(2024, 6, 7), datetime.date(2024, 6, 9), datetime.date(2024, 6, 15), datetime.date(2024, 6, 22), datetime.date(2024, 6, 29)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 7), datetime.date(2024, 6, 12), datetime.date(2024, 6, 22), datetime.date(2024, 6, 23), datetime.date(2024, 6, 29), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 3), datetime.date(2024, 6, 28), datetime.date(2024, 6, 29), datetime.date(2024, 6, 30)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 6, 6), datetime.date(2024, 6, 23)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 14), datetime.date(2024, 6, 15)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 1), datetime.date(2024, 6, 6), datetime.date(2024, 6, 7), datetime.date(2024, 6, 8)]),
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 6, 11), datetime.date(2024, 6, 27), datetime.date(2024, 6, 28), datetime.date(2024, 6, 29), datetime.date(2024, 6, 30)]),
    ]
    main(args.year, args.month, args.er_count, args.icu_count, args.max_attempt, pto_requests)