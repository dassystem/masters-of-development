import pygame

class Timer(object):
    COUNTDOWN_EVENT = pygame.USEREVENT + 2
    ELASPED_EVENT = pygame.USEREVENT + 3
    
    def __init__(self, initial_seconds):
        self.__initial_seconds = initial_seconds
        self.__started = False
        self.__seconds_left = 0
        self.__event_handler = TimerCountdownEventHandler(self)

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
