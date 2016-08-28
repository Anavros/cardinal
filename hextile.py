#!/usr/bin/env python3

from vispy import gloo, app, io
import numpy as np


def main():
    app.use_app('glfw')
    canvas = app.Canvas(title="Hexes", size=(200, 200), keys="interactive", px_scale=1)
    program = gloo.Program(VERTEX, FRAGMENT)

    program['a_position'] = np.array([
        (-0.5, +0.5), (-0.5, -0.5),
        (+0.5, +0.5), (+0.5, -0.5)
    ]).astype(np.float32)


    vertices = np.array([
        (0, 0),         # center
        (+0.5, 0),      # right point
        (+0.25, +0.5),  # top right corner
        (-0.25, +0.5),  # top left corner
        (-0.5, 0),      # left point
        (-0.25, -0.5),  # bottom left corner
        (+0.25, -0.5),  # bottom right corner
    ]).astype(np.float32)
    indices = np.array([
        0, 1, 2, 3, 4, 5, 6, 1
    ]).astype(np.uint32)

    vertices, indices = gen_vertices(0.2, 10, 10)

    vertex_buffer = gloo.VertexBuffer(vertices)
    element_buffer = gloo.IndexBuffer(indices)
    program['a_position'] = vertex_buffer

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('line_strip', element_buffer)

    canvas.show()
    app.run()


def gen_vertices(size, cols, rows):
    vertices = np.zeros((rows*cols*7, 2), dtype=np.float32)
    indices = np.zeros((rows*cols*8), dtype=np.uint32)
    # make a blank array
    # flat topped so vertical space divides evenly
    # every other col is shifted by 1/2 height, but they stack 1:1
    # or if we just do size
    # figure out how much space each tile takes using cols and rows
    # iterate over cols and rows
    i = 0
    ii = 0
    half = size/2
    quarter = size/4
    for c in range(cols):
        for r in range(rows):
            #x = c*(3*quarter) + half + size if c%2 else 0
            x = c*(3*quarter)

            #y = r*size + half + (half if r%2 else 0)
            y = r*size + (half if c%2 else 0)

            tl = (x-quarter, y+half)
            tr = (x+quarter, y+half)
            bl = (x-quarter, y-half)
            br = (x+quarter, y-half)
            le = (x-half, y)
            re = (x+half, y)
            vertices[i:i+7] = np.array([(x, y), re, tr, tl, le, bl, br])
            indices[ii:ii+8] = np.array([0, 1, 2, 3, 4, 5, 6, 1]) + i
            i += 7
            ii += 8
    print(vertices)
    return vertices, indices

VERTEX = r"""
#version 120

attribute vec2 a_position;

void main(void) {
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""
FRAGMENT = r"""
#version 120

void main(void) {
    gl_FragColor = vec4(0.0, 0.0, 0.5, 1.0);
}
"""

if __name__ == '__main__':
    main()
