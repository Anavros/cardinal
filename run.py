#!/usr/bin/env python3.4
# coding=utf-8

import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
import os

import image
import spacing
#import internal
import effects
import birdie

# new libraries
import rocket
from rocket.aux import load_shaders, Storage, Cycler, LookupAtlas
import manipulate

W, H, S = 300, 200, 2
TITLE = "Birdies"

def _part_atlas():
    # access by nickname or index
    #atlas.get("legs", 0)
    # keep a data structure for each quad and texcoord for gui panels

    atlas = LookupAtlas(64, 8)
    for path in os.listdir("assets/"):
        part = path.split('_')[0]
        if part not in ['legs','BODY','beak','tummy','tail','wing','eye','flower']:
            print("Unknown part type:", part)
        atlas.insert(io.imread("assets/"+path), part)
    io.imsave("atlas.png", atlas.texture)
    return atlas

# how to render birds with compositing?
# keep all pieces in texture atlas
# and add them together directly in the fragment shader?
# maybe we should work on something else first

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
program = load_shaders('shaders/vertex.glsl', 'shaders/fragment.glsl')

blank_screen = np.zeros((W, H, 4), dtype=np.uint8)
program['tex_color'] = gloo.Texture2D(blank_screen)

bird_parts, part_counts = _cache_bird_parts()
game = Storage(
    needs_redraw = False,
    current_state = None,
    slate = None,
    #parts = bird_parts,
    #n_parts = part_counts,
    selected_bird = (0, 0),
)
game.build = Storage(
    handle = 'build',
    layout = spacing.create('layouts/build.layout', W, H),
    parts = Cycler(bird_parts),
)

game.pen = Storage(
    handle='pen',
    layout=spacing.create('layouts/pen.layout', W, H),
    birds=[
        [Cycler(bird_parts), Cycler(bird_parts)],
        [Cycler(bird_parts), Cycler(bird_parts)],
    ],
)
game.pause = Storage(
    handle='pause',
    layout=spacing.create('layouts/pause.layout', W, H)
)
game.demo = Storage(
    handle='demo',
    layout=spacing.create('layouts/map.layout', W, H)
)
game.state = game.pause
game.needs_redraw=True
#game.slate = internal.render(
    #game, image.render_as_colors(game.state.layout), program, bird_parts)
game.slate = image.render_as_colors(game.state.layout)


def main():
    rocket.prep(size=(W, H), scale=S, title=TITLE)
    rocket.launch()


def mock_draw():
    ui = game.state.ui
    for (verts, coord, index) in ui.renderables():
        program['a_vert'] = verts
        program['a_cord'] = coord
        program.draw('triangle_strip', index)


renderables = image.gpu_render_as_colors(game.state.layout)
@rocket.attach
def draw():
    global renderables
    verts, color, index = renderables[0]
    #for verts, color, index in renderables:
    program['a_position'] = gloo.VertexBuffer(verts)
    #program['a_poscolor'] = gloo.VertexBuffer(color)
    program['a_poscolor'] = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
    program.draw('triangle_strip', gloo.IndexBuffer(index))

    return # XXX

    state = game.state
    slate = game.slate
    if game.needs_redraw:
        slate = image.render_as_colors(state.layout)
        game.needs_redraw = False

    # Bird Builder
    if state.handle == 'build':
        #print("rendering build state")
        bird_image = birdie.build_a_bird(state.parts)
        # backgrounds
        slate = image.fill('images/button.png', state.layout['remainder'], slate, 2)
        slate = image.fill('images/nine.png', state.layout['menu'][0,0], slate, 12)
        slate = image.fill('images/nine.png', state.layout['cycle'], slate, 12)
        # buttons
        slate = image.fill_all('images/button.png', state.layout['cycle'], slate, 2)
        # labels
        slate = effects.label(state.layout['menu'], "Menu", slate)
        # bird image
        bird_image = np.repeat(np.repeat(bird_image, 2, axis=0), 2, axis=1)
        slate = image.blit(bird_image, state.layout['remainder'][0,0], slate)

    # Birdie Pen
    elif state.handle == 'pen':
        #print("rendering pen state")
        slate = image.fill('images/nine.png', state.layout['menu'][0,0], slate, 12)
        slate = image.fill_all('images/dirt.png', state.layout['selection'], slate, 2)
        slate = effects.label(state.layout['menu'], "Menu", slate)

        for r in range(2):
            for c in range(2):
                slate = image.blit(birdie.build_a_bird(state.birds[c][r]),
                    state.layout['selection'][c,r], slate)

    elif state.handle == 'demo':
        #print("rendering map state")
        slate = image.fill('images/nine.png', state.layout, slate, 12)
        slate = image.fill('images/nine.png', state.layout['menu'][0,0], slate, 12)
        slate = effects.label(state.layout, 'lol', slate)
        slate = effects.label(state.layout['menu'], "Menu", slate)

    # Pause Menu
    elif state.handle == 'pause':
        #print("rendering pause state")
        slate = image.fill('images/button.png', state.layout, slate, 2)
        slate = image.fill_all('images/nine.png', state.layout['menu'], slate, 12)
        menu = state.layout['menu']
        slate = effects.label(menu[0, 0], "Build Mode", slate)
        slate = effects.label(menu[0, 1], "Birdie Pen", slate)
        slate = effects.label(menu[0, 2], "Hxmap Demo", slate)
        slate = effects.label(menu[0, 3], "Quit", slate)
    else:
        raise ValueError("Trying to render unknown state: {}".format(state.handle))

    program['tex_color'] = gloo.Texture2D(slate)
    verts, coord, index = manipulate.coord_stub()
    program['a_position'] = gloo.VertexBuffer(verts)
    program['a_texcoord'] = gloo.VertexBuffer(coord)
    program.draw('triangle_strip', gloo.IndexBuffer(index))


@rocket.attach
def left_click(point):
    (x, y) = int(point[0]/S), int(point[1]/S)
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


if __name__ == '__main__':
    main()
