#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
import os

import image
import spacing
import internal

def main():
    logical_w = 300
    logical_h = 200
    scale = 2
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
    bird_parts, part_counts = _cache_bird_parts()
    game = Game()
    game.add_state('build', GameState(
        'build',
        spacing.create('build.layout', logical_w, logical_h),
        n=part_counts,
        legs=0,
        beak=0,
        tummy=0,
        tail=0,
        wing=0,
        eye=0,
        flower=0
    ))
    game.add_state('pen', GameState(
        'pen',
        spacing.create('pen.layout', logical_w, logical_h),
        birds=0
    ))
    game.add_state('pause', GameState(
        'pause',
        spacing.create('pause.layout', logical_w, logical_h)
    ))
    game.add_state('map', GameState(
        'map',
        spacing.create('map.layout', logical_w, logical_h)
    ))
    game.use('pause')
    game.slate = internal.render(
        game, image.render_as_colors(game.get_state().layout), program, bird_parts)

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        program.draw('triangle_strip')

    @canvas.connect
    def on_mouse_press(event):
        state = game.get_state()
        print("clicking in {} state".format(state.handle))
        (x, y) = event.pos
        (x, y) = int(x/scale), int(y/scale)
        tup = state.layout.at(x, y)
        if tup is None:
            print("Nothing there!")
            return
        (panel, element) = tup
        if element is None:
            print("No element there.")
            return
        internal.click(game, panel.handle, element.col, element.row)
        game.slate = internal.render(game, game.slate, program, bird_parts)

    canvas.start()
    app.run()


class GameState(object):
    def __init__(self, handle, layout, **kwargs):
        self.handle = handle
        self.layout = layout
        for (k, v) in kwargs.items():
            self.__dict__[k] = v


class Game(object):
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.needs_redraw = False
        self.slate = None

    def add_state(self, handle, state):
        self.states[handle] = state

    def use(self, handle):
        self.current_state = self.states[handle]
        self.needs_redraw = True
        print("entering {} state".format(handle))

    def get_state(self):
        return self.current_state


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
    ns = {k:len(v) for k, v in cache.items()}
    return cache, ns

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


def build_program(v_path, f_path):
    """Load shader programs as strings."""
    with open(v_path, 'r') as v_file:
        v_string = v_file.read()
    with open(f_path, 'r') as f_file:
        f_string = f_file.read()
    return gloo.Program(v_string, f_string)


if __name__ == '__main__':
    main()
