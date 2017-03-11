import sys
import math
import time
from inspect import currentframe
from operator import methodcaller
from operator import attrgetter


class DebugTool:
    def __init__(self):
        try:
            self.fd = open(r"input.txt")
        except (ImportError, OSError):
            self.debug_mode = False
        else:
            import matplotlib.pyplot as plt
            self.plt = plt
            self.fg = None
            self.ax = None
            self.debug_mode = True

    def input(self):
        if self.debug_mode:
            data = self.fd.readline()
        else:
            data = input()
        print(data, file=sys.stderr, flush=True)
        return data

    def start_timer(self):
        self.timer = time.time()

    def elapsed_time(self):
        end_time = time.time()
        interval = end_time - self.timer
        self.stderr(interval * 1000, "m sec")

    @staticmethod
    def stderr(*args):
        cf = currentframe()
        print(*args, "@" + str(cf.f_back.f_lineno), file=sys.stderr, flush=True)

    def plot_vector_clock(self, vct, clr="b", txt=""):
        # todo: refactor in OO style
        self.plt.plot((0, vct[0]), (0, vct[1]), color=clr)
        self.plt.text(vct[0], vct[1], txt)


class Factory:
    def __init__(self, entity_id, owner, cyborgs, production):
        self.entity_id = int(entity_id)
        self.owner = int(owner)
        self.cyborgs = int(cyborgs)  # number of stationed cyborgs
        self.production = int(production)

        # Represents number of cyborgs available for garrison or troop in this factory
        if self.owner == 1:
            self.reserved = int(cyborgs)
        else:
            self.reserved = 0

        # Approximate turns_turns_to_capture by using distance of 2nd closest factory
        # ToDo: Adjust the approximating formula by the game result
        if self.owner == 1:
            self.turns_to_capture = 0
        else:
            distances = [f.distance_to(self) for f in [f for f in factories if f.owner == 1]]
            distances.sort()
            self.turns_to_capture = distances[1]

        # Represents number of cyborgs required to send from other factories in order to keep or capture this factory
        # Does not include number of garrisons
        self.cyborgs_required = -sum((t.owner for t in troops.coming_to(self)))
        if self.owner == 1:
            self.cyborgs_required -= self.cyborgs
        elif self.owner == 0:
            self.cyborgs_required += self.cyborgs
        else:
            self.cyborgs_required += self.cyborgs
            self.cyborgs_required += self.production * self.turns_to_capture

        turns_for_rating = 100
        return_ = self.production * (turns_for_rating - self.turns_to_capture)
        expense = base_garrisons * (turns_for_rating - self.turns_to_capture)
        investment = self.cyborgs_required
        self.rating = return_ / expense + investment

    def ppc(self):
        # TODO: Consider the cyborgs to be produced and moving to defence
        production_per_cyborgs = self.production / (self.cyborgs + base_garrisons)
        # TODO: Implement this after #1
        # if self.owner == -1:
        #     production_per_cyborgs *= 1.5
        return production_per_cyborgs

    def distance_to(self, factory):
        """Returns distance from self to factory.
        Requires variable 'links' defined."""
        for link in links:
            if {link[0], link[1]} == {self.entity_id, factory.entity_id}:
                return link[2]

    def summon_cyborgs(self, cyborgs):
        """Returns tuple of tuple of factories that send cyborgs, number of cyborgs.
        Requires variable 'factories' defined"""
        cs = cyborgs
        fs = factories.ally()
        moves = []

        # Factories are ordered by the distance from self.
        fs.sort(key=methodcaller("distance_to", self))
        for f in fs:
            if f.reserved >= cs:
                moves.append([f.entity_id, cs])
                f.reserved -= cs
                cs = 0
                break
            else:
                moves.append([f.entity_id, f.reserved])
                cs -= f.reserved
                f.reserved = 0
        return moves


class Factories(list):
    def find_bomb_target(self):
        """Returns source and destination for the bombing operation.
        Source: my factory closest to the target
        Destination: opponent's factory that hold most cyborgs and production"""
        dst = max((f for f in self if f.owner == -1), key=attrgetter("cyborgs", "production"))
        src = min((f for f in self if f.owner == 1), key=methodcaller("distance_to", dst))
        return src, dst

    def ally(self):
        return [e for e in self if e.owner == 1]  # type: Factories

    def enemy(self):
        return [e for e in self if e.owner == -1]  # type: Factories

    def coming_to(self, factory):
        return [e for e in self if e.factory_to == factory]  # type: Factories


class Troop:
    def __init__(self, entity_id, owner, factory_from, factory_to, cyborgs, turns_to_arrive):
        self.entity_id = int(entity_id)
        self.owner = int(owner)
        self.factory_from = int(factory_from)
        self.factory_to = int(factory_to)
        self.cyborgs = int(cyborgs)
        self.turns_to_arrive = int(turns_to_arrive)


class Troops(list):
    def ally(self):
        return [e for e in self if e.owner == 1]  # type: Troops

    def enemy(self):
        return [e for e in self if e.owner == -1]  # type: Troops

    def coming_to(self, factory):
        return [e for e in self if e.factory_to == factory]  # type: Troops


DT = DebugTool()

# Initial Input
factory_count = int(DT.input())  # the number of factories
link_count = int(DT.input())  # the number of links between factories
links = []
for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in DT.input().split()]
    links.append((factory_1, factory_2, distance))

# Global Variables
current_turn = 0
base_garrisons = 1  # Default number of base defender
my_bombs = 2
command = ""

# Global Parameters
ttb = (15, 30)  # Thresholds To Bomb
dcr = 1 / 4  # Ratio to calculate the number of stationed cyborg for initial number of cyborg

# Game Loop
while True:
    entity_count = int(DT.input())  # the number of entities (e.g. factories and troops)
    factories = Factories()
    troops = Troops()

    for i in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = DT.input().split()
        if entity_type == "FACTORY":
            factories.append(Factory(entity_id, arg_1, arg_2, arg_3))
        elif entity_type == "TROOP":
            troops.append(Troop(entity_id, arg_1, arg_2, arg_3, arg_4, arg_5))

    # Determine defending troop size
    if current_turn == 0:
        fct = max([f for f in factories if f.owner == 1], attrgetter("cyborgs"))  # type: Factory
        base_garrisons = int(fct.cyborgs * dcr)

    # MAIN LOGIC
    # Check if my factory and the opponent's exists
    owners = [f.owner for f in factories]
    if owners.count(1) != 0 and owners.count(-1) != 0:
        # Dispatch bomb when conditions match
        src, dst = factories.find_bomb_target()  # type: Factory, Factory
        if (my_bombs > 1 and dst.cyborgs > ttb[0]) or (my_bombs > 0 and dst.cyborgs > ttb[1]):
            if len(command):
                command += ";"
            command += "BOMB {0} {1} ".format(src.entity_id, dst.entity_id)
            my_bombs -= 1

        # Order factories by rating
        factories.sort(key=attrgetter("rating", "owner"))
        for f in factories:  # type: Factory
            cr = f.cyborgs_required
            if f.reserved >= cr:
                f.reserved -= cr
                cr = 0
            else:
                cr -= f.reserved
                f.reserved = 0
                moves = f.summon_cyborgs(cr)
                for m in moves:
                    if len(command):
                        command += ";"
                    command += "MOVE {0} {1} {2}".format(m[0], m[1], f.entity_id)

                    # # For all of my factories
                    # for fct in [f for f in factories if f.owner == 1]:
                    #
                    #     # Select target factory
                    #     target = max([f for f in factories if f.owner != 1], key=lambda f: f.ppc())  # type: Factory
                    #     # for i in [f for f in factories if f.owner != 1]:
                    #     #     DT.stderr("ppc:", i.ppc())
                    #
                    #     # Determine attacking troop size
                    #     if fct.production == 0:
                    #         attackers = fct.cyborgs
                    #     else:
                    #         attackers = fct.cyborgs - minimal_garrison
                    #
                    #     if fct.cyborgs > minimal_garrison:
                    #         if len(command):
                    #             command += ";"
                    #         command += "MOVE {0} {1} {2}".format(fct.entity_id, target.entity_id, attackers)

    # Turn End Process
    if len(command):
        print(command)
    else:
        print("WAIT")
    command = ""
    current_turn += 1
