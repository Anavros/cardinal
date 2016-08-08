

def on_click(event):
    # when clicked, detect where the click occurred and reference against a table
    # of elements. if the click matches an element, signal that element.
    # so we'll need a table of elements and their locations.
    # if we have a table, we could use that for rendering too.
    # plus then you could edit it externally in a text file or something.
    pass


def fit(anchor, x, y):
    """Calculates stretch and slip to make a quad fill a certain amount of space."""

    # fit(left, 1, 0.5): scale.x = 1, scale.y=0.5, slip.x=0, slip.y=0
    scale = (x, y)
    if anchor == 'top':
        slip = (0, 1-y)
    elif anchor == 'bottom':
        slip = (0, -1+y)
    elif anchor == 'left':
        slip = (-1+x, 0)
    elif anchor == 'right':
        slip = (1-x, 0)
    else:
        raise ValueError
    
    return scale, slip

r"""
Example:
div bird_display top 90%
div color_select left 10%
div shape_select bottom 20%
"""
