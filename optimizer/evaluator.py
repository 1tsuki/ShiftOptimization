import datetime
from optimizer.workSchedule import NIGHT_ASSIGN_LIMIT_ER, NIGHT_ASSIGN_LIMIT_ICU, Role, Section
from statistics import stdev

class Evaluator:
    def evaluate(workSchedules: list):
        # シフトの質を評価する評価関数
        # 個人観点のシフトの質
        score = 0

        for workSchedule in workSchedules:
            year = 0
            month = 0
            for date in workSchedule.get_work_schedule_range():
                # 月初に月全体の計算を実施
                if year != date.year or month != date.month:
                    year = date.year
                    month = date.month

                    if workSchedule.role == Role.ER:
                        # 総夜勤日数は上限より少ないほうが好ましい
                        score += NIGHT_ASSIGN_LIMIT_ER - workSchedule.monthly_assign_count(year, month, Section.NER)

                        # ER従事医はER、EICUの勤務日数の差が大きいと減点
                        score -= abs(workSchedule.monthly_assign_count(year, month, Section.ER) - workSchedule.monthly_assign_count(year, month, Section.EICU))

                    if workSchedule.role == Role.ICU:
                        # 総夜勤日数は上限より少ないほうが好ましい
                        score += NIGHT_ASSIGN_LIMIT_ICU - workSchedule.monthly_assign_count(year, month, Section.NER)

                # 土日の休暇は加点
                if date.weekday in [5, 6] and workSchedule.is_day_off(date):
                    score += 1

                # 連続休暇は加点
                if workSchedule.is_day_off(date - datetime.timedelta(days=1)) and workSchedule.is_day_off(date):
                    score += 1

                # 同種連日勤務は加点
                if workSchedule.assign_of(date - datetime.timedelta(days=1)) == workSchedule.assign_of(date):
                    score += 1

        # 全体観点でのシフトの質
        er_workSchedules = [workSchedule for workSchedule in workSchedules if workSchedule.role == Role.ER]
        icu_workSchedules = [workSchedule for workSchedule in workSchedules if workSchedule.role == Role.ICU]

        # ER、ICUの日勤、夜勤のバラつきが少ないほうが好ましい
        score -= stdev([workSchedule.total_assign_count(Section.ER) + workSchedule.total_assign_count(Section.ICU) + workSchedule.total_assign_count(Section.EICU) for workSchedule in er_workSchedules]) * 100
        score -= stdev([workSchedule.total_assign_count(Section.NER) for workSchedule in er_workSchedules]) * 100
        score -= stdev([workSchedule.total_assign_count(Section.ER) + workSchedule.total_assign_count(Section.ICU) + workSchedule.total_assign_count(Section.EICU) for workSchedule in icu_workSchedules]) * 100
        score -= stdev([workSchedule.total_assign_count(Section.NER) for workSchedule in icu_workSchedules]) * 100

        return score