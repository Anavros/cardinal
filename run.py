#!/usr/bin/env python3.4

from vispy import gloo, io
import numpy as np

import aux
import rocket
import spacing
import manipulate

W, H, S = 100, 100, 4

gui_prog = aux.load_shaders('shaders/ui.v.glsl', 'shaders/ui.f.glsl')
#map_prog = aux.load_shaders('shaders/v_world.glsl', 'shaders/f_world.glsl')

#game = aux.Storage()
#game.build = aux.Storage(layout=spacing.create('layouts/build.layout', W, H))
#game.pause = aux.Storage(layout=spacing.create('layouts/pause.layout', W, H))
#game.demo = aux.Storage(layout=spacing.create('layouts/demo.layout', W, H))
#game.pen = aux.Storage(layout=spacing.create('layouts/pen.layout', W, H))
#game.state = game.build
#game.state_name = 'build'


def main():
    rocket.prep(size=(W, H), scale=S)
    rocket.launch()


@rocket.attach
def draw():
    # Draw the world first.
    pass
    # Then the gui.
    verts, coord, index = manipulate.gui_nine_split(100, 32, 12)
    gui_prog['a_ver'] = gloo.VertexBuffer(verts)
    gui_prog['a_tex'] = gloo.VertexBuffer(coord)
    gui_prog['t_gui'] = io.imread('images/nine.png')
    gui_prog.draw('triangle_strip', gloo.IndexBuffer(index))

    for (verts, coord, index) in ui.coordinate():
        gui_prog['a_ver'] = gloo.VertexBuffer(verts)
        gui_prog['a_tex'] = gloo.VertexBuffer(coord)
        gui_prog['t_gui'] = io.imread('images/nine.png')
        gui_prog.draw('triangle_strip', gloo.IndexBuffer(index))

    clicked = ui.at(x, y)
    if clicked == 'enter_build_mode':
        pass

    if clicked.panel == 'menu':
        if clicked.element == 'pause':
            game.state = game.pause

@rocket.call
def left_click(point):
    element = game.state.ui.at(point)
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
