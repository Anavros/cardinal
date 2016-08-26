

import spacing
import backend


LOGICAL_W = 300
LOGICAL_H = 200
SCALE = 2


def main():
    canvas, program = backend.init("Birdies", LOGICAL_W, LOGICAL_H, SCALE)
    build_layout = spacing.create('build.layout', LOGICAL_W, LOGICAL_H)
    pause_layout = spacing.create('pause.layout', LOGICAL_W, LOGICAL_H)

    # Set a layout to run first and state transitions between.
    start(build_layout)
    # Start in build layout
    # When certain button is pressed, switch to pause layout
    # Set the right textures to fit into the spaces.
    textures = get_textures()
    render(texture, build_layout['space'])
    # Set up trigger events for when spaces get clicked on.
    when_clicked(build_layout['space'][0, 0], func)
    # Run a loop.


"""
declaritave, deferred syntax?
def game():
    bird_color = 0
    bird_feather = 0
    bird_shape = 0

    when clicked build_layout['plus'][0, 0]: bird_color += 1
    when clicked build_layout['plus'][0, 1]: bird_feather += 1
    when clicked build_layout['plus'][0, 2]: bird_shape += 1
    when clicked build_layout['minus'][0, 0]: bird_color -= 1
    when clicked build_layout['minus'][0, 1]: bird_feather -= 1
    when clicked build_layout['minus'][0, 2]: bird_shape -= 1

    when drawn build_layout['rest'][0, 0] = render_bird(...)
    when drawn build_layout['item'][0, 1] = get_tex('color', bird_color)
    when drawn build_layout['item'][0, 2] = get_tex('feather', bird_feather)
    when drawn build_layout['item'][0, 3] = get_tex('shape', bird_shape)

    when drawn build_layout['item'].background = color(x)
"""
or more of a toolkit-style structured syntax
maybe with deferred rendering

states/build.py
def update(layout, state, events):
    for event in events:
        panel, element = layout.at(event.x, event.y)
        if panel.handle == 'plus':
            if element.row == 0:
                state.bird_color += 1
            elif element.row == 1:
                state.bird_feather += 1
            elif element.row == 2:
                state.bird_shape += 1
        elif panel.handle == 'minus':
            if element.row == 0:
                state.bird_color -= 1
            elif element.row == 1:
                state.bird_feather -= 1
            elif element.row == 2:
                state.bird_shape -= 1

def render(state, layout):
    defer_draw(get_tex(state.bird_color), layout['item'][0][0])
    defer_draw(get_tex(state.bird_feather), layout['item'][0][1])
    defer_draw(get_tex(state.bird_shape), layout['item'][0][2])
    defer_draw(layout.shortcut('item background'), rand_color())
"""
