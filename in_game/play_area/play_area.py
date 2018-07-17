import pygame

from colors import DARK_GRAY, GREEN, RED, WHITE

from in_game.play_area.block_area import BlockArea

from in_game.play_area.event_handlers.player_joystick_event_handler import PlayerJoystickEventHandler
from in_game.play_area.event_handlers.player_keyboard_event_handler import PlayerKeyboardEventHandler

from in_game.play_area.sprites.block import Block
from in_game.play_area.sprites.debug_info import DebugInfo
from in_game.play_area.sprites.line_number import LineNumber
from in_game.play_area.sprites.score import Score

from leaderboard import Keyboard

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
        
        self.__text = self.__fonts["big"].render(
            "PLAYER {0:d}: ".format(player.get_number()), True, GREEN)
        self.__score = pygame.sprite.GroupSingle(Score(fonts["big"], sounds["score"]))
        
        self.__debug_info = pygame.sprite.GroupSingle(DebugInfo(self, fonts))
        self.__scroll_velocity = 8
        self.__line_numbers = pygame.sprite.OrderedUpdates()
        
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
        self.__keyboard.reset()
    
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
        
        self.__block_area.update(seconds)
        self.__generate_line_numbers()
        self.__render_line_numbers()
        
        text_rect = self.__text.get_rect(topright = (self.__surface.get_width() // 2, 5))
        self.__surface.blit(self.__text, text_rect)
        
        self.__score.update(self.__surface)
        self.__debug_info.update(seconds)

        self.__score.draw(self.__surface)
        
        if self.__debug_info.sprite.is_visible():
            self.__debug_info.draw(self.__surface)
        
        power_ups = self.get_player().get_power_ups()
            
        if "power_up_bug_resistant" in power_ups:
            same_power_ups = power_ups["power_up_bug_resistant"]
            if len(same_power_ups) > 0:
                self.__render_bug_resistant(same_power_ups[0], text_rect)
        if "power_up_jump" in power_ups:
            same_power_ups = power_ups["power_up_jump"]
            if len(same_power_ups) > 0:
                self.__render_double_jump(same_power_ups[0], text_rect)

    def __render_bug_resistant(self, power_up, text_rect):
        rect = text_rect.move((power_up.rect.width + 5) * -1, -4)
        self.__surface.blit(power_up.image, rect)
    
    def __render_double_jump(self, power_up, text_rect):
        rect = text_rect.move((power_up.rect.width + 5) * -2, -4)
        self.__surface.blit(power_up.image, rect)

    def __render_game_over(self):
        bg = None
        text = None
        
        if self.get_screen().all_dead():
            other_player = None
            score_color = None
            
            if self.get_player().get_number() == 1:
                other_player = self.get_screen().get_players()[1]
            else:
                other_player = self.get_screen().get_players()[0]
            
            if self.get_player().get_score() > other_player.get_score():
                bg = self.__images["in_game_screen_win_bg"]
                score_color = GREEN
                self.__screen.play_ending_sound(self.get_player())
            elif self.get_player().get_score() < other_player.get_score():
                bg = self.__images["in_game_screen_loose_bg"]
                score_color = RED
                self.__screen.play_ending_sound(other_player)
            else:
                # draw
                bg = self.__images["in_game_screen_win_bg"]
                score_color = GREEN
                self.__screen.set_ending_sound_played()
                
            text = self.__fonts["big"].render(str(self.get_player().get_score()), True, score_color)
            
            self.get_screen().set_keyboard_states()
        else:
            bg = self.__images["in_game_screen_game_over_bg"]
        
        self.__surface.blit(bg, (0, 0))
        self.__keyboard.render()
        
        if text is not None:
            self.__surface.blit(text, text.get_rect(center = (426, 604)))
    
    def __render_line_numbers(self):
        self.__line_numbers.draw(self.__surface)

    def get_player(self):
        return self.__block_area.get_player()
    
    def get_scroll_velocity(self):
        return self.__scroll_velocity
    
    def get_score(self):
        return self.__score.sprite
    
    def get_screen(self):
        return self.__screen
    
    def get_surface(self):
        return self.__surface
    
    def get_keyboard(self):
        return self.__keyboard
