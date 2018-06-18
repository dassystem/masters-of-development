import pygame
from screens.base import BaseScreen, BaseScreenEventHandler
from utils import Utils
import tarentjumper

class GetReadyScreen(BaseScreen):
    def __init__(self, surface, players, font):
        BaseScreen.__init__(self, surface, [GetReadyScreenEventHandler(self)])
        self.__players = players
        self.__player_screens = Utils.split_screen(self._surface)
        
        self.__font = font

    def set_player_ready(self, player_number):
        self.__players[player_number].set_ready(True)
        
        all_players_ready = True
        
        for player in self.__players:
            all_players_ready = all_players_ready and player.is_ready()
            
        self.set_active(not all_players_ready)
    
    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(tarentjumper.TarentJumper.BACKGROUND_COLOR)
        
        #TODO change text to (Player X is ready!)
        for index, player_screen in enumerate(self.__player_screens):
            if self.__players[index].is_ready():
                text = "Ready player "
                hint1 = None
                hint2 = None
            else:
                text = "Get ready player "
                if index == 0:
                    hint1 = "Press any button"
                    hint2 = "or W to get ready!"
                else:
                    hint1 = "Press any button"
                    hint2 = "or UP to get ready!"
            
            text += str(index + 1)
                
            text_surface = self.__font.render(text, True, tarentjumper.TarentJumper.TARENT_RED)
            text_surface_rect = Utils.center(text_surface, player_screen)
            player_screen.blit(text_surface, text_surface_rect)

            if not hint1 is None:
                text_surface_hint1 = self.__font.render(hint1, True , tarentjumper.TarentJumper.TARENT_RED)
                text_rect_hint1 = Utils.center(text_surface_hint1, player_screen)
                text_rect_hint1.move_ip(0, text_surface_rect.height)
                player_screen.blit(text_surface_hint1, text_rect_hint1)
                
                text_surface_hint2 = self.__font.render(hint2, True , tarentjumper.TarentJumper.TARENT_RED)
                text_rect_hint2 = Utils.center(text_surface_hint2, player_screen)
                text_rect_hint2.move_ip(0, text_surface_rect.height + text_rect_hint1.height)
                player_screen.blit(text_surface_hint2, text_rect_hint2)
    
class GetReadyScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, ready_screen):
        BaseScreenEventHandler.__init__(self, ready_screen)
    
    def can_handle(self, event):
        if not BaseScreenEventHandler.can_handle(self, event):
            return False
    
        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN
    
    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.get_screen().set_player_ready(0)
            elif event.key == pygame.K_UP:
                self.get_screen().set_player_ready(1)
        elif event.type == pygame.JOYBUTTONDOWN:
            player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)

            if player is not None:
                self.get_screen().set_player_ready(player.getNumber())
