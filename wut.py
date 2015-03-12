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

print("[Only printed on module load")

def update():
    t = time.time()
    dt = t - pt[0]
    pt[0] = t
    
    controller = logic.getCurrentController()
    self = controller.owner
    
    
    k = (t % 5.) / 5.
    self.worldPosition.x = x0 + x1 * k
    self.worldPosition.y = y0 + y1 * k
    self.worldPosition.z = z0 + z1 * k
    
    #motion = controller.actuators['Motion']
    
    key = logic.keyboard.events
    kbleft = key[events.AKEY]
    kbright = key[events.DKEY]
    kbup = key[events.WKEY]
    kbdown = key[events.SKEY]
    
    # Una game property :>
    print(self['mario'])
    
    
    print(dt, kbleft, kbright, kbup, kbdown)