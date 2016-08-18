#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
from vispy.util import transforms

import interface

def main():
    logical_w = 300
    logical_h = 200
    scale = 2
    pixel_w = logical_w*scale
    pixel_h = logical_h*scale
    app.use_app('glfw')
    canvas = app.Canvas(
        title="Birdies",
        size=(pixel_w, pixel_h),
        keys="interactive",
        resizable=False
    )

    # should enable transparency?
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    program = build_program('vertex.glsl', 'fragment.glsl')
    blank = np.full((logical_h, logical_w, 4), 255, dtype=np.uint8)

    elements = interface.build_gui('config.gui', logical_w, logical_h)
    render = np.flipud(interface.xrender(elements, blank))
    # v-- this looks fine, the transparency and flipping problems are both gl
    io.imsave('rendered_texture.png', render)
    texture = gloo.Texture2D(render, format='rgba')
    #texture = gloo.Texture2D(io.imread('test.png'))

    program['tex_color'] = texture
    # not supposed to be negative! 0 -> 1, not -1 -> 1
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    program['a_position'] = np.array([
        (-1.0, -1.0), (-1.0, +1.0), (+1.0, -1.0), (+1.0, +1.0)
        #(-0.5, -0.5), (-0.5, +0.5), (+0.5, -0.5), (+0.5, +0.5)
    ]).astype(np.float32)
    # maybe we just use one vbo quad and redraw it over and over with different
    # textures in different locations...
    #program['u_ortho'] = transforms.ortho(-1, 1, -1, 1, -1, 1) # not necessary?
    program['u_scale'] = scale

    @canvas.connect
    def on_mouse_press(event):
        (x, y) = event.pos
        (x, y) = (int(x/scale), int(y/scale))
        print("Click: ", end='')
        handle = interface.locate(x, y, elements)
        if handle:
            print("Element '{}' has been triggered!".format(handle))
        else:
            print()

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
