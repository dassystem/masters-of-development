import pygame

class BaseScreen:
    DEACTIVE_SCREEN_EVENT = pygame.USEREVENT + 1
    
    def __init__(self, surface, event_handlers, active = False):
        self._surface = surface
        self.__event_handlers = event_handlers
        self.__active = active
        
    def get_event_handlers(self):
        return self.__event_handlers
    
    def is_active(self):
        return self.__active
    
    def set_active(self, active):
        self.__active = active
        
        if not self.__active:
            pygame.event.post(pygame.event.Event(BaseScreen.DEACTIVE_SCREEN_EVENT, {"screen": self}))
    
    def get_next_screen(self):
        return self.__next_screen
    
    def set_next_screen(self, next_screen):
        self.__next_screen = next_screen
    
    def render(self):
        if not self.__active:
            return

class BaseScreenEventHandler:
    def __init__(self, screen):
        self.__screen = screen

    def get_screen(self):
        return self.__screen;

    def can_handle(self, event):
        return self.__screen.is_active()

    def handle_event(self, event):
       pass
