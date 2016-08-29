
import numpy as np
from vispy import gloo

import image
import splitnine
import text
import effects
import birdie


def click(game, panel_name, col, row):
    state = game.get_state()
    
    # Bird Builder
    if state.handle == 'build':
        if panel_name == 'cycle':
            if row == 0:
                state.legs = (state.legs+1) % state.n['legs']
            elif row == 1:
                state.beak = (state.beak+1) % state.n['beak']
            elif row == 2:
                state.tummy = (state.tummy+1) % state.n['tummy']
            elif row == 3:
                state.tail = (state.tail+1) % state.n['tail']
            elif row == 4:
                state.wing = (state.wing+1) % state.n['wing']
            elif row == 5:
                state.eye = (state.eye+1) % state.n['eye']
            elif row == 6:
                state.flower = (state.flower+1) % state.n['flower']
        elif panel_name == 'menu':
            game.use("pause")

    # Birdie Pen
    elif state.handle == 'pen':
        if panel_name == 'menu':
            game.use("pause")
        elif panel_name == 'selection':
            bird = state.birds[col][row]
            print("selecting bird", col, row)
            game.selected_bird = (col, row)
            game.use("build")
    
    # Tile Rendering Demo
    elif state.handle == 'map':
        if panel_name == 'menu':
            game.use("pause")

    # Pause Menu
    elif state.handle == 'pause':
        if panel_name == 'menu':
            if row == 0:
                game.use("build")
            elif row == 1:
                game.use("pen")
            elif row == 2:
                game.use("map")
            elif row == 3:
                raise SystemExit


def render(game, slate, program, texture_cache):
    state = game.get_state()
    if game.needs_redraw:
        slate = image.render_as_colors(state.layout)
        game.needs_redraw = False

    # Bird Builder
    if state.handle == 'build':
        #print("rendering build state")
        bird_image = image.composite([
            texture_cache['legs'][state.legs],
            texture_cache['BODY'][0],
            texture_cache['beak'][state.beak],
            texture_cache['tummy'][state.tummy],
            texture_cache['tail'][state.tail],
            texture_cache['wing'][state.wing],
            texture_cache['eye'][state.eye],
            texture_cache['flower'][state.flower],
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

    elif state.handle == 'map':
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
