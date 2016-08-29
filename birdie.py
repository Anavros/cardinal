
import image


class Birdie(object):
    def __init__(self):
        self.parts = {
            "legs": 0,
            "beak": 0,
            "tummy": 0,
            "tail": 0,
            "wing": 0,
            "eye": 0,
            "flower": 0
        }


def build_a_bird(birdie, parts):
    bird_image = image.composite([
        parts['legs'][birdie.parts['legs']],
        parts['BODY'][0],
        parts['beak'][birdie.parts['beak']],
        parts['tummy'][birdie.parts['tummy']],
        parts['tail'][birdie.parts['tail']],
        parts['wing'][birdie.parts['wing']],
        parts['eye'][birdie.parts['eye']],
        parts['flower'][birdie.parts['flower']],
    ])
    return bird_image
