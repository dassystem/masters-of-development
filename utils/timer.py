import pygame

COUNTDOWN_EVENT = pygame.USEREVENT + 2
ELAPSED_EVENT = pygame.USEREVENT + 3

class Timer(object):
    def __init__(self, name, initial_seconds):
        self._name = name
        self._initial_seconds = initial_seconds
        self._countdown_event = COUNTDOWN_EVENT
        self._started = False
        self._seconds_left = 0

        self._event_handler = TimerCountdownEventHandler(self)

    def get_event_handler(self):
        return self._event_handler

    def get_seconds_left(self):
        return self._seconds_left

    def is_started(self):
        return self._started

    def start(self):
        if not self._started:
            self._started = True
            self._seconds_left = self._initial_seconds

    def stop(self):
        self._started = False

    def countdown(self):
        if not self._started:
            return

        self._seconds_left -= 1

        if self._seconds_left <= 0:
            self.stop()
            pygame.event.post(pygame.event.Event(ELAPSED_EVENT, {"timer": self}))

class SpriteTimer(pygame.sprite.Sprite, Timer):
    """A sprite representing a timer."""

    def __init__(self, name, initial_seconds, pos_dict, sounds):
        Timer.__init__(self, name, initial_seconds)

        # IMPORTANT: call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self._pos_dict = pos_dict
        self._sounds = sounds

        self._dirty = True

    def update(self):
        """Updates the timer in order to be drawn to a surface later on.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self._dirty:
            return

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = self._update_image()

        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        # ** unpacks the dictionary to keyword arguments
        self.rect = self.image.get_rect(**self._pos_dict)

        self._dirty = False

    def _update_image(self):
        pass

    def start(self):
        Timer.start(self)
        self._dirty = True

        if self._seconds_left <= 10:
            self._sounds[str(self._seconds_left)].play()

    def countdown(self):
        if not self._started:
            return

        self._dirty = True
        Timer.countdown(self)

        if self._seconds_left <= 10 and self._seconds_left > 0:
            self._sounds[str(self._seconds_left)].play()

class FontSpriteTimer(SpriteTimer):
    """A sprite representing a timer."""

    def __init__(self, name, initial_seconds, pos_dict, font, font_color_1, font_color_2, sounds, change_font_color_at = 0, format_string = "{0:d}"):
        super(FontSpriteTimer, self).__init__(name, initial_seconds, pos_dict, sounds)

        self.__font = font
        self.__font_color_1 = font_color_1
        self.__font_color_2 = font_color_2
        self.__change_font_color_at = change_font_color_at
        self.__format_string = format_string

    def _update_image(self):
        color = self.__font_color_1

        if self.__change_font_color_at > 0 and self._seconds_left <= self.__change_font_color_at:
            color = self.__font_color_2

        return self.__font.render(self.__format_string.format(self._seconds_left), True, color)

class ImageSpriteTimer(SpriteTimer):
    """A sprite representing a timer."""

    def __init__(self, name, initial_seconds, pos_dict, sounds, images):
        super(ImageSpriteTimer, self).__init__(name, initial_seconds, pos_dict, sounds)

        self.__images = images

    def countdown(self):
        if not self._started:
            return

        self._dirty = True
        self._seconds_left -= 1

        if self._seconds_left <= 10 and self._seconds_left > 0:
            self._sounds[str(self._seconds_left)].play()

        if self._seconds_left <= -1:
            self.stop()
            pygame.event.post(pygame.event.Event(ELAPSED_EVENT, {"timer": self}))

    def _update_image(self):
        key = "countdown_{0:d}".format(self._seconds_left)
        return self.__images[key]

class TimerCountdownEventHandler(object):
    def __init__(self, timer):
        self.__timer = timer

    def can_handle(self, event):
        if event.type != COUNTDOWN_EVENT:
            return False

        return self.__timer.is_started()

    def handle_event(self, event):
        self.__timer.countdown()
