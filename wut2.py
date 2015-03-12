from bge import logic
from bge import events
from bge import render

import time

pt = [time.time()]

x0 = 0.
y0 = 0.
z0 = 0.
x1 = 1.
y1 = 1.
z1 = 1.

class Mongo:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.
        self.dx = 1.
        self.dy = 1.
        self.dz = 1.

m = Mongo()

print("[Only printed on module load")

def update():
    t = time.time()
    dt = t - pt[0]
    pt[0] = t
    
    controller = logic.getCurrentController()
    self = controller.owner

    bpm = 130.
    bps = bpm / 60.
    period = 1. / bps
    k = (t % period) / period

    self.worldPosition.x = m.x + m.dx * k
    self.worldPosition.y = m.y + m.dy * k
    self.worldPosition.z = m.z + m.dz * k

    #motion = controller.actuators['Motion']

    key = logic.keyboard.events
    kbleft = key[events.AKEY]
    kbright = key[events.DKEY]
    kbup = key[events.WKEY]
    kbdown = key[events.SKEY]

    if kbleft:
        m.x -= 10. * dt
    if kbright:
        m.x += 10. * dt
    if kbup:
        m.y += 10. * dt
    if kbdown:
        m.y -= 10. * dt

    # Una game property :>
    print(self['mario'])
    
    
    print(dt, kbleft, kbright, kbup, kbdown)