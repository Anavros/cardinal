
import image


def build_a_bird(bird):
    return image.composite([
        bird.get('legs'),
        bird.get('BODY'),
        bird.get('beak'),
        bird.get('tummy'),
        bird.get('tail'),
        bird.get('wing'),
        bird.get('eye'),
        bird.get('flower'),
    ])
