import calendar

class MonthlyCalendar:
    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month

    def number_of_days(self) -> int:
        return calendar.monthrange(self.year, self.month)[1]

    def is_weekday(self, day: int) -> bool:
        return calendar.weekday(self.year, self.month, day) in range(0, 5)

    def is_weekend(self, day: int) -> bool:
        return not self.is_weekday(day)

    def print_dates(self):
        print('{0}月'.format(self.month), end='\t')
        for day in range(1, self.number_of_days() + 1):
            print(day, end='\t')
        print()