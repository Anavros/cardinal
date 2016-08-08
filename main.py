#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo


def main():
    canvas = app.Canvas(keys="interactive")
    program = build_program('vertex.glsl', 'fragment.glsl')

    program['a_position'] = np.c_[
        np.linspace(-1.0, +1.0, 1000),
        np.random.uniform(-0.5, +0.5, 1000)
    ].astype(np.float32)

    program['a_color'] = (0, 0, 1, 1) 

    @canvas.connect
    def on_resize(event):
        gloo.set_viewport(0, 0, *event.size)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('line_strip')

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
