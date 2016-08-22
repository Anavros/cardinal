#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
from vispy.util import transforms

#import interface
import image
import spacing

def main():
    logical_w = 300
    logical_h = 200
    scale = 1
    app.use_app('glfw')
    canvas = app.Canvas(
        title="Birdies",
        #size=(pixel_w, pixel_h),
        size=(logical_w, logical_h),
        keys="interactive",
        resizable=False,
        px_scale=scale
    )

    # should enable transparency?
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    program = build_program('vertex.glsl', 'fragment.glsl')
    gui = spacing.create('builder.layout', logical_w, logical_h)

    build_layout = spacing.create('builder.layout', logical_w, logical_h)
    pause_layout = spacing.create('pause.layout', logical_w, logical_h)

    render = image.render_as_colors(gui)
    render = np.flipud(render) # shader problem

    nine = io.imread('nine.png')
    render = image.blit(nine, gui['item'][0, 0], render)
    render = image.blit(nine, gui['item'][0, 1], render)
    render = image.blit(nine, gui['item'][0, 2], render)

    plus = io.imread('plus.png')
    render = image.blit(plus, gui['plus'][0, 0], render)
    render = image.blit(plus, gui['plus'][0, 1], render)
    render = image.blit(plus, gui['plus'][0, 2], render)

    minus = io.imread('minus.png')
    render = image.blit(minus, gui['minus'][0, 0], render)
    render = image.blit(minus, gui['minus'][0, 1], render)
    render = image.blit(minus, gui['minus'][0, 2], render)

    io.imsave('rendered_texture.png', render)
    texture = gloo.Texture2D(render)
    program['tex_color'] = texture
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    program['a_position'] = np.array([
        (-1.0, -1.0), (-1.0, +1.0), (+1.0, -1.0), (+1.0, +1.0)
        #(-0.5, -0.5), (-0.5, +0.5), (+0.5, -0.5), (+0.5, +0.5)
    ]).astype(np.float32)
    program['u_scale'] = scale

    @canvas.connect
    def on_mouse_press(event):
        (x, y) = event.pos
        (x, y) = (int(x/scale), int(y/scale))
        print("Click: ", end='')
        panel = gui.at(x, y)
        if panel.handle in ['plus', 'minus']:
            nine = image.color_block(32, 32)
            render = image.blit(nine, gui['item'][0, 0], render)
            program['tex_color'] = gloo.Texture2D(render)

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
