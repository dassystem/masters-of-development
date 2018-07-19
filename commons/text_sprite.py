import pygame

class TextSprite(pygame.sprite.Sprite):
    render_cache = {}

    def __init__(self, initial_pos, text, font, font_color):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(TextSprite, self).__init__()

        self._initial_pos = initial_pos
        self._text = text
        self._font = font
        self._font_color = font_color

        self.image = self.__render(self._text, self._font, self._font_color)
        self.rect = self.image.get_rect(topleft = self._initial_pos)

        self._dirty = False

    def __render(self, text, font, font_color):
        key = (text, font, font_color.normalize())

        if key in TextSprite.render_cache:
            surface = TextSprite.render_cache[key]
        else:
            surface = font.render(text, True, font_color)
            TextSprite.render_cache[key] = surface

        return surface

    def update(self, new_text):
        self._dirty = self._text != new_text

        if self._dirty:
            self._text = new_text

            self.image = self.__render(self._text, self._font, self._font_color)
            self.rect = self.image.get_rect(topleft = self._initial_pos)

            self._dirty = False
