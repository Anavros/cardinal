#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io


def main():
    canvas = app.Canvas(size=(512, 512), keys="interactive")
    program = build_program('vertex.glsl', 'fragment.glsl')
    texture = gloo.Texture2D(io.imread('image.png'), interpolation='nearest')

    program['a_position'] = [
        (-1.0, -1.0), (-1.0, +1.0),
        (+1.0, -1.0), (+1.0, +1.0)
    ]


    vertex_data = np.zeros(4, dtype=[('a_position', np.float32, 3),
                                     ('a_texcoord', np.float32, 2)])
    vertex_data['a_position'] = np.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                                          [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0, ]])
    vertex_data['a_texcoord'] = np.array([[0.0, 0.0], [0.0, 1.0],
                                          [1.0, 0.0], [1.0, 1.0]])

    vbo = gloo.VertexBuffer(vertex_data)
    program['texture1'] = texture
    program.bind(vbo)
    # same as:
    # program['a_position'] = ...

    @canvas.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('triangle_strip')

    canvas.show()
    app.run()


def build_program(v_path, f_path):
    # redundant but simple and easy to read
    with open(v_path, 'r') as v_file:
        v_string = v_file.read()
    with open(f_path, 'r') as f_file:
        f_string = f_file.read()

    #print(v_string, f_string)
    #input()

    return gloo.Program(v_string, f_string)


if __name__ == '__main__':
    main()
