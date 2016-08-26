#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl

import image
import spacing

def main():
    logical_w = 300
    logical_h = 200
    scale = 1
    app.use_app('glfw')
    canvas = Canvas(
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

    gui = spacing.create('build.layout', logical_w, logical_h)
    build_layout = spacing.create('build.layout', logical_w, logical_h)
    pause_layout = spacing.create('pause.layout', logical_w, logical_h)
    render = image.render_as_colors(gui)
    render = np.flipud(render) # shader problem
    io.imsave('images/rendered_texture.png', render)

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

    # included in callback scope
    # messy, but less messy than other options using vispy
    layout = build_layout

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('triangle_strip')
        print("drawing screen")

    @canvas.connect
    def on_mouse_press(event):
        (panel, element) = which_element(event, layout, scale)
        if element is None: return
        block = image.color_block(element.w, element.h)
        local_render = render # get around scoping problem
        texture = image.blit(block, element, local_render)
        texture = gloo.Texture2D(render)
        program['tex_color'] = texture
        canvas.update()

    canvas.start()
    app.run()


# automatically updates
# might do something fancy later, but solid 60fps for now
class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.timer = app.Timer(connect=self.on_timer)

    def on_timer(self, event):
        self.update()

    def start(self):
        self.show()
        self.timer.start()


def which_element(event, layout, scale):
    (x, y) = event.pos
    (x, y) = int(x/scale), int(y/scale)
    panel, element = layout.at(x, y)
    return (panel, element)


class GameState(object):
    def __init__(self):
        self.layout = ""


def build_program(v_path, f_path):
    """Load shader programs as strings."""
    with open(v_path, 'r') as v_file:
        v_string = v_file.read()
    with open(f_path, 'r') as f_file:
        f_string = f_file.read()
    return gloo.Program(v_string, f_string)


if __name__ == '__main__':
    main()
