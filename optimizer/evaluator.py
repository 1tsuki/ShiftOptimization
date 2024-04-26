import datetime
from optimizer.intern import NIGHT_ASSIGN_LIMIT_ER, NIGHT_ASSIGN_LIMIT_ICU, Role, Section
from statistics import stdev

class Evaluator:
    def evaluate(interns: list):
        # シフトの質を評価する評価関数
        # 個人観点のシフトの質
        score = 0

        for intern in interns:
            year = 0
            month = 0

            for date in intern.get_work_schedule_range():
                # 月初に月全体の情報を処理
                if year != date.year or month != date.month:
                    year = date.year
                    month = date.month

                    if intern.role == Role.ER:
                        # 総夜勤日数は上限より少ないほうが好ましい
                        score += NIGHT_ASSIGN_LIMIT_ER - intern.monthly_assign_count(year, month, Section.NER)

                        # ER従事医はER、EICUの勤務日数の差が大きいと減点
                        score -= abs(intern.monthly_assign_count(year, month, Section.ER) - intern.monthly_assign_count(year, month, Section.EICU))

                    if intern.role == Role.ICU:
                        # 総夜勤日数は上限より少ないほうが好ましい
                        score += NIGHT_ASSIGN_LIMIT_ICU - intern.monthly_assign_count(year, month, Section.NER)

                # 土日の休暇は加点
                if date.weekday in [5, 6] and intern.is_day_off(date):
                    score += 1

                # 連続休暇は加点
                if intern.is_day_off(date - datetime.timedelta(days=1)) and intern.is_day_off(date):
                    score += 1

                # 同種連日勤務は加点
                if intern.assign_of(date - datetime.timedelta(days=1)) == intern.assign_of(date):
                    score += 1

        # 全体観点でのシフトの質
        er_interns = [intern for intern in interns if intern.role == Role.ER]
        icu_interns = [intern for intern in interns if intern.role == Role.ICU]

        # ER、ICUの日勤、夜勤のバラつきが少ないほうが好ましい
        score -= stdev([intern.total_assign_count(Section.ER) + intern.total_assign_count(Section.ICU) + intern.total_assign_count(Section.EICU) for intern in er_interns]) * 100
        score -= stdev([intern.total_assign_count(Section.NER) for intern in er_interns]) * 100
        score -= stdev([intern.total_assign_count(Section.ER) + intern.total_assign_count(Section.ICU) + intern.total_assign_count(Section.EICU) for intern in icu_interns]) * 100
        score -= stdev([intern.total_assign_count(Section.NER) for intern in icu_interns]) * 100

        return score