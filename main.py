#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.util.transforms import ortho

import gui

def main():
    canvas = app.Canvas(size=(512, 512), keys="interactive")
    program = build_program('vertex.glsl', 'fragment.glsl')
    texture = gloo.Texture2D(io.imread('image.png'), interpolation='linear')

    program['texture1'] = texture
    # not supposed to be negative! 0 -> 1, not -1 -> 1
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    # maybe we just use one vbo quad and redraw it over and over with different
    # textures in different locations...

    #program['u_transform'] = ortho(0, 1, 0, 0.5, -1, 1)

    @canvas.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program['a_position'] = np.array([
            (-1.0, -1.0), (+1.0, -1.0), (-1.0, +1.0), (+1.0, +1.0)
        ]).astype(np.float32)

        scale, slip = gui.fit('right', 0.2, 1.0)

        program['u_scale'] = scale
        program['u_slide'] = slip
        program['u_color'] = (0.5, 0.2, 0.8, 1)
        program.draw('triangle_strip')
        #draw_all_vbos(program, bars, colors)

    canvas.show()
    app.run()


def draw_quads(program, slides):
    for s in slides:
        program['u_slide'] = s
        program.draw('triangle_strip')


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
