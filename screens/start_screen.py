import pygame
import masters_of_development
from utils import Utils
from screens.base import BaseScreen, BaseScreenEventHandler

class StartScreen(BaseScreen):
    def __init__(self, surface, fonts):
        super(StartScreen, self).__init__(surface, [StartScreenEventHandler(self)], True)

        self.__start_title = fonts["big"].render("Masters of Development", True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        self.__start_hint = fonts["small"].render("Press Button or Enter to start the game", True, masters_of_development.MastersOfDevelopment.TARENT_GREY)
        self.__start_sound = pygame.mixer.Sound("assets/sounds/start_game.wav")
  
    def start(self):
        self.__start_sound.play()
        self.set_active(False)
    
    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(masters_of_development.MastersOfDevelopment.WHITE)
        
        start_title_rect = Utils.center(self.__start_title, self._surface)
        start_title_rect.move_ip(0, -100)
        
        self._surface.blit(self.__start_title, start_title_rect)
        
        start_hint_rect = Utils.center(self.__start_hint, self._surface)
        start_hint_rect.move_ip(0, 50)
        
        self._surface.blit(self.__start_hint, start_hint_rect)

class StartScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, start_screen):
        super(StartScreenEventHandler, self).__init__(start_screen)
        
    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN or event.type == pygame.JOYBUTTONDOWN:
            self.get_screen().start()
