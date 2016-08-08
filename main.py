#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io


def main():
    canvas = app.Canvas(size=(512, 512), keys="interactive")
    program = build_program('vertex.glsl', 'fragment.glsl')
    texture = gloo.Texture2D(
        io.imread('image.png'), interpolation='linear')

    program['texture1'] = texture
    program['a_position'] = np.array([
        (-1.0, -1.0), (+1.0, -1.0),
        (-1.0, +1.0), (+1.0, +1.0)
    ]).astype(np.float32)

    top = np.array([
        (-1.0, -0.7), (+1.0, -0.7),
        (-1.0, +1.0), (+1.0, +1.0)
    ]).astype(np.float32)

    bottom = np.array([
        (-1.0, -1.0), (+1.0, -1.0),
        (-1.0, +0.3), (+1.0, +0.3)
    ]).astype(np.float32)

    # not supposed to be negative! 0 -> 1, not -1 -> 1
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    # maybe we just use one vbo quad and redraw it over and over with different
    # textures in different locations...

    @canvas.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program['u_color'] = (1, 0, 0, 1)
        program['a_position'] = top
        program.draw('triangle_strip')
        program['u_color'] = (0, 0, 1, 1)
        program['a_position'] = bottom
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
