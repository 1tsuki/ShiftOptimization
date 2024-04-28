import random
import datetime
from copy import deepcopy
from optimizer.workSchedule import Role, Section

class Modifier:
    def __init__(self, workSchedules: list):
        self.workSchedules = deepcopy(workSchedules)

    def modify(self):
        date = random.choice(self.workSchedules[0].get_work_schedule_range())
        section = random.choice([section for section in list(Section) if section not in [Section.OFF, Section.PTO]])

        role = None if section == Section.NER else Role.ICU if section == Section.ICU else Role.ER

        assigned_candidates = self.filter_assignable(date, Section.OFF, self.find_assigned(date, section))
        if len(assigned_candidates) == 0:
            return self.workSchedules
        assigned = random.choice(self.filter_assignable(date, Section.OFF, assigned_candidates))

        unassigned_candidates = self.filter_assignable(date, section, self.find_unassigned(date, role))
        if len(unassigned_candidates) == 0:
            return self.workSchedules
        unassigned = random.choice(unassigned_candidates)

        assigned.assign(date, Section.OFF)
        unassigned.assign(date, section)

        return self.workSchedules

    def find_assigned(self, date: datetime.date, section: Section):
        return [workSchedule for workSchedule in self.workSchedules if workSchedule.assign_of(date) == section]

    def find_unassigned(self, date: datetime.date, role: Role = None):
        if role == None:
            return [workSchedule for workSchedule in self.workSchedules if workSchedule.assign_of(date) == Section.OFF]
        else:
            return [workSchedule for workSchedule in self.workSchedules if workSchedule.assign_of(date) == Section.OFF and workSchedule.role == role]

    def filter_assignable(self, date: datetime.date, section: Section, workSchedules: list):
        return [workSchedule for workSchedule in workSchedules if workSchedule.can_assign(date, section)]
