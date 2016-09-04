
import numpy as np
from vispy import gloo

import image
import splitnine
import text
import effects
import birdie


def render(game, slate, program, texture_cache):
    state = game.state
    if game.needs_redraw:
        slate = image.render_as_colors(state.layout)
        game.needs_redraw = False

    # Bird Builder
    if state.handle == 'build':
        #print("rendering build state")
        bird_image = image.composite([
            state.parts.get('legs'),
            state.parts.get('BODY'),
            state.parts.get('beak'),
            state.parts.get('tummy'),
            state.parts.get('tail'),
            state.parts.get('wing'),
            state.parts.get('eye'),
            state.parts.get('flower'),
        ])
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
                slate = image.blit(birdie.build_a_bird(state.birds[c][r], game.parts),
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
    return slate
