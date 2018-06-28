import pygame
import masters_of_development
from utils import Utils
import utils.timer
from screens.base import BaseScreen, BaseScreenEventHandler

class StartScreen(BaseScreen):
    def __init__(self, surface, fonts, players, seconds = 5):
        super(StartScreen, self).__init__(surface, [StartScreenEventHandler(self, players)], True)

        self.__fonts = fonts;

        self.__text_title_1 = fonts["big"].render("Masters", True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        self.__text_title_2 = fonts["big"].render("of" , True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        self.__text_title_3 = fonts["big"].render("Development", True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        
        self.__text_player_1 = fonts["small"].render("PLAYER 1", True, masters_of_development.MastersOfDevelopment.TARENT_GREY)
        self.__text_player_2 = fonts["small"].render("PLAYER 2", True, masters_of_development.MastersOfDevelopment.TARENT_GREY)

        self.__text_start = fonts["small"].render("START", True, masters_of_development.MastersOfDevelopment.TARENT_GREY)
        self.__text_ready = fonts["small"].render("READY", True, masters_of_development.MastersOfDevelopment.TARENT_GREY)
        
        self.__players = players
        
        timer = utils.timer.SpriteTimer(
            "start",
            seconds,
            {"center": surface.get_rect().center},
            fonts["big"],
            masters_of_development.MastersOfDevelopment.BLACK)
        
        self.__timer = pygame.sprite.GroupSingle(timer)
        self.__start_sound = pygame.mixer.Sound("assets/sounds/start_game.wav")
  
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
        
        self._surface.fill(masters_of_development.MastersOfDevelopment.WHITE)
        
        x = self._surface.get_width() // 4
        y = self._surface.get_height() // 4
        
        rect_title_2 = self.__text_title_2.get_rect(center = (x * 2, y))
        self._surface.blit(self.__text_title_2, rect_title_2)
        
        rect_title_1 = self.__text_title_1.get_rect(center = (rect_title_2.centerx, rect_title_2.centery - self.__text_title_1.get_height()))
        self._surface.blit(self.__text_title_1, rect_title_1)
        
        rect_title_3 = self.__text_title_3.get_rect(center = (rect_title_2.centerx, rect_title_2.centery + self.__text_title_3.get_height()))
        self._surface.blit(self.__text_title_3, rect_title_3)

        rect_player_1 = self.__text_player_1.get_rect(center = (x, y * 3 - self.__text_player_1.get_height()))
        self._surface.blit(self.__text_player_1, rect_player_1)

        rect_player_2 = self.__text_player_2.get_rect(center = (x * 3, y * 3 - self.__text_player_2.get_height()))
        self._surface.blit(self.__text_player_2, rect_player_2)
        
        text = None
        rect = None
        
        if self.__players[0].is_ready():
            text = self.__text_ready
            rect = text.get_rect(
                center = (rect_player_1.centerx, rect_player_1.centery + text.get_height()))
        else:
            text = self.__text_start
            rect = text.get_rect(
                center = (rect_player_1.centerx, rect_player_1.centery + text.get_height()))
        
        self._surface.blit(text, rect)
        
        if self.__players[1].is_ready():
            text = self.__text_ready
            rect = text.get_rect(
                center = (rect_player_2.centerx, rect_player_2.centery + text.get_height()))
        else:
            text = self.__text_start
            rect = text.get_rect(
                center = (rect_player_2.centerx, rect_player_2.centery + text.get_height()))
        
        self._surface.blit(text, rect)
        
        if self.__get_timer().is_started():
            self.render_countdown();

    def render_countdown(self):
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
