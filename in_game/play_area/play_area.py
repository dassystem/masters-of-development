import pygame

from colors import DARK_GRAY, GREEN, RED, WHITE
from commons.text_sprite import TextSprite

from in_game.play_area.block_area import BlockArea

from in_game.play_area.event_handlers.player_joystick_event_handler import PlayerJoystickEventHandler
from in_game.play_area.event_handlers.player_keyboard_event_handler import PlayerKeyboardEventHandler

from in_game.play_area.sprites.block import Block
from in_game.play_area.sprites.debug_info import DebugInfo
from in_game.play_area.sprites.line_number import LineNumber
from in_game.play_area.sprites.power_up_jump import PowerUpJump
from in_game.play_area.sprites.power_up_shield import PowerUpShield
from in_game.play_area.sprites.score import Score

from leaderboard import Keyboard

class GroupSingleAnyRect(pygame.sprite.GroupSingle):
    def __init__(self, sprite = None):
        super(GroupSingleAnyRect, self).__init__(sprite)
        
    def draw(self, surface, rect):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, rect)
        self.lostsprites = []

class PlayArea(object):
    """A area where a player is playing."""
    
    LEFT_MARGIN = 85
    TOP_MARGIN = 35

    key_mappings = [
        {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d
        },
        {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT
        }
    ]
    
    def __init__(self, screen, surface, fonts, sounds, images, player):
        self.__screen = screen
        self.__surface = surface
        self.__fonts = fonts
        self.__sounds = sounds
        self.__images = images
        self.__keyboard = Keyboard(
            screen,
            surface,
            player,
            self.__fonts,
            WHITE)

        for event_handler in self.__keyboard.get_event_handlers():
            screen.add_event_handler(event_handler)

        block_rect = surface.get_rect(
            topleft = (PlayArea.LEFT_MARGIN, PlayArea.TOP_MARGIN),
            width = surface.get_width() - PlayArea.LEFT_MARGIN,
            height = surface.get_height() - PlayArea.TOP_MARGIN)
        block_surface = surface.subsurface(block_rect)
        self.__block_area = BlockArea(self, block_surface, fonts, images, sounds, player)
        
        player_string = "PLAYER {0:d}: ".format(player.get_number())
        size = self.__fonts["big"].size(player_string)
        initial_pos = (self.__surface.get_width() // 2 - size[0], 5)
        self.__player_text = pygame.sprite.GroupSingle(TextSprite(initial_pos, player_string, self.__fonts["big"], GREEN))
        
        initial_pos = (self.__surface.get_width() // 2, 5)
        score = Score(initial_pos, fonts["big"], sounds["score"])
        self.__score = pygame.sprite.GroupSingle(score)
        
        self.__debug_info = pygame.sprite.GroupSingle(DebugInfo(self, fonts))
        self.__scroll_velocity = 8
        self.__line_numbers = pygame.sprite.OrderedUpdates()
        self.__active_power_up_jump = GroupSingleAnyRect()
        self.__active_power_up_shield = GroupSingleAnyRect()
        
        self.__game_over_score = pygame.sprite.GroupSingle()
        
        # (735 - 35) / 32 = 22 
        self.__max_line_numbers = round((surface.get_height() - PlayArea.TOP_MARGIN) / Block.BLOCK_HEIGHT)
        
        if player.get_joystick() is not None:
            screen.add_event_handler(PlayerJoystickEventHandler(screen, player.get_joystick(), player))
        event_handler = PlayerKeyboardEventHandler(
            screen, PlayArea.key_mappings[player.get_number() - 1], player)
        screen.add_event_handler(event_handler)
        
    def reset(self):
        """Resets the state of the play area so that it can be (re-) used for a new game.
        
           Resets the player and generates new blocks.
        """
        self.__block_area.reset()
        self.__score.sprite.reset()
        self.__line_numbers.empty()
        self.__generate_line_numbers()
        
        self.__game_over_bg = None
        self.__game_over_score.empty()
        self.__keyboard.reset()
        
        pygame.draw.rect(
            self.__surface,
            DARK_GRAY,
            pygame.Rect(0, 0, self.__surface.get_width(), PlayArea.TOP_MARGIN)
        )
        pygame.draw.rect(
            self.__surface,
            DARK_GRAY,
            pygame.Rect(0, PlayArea.TOP_MARGIN, PlayArea.LEFT_MARGIN, self.__surface.get_height())
        )
    
    def __generate_line_numbers(self):
        new_lines = self.__max_line_numbers - len(self.__line_numbers)

        if new_lines <= 0:
            return
        
        highest_line_number = 0
        
        if self.__line_numbers:
            highest_line_number = self.__line_numbers.sprites()[-1].get_number()
        
        dy = new_lines * Block.BLOCK_HEIGHT
        
        for i in range(highest_line_number + 1, highest_line_number + new_lines + 1):
            new_line_number = LineNumber(i, dy, PlayArea.LEFT_MARGIN, self.__fonts)
            self.__line_numbers.add(new_line_number)
            dy -= Block.BLOCK_HEIGHT

    def scroll(self, seconds):
        self.__line_numbers.update(self.__scroll_velocity, self.__surface.get_height(), seconds)

    def switch_debug(self):
        """Switches the debug information on/off."""
        self.__debug_info.sprite.switch_visibility()
      
    def update(self, seconds):
        """Updates all sprites and draws them on the play area. Scrolls if necessary.
           see also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        
        if self.get_player().is_dead():
            self.__render_game_over()
            return
        
        self.__line_numbers.clear(self.__surface, fill_with_dark_gray)
        self.__player_text.clear(self.__surface, fill_with_dark_gray)
        self.__score.clear(self.__surface, fill_with_dark_gray)
        self.__debug_info.clear(self.__surface, fill_with_dark_gray)
        self.__active_power_up_jump.clear(self.__surface, fill_with_dark_gray)
        self.__active_power_up_shield.clear(self.__surface, fill_with_dark_gray)
        
        self.__block_area.update(seconds)
        self.__generate_line_numbers()
        
        self.__debug_info.update(seconds)

        self.__add_active_power_ups()

        self.__player_text.draw(self.__surface)
        self.__score.draw(self.__surface)
        self.__line_numbers.draw(self.__surface)
        
        if self.__debug_info.sprite.is_visible():
            self.__debug_info.draw(self.__surface)

        self.__draw_active_power_ups(self.__player_text.sprite.rect)
       
    def __add_active_power_ups(self):
        player_power_ups = self.get_player().get_power_ups()
        
        if not bool(self.__active_power_up_jump) and PowerUpJump.NAME in player_power_ups:
            power_ups = player_power_ups[PowerUpJump.NAME]
            
            if len(power_ups) > 0:
                self.__active_power_up_jump.add(power_ups[0])
        
        if not bool(self.__active_power_up_shield) and PowerUpShield.NAME in player_power_ups:
            power_ups = player_power_ups[PowerUpShield.NAME]
            
            if len(power_ups) > 0:
                self.__active_power_up_shield.add(power_ups[0])

    def __draw_active_power_ups(self, text_rect):
        if bool(self.__active_power_up_jump):
            original_rect = self.__active_power_up_jump.sprite.rect
            self.__active_power_up_jump.draw(self.__surface, text_rect.move((original_rect.width + 5) * -2, -4))
        
        if bool(self.__active_power_up_shield):
            original_rect = self.__active_power_up_shield.sprite.rect
            self.__active_power_up_shield.draw(self.__surface, text_rect.move((original_rect.width + 5) * -1, -4))
            
    def __render_game_over(self):
        if  self.__game_over_bg is not None and not self.get_screen().all_dead():
            return
                
        if self.get_screen().all_dead():
            other_player = None
            score_color = None
            
            if self.get_player().get_number() == 1:
                other_player = self.get_screen().get_players()[1]
            else:
                other_player = self.get_screen().get_players()[0]
            
            if self.get_player().get_score() > other_player.get_score():
                self.__game_over_bg = self.__images["in_game_screen_win_bg"]
                score_color = GREEN
                self.__screen.play_ending_sound(self.get_player())
            elif self.get_player().get_score() < other_player.get_score():
                self.__game_over_bg = self.__images["in_game_screen_loose_bg"]
                score_color = RED
                self.__screen.play_ending_sound(other_player)
            else:
                # draw
                self.__game_over_bg = self.__images["in_game_screen_win_bg"]
                score_color = GREEN
                self.__screen.set_ending_sound_played()
            
            score_string = str(self.get_player().get_score())
            score_size = self.__fonts["big"].size(score_string)
            initial_pos = (426 - score_size[0]  // 2, 604 - score_size[1] // 2)
            self.__game_over_score.add(TextSprite(initial_pos, score_string, self.__fonts["big"], score_color))
                
            self.get_screen().set_keyboard_states()
        else:
            self.__game_over_bg = self.__images["in_game_screen_game_over_bg"]
        
        self.__surface.blit(self.__game_over_bg, (0, 0))
        self.__keyboard.render()
        
        self.__game_over_score.draw(self.__surface)
    
    def get_player(self):
        return self.__block_area.get_player()
    
    def get_scroll_velocity(self):
        return self.__scroll_velocity
    
    def get_score(self):
        return self.__score.sprite
    
    def __get_active_power_ups(self):
        return self.__active_power_ups.sprites()
    
    def get_screen(self):
        return self.__screen
    
    def get_surface(self):
        return self.__surface
    
    def get_keyboard(self):
        return self.__keyboard

def fill_with_dark_gray(surface, rect):
    """see https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.clear"""
    surface.fill(DARK_GRAY, rect)
