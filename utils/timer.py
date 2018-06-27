import pygame

class Timer(pygame.sprite.Sprite):
    """A sprite representing a timer."""
    
    COUNTDOWN_EVENT = pygame.USEREVENT + 2
    ELASPED_EVENT = pygame.USEREVENT + 3
    
    def __init__(self, initial_seconds, pos_dict, font, font_color, background_color = None, blink_at = 0, format_string = "{0:d}"):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Timer, self).__init__()
        
        self.__initial_seconds = initial_seconds
        self.__pos_dict = pos_dict
        self.__font = font
        self.__font_color = font_color
        self.__background_color = background_color
        self.__blink_at = blink_at
        self.__format_string = format_string
        self.__started = False
        self.__seconds_left = 0
        self.__event_handler = TimerCountdownEventHandler(self)
        self.__dirty = True

    def update(self):
        """Updates the timer in order to be drawn to a surface later on.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dirty:
            return
        
        color = self.__font_color
        
        if self.__blink_at > 0 and self.__seconds_left <= self.__blink_at:
            if self.__seconds_left % 2 == 0:
                color = self.__background_color
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute image
        self.image = self.__font.render(self.__format_string.format(self.__seconds_left), True , color)
        
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        # ** unpacks the dictionary to keyword arguments
        self.rect = self.image.get_rect(**self.__pos_dict)
        
        self.__dirty = False

    def get_event_handler(self):
        return self.__event_handler
        
    def get_seconds_left(self):
        return self.__seconds_left

    def is_started(self):
        return self.__started

    def start(self):
        if not self.__started:
            self.__started = True
            self.__seconds_left = self.__initial_seconds
            pygame.time.set_timer(Timer.COUNTDOWN_EVENT, 1000)

    def stop(self):
        pygame.time.set_timer(Timer.COUNTDOWN_EVENT, 0)
        self.__started = False
    
    def countdown(self):
        if not self.__started:
            return
        
        self.__seconds_left -= 1
        self.__dirty = True
        
        if self.__seconds_left <= 0:
            self.stop()
            pygame.event.post(pygame.event.Event(Timer.ELASPED_EVENT, {"timer": self}))

class TimerCountdownEventHandler(object):
    def __init__(self, timer):
        self.__timer = timer
    
    def can_handle(self, event):
        return event.type == Timer.COUNTDOWN_EVENT and self.__timer.is_started()
    
    def handle_event(self, event):
        self.__timer.countdown()
