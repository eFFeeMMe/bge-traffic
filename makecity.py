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

import bpy

def instances_from_ascii(txt):
    becomes = {' ': 'tile_Grass0',
               '-': 'tile_RoadH',
               '|': 'tile_RoadV',
               '+': 'tile_RoadX',
               '0': 'tile_Building0',
               '1': 'tile_Building1',
               '2': 'tile_Building2',
    }

    cell_w = 2.
    cell_h = 2.
    
    lines = txt.splitlines()
    h = len(lines)
    w = max(len(line) for line in lines)
    
    grid = [[None for y in range(h)] for x in range(w)]

    for y, line in enumerate(lines):
        for x, symbol in enumerate(line):
            obj_x = x * cell_w
            obj_y = - y * cell_h # So that when in default blender game projection, orientation is like text
            if symbol in becomes:
                group_name = becomes[symbol]
                bpy.ops.object.group_instance_add(group=group_name,
                                                  view_align=False,
                                                  location=(obj_x, obj_y, 0.))
                grid[x][y] = o = bpy.context.selected_objects[0]
                bpy.ops.object.game_property_new(type='STRING', name="adj_e")
                bpy.ops.object.game_property_new(type='STRING', name="adj_w")
                bpy.ops.object.game_property_new(type='STRING', name="adj_n")
                bpy.ops.object.game_property_new(type='STRING', name="adj_s")
                o.game.properties['adj_e'].value = ''
                o.game.properties['adj_w'].value = ''
                o.game.properties['adj_n'].value = ''
                o.game.properties['adj_s'].value = ''
    
    # Setting graph links. Sadly, grid[w-1][h-1] won't be linked.
    for x in range(w - 1):
        for y in range(h - 1):
            o = grid[x][y]
            if o:
                a = grid[x+1][y]
                b = grid[x][y+1]
                if a:
                    o.game.properties['adj_e'].value = a.name
                    a.game.properties['adj_w'].value = o.name
                if b:
                    o.game.properties['adj_s'].value = b.name
                    b.game.properties['adj_n'].value = o.name
            

instances_from_ascii("""
11201101201201201101210202101020121
0        |     |     |            0
2        |     |     |            1
1        |     |     +-----+      0
1   1    |     |     |     |      1
0 0   2  | 10  |  0  | 1   |      2
2    1   |  2  | 2   |  2  |      1
0      20|    1| 1   |   0 |      0
0 21 01  | 012 | 0 21|102  |0     2
1--------+-----+-----+-----+------1
0      22|     |     | 12 0       1
2        |     |     |0    21     1
1        |     |     |   1 0      1
1        |     +-----+------------1
1        |            1           0
""")