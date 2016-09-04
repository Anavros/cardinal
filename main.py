#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
import os

import image
import spacing
import internal
from birdie import Birdie

# new libraries
import rocket
from aux import load_shaders, Storage, Cycler
import manipulate

W, H, S = 300, 200, 2
TITLE = "Birdies"

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

# Module-Level
program = load_shaders('vertex.glsl', 'fragment.glsl')

blank_screen = np.zeros((W, H, 4), dtype=np.uint8)
program['tex_color'] = gloo.Texture2D(blank_screen)

bird_parts, part_counts = _cache_bird_parts()
game = Storage(
    needs_redraw = False,
    current_state = None,
    slate = None,
    parts = bird_parts,
    n_parts = part_counts,
    selected_bird = (0, 0),
)
game.build = Storage(
    handle = 'build',
    layout = spacing.create('build.layout', W, H),
    parts = Cycler(bird_parts),
)

game.pen = Storage(
    handle='pen',
    layout=spacing.create('pen.layout', W, H),
    birds=[
        [Birdie(), Birdie()],
        [Birdie(), Birdie()],
    ],
)
game.pause = Storage(
    handle='pause',
    layout=spacing.create('pause.layout', W, H)
)
game.demo = Storage(
    handle='demo',
    layout=spacing.create('map.layout', W, H)
)
game.state = game.pause
game.needs_redraw=True
game.slate = internal.render(
    game, image.render_as_colors(game.state.layout), program, bird_parts)


def main():
    rocket.prep(size=(W, H), scale=S, title=TITLE)
    rocket.launch()


@rocket.attach
def draw():
    verts, coord, index = manipulate.coord_stub()
    program['a_position'] = gloo.VertexBuffer(verts)
    program['a_texcoord'] = gloo.VertexBuffer(coord)
    program.draw('triangle_strip', gloo.IndexBuffer(index))


@rocket.attach
def left_click(point):
    (x, y) = int(point[0]/S), int(point[1]/S)
    print(x, y)
    tup = game.state.layout.at(x, y)
    if tup is None:
        print("Nothing there!")
        return
    (panel, element) = tup
    if element is None:
        print("No element there.")
        return

    state = game.state
    col = element.col
    row = element.row

    # Bird Builder
    if state.handle == 'build':
        if panel.handle == 'cycle':
            mappings = {
                0: 'legs',
                1: 'beak',
                2: 'tummy',
                3: 'tail',
                4: 'wing',
                5: 'eye',
                6: 'flower',
            }
            state.parts.cycle(mappings[row])
        elif panel.handle == 'menu':
            game.state = game.pause

    # Birdie Pen
    elif state.handle == 'pen':
        if panel.handle == 'menu':
            game.state = game.pause
            game.needs_redraw = True
        elif panel.handle == 'selection':
            bird = state.birds[col][row]
            print("selecting bird", col, row)
            game.selected_bird = (col, row)
            game.state = game.build
            game.needs_redraw = True

    # Tile Rendering Demo
    elif state.handle == 'demo':
        if panel.handle == 'menu':
            game.state = game.pause
            game.needs_redraw = True

    # Pause Menu
    elif state.handle == 'pause':
        if panel.handle == 'menu':
            if row == 0:
                game.state = game.build
                game.needs_redraw = True
            elif row == 1:
                game.state = game.pen
                game.needs_redraw = True
            elif row == 2:
                game.state = game.demo
                game.needs_redraw = True
            elif row == 3:
                raise SystemExit
    game.slate = internal.render(game, game.slate, program, bird_parts)


if __name__ == '__main__':
    main()
