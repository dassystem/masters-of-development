from screens.base import BaseScreen, BaseScreenEventHandler
import tarentjumper
from utils import Utils
import pygame

class CountdownScreen(BaseScreen):
    def __init__(self, surface, font, seconds = 5):
        BaseScreen.__init__(self, surface, [CountdownScreenEventHandler(self)])
        self.__font = font
        self.__seconds = seconds
        self.__timer_started = False
        
    def set_active(self, active):
        BaseScreen.set_active(self, active)
        
        if self.is_active():
            self.__start_timer()
        else:
            self.__stop_timer()
    
    def __start_timer(self):
        if not self.__timer_started:
            self.__timer_started = True
            self.__seconds_left = self.__seconds
            pygame.time.set_timer(pygame.USEREVENT, 1000)

    def __stop_timer(self):
        pygame.time.set_timer(pygame.USEREVENT, 0)
        self.__timer_started = False
    
    def countdown(self):
        self.__seconds_left -= 1
        
        self.set_active(self.__seconds_left > 0)
    
    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(tarentjumper.TarentJumper.BACKGROUND_COLOR)

        countdown_txt = self.__font.render("Games starts in", True, tarentjumper.TarentJumper.BLACK)
        countdown_txt_rect = Utils.center_with_offset(countdown_txt, self._surface, 0, 100)
        self._surface.blit(countdown_txt, countdown_txt_rect)

        time_txt = self.__font.render(str(self.__seconds_left), True, tarentjumper.TarentJumper.BLACK)
        time_txt_rect = Utils.center_with_offset(time_txt, self._surface, 0 , 150)
        time_txt_rect.move_ip(0, 200)
        
        self._surface.blit(time_txt, time_txt_rect)

class CountdownScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, count_down_screen):
        BaseScreenEventHandler.__init__(self, count_down_screen)
    
    def can_handle(self, event):
        if not BaseScreenEventHandler.can_handle(self, event):
            return False
        
        return event.type == pygame.USEREVENT
    
    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.USEREVENT:
            self.get_screen().countdown()
