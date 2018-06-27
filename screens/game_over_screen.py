import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
import utils

class GameOverScreen(BaseScreen):
    def __init__(self, surface, players, fonts, font_color, background_color, sounds):
        super(GameOverScreen, self).__init__(surface, [GameOverScreenEventHandler(self)])
        self.__players = players
        self.__font = fonts["small"]
        self.__font_color = font_color
        self.__background_color = background_color
        self.__sounds = sounds
    
    def set_active(self, active):
        super().set_active(active)
        
        self.__dirty = active
    
    def render(self):
        if not self.is_active() or not self.__dirty:
            return
        
        self._surface.fill(self.__background_color)
        
        winner = None
        looser = None
        
        if self.__players[0].get_score() > self.__players[1].get_score():
            winner = self.__players[0]
            looser = self.__players[1]
            self.__sounds["player1wins"].play()
        elif self.__players[0].get_score() < self.__players[1].get_score():
            winner = self.__players[1]
            looser = self.__players[0]
            self.__sounds["player2wins"].play()
        
        if winner is None:
            text_1 = "draw"
            text_2 = "draw"
        else:
            text_1 = "Congratulations player " + str(winner.get_number()) + ", your score " + str(winner.get_score())
            text_2 = "Sorry player " + str(looser.get_number()) + ", your score " + str(looser.get_score())
        
        surface_text_1 = self.__font.render(text_1, True, self.__font_color)
        
        rect_text_1 = utils.Utils.center(surface_text_1, self._surface)
        rect_text_1.move_ip(0, -surface_text_1.get_height() // 2)
        
        self._surface.blit(surface_text_1, rect_text_1)
        
        surface_text_2 = self.__font.render(text_2, True, self.__font_color)
        
        rect_text_2 = utils.Utils.center(surface_text_2, self._surface)
        rect_text_2.move_ip(0, surface_text_1.get_height() // 2)
        
        self._surface.blit(surface_text_2, rect_text_2)
        self.__dirty = False
    
class GameOverScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, game_over_screen):
        super(GameOverScreenEventHandler, self).__init__(game_over_screen)
        
    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN
        
    def handle_event(self, event):
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.get_screen().set_active(False)
