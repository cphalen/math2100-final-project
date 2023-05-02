from enum import Enum
import matplotlib.pyplot as plt
import pprint
import copy

ONE_YEAR = 365

class Group(Enum):
    RAIDER = 1
    SURVIVALIST = 2
    CIVILIAN = 3
    ZOMBIE = 4
    REMOVED = 5

class Params:
    EPSILON = 0.000001 # 10^10

    def birth_rate(group: Group):
        match group:
            case Group.RAIDER:
                return 0.000004
            case Group.SURVIVALIST:
                return 0.000001
            case Group.CIVILIAN:
                return 0.000016
            case _:
                return None

    def death_rate(group: Group):
        match group:
            case Group.RAIDER:
                return 0.0001
            case Group.SURVIVALIST:
                return 0.0003
            case Group.CIVILIAN:
                return 0.00006
            case Group.ZOMBIE:
                return 0.00003
            case _:
                return None

    def zombie_rate(group: Group):
        match group:
            case Group.RAIDER:
                return 0.0002
            case Group.SURVIVALIST:
                return 0.0004
            case Group.CIVILIAN:
                return 0.00003
            case _:
                return None
            
    def exchange_rate(src_group: Group, dest_group: Group):
        match (src_group, dest_group):
            case (Group.RAIDER, Group.SURVIVALIST):
                return 0.0
            case (Group.SURVIVALIST, Group.RAIDER):
                return 0.0008
            case (Group.SURVIVALIST, Group.CIVILIAN):
                return 0.0
            case (Group.CIVILIAN, Group.SURVIVALIST):
                return 0.0003
            case _:
                return None
            
class Sim:

    def __init__(self):
        self.populations = {
            Group.RAIDER: 1.0,
            Group.SURVIVALIST: 1.0,
            Group.CIVILIAN: 1.0,
            Group.ZOMBIE: 1.0,
            Group.REMOVED: 0,
        }

        self.history = {}
        for group in self.populations.keys():
            self.history[group] = [self.populations[group]]

        self.printer = pprint.PrettyPrinter(indent=4)

    def step_group(self, group):
        match group:
            case Group.RAIDER:
                from_birth = Params.birth_rate(Group.RAIDER) * self.populations.get(Group.RAIDER)
                from_survivalist = Params.exchange_rate(Group.SURVIVALIST, Group.RAIDER) * self.populations.get(Group.RAIDER) * self.populations.get(Group.SURVIVALIST)
                to_survivalist = Params.exchange_rate(Group.RAIDER, Group.SURVIVALIST) * self.populations.get(Group.RAIDER) * self.populations.get(Group.SURVIVALIST)
                to_zombie = Params.zombie_rate(Group.RAIDER) * self.populations.get(Group.RAIDER) * self.populations.get(Group.ZOMBIE)
                to_removed = Params.death_rate(Group.RAIDER) * self.populations.get(Group.RAIDER)
                return from_birth + from_survivalist - to_survivalist - to_zombie - to_removed
            case Group.SURVIVALIST:
                from_birth = Params.birth_rate(Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST)
                from_raider = Params.exchange_rate(Group.RAIDER, Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST) * self.populations.get(Group.RAIDER)
                from_civilian = Params.exchange_rate(Group.CIVILIAN, Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST) * self.populations.get(Group.CIVILIAN)
                to_raider = Params.exchange_rate(Group.SURVIVALIST, Group.RAIDER) * self.populations.get(Group.SURVIVALIST) * self.populations.get(Group.RAIDER)
                to_civilian = Params.exchange_rate(Group.SURVIVALIST, Group.CIVILIAN) * self.populations.get(Group.SURVIVALIST) * self.populations.get(Group.CIVILIAN)
                to_zombie = Params.zombie_rate(Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST) * self.populations.get(Group.ZOMBIE)
                to_removed = Params.death_rate(Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST)
                return from_birth + from_raider + from_civilian - to_raider - to_civilian - to_zombie - to_removed
            case Group.CIVILIAN:
                from_birth = Params.birth_rate(Group.SURVIVALIST) * self.populations.get(Group.CIVILIAN)
                from_survivalist = Params.exchange_rate(Group.SURVIVALIST, Group.CIVILIAN) * self.populations.get(Group.CIVILIAN) * self.populations.get(Group.SURVIVALIST)
                to_survivalist = Params.exchange_rate(Group.CIVILIAN, Group.SURVIVALIST) * self.populations.get(Group.CIVILIAN) * self.populations.get(Group.SURVIVALIST)
                to_zombie = Params.zombie_rate(Group.CIVILIAN) * self.populations.get(Group.CIVILIAN) * self.populations.get(Group.ZOMBIE)
                to_removed = Params.death_rate(Group.CIVILIAN) * self.populations.get(Group.CIVILIAN)
                return from_birth + from_survivalist - to_survivalist - to_zombie - to_removed
            case Group.ZOMBIE:
                from_raider = Params.zombie_rate(Group.RAIDER) * self.populations.get(Group.ZOMBIE) * self.populations.get(Group.RAIDER)
                from_survivalist = Params.zombie_rate(Group.SURVIVALIST) * self.populations.get(Group.ZOMBIE) * self.populations.get(Group.SURVIVALIST)
                from_civilian = Params.zombie_rate(Group.CIVILIAN) * self.populations.get(Group.ZOMBIE) * self.populations.get(Group.CIVILIAN)
                to_removed = Params.death_rate(Group.ZOMBIE) * self.populations.get(Group.ZOMBIE)
                return from_raider + from_survivalist + from_civilian - to_removed
            case Group.REMOVED:
                from_raider = Params.death_rate(Group.RAIDER) * self.populations.get(Group.RAIDER)
                from_survivalist = Params.death_rate(Group.SURVIVALIST) * self.populations.get(Group.SURVIVALIST)
                from_civilian = Params.death_rate(Group.CIVILIAN) * self.populations.get(Group.CIVILIAN)
                from_zombie = Params.death_rate(Group.ZOMBIE) * self.populations.get(Group.ZOMBIE)
                return from_raider + from_survivalist + from_civilian + from_zombie
            
    def step(self):
        updates = {}

        # simulate all of these transformations happening simultaneous
        for group in self.populations.keys():
            new_population = self.step_group(group)
            updates[group] = new_population

        # update state with new population values
        for group in updates.keys():
            self.populations[group] += updates[group]
            self.populations[group] = max(self.populations[group], 0)
            self.history[group].append(self.populations[group])

    def simulate(self, limit=None):
        i = 0
        while True:
            old_populations = copy.copy(self.populations)
            self.step()

            diff = 0
            i += 1
            for group in old_populations.keys():
                diff += abs(self.populations.get(group) - old_populations.get(group))

            if diff < Params.EPSILON or (limit is not None and i >= limit):
                print(i)
                return

    def print(self):
        self.printer.pprint(self.populations)
        total = 0
        for value in self.populations.values():
            total += value
        print(total)


    def plot(self):
        for group, history in self.history.items():
            if group == Group.REMOVED:
                # we don't need to display the removed
                continue
            plt.plot(list(range(len(history))), history, label=str(group), markersize=1)

        plt.xlabel('time (days)')
        plt.ylabel('population (relative to inital value)')
        plt.title('Group populations vs. time')
        plt.legend()

        plt.show()


if __name__ == "__main__":
    sim = Sim()
    sim.simulate(limit=10*ONE_YEAR)
    sim.print()
    sim.plot()
