
import image
import text

font = text.load_font('images/font.png', 18, 18)

def label(element, string, slate):
    label_tex = text.arrange(font, string)
    slate = image.imperfect_blit(label_tex, element, "center", slate)
    return slate
