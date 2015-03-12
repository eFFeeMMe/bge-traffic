"""Copyright (c) 2015 Francesco Mastellone

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
The road system is implemented as a graph of inter-referenced Way objects.
Ways keep track of which Vehicles are travelling along them, to inform other
Vehicles of who's in front of them and how far ahead they are, so that they may
keep a safe distance.

Intersections are a considerable approximation in that only one Way at a time is
allowed through. Still figuring out ways to prevent the collisions that would
result otherwise.

Cars have their origin in the back.

Each Way has a traffic_light value, that Intersections set.
...There's surely a better way to do that.

"""

from random import random, choice
from math import hypot

MAX_POS = 9999.

class Intersection:
    def __init__(self, ways=None):
        self.ways = ways if ways else []
        self.i = 0 # Active way
        self.t = 0.
        self.go = True
        self.go_time = 6.
        self.stop_time = 2. # Yellow traffic light

    def update(self, dt):
        self.t -= dt
        if self.t < 0.:
            if self.go:
                self.ways[self.i].traffic_light = 'yellow'
                self.t = self.stop_time
                self.go = False
            else:
                self.ways[self.i].traffic_light = 'red'
                self.i += 1
                self.i %= len(self.ways)
                self.ways[self.i].traffic_light = 'green'
                self.t = self.go_time
                self.go = True

class Way:
    def __init__(self, speed_limit=13.89/8.):
        self.traffic_light = 'green'
        self.speed_limit = speed_limit # m/s
        self.to = [] # Directed graph neighbors
        self.cars = []

    def next_car(self, car):
        """Picks the next [pos, car] from self and self.to"""
        self.cars.sort(key=lambda car: car.pos)
        i = self.cars.index(car)
        if i + 1 < len(self.cars):
            car2 = self.cars[i + 1]
            return car2.pos, car2

        elif self.to and self.to[0].cars: # TODO foresee where car goes
            car2 = self.to[0].cars[0]
            return car2.pos + self.length, car2
        else:
            return None, None

    def next_obstacle_position(self, car):
        """Returns distance from obstacle obstacle.pos or None if no obstacles
        are in sight"""
        obpos = MAX_POS # Obstacle position

        # Traffic lights
        if self.traffic_light == 'red':
            obpos = self.length
        elif self.traffic_light == 'yellow':
            if car.pos + car.safety_distance < self.length:
                obpos = self.length

        next_car_pos, _ = self.next_car(car)
        if next_car_pos and next_car_pos < obpos:
            obpos = next_car_pos

        return obpos

    def reach(self, car):
        self.cars.insert(0, car)

    def leave(self, car):
        self.cars.remove(car)

class LinearWay(Way):
    def __init__(self, x0, y0, x1, y1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x0 = x0
        self.y0 = y0
        self.dx = x1 - x0
        self.dy = y1 - y0
        self.length = hypot(x1 - x0, y1 - y0) # m

    x1 = property(lambda self: self.x0 + self.dx)
    y1 = property(lambda self: self.y0 + self.dy)

    def position_car(self, car):
        car.x = self.x0 + self.dx * (car.pos / self.length)
        car.y = self.y0 + self.dy * (car.pos / self.length)

class BezierWay(Way):
    def __init__(self, x0, y0, x1, y1, x2, y2, x3, y3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

        self.length = 0.
        xp = self.x0
        yp = self.y0
        for i in range(1, 65):
            t = float(i) / 64.
            u = 1. - t
            x = u*u*u*self.x0 + \
             3.*u*u*t*self.x1 + \
             3.*u*t*t*self.x2 + \
                t*t*t*self.x3
            y = u*u*u*self.y0 + \
             3.*u*u*t*self.y1 + \
             3.*u*t*t*self.y2 + \
                t*t*t*self.y3
            self.length += hypot(x - xp, y - yp)
            xp = x
            yp = y

    def position_car(self, car):
        t = car.pos / self.length
        u = 1. - t
        car.x = u*u*u*self.x0 + \
             3.*u*u*t*self.x1 + \
             3.*u*t*t*self.x2 + \
                t*t*t*self.x3
        car.y = u*u*u*self.y0 + \
             3.*u*u*t*self.y1 + \
             3.*u*t*t*self.y2 + \
                t*t*t*self.y3

class Vehicle:
    length = 4.
    acceleration = 7.84 / 2.
    deceleration = 7.84 # Max possible with g=9.81m/s, frictioncoeff=.8

    def __init__(self, way):
        self.pos = 0. # m along current way
        self.speed = 0. # m/s
        self.speed_mul = 1.0 - 0.3 * random() # % of speedlimit this car reaches

        self.way = way
        self.x = self.xp = way.x0
        self.y = self.yp = way.y0

    def update(self, dt):
        if self.pos > self.way.length:
            self.way.leave(self)
            self.pos -= self.way.length
            if self.way.to:
                self.way = choice(self.way.to)
                self.way.reach(self)
            else:
                self.on_dead_end()

        w = self.way

        # Reach top speed / Decelerate to top speed
        if self.speed < w.speed_limit * self.speed_mul:
            acc = self.acceleration
        else:
            acc = 0.

        # Keep safe distance from obstacles(cars, traffic stops...)
        obstacle_pos = w.next_obstacle_position(self)
        obstacle_dist = obstacle_pos - self.pos
        if obstacle_dist < self.safety_distance + self.length * 1.5:
            acc = -self.deceleration

        self.speed += acc * dt
        if self.speed < 0.:
            self.speed = 0.
        self.pos += self.speed * dt

        # update coordinates
        self.xp = self.x
        self.yp = self.y
        self.way.position_car(self)

    @property
    def safety_distance(self):
        t = self.speed / self.deceleration  # Braking time
        return self.speed * t + self.deceleration * t * t

    def on_dead_end(self):
        """Called when leaving a dead end Way. e.g.: to destroy self."""
        pass