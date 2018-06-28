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
    
    def __init__(self, name, initial_seconds, pos_dict, font, font_color, background_color = None, blink_at = 0, format_string = "{0:d}"):
        Timer.__init__(self, name, initial_seconds)
        
        # IMPORTANT: call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        
        self.__pos_dict = pos_dict
        self.__font = font
        self.__font_color = font_color
        self.__background_color = background_color
        self.__blink_at = blink_at
        self.__format_string = format_string

        self.__dirty = True

    def update(self):
        """Updates the timer in order to be drawn to a surface later on.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dirty:
            return
        
        color = self.__font_color
        
        if self.__blink_at > 0 and self._seconds_left <= self.__blink_at:
            if self._seconds_left % 2 == 0:
                color = self.__background_color
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = self.__font.render(self.__format_string.format(self._seconds_left), True , color)
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        # ** unpacks the dictionary to keyword arguments
        self.rect = self.image.get_rect(**self.__pos_dict)
        
        self.__dirty = False

    def countdown(self):
        if not self._started:
            return
        
        self.__dirty = True
        Timer.countdown(self)

class TimerCountdownEventHandler(object):
    def __init__(self, timer):
        self.__timer = timer
    
    def can_handle(self, event):
        if event.type != COUNTDOWN_EVENT:
            return False
        
        return self.__timer.is_started()
    
    def handle_event(self, event):
        self.__timer.countdown()
