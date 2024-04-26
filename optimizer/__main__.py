import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year', type=int, default=datetime.now().year, help='target year to generate shift')
parser.add_argument('-m', '--month', type=int, default=datetime.now().month, help='target month to generate shift')
parser.add_argument('-e', '--er_count', type=int, default=15, help='number of ER interns')
parser.add_argument('-i', '--icu_count', type=int, default=5, help='number of ICU interns')
parser.add_argument('-a', '--max_attempt', type=int, default=100, help='max attempt to improve shift')

args = parser.parse_args()

if __name__ == '__main__':
    from .cli import main
    main(args.year, args.month, args.er_count, args.icu_count, args.max_attempt)