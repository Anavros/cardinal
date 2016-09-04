#!/usr/bin/env python3


import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl
import os

import image
import spacing
import internal
from objects import Game
from birdie import Birdie

# new libraries
import rocket
from aux import load_shaders, Storage

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
program['a_texcoord'] = np.array([
    (0, 0), (0, 1),
    (1, 0), (1, 1)
]).astype(np.float32)
program['a_position'] = np.array([
    (-1.0, +1.0), (-1.0, -1.0),
    (+1.0, +1.0), (+1.0, -1.0)
]).astype(np.float32)

blank_screen = np.zeros((W, H, 4), dtype=np.uint8)
program['tex_color'] = gloo.Texture2D(blank_screen)

bird_parts, part_counts = _cache_bird_parts()
game = Game(
    parts = bird_parts,
    n_parts = part_counts,
    selected_bird = (0, 0),
)
game.add_state('build', Storage(
    handle='build',
    layout=spacing.create('build.layout', W, H),
    n=part_counts,
    legs=0,
    beak=0,
    tummy=0,
    tail=0,
    wing=0,
    eye=0,
    flower=0,
))

game.add_state('pen', Storage(
    handle='pen',
    layout=spacing.create('pen.layout', W, H),
    birds=[
        [Birdie(), Birdie()],
        [Birdie(), Birdie()],
    ],
))
game.add_state('pause', Storage(
    handle='pause',
    layout=spacing.create('pause.layout', W, H)
))
game.add_state('map', Storage(
    handle='map',
    layout=spacing.create('map.layout', W, H)
))
game.use('pause')
game.slate = internal.render(
    game, image.render_as_colors(game.get_state().layout), program, bird_parts)


def main():
    rocket.prep(size=(W, H), scale=S, title=TITLE)
    rocket.launch()


@rocket.attach
def draw():
    program.draw('triangle_strip')


@rocket.attach
def left_click(point):
    state = game.get_state()
    (x, y) = point
    (x, y) = int(x/S), int(y/S)
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


if __name__ == '__main__':
    main()
