import random
import datetime
from copy import deepcopy
from optimizer.intern import Role, Section

class Modifier:
    def __init__(self, interns: list):
        self.interns = deepcopy(interns)

    def modify(self):
        date = random.choice(self.interns[0].get_work_schedule_range())
        section = random.choice([section for section in list(Section) if section not in [Section.OFF, Section.PTO]])

        role = None if section == Section.NER else Role.ICU if section == Section.ICU else Role.ER

        assigned_candidates = self.filter_assignable(date, Section.OFF, self.find_assigned(date, section))
        if len(assigned_candidates) == 0:
            return self.interns
        assigned = random.choice(self.filter_assignable(date, Section.OFF, assigned_candidates))

        unassigned_candidates = self.filter_assignable(date, section, self.find_unassigned(date, role))
        if len(unassigned_candidates) == 0:
            return self.interns
        unassigned = random.choice(unassigned_candidates)

        assigned.assign(date, Section.OFF)
        unassigned.assign(date, section)

        return self.interns

    def find_assigned(self, date: datetime.date, section: Section):
        return [intern for intern in self.interns if intern.assign_of(date) == section]

    def find_unassigned(self, date: datetime.date, role: Role = None):
        if role == None:
            return [intern for intern in self.interns if intern.assign_of(date) == Section.OFF]
        else:
            return [intern for intern in self.interns if intern.assign_of(date) == Section.OFF and intern.role == role]

    def filter_assignable(self, date: datetime.date, section: Section, interns: list):
        return [intern for intern in interns if intern.can_assign(date, section)]
