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
        PaidTimeOffRequest(Role.ER, [datetime.date(2024, 4, 5), datetime.date(2024, 4, 6)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 4, 1), datetime.date(2024, 4, 2)]),
        PaidTimeOffRequest(Role.ICU, [datetime.date(2024, 4, 15), datetime.date(2024, 4, 16)]),
    ]
    main(args.year, args.month, args.er_count, args.icu_count, args.max_attempt, pto_requests)