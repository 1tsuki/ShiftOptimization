from optimizer.calendar import MonthlyCalendar
from optimizer.intern import NIGHT_ASSIGN_LIMIT_ER, NIGHT_ASSIGN_LIMIT_ICU, Role, Section
from statistics import stdev

class Evaluator:
    def evaluate(cal: MonthlyCalendar, interns: list):
        # シフトの質を評価する評価関数
        # 個人観点のシフトの質
        score = 0
        for intern in interns:
            if intern.role == Role.ER:
                # 総夜勤日数は上限より少ないほうが好ましい
                score += NIGHT_ASSIGN_LIMIT_ER - intern.assign_count(Section.NER)

                # ER従事医はER、EICUの勤務日数の差が大きいと減点
                score -= abs(intern.assign_count(Section.ER) - intern.assign_count(Section.EICU))

            if intern.role == Role.ICU:
                # 総夜勤日数は上限より少ないほうが好ましい
                score += NIGHT_ASSIGN_LIMIT_ICU - intern.assign_count(Section.NER)

            for day in range(1, len(intern.work_schedule) + 1):
                # 土日の休暇は加点
                if cal.is_weekend(day) and intern.is_day_off(day):
                    score += 1

                # 連続休暇は加点
                if 2 <= day and intern.is_day_off(day - 1) and intern.is_day_off(day):
                    score += 1

                # 同種連日勤務は加点
                if 2 <= day and intern.assign_of(day) in [Section.ICU, Section.EICU] and intern.assign_of(day - 1) == intern.assign_of(day):
                    score += 1

        # 全体観点でのシフトの質
        er_interns = [intern for intern in interns if intern.role == Role.ER]
        icu_interns = [intern for intern in interns if intern.role == Role.ICU]

        er_day_shift_dev = stdev([intern.assign_count(Section.ER) + intern.assign_count(Section.ICU) + intern.assign_count(Section.EICU) for intern in er_interns])
        er_night_shift_dev = stdev([intern.assign_count(Section.NER) for intern in er_interns])
        icu_day_shift_dev = stdev([intern.assign_count(Section.ER) + intern.assign_count(Section.ICU) + intern.assign_count(Section.EICU) for intern in icu_interns])
        icu_night_shift_dev = stdev([intern.assign_count(Section.NER) for intern in icu_interns])

        return score - er_day_shift_dev * len(er_interns) - er_night_shift_dev * len(er_interns) - icu_day_shift_dev * len(icu_interns) - icu_night_shift_dev * len(icu_interns)