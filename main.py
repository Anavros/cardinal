#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io

import gui

def main():
    canvas = app.Canvas(
        title="Birdies",
        size=(800, 600),
        keys="interactive",
        resizable=False
    )
    program = build_program('vertex.glsl', 'fragment.glsl')

#    fit_test = [
#        ('top', 1, 0.8, (0.5, 0.2, 0.8, 1)),
#        ('bottom', 1, 0.2, (0.8, 0.6, 0.2, 1)),
#        ('left', 0.1, 1, (0.2, 0.3, 0.5, 1))
#    ]

    texture = gloo.Texture2D(
        gui.stretch_nine('image.png', 800, 600), interpolation='nearest')

    program['texture1'] = texture
    # not supposed to be negative! 0 -> 1, not -1 -> 1
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    # maybe we just use one vbo quad and redraw it over and over with different
    # textures in different locations...

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program['a_position'] = np.array([
            (-1.0, -1.0), (+1.0, -1.0), (-1.0, +1.0), (+1.0, +1.0)
        ]).astype(np.float32)

        program.draw('triangle_strip')

#        for (side, x, y, color) in fit_test:
#            scale, slide = gui.fit(side, x, y)
#            program['u_scale'] = scale
#            program['u_slide'] = slide
#            program['u_color'] = color
#            program.draw('triangle_strip')

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
