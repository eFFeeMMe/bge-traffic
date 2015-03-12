from random import random

from bge import logic
from bge import events
from bge import render

import time

pt = [time.time()]

scene = logic.getCurrentScene()

class Master:
    def __init__(self):
        self.cubes = []
        print("[Only printed on module load")

    def add_cube(self, cube):
        self.cubes.append(cube)

master = Master()

def update():
    t = time.time()
    dt = t - pt[0] # better fix this
    pt[0] = t

    key = logic.keyboard.events
    kbleft = key[events.AKEY]
    kbright = key[events.DKEY]
    kbup = key[events.WKEY]
    kbdown = key[events.SKEY]

    controller = logic.getCurrentController()
    self = controller.owner

    if not self['init']:
        self['init'] = True
        self['k'] = 5. * random()
        master.add_cube(self)
        print(master.cubes)

    self.worldPosition.x = ((self['k'] + t) % 3.) * self['k']
    self.worldPosition.y = ((self['k'] + t) % 3.) * self['k']
    self.worldPosition.z = ((self['k'] + t) % 3.) * self['k']