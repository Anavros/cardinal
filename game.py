
import numpy as np
from vispy import gloo
import image


def click(state, panel_name, col, row):
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
            print("Do the menu thing!")
    elif state.handle == 'pen':
        if panel_name == 'menu':
            print("Do the menu thing!")

def render(state, slate, program, texture_cache):
    if state.handle == 'build':
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
        bird_image = np.repeat(np.repeat(bird_image, 2, axis=0), 2, axis=1)
        new_slate = image.blit(bird_image, state.layout['remainder'][0,0], slate)
    elif state.handle == 'pen':
        new_slate = slate

    program['tex_color'] = gloo.Texture2D(new_slate)
    return new_slate
