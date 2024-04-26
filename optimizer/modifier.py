import random
from copy import deepcopy
from optimizer.intern import Role, Section

class Modifier:
    def __init__(self, interns: list):
        self.interns = deepcopy(interns)

    def modify(self):
        day = random.randint(1, len(self.interns[0].work_schedule))
        section = random.choice([section for section in list(Section) if section != Section.OFF])

        role = None if section == Section.NER else Role.ICU if section == Section.ICU else Role.ER

        assigned_candidates = self.filter_assignable(day, Section.OFF, self.find_assigned(day, section))
        if len(assigned_candidates) == 0:
            return self.interns
        assigned = random.choice(self.filter_assignable(day, Section.OFF, assigned_candidates))

        unassigned_candidates = self.filter_assignable(day, section, self.find_unassigned(day, role))
        if len(unassigned_candidates) == 0:
            return self.interns
        unassigned = random.choice(unassigned_candidates)

        assigned.assign(day, Section.OFF)
        unassigned.assign(day, section)

        return self.interns

    def find_assigned(self, day: int, section: Section):
        return [intern for intern in self.interns if intern.assign_of(day) == section]

    def find_unassigned(self, day: int, role: Role = None):
        if role == None:
            return [intern for intern in self.interns if intern.assign_of(day) == Section.OFF]
        else:
            return [intern for intern in self.interns if intern.assign_of(day) == Section.OFF and intern.role == role]

    def filter_assignable(self, day: int, section: Section, interns: list):
        return [intern for intern in interns if intern.can_assign(day, section)]
