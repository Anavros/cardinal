#!/usr/bin/env python3.4

from vispy import gloo
import numpy as np

import aux
import rocket
import spacing

W, H, S = 500, 500, 1

gui_prog = aux.load_shaders('shaders/ui.v.glsl', 'shaders/ui.f.glsl')
#map_prog = aux.load_shaders('shaders/v_world.glsl', 'shaders/f_world.glsl')

game = aux.Storage()
game.build = aux.Storage(layout=spacing.create('layouts/build.layout', W, H))
game.pause = aux.Storage(layout=spacing.create('layouts/pause.layout', W, H))
game.demo = aux.Storage(layout=spacing.create('layouts/demo.layout', W, H))
game.pen = aux.Storage(layout=spacing.create('layouts/pen.layout', W, H))
game.state = game.build
game.state_name = 'build'


def main():
    rocket.prep()
    gui_prog['a_position'] = gloo.VertexBuffer(np.array([
        (-1.0, +1.0), (-1.0, -1.0),
        (+1.0, +1.0), (+1.0, -1.0)
    )], dtype=np.float32)
    gui_prog['a_texcoord'] = gloo.VertexBuffer(np.array([
        (0, 0), (0, 1),
        (1, 0), (1, 1)
    )], dtype=np.float32)
    rocket.launch()


@rocket.call
def draw():
    gui_prog.draw('triangles')


@rocket.call
def left_click(point):
    panel, element = game.state.layout.at(point)
    if game.state_name == 'build':
        if panel.handle == 'cycle':
            if element.row == 0:
                pass
        elif panel.handle == 'menu':
            game.state = game.pause
            return
    elif game.state_name == 'pause':
        if panel.handle == 'menu':
            if row == 0:  # Build Mode
                game.state = game.build
            elif row == 1:  # Birdie Pen
                game.state = game.pen
            elif row == 2:  # Hexmap Demo
                game.state = game.demo
            elif row == 3:  # Quit
                raise SystemExit
    elif game.state_name == 'pen':
        pass
    elif game.state_name == 'demo':
        pass


if __name__ == '__main__':
    main()
