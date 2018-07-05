import pygame
from utils import Utils
import utils.timer
from screens.base import BaseScreen, BaseScreenEventHandler

class StartScreen(BaseScreen):
    def __init__(self, surface, fonts, sounds, images, players, seconds = 3):
        super(StartScreen, self).__init__(surface, [StartScreenEventHandler(self, players)], True)

        self.__fonts = fonts;

        self.__images = images
        
        self.__players = players
        
        timer_images = {}
        
        timer_images["countdown_0"] = images["start_screen_countdown_go"]

        for i in range(1, 4):
            timer_images["countdown_{0:d}".format(i)] = images["start_screen_countdown_{0:d}".format(i)]
        
        timer = utils.timer.ImageSpriteTimer(
            "start",
            seconds,
            {"center": surface.get_rect().center},
            sounds,
            timer_images)
        
        self.__timer = pygame.sprite.GroupSingle(timer)
        self.__start_sound = sounds["start_game"]
  
    def set_player_ready(self, player_number):
        self.__players[player_number].set_ready(True)
        
        if self.all_players_ready():
            self.__start_sound.play()
            self.__get_timer().start()
            self.add_event_handler(self.__get_timer().get_event_handler())
  
    def all_players_ready(self):
        all_players_ready = True
        
        for player in self.__players:
            all_players_ready = all_players_ready and player.is_ready()

        return all_players_ready
  
    def countdown(self):
        self.__get_timer().countdown()
  
    def set_active(self, active):
        super().set_active(active)
        
        if not self.is_active():
            self.remove_event_handler(self.__get_timer().get_event_handler())
    
    def render(self):
        if not self.is_active():
            return
        
        if self.__get_timer().is_started():
            self.render_countdown();
        else:
            self._surface.blit(self.__images["start_screen_bg"], (0, 0))
            
            rect_player_1 = self.__images["start_screen_player_1"].get_rect(topleft = (450, 740))
            self._surface.blit(self.__images["start_screen_player_1"], rect_player_1)
    
            rect_player_2 = self.__images["start_screen_player_2"].get_rect(topleft = (1185, 740))
            self._surface.blit(self.__images["start_screen_player_2"], rect_player_2)
    
            image = None
            rect = None
            
            if self.__players[0].is_ready():
                image = self.__images["start_screen_start_pushed"]

            else:
                image = self.__images["start_screen_start_normal"]

            rect = image.get_rect(topleft = (450, 860))
            
            self._surface.blit(image, rect)
            
            if self.__players[1].is_ready():
                image = self.__images["start_screen_start_pushed"]
            else:
                image = self.__images["start_screen_start_normal"]
            
            rect = image.get_rect(topleft = (1185, 860))
            
            self._surface.blit(image, rect)

    def render_countdown(self):
        self._surface.blit(self.__images["start_screen_countdown_bg"], (0, 0))
        
        self.__timer.update()
        self.__timer.draw(self._surface)

    def __get_timer(self):
        """Get the timer out of the sprite group."""
        return self.__timer.sprite

class StartScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, start_screen, players):
        super(StartScreenEventHandler, self).__init__(start_screen)
        self.__players = players
        
        self.__joysticks =  []
        for player in players:
            self.__joysticks.append(player.get_joystick())
        
    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN or event.type == utils.timer.ELAPSED_EVENT

    def handle_event(self, event):
        if self.get_screen().all_players_ready():
            if event.type == utils.timer.ELAPSED_EVENT:
                self.get_screen().set_active(False)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.get_screen().set_player_ready(0)
                elif event.key == pygame.K_UP:
                    self.get_screen().set_player_ready(1)
            elif event.type == pygame.JOYBUTTONDOWN:
                player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)
    
                if player is not None:
                    self.get_screen().set_player_ready(player.get_number() - 1)
