import sys
import math
import time
from inspect import currentframe


class DebugTool:
    def __init__(self):
        try:
            self.fd = open(r"C:\Users\JUNJI\Documents\Condingame\pyCharmProject\FantasticBits\input.txt")
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
        self.cyborgs = int(cyborgs)
        self.production = int(production)

    def ppc(self):
        # TODO: Consider the cyborgs to be produced and moving to defence
        production_per_cyborgs = self.production / (self.cyborgs + defenders)
        # TODO: Implement this after #1
        # if self.owner == -1:
        #     production_per_cyborgs *= 1.5
        return production_per_cyborgs


class Troop:
    def __init__(self, entity_id, owner, factory_from, factory_to, cyborgs, turns_to_arrive):
        self.entity_id = int(entity_id)
        self.owner = int(owner)
        self.factory_from = int(factory_from)
        self.factory_to = int(factory_to)
        self.cyborgs = int(cyborgs)
        self.turns_to_arrive = int(turns_to_arrive)


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
defenders = 1
command = ""

# Game Loop
while True:
    entity_count = int(DT.input())  # the number of entities (e.g. factories and troops)
    factories = []  # type: List[Factory]
    troops = []  # type: List[Troop]

    for i in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = DT.input().split()
        if entity_type == "FACTORY":
            factories.append(Factory(entity_id, arg_1, arg_2, arg_3))
        elif entity_type == "TROOP":
            troops.append(Troop(entity_id, arg_1, arg_2, arg_3, arg_4, arg_5))

    # MAIN LOGIC
    # Check if the opponent's factory exists
    if [f for f in factories if f.owner != 1]:

        # Determine defending troop size
        if current_turn == 0:
            fct = max([f for f in factories if f.owner == 1], key=lambda f: f.cyborgs)  # type: Factory
            defenders = int(fct.cyborgs / 2)

        # For all of my factories
        for fct in [f for f in factories if f.owner == 1]:

            # Select target factory
            target = max([f for f in factories if f.owner != 1], key=lambda f: f.ppc())  # type: Factory
            # for i in [f for f in factories if f.owner != 1]:
            #     DT.stderr("ppc:", i.ppc())

            # Determine attacking troop size
            if fct.production == 0:
                attackers = fct.cyborgs
            else:
                attackers = fct.cyborgs - defenders

            if fct.cyborgs > defenders:
                if len(command):
                    command += ";"
                command += "MOVE {0} {1} {2}".format(fct.entity_id, target.entity_id, attackers)

    # Turn End Process
    if len(command):
        print(command)
    else:
        print("WAIT")
    command = ""
    current_turn += 1
