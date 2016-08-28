#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
import os

import image
import spacing

def main():
    logical_w = 300
    logical_h = 200
    scale = 4
    app.use_app('glfw')
    canvas = Canvas(
        title="Birdies",
        #size=(pixel_w, pixel_h),
        size=(logical_w, logical_h),
        keys="interactive",
        resizable=False,
        px_scale=scale
    )
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    program = build_program('vertex.glsl', 'fragment.glsl')
    blank_screen = np.zeros((logical_w, logical_h, 4), dtype=np.uint8)
    program['tex_color'] = gloo.Texture2D(blank_screen)
    program['a_texcoord'] = np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    ]).astype(np.float32)
    program['a_position'] = np.array([
        (-1.0, +1.0), (-1.0, -1.0),
        (+1.0, +1.0), (+1.0, -1.0)
    ]).astype(np.float32)

    # included in callback scope
    # messy, but less messy than other options using vispy
    build_state = GameState(
        'build',
        spacing.create('build.layout', logical_w, logical_h),
        legs=0,
        beak=0,
        tummy=0,
        tail=0,
        wing=0,
        eye=0,
        flower=0
    )
    state = build_state
    # mvc type architecture
    # keep a state object
    # modify only the state object in event handling
    # use the layout to help render the state
    # I guess each section gets its own state object and layout
    screen = render(state, program)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('triangle_strip')
        #print("drawing screen")

    @canvas.connect
    def on_mouse_press(event):
        (panel, element) = which_element(event, state.layout, scale)
        if element is None: return
        affect(state, panel.handle, element.col, element.row)
        #block = image.color_block(element.w, element.h)
        #rerender(screen, program, [(element, block)])
        render_build_mode(state, program, screen)

    canvas.start()
    app.run()


class GameState(object):
    def __init__(self, handle, layout, **kwargs):
        self.handle = handle
        self.layout = layout
        for (k, v) in kwargs.items():
            self.__dict__[k] = v


def affect(state, handle, col, row):
    global _bird_part_cache
    if not _bird_part_cache:
        _bird_part_cache = _cache_bird_parts()
    n = {k:len(v) for k, v in _bird_part_cache.items()}
    if handle != 'cycle': return
    if row == 0:
        state.legs = (state.legs+1) % n['legs']
    elif row == 1:
        state.beak = (state.beak+1) % n['beak']
    elif row == 2:
        state.tummy = (state.tummy+1) % n['tummy']
    elif row == 3:
        state.tail = (state.tail+1) % n['tail']
    elif row == 4:
        state.wing = (state.wing+1) % n['wing']
    elif row == 5:
        state.eye = (state.eye+1) % n['eye']
    elif row == 6:
        state.flower = (state.flower+1) % n['flower']


def rerender(screen, program, changes):
    for (ele, tex) in changes:
        image.blit(tex, ele, screen)
    program['tex_color'] = gloo.Texture2D(screen)
    return screen


def render(state, program):
    screen = image.render_as_colors(state.layout)
    program['tex_color'] = gloo.Texture2D(screen)
    return screen


_bird_part_cache = {}
def render_build_mode(state, program, screen):
    global _bird_part_cache
    if not _bird_part_cache:
        _bird_part_cache = _cache_bird_parts()
    bird_image = image.composite([
        _bird_part_cache['legs'][state.legs],
        _bird_part_cache['BODY'][0],
        _bird_part_cache['beak'][state.beak],
        _bird_part_cache['tummy'][state.tummy],
        _bird_part_cache['tail'][state.tail],
        _bird_part_cache['wing'][state.wing],
        _bird_part_cache['eye'][state.eye],
        _bird_part_cache['flower'][state.flower],
    ])
    bird_image = np.repeat(np.repeat(bird_image, 2, axis=0), 2, axis=1)
    new_screen = image.blit(bird_image, state.layout['remainder'][0,0], screen)
    program['tex_color'] = gloo.Texture2D(new_screen)

def _cache_bird_parts():
    cache = {
        'legs': [],
        'BODY': [],
        'beak': [],
        'tummy': [],
        'tail': [],
        'wing': [],
        'eye': [],
        'flower': []
    }
    for path in os.listdir("assets/"):
        part_type = path.split('_')[0]
        if part_type not in cache.keys():
            print("Unknown part type:", part_type)
        cache[part_type].append(io.imread("assets/"+path))
    return cache

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


def build_program(v_path, f_path):
    """Load shader programs as strings."""
    with open(v_path, 'r') as v_file:
        v_string = v_file.read()
    with open(f_path, 'r') as f_file:
        f_string = f_file.read()
    return gloo.Program(v_string, f_string)


if __name__ == '__main__':
    main()
